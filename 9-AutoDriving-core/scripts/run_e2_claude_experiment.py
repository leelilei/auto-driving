#!/usr/bin/env python3
"""Run E2 Experiment for Claude Models (Haiku 4.5 & Sonnet 4.6).

Performs exploratory cross-family evaluation on DARC-Route E2 confirmation set.
Includes:
- Robust JSON extraction (immune to markdown fences & trailing comments)
- Full token usage tracking (mapped from input_tokens/output_tokens)
- Returned model tracking in call records
- Strict immutable route_key normalization
- Hard assertion of candidate_A/B non-null in Review Prompt
- Support for pilot (e.g. 4 groups) and full 40 groups
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import generate_synthetic_graph, SyntheticGraph
from src.solver import ExactRouteSolver, RouteResult
from src.intent import Intent
from src.evaluation import check_route
from src.gating import (
    execute_method_decision,
    compute_protection_trigger,
    compute_cross_utility_delta,
    calculate_route_utility,
    calculate_route_regret,
)
from src.metrics import (
    compute_tsr,
    compute_gtsr,
    compute_route_flip,
    compute_paired_bootstrap,
)
from src.llm_client import LLM, load_config

SCHEMA = '''Extract only the route intent supported by the user's instruction.
Return one JSON object with required keys:
pois: array of requested categories, limited to shopping_mall, supermarket, pharmacy, bank, library;
time_limit: latest return time as integer minutes from midnight (11 PM = 1380), or null if absent;
dependencies: array of [before_category, after_category] pairs for explicit ordering only;
quality_weight: number between 0 and 1, with implied distance_weight = 1-quality_weight.
Use quality_weight > 0.5 for quality/rating priority, < 0.5 for route efficiency/distance priority,
and 0.5 for a balanced preference. Do not infer exact numerical weights from nonexistent evidence.
Do not add an ordering just because places are listed in a particular order.
Do not invent deadlines, new destinations, modes of travel, or constraints.
'''

PROMPTS = {
    "A": SCHEMA + "Extract the fields directly and return only the JSON object.",
    "B": SCHEMA + "Check each field against an exact short span from the instruction. Add an evidence object of short quotations. Return JSON only.",
    "review": SCHEMA + "Reconsider the two candidate interpretations against the original instruction. Neither candidate is guaranteed correct. Return a single complete corrected intent and an evidence object of short quotations. No route decisions are provided or needed.",
}


def route_key(r: Any) -> Tuple[str, ...]:
    """Strictly normalize poi_ids to an immutable tuple of strings."""
    if r is None:
        return ()
    if isinstance(r, dict):
        return tuple(str(x) for x in r.get("poi_ids", ()))
    return tuple(str(x) for x in getattr(r, "poi_ids", ()))


def extract_and_clean_json(raw: str) -> str:
    """Robustly extract JSON object from raw response text, ignoring code blocks or trailing text."""
    text = raw.strip()
    # 1. Search for markdown code block enclosing JSON object
    m_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m_block:
        return m_block.group(1).strip()
    # 2. Search for outermost curly braces
    m_obj = re.search(r"(\{.*\})", text, re.DOTALL)
    if m_obj:
        return m_obj.group(1).strip()
    return text


def normalize_parsed_intent_dict(data: Any) -> Any:
    """Unwrap nested intent and sanitize invalid dependency pairs."""
    if not isinstance(data, dict):
        return data
    required = {"pois", "time_limit", "dependencies", "quality_weight"}
    if not required <= data.keys():
        for k in ["intent", "parsed_intent", "extracted_intent", "route_intent"]:
            if k in data and isinstance(data[k], dict) and required <= data[k].keys():
                data = dict(data[k])
                break
    # Sanitize dependencies: filter out pairs with None or non-string elements
    if "dependencies" in data and isinstance(data["dependencies"], list):
        cleaned_deps = []
        for dep in data["dependencies"]:
            if isinstance(dep, (list, tuple)) and len(dep) == 2:
                if isinstance(dep[0], str) and isinstance(dep[1], str):
                    cleaned_deps.append(list(dep))
        data["dependencies"] = cleaned_deps
    return data


def write_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def run_utterance(
    record: dict[str, Any],
    graph: SyntheticGraph,
    solver: ExactRouteSolver,
    config: Any,
) -> dict[str, Any]:
    gid = record["group_id"]
    uid = record["utterance_id"]
    v_type = record["variant_type"]
    text = record["text"]
    gh = record["gold_hard"]

    gold = Intent.parse({
        "pois": gh["pois"],
        "time_limit": gh["time_limit"],
        "dependencies": gh["dependencies"],
        "quality_weight": record["w_synthetic"],
    })
    oracle_route = solver.solve(**gold.solver_args())

    res: dict[str, Any] = {
        "group_id": gid,
        "utterance_id": uid,
        "variant_type": v_type,
        "source_index": record["source_index"],
        "source_cluster_id": record["source_cluster_id"],
        "text": text,
        "gold_intent": asdict(gold),
        "oracle_route": asdict(oracle_route) if oracle_route else None,
        "oracle_check": check_route(graph, oracle_route, gold),
        "calls": {},
        "candidates": {},
        "routes": {},
    }

    llm = LLM(config)
    candidates: dict[str, Intent | None] = {}
    raw_candidates: dict[str, Any] = {}

    for method in ["A", "B", "review"]:
        if method != "review":
            user_msg = text
        else:
            cand_a_dict = raw_candidates.get("A")
            cand_b_dict = raw_candidates.get("B")
            if cand_a_dict is None or cand_b_dict is None:
                raise ValueError(f"[CONTRACT_VIOLATION] Review requires valid candidates: A={cand_a_dict is not None}, B={cand_b_dict is not None} for {uid}")
            user_msg = json.dumps({
                "instruction": text,
                "candidate_A": cand_a_dict,
                "candidate_B": cand_b_dict,
            }, ensure_ascii=False)

        call_record: dict[str, Any] = {
            "method": method,
            "system_prompt": PROMPTS[method],
            "user_prompt": user_msg,
        }

        try:
            raw = llm.complete(PROMPTS[method], user_msg)
            call_record["raw_response"] = raw
            
            # Extract usage and normalize for Anthropic
            raw_usage = getattr(llm.client, "last_usage", None)
            if isinstance(raw_usage, dict):
                in_tok = raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0))
                out_tok = raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0))
                call_record["usage"] = {
                    "prompt_tokens": in_tok,
                    "completion_tokens": out_tok,
                    "total_tokens": in_tok + out_tok,
                    "raw": raw_usage,
                }
            else:
                call_record["usage"] = None

            # Extract returned model from response
            last_resp = getattr(llm.client, "last_response", None)
            if isinstance(last_resp, dict) and "model" in last_resp:
                call_record["returned_model"] = last_resp["model"]

            try:
                cleaned = extract_and_clean_json(raw)
                parsed = json.loads(cleaned)
                normalized_dict = normalize_parsed_intent_dict(parsed)
                cand = Intent.parse(normalized_dict)
                candidates[method] = cand
                raw_candidates[method] = asdict(cand)
                call_record["schema_valid"] = True
                call_record["parsed_intent"] = asdict(cand)
            except Exception as e:
                call_record["schema_valid"] = False
                call_record["parse_error"] = str(e)
                candidates[method] = None
                raw_candidates[method] = None
        except Exception as e:
            call_record["transport_error_type"] = type(e).__name__
            call_record["transport_error_message"] = str(e)
            candidates[method] = None
            raw_candidates[method] = None

        res["calls"][method] = call_record

    # Solve routes for A and B
    for m in ["A", "B"]:
        cand = candidates.get(m)
        r = solver.solve(**cand.solver_args()) if cand is not None else None
        res["routes"][m] = asdict(r) if r else None
        res["candidates"][m] = asdict(cand) if cand else None

    # Review candidate and route
    cand_rev = candidates.get("review")
    r_rev = solver.solve(**cand_rev.solver_args()) if cand_rev is not None else None
    res["routes"]["review"] = asdict(r_rev) if r_rev else None
    res["candidates"]["review"] = asdict(cand_rev) if cand_rev else None

    return res


def run_group(
    group_records: list[dict[str, Any]],
    config: Any,
    run_dir: Path,
) -> dict[str, Any]:
    gid = group_records[0]["group_id"]
    group_num = int(gid.split("_")[-1])
    seed = 6000 + group_num
    graph = generate_synthetic_graph(graph_id=f"{gid}_graph", seed=seed)
    graph_path = run_dir / f"{gid}_graph.json"
    graph.save(graph_path)
    graph = SyntheticGraph.load(graph_path)
    solver = ExactRouteSolver(graph)

    utterance_results = []
    for rec in group_records:
        u_res = run_utterance(rec, graph, solver, config)
        utterance_results.append(u_res)

    group_data = {
        "group_id": gid,
        "utterances_count": len(utterance_results),
        "utterances": utterance_results,
    }
    write_json(run_dir / f"{gid}.json", group_data)
    return group_data


def evaluate_run(run_dir: Path, model_name: str) -> dict[str, Any]:
    group_files = sorted([f for f in run_dir.glob("e2_clean_*.json") if not f.name.endswith("_graph.json")])
    flat_utts = []
    graphs = {}
    for gf in group_files:
        g_data = json.loads(gf.read_text(encoding="utf-8"))
        gid = g_data["group_id"]
        graph_path = run_dir / f"{gid}_graph.json"
        graphs[gid] = SyntheticGraph.load(graph_path)
        flat_utts.extend(g_data["utterances"])

    n_total = len(flat_utts)
    gids = sorted(list(set(u["group_id"] for u in flat_utts)))
    pair_variants = [("V0", "V1"), ("V0", "V2"), ("V0", "V3"), ("V1", "V2"), ("V1", "V3"), ("V2", "V3")]

    # Pre-solve fallback if review candidate is None
    for u in flat_utts:
        if not u["candidates"].get("review"):
            u["routes"]["review"] = u["routes"].get("A")

    items = []
    for idx, u in enumerate(flat_utts):
        gid = u["group_id"]
        uid = u["utterance_id"]
        graph = graphs[gid]
        solver = ExactRouteSolver(graph)
        gold = Intent.parse(u["gold_intent"])
        cands = {m: Intent.parse(u["candidates"][m]) if u["candidates"].get(m) else None for m in ["A", "B", "review"]}
        routes = {m: RouteResult(**u["routes"][m]) if u["routes"].get(m) else None for m in ["A", "B", "review"]}

        cand_a, cand_b = cands.get("A"), cands.get("B")
        r_a, r_b, r_rev = routes.get("A"), routes.get("B"), routes.get("review")

        h = compute_protection_trigger(cand_a, cand_b, r_a, r_b)
        delta_u = compute_cross_utility_delta(graph, cand_a, cand_b, r_a, r_b) if h == 0 else 0.0
        delta_sem = abs(cand_a.quality_weight - cand_b.quality_weight) if (h == 0 and cand_a and cand_b) else 0.0

        succ_a = check_route(graph, r_a, gold)["task_success"] if r_a else False
        succ_rev = check_route(graph, r_rev, gold)["task_success"] if r_rev else False

        oracle_route = solver.solve(**gold.solver_args())
        u_a = calculate_route_utility(graph, r_a, gold.quality_weight)
        u_rev = calculate_route_utility(graph, r_rev, gold.quality_weight)
        reg_a = calculate_route_regret(graph, oracle_route, r_a, gold.quality_weight)
        reg_rev = calculate_route_regret(graph, oracle_route, r_rev, gold.quality_weight)

        items.append({
            "index": idx,
            "uid": uid,
            "gid": gid,
            "v_type": u["variant_type"],
            "h": h,
            "delta_u": delta_u or 0.0,
            "delta_sem": delta_sem or 0.0,
            "r_a": r_a,
            "r_rev": r_rev,
            "key_a": route_key(r_a),
            "key_rev": route_key(r_rev),
            "succ_a": succ_a,
            "succ_rev": succ_rev,
            "u_a": u_a,
            "u_rev": u_rev,
            "reg_a": reg_a,
            "reg_rev": reg_rev,
            "gold": gold,
            "graph": graph,
            "calls_dict": u["calls"],
            "review_valid": bool(u["candidates"].get("review")),
        })

    h_indices = set(it["index"] for it in items if it["h"] == 1)
    non_h_items = [it for it in items if it["h"] == 0]

    # Online methods
    online_results = {}
    for om_name in ["B0", "B4_online", "DARC_online", "B6"]:
        choices = {}
        for it in items:
            if om_name == "B0":
                ch = False
            elif om_name == "B6":
                ch = True
            elif om_name == "B4_online":
                ch = (it["h"] == 1) or (it["delta_sem"] > 0.10)
            elif om_name == "DARC_online":
                ch = (it["h"] == 1) or (it["delta_u"] > 0.02)
            choices[it["index"]] = ch

        succs = [it["succ_rev"] if choices[it["index"]] else it["succ_a"] for it in items]
        keys = {(it["gid"], it["v_type"]): (it["key_rev"] if choices[it["index"]] else it["key_a"]) for it in items}
        succ_map = {(it["gid"], it["v_type"]): (it["succ_rev"] if choices[it["index"]] else it["succ_a"]) for it in items}
        utils = [it["u_rev"] if choices[it["index"]] else it["u_a"] for it in items]
        regrets = [it["reg_rev"] if choices[it["index"]] else it["reg_a"] for it in items]

        all_pairs = [(gid, v1, v2) for gid in gids for v1, v2 in pair_variants if (gid, v1) in keys and (gid, v2) in keys]
        common_pairs = [p for p in all_pairs if succ_map[(p[0], p[1])] and succ_map[(p[0], p[2])]]

        diff_common = [1 if keys[(p[0], p[1])] != keys[(p[0], p[2])] else 0 for p in common_pairs]
        pair_weighted_flip = statistics.mean(diff_common) if diff_common else 0.0

        g_diffs = defaultdict(list)
        for p in common_pairs:
            g_diffs[p[0]].append(1 if keys[(p[0], p[1])] != keys[(p[0], p[2])] else 0)
        group_macro_flip = statistics.mean([statistics.mean(v) for v in g_diffs.values()]) if g_diffs else 0.0

        online_results[om_name] = {
            "tsr": sum(succs) / len(succs),
            "degraded_count": sum(1 for it in items if it["succ_a"] and not (it["succ_rev"] if choices[it["index"]] else it["succ_a"])),
            "review_rate": sum(1 for it in items if choices[it["index"]]) / len(items),
            "common_pair_weighted_flip": pair_weighted_flip,
            "common_group_macro_flip": group_macro_flip,
            "mean_route_utility": statistics.mean(utils),
            "mean_regret": statistics.mean(regrets),
        }

    # Equal quota at 10%
    k10 = math.floor(0.10 * n_total)
    rem_k10 = max(0, k10 - len(h_indices))
    darc_sorted = sorted(non_h_items, key=lambda x: (x["delta_u"], -x["index"]), reverse=True)
    darc_sel = h_indices.union(set(it["index"] for it in darc_sorted[:rem_k10]))

    b4_sorted = sorted(non_h_items, key=lambda x: (x["delta_sem"], -x["index"]), reverse=True)
    b4_sel = h_indices.union(set(it["index"] for it in b4_sorted[:rem_k10]))

    b3_seeds = list(range(20))
    b3_sel_by_seed = {}
    for s in b3_seeds:
        rng = random.Random(s)
        shf = list(non_h_items)
        rng.shuffle(shf)
        b3_sel_by_seed[s] = h_indices.union(set(it["index"] for it in shf[:rem_k10]))

    def get_map(sel_set: Set[int]):
        return {(it["gid"], it["v_type"]): (
            it["key_rev"] if it["index"] in sel_set else it["key_a"],
            it["succ_rev"] if it["index"] in sel_set else it["succ_a"]
        ) for it in items}

    darc_map = get_map(darc_sel)
    b4_map = get_map(b4_sel)
    b3_maps = [get_map(b3_sel_by_seed[s]) for s in b3_seeds]

    all_pairs = [(gid, v1, v2) for gid in gids for v1, v2 in pair_variants]
    common_pairs = [p for p in all_pairs if (
        darc_map[(p[0], p[1])][1] and darc_map[(p[0], p[2])][1] and
        b4_map[(p[0], p[1])][1] and b4_map[(p[0], p[2])][1] and
        all(m[(p[0], p[1])][1] and m[(p[0], p[2])][1] for m in b3_maps)
    )]

    darc_diffs = [1 if darc_map[(p[0], p[1])][0] != darc_map[(p[0], p[2])][0] else 0 for p in common_pairs]
    b4_diffs = [1 if b4_map[(p[0], p[1])][0] != b4_map[(p[0], p[2])][0] else 0 for p in common_pairs]
    b3_diffs_by_seed = [[1 if m[(p[0], p[1])][0] != m[(p[0], p[2])][0] else 0 for p in common_pairs] for m in b3_maps]

    pair_darc = statistics.mean(darc_diffs) if darc_diffs else 0.0
    pair_b4 = statistics.mean(b4_diffs) if b4_diffs else 0.0
    pair_b3 = statistics.mean([statistics.mean(d) for d in b3_diffs_by_seed]) if b3_diffs_by_seed and b3_diffs_by_seed[0] else 0.0

    g_darc = defaultdict(list)
    g_b4 = defaultdict(list)
    g_b3 = [defaultdict(list) for _ in b3_seeds]
    for idx, p in enumerate(common_pairs):
        g_darc[p[0]].append(darc_diffs[idx])
        g_b4[p[0]].append(b4_diffs[idx])
        for s in range(len(b3_seeds)):
            g_b3[s][p[0]].append(b3_diffs_by_seed[s][idx])

    macro_darc = statistics.mean([statistics.mean(v) for v in g_darc.values()]) if g_darc else 0.0
    macro_b4 = statistics.mean([statistics.mean(v) for v in g_b4.values()]) if g_b4 else 0.0
    macro_b3 = statistics.mean([statistics.mean([statistics.mean(v) for v in g_b3[s].values()]) for s in range(len(b3_seeds))]) if b3_seeds else 0.0

    equal_quota_10 = {
        "k": k10,
        "h": len(h_indices),
        "pair_weighted_darc_flip": pair_darc,
        "pair_weighted_b4_flip": pair_b4,
        "pair_weighted_b3_flip": pair_b3,
        "gain_pair_vs_random_pp": (pair_b3 - pair_darc) * 100,
        "group_macro_darc_flip": macro_darc,
        "group_macro_b4_flip": macro_b4,
        "group_macro_b3_flip": macro_b3,
        "gain_macro_vs_random_pp": (macro_b3 - macro_darc) * 100,
    }

    audit_checks = {
        "candidate_match_count": sum(1 for it in items if json.loads(it["calls_dict"].get("review", {}).get("user_prompt", "{}")).get("candidate_A") is not None),
        "review_valid_count": sum(1 for it in items if it["review_valid"]),
        "review_fallback_count": sum(1 for it in items if not it["review_valid"]),
        "review_fallback_ratio": sum(1 for it in items if not it["review_valid"]) / len(items) if items else 0.0,
    }

    summary = {
        "model": model_name,
        "run_dir": str(run_dir),
        "groups_count": len(gids),
        "utterances_count": len(items),
        "audit_checks": audit_checks,
        "online_methods": online_results,
        "equal_quota_10pct": equal_quota_10,
    }
    write_json(run_dir / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run E2 Experiment for Claude Models")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/e2/e2_strictly_unexposed_utterances.json")
    parser.add_argument("--pilot-groups", type=int, default=0, help="If > 0, run only first N groups as pilot")
    parser.add_argument("--workers", type=int, default=4, help="Concurrency workers")
    args = parser.parse_args()

    base_config = load_config(args.config)
    model_name = base_config.model
    model_slug = model_name.replace(".", "_")

    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pilot_tag = f"_pilot{args.pilot_groups}" if args.pilot_groups > 0 else ""
    run_id = f"{utc_now}_e2_{model_slug}{pilot_tag}"
    run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Initializing DARC-Route Claude E2 Experiment ===")
    print(f"Model:        {model_name}")
    print(f"Dataset:      {args.dataset}")
    print(f"Pilot Groups: {args.pilot_groups or 'Full 40'}")
    print(f"Workers:      {args.workers}")
    print(f"Output:       {run_dir}")

    raw_data = json.loads(args.dataset.read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for u in raw_data:
        groups[u["group_id"]].append(u)

    selected_gids = sorted(groups.keys())
    if args.pilot_groups > 0:
        selected_gids = selected_gids[:args.pilot_groups]

    print(f"Selected {len(selected_gids)} groups ({len(selected_gids)*4} utterances).")
    config = replace(base_config, retries=3, retry_sleep=2.0, timeout=max(base_config.timeout, 60))

    start_time = time.time()
    group_results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_gid = {
            executor.submit(run_group, groups[gid], config, run_dir): gid
            for gid in selected_gids
        }
        completed_count = 0
        for future in as_completed(future_to_gid):
            gid = future_to_gid[future]
            try:
                g_data = future.result()
                group_results.append(g_data)
                completed_count += 1
                print(f"  [{completed_count}/{len(selected_gids)}] Group {gid} processed ({time.time() - start_time:.1f}s)")
            except Exception as e:
                print(f"  [ERROR] Group {gid} failed: {e}")

    print(f"\nCompleted collection in {time.time() - start_time:.1f}s. Evaluating results...")
    summary = evaluate_run(run_dir, model_name)
    print("\n=== Experiment Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
