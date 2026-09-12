#!/usr/bin/env python3
"""Run Full 160 Test Experiment for Claude Models (Haiku 4.5 & Sonnet 4.6).

Evaluates 160 groups x 4 variants = 640 utterances on historical test benchmark:
- Model: claude-haiku-4-5-20251001 or claude-sonnet-4-6 via https://www.fhl.mom
- Preserves full telemetry, usage tokens, and returned_model in call records
- Immutable route_key normalization (tuple of string POI IDs)
- Exact graph reconstruction with seed = 5000 + group_num
- Non-empty candidate injection assertion in review prompt
- Evaluates Full 160 and Clean 146 cohorts
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
and 0.5 when balanced or unmentioned. Do not invent constraints.'''

PROMPTS = {
    "A": SCHEMA + "Extract the fields directly and return only the JSON object.",
    "B": SCHEMA + "Check each field against an exact short span from the instruction. Add an evidence object of short quotations. Return JSON only.",
    "review": SCHEMA + "Reconsider the two candidate interpretations against the original instruction. Neither candidate is guaranteed correct. Return a single complete corrected intent and an evidence object of short quotations. No route decisions are provided or needed.",
}

DRIFT_14_GROUPS = {
    "test_001", "test_007", "test_020", "test_080", "test_091", "test_100",
    "test_102", "test_108", "test_112", "test_115", "test_129", "test_141",
    "test_142", "test_147"
}


def route_key(r: Any) -> Tuple[str, ...]:
    """Strictly normalize poi_ids to an immutable tuple of strings."""
    if r is None:
        return ()
    if isinstance(r, dict):
        return tuple(str(x) for x in r.get("poi_ids", ()))
    return tuple(str(x) for x in getattr(r, "poi_ids", ()))


def extract_and_clean_json(raw: str) -> str:
    """Robustly extract JSON object from raw response text, finding outermost braces."""
    text = raw.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
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
    if "dependencies" in data and isinstance(data["dependencies"], list):
        cleaned_deps = []
        for dep in data["dependencies"]:
            if isinstance(dep, (list, tuple)) and len(dep) == 2:
                u, v = dep
                if isinstance(u, str) and isinstance(v, str):
                    cleaned_deps.append([u, v])
        data["dependencies"] = cleaned_deps
    return data


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
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
        "oracle_check": check_route(graph, oracle_route, gold) if oracle_route else None,
        "calls": {},
        "candidates": {},
        "routes": {},
    }

    llm = LLM(config)
    candidates: dict[str, Intent | None] = {}
    raw_candidates: dict[str, Any] = {}

    for method in ["A", "B", "review"]:
        if method != "review":
            user_msg = f'User instruction to analyze:\n"{text}"\n\nExtract the route intent JSON:'
        else:
            cand_a_dict = raw_candidates.get("A")
            cand_b_dict = raw_candidates.get("B")
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

        if method == "review" and (cand_a_dict is None or cand_b_dict is None):
            call_record["schema_valid"] = False
            call_record["review_skipped_missing_candidates"] = True
            call_record["parse_error"] = "Skipped review because candidate A or B was null."
            candidates[method] = None
            raw_candidates[method] = None
            res["calls"][method] = call_record
            continue

        # Retry up to 3 times per call on transport or parse failure
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                raw = llm.complete(PROMPTS[method], user_msg)
                call_record["raw_response"] = raw

                last_usage = getattr(llm.client, "last_usage", None)
                if isinstance(last_usage, dict):
                    in_tok = last_usage.get("prompt_tokens") or last_usage.get("input_tokens") or 0
                    out_tok = last_usage.get("completion_tokens") or last_usage.get("output_tokens") or 0
                    call_record["usage"] = {
                        "prompt_tokens": in_tok,
                        "completion_tokens": out_tok,
                        "total_tokens": in_tok + out_tok,
                        "raw": last_usage,
                    }
                else:
                    call_record["usage"] = None

                last_resp = getattr(llm.client, "last_response", None)
                if isinstance(last_resp, dict) and "model" in last_resp:
                    call_record["returned_model"] = last_resp["model"]

                cleaned = extract_and_clean_json(raw)
                parsed = json.loads(cleaned)
                normalized_dict = normalize_parsed_intent_dict(parsed)
                cand = Intent.parse(normalized_dict)
                candidates[method] = cand
                raw_candidates[method] = asdict(cand)
                call_record["schema_valid"] = True
                call_record["parsed_intent"] = asdict(cand)
                if "parse_error" in call_record:
                    del call_record["parse_error"]
                if "transport_error_message" in call_record:
                    del call_record["transport_error_message"]
                break
            except Exception as e:
                call_record["schema_valid"] = False
                call_record["parse_error"] = str(e)
                if attempt < max_attempts:
                    time.sleep(1.0 * attempt)
                    continue
                candidates[method] = None
                raw_candidates[method] = None

        res["calls"][method] = call_record

    for m in ["A", "B"]:
        cand = candidates.get(m)
        r = solver.solve(**cand.solver_args()) if cand is not None else None
        res["routes"][m] = asdict(r) if r else None
        res["candidates"][m] = asdict(cand) if cand else None

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
    group_file = run_dir / f"{gid}.json"
    graph_path = run_dir / f"{gid}_graph.json"

    # Checkpoint/resume: skip if group is already fully completed
    if group_file.exists() and graph_path.exists():
        try:
            existing = json.loads(group_file.read_text(encoding="utf-8"))
            if len(existing.get("utterances", [])) == len(group_records):
                return existing
        except Exception:
            pass

    group_num = int(gid.split("_")[-1])
    seed = (5000 if gid.startswith("test_") else 6000) + group_num
    graph = generate_synthetic_graph(graph_id=f"{gid}_graph", seed=seed)
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
    write_json(group_file, group_data)
    return group_data


def evaluate_cohort(utts: list[dict[str, Any]], graphs: dict[str, SyntheticGraph], cohort_name: str) -> dict[str, Any]:
    solver_cache = {gid: ExactRouteSolver(g) for gid, g in graphs.items()}
    items = []
    for idx, u in enumerate(utts):
        gid = u["group_id"]
        uid = u["utterance_id"]
        graph = graphs[gid]
        gold = Intent.parse(u["gold_intent"])
        cands = {m: Intent.parse(u["candidates"][m]) if u["candidates"].get(m) else None for m in ["A", "B", "review"]}
        routes = {m: RouteResult(**u["routes"][m]) if u["routes"].get(m) else None for m in ["A", "B", "review"]}

        cand_a, cand_b = cands.get("A"), cands.get("B")
        r_a, r_b, r_rev = routes.get("A"), routes.get("B"), routes.get("review")

        # Fallback to A if review is missing
        if r_rev is None:
            r_rev = r_a

        h = compute_protection_trigger(cand_a, cand_b, r_a, r_b)
        delta_u = compute_cross_utility_delta(graph, cand_a, cand_b, r_a, r_b) if h == 0 else 0.0
        delta_sem = abs(cand_a.quality_weight - cand_b.quality_weight) if (h == 0 and cand_a and cand_b) else 0.0

        succ_a = check_route(graph, r_a, gold)["task_success"] if r_a else False
        succ_rev = check_route(graph, r_rev, gold)["task_success"] if r_rev else False

        oracle_route = solver_cache[gid].solve(**gold.solver_args())
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

    gids = sorted(list(set(it["gid"] for it in items)))
    pair_variants = [("v0", "v1"), ("v0", "v2"), ("v0", "v3"), ("v1", "v2"), ("v1", "v3"), ("v2", "v3")]

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

        degr_uids = [it["uid"] for it in items if it["succ_a"] and not (it["succ_rev"] if choices[it["index"]] else it["succ_a"])]

        online_results[om_name] = {
            "tsr": sum(succs) / len(succs),
            "degraded_count": len(degr_uids),
            "review_rate": sum(1 for it in items if choices[it["index"]]) / len(items),
            "common_pairs_count": len(common_pairs),
            "common_pair_weighted_flip": pair_weighted_flip,
            "common_group_macro_flip": group_macro_flip,
            "mean_route_utility": statistics.mean(utils),
            "mean_regret": statistics.mean(regrets),
        }

    # Equal Quota 10%
    n_total = len(items)
    k10 = math.floor(0.10 * n_total)
    rem_k = k10 - len(h_indices)

    equal_quota_10 = {}
    if rem_k >= 0:
        darc_sorted = sorted(non_h_items, key=lambda x: (x["delta_u"], -x["index"]), reverse=True)
        darc_sel = h_indices.union(set(it["index"] for it in darc_sorted[:rem_k]))

        b4_sorted = sorted(non_h_items, key=lambda x: (x["delta_sem"], -x["index"]), reverse=True)
        b4_sel = h_indices.union(set(it["index"] for it in b4_sorted[:rem_k]))

        random.seed(20260912)
        b3_seeds = [random.randint(0, 1000000) for _ in range(20)]
        b3_sel_by_seed = {}
        for s in b3_seeds:
            rng = random.Random(s)
            shuffled = list(non_h_items)
            rng.shuffle(shuffled)
            b3_sel_by_seed[s] = h_indices.union(set(it["index"] for it in shuffled[:rem_k]))

        darc_keys = {(it["gid"], it["v_type"]): (it["key_rev"] if it["index"] in darc_sel else it["key_a"]) for it in items}
        darc_succ = {(it["gid"], it["v_type"]): (it["succ_rev"] if it["index"] in darc_sel else it["succ_a"]) for it in items}
        b4_keys = {(it["gid"], it["v_type"]): (it["key_rev"] if it["index"] in b4_sel else it["key_a"]) for it in items}
        b4_succ = {(it["gid"], it["v_type"]): (it["succ_rev"] if it["index"] in b4_sel else it["succ_a"]) for it in items}

        b3_keys_by_seed = {}
        b3_succ_by_seed = {}
        for s in b3_seeds:
            b3_keys_by_seed[s] = {(it["gid"], it["v_type"]): (it["key_rev"] if it["index"] in b3_sel_by_seed[s] else it["key_a"]) for it in items}
            b3_succ_by_seed[s] = {(it["gid"], it["v_type"]): (it["succ_rev"] if it["index"] in b3_sel_by_seed[s] else it["succ_a"]) for it in items}

        common_pairs = [
            p for p in all_pairs
            if darc_succ[(p[0], p[1])] and darc_succ[(p[0], p[2])]
            and b4_succ[(p[0], p[1])] and b4_succ[(p[0], p[2])]
            and all(b3_succ_by_seed[s][(p[0], p[1])] and b3_succ_by_seed[s][(p[0], p[2])] for s in b3_seeds)
        ]

        pair_darc = statistics.mean([1 if darc_keys[(p[0], p[1])] != darc_keys[(p[0], p[2])] else 0 for p in common_pairs]) if common_pairs else 0.0
        pair_b4 = statistics.mean([1 if b4_keys[(p[0], p[1])] != b4_keys[(p[0], p[2])] else 0 for p in common_pairs]) if common_pairs else 0.0
        pair_b3_list = [statistics.mean([1 if b3_keys_by_seed[s][(p[0], p[1])] != b3_keys_by_seed[s][(p[0], p[2])] else 0 for p in common_pairs]) for s in b3_seeds] if common_pairs else [0.0]
        pair_b3 = statistics.mean(pair_b3_list)

        g_darc = defaultdict(list)
        g_b4 = defaultdict(list)
        g_b3 = {s: defaultdict(list) for s in b3_seeds}
        for p in common_pairs:
            g_darc[p[0]].append(1 if darc_keys[(p[0], p[1])] != darc_keys[(p[0], p[2])] else 0)
            g_b4[p[0]].append(1 if b4_keys[(p[0], p[1])] != b4_keys[(p[0], p[2])] else 0)
            for s in b3_seeds:
                g_b3[s][p[0]].append(1 if b3_keys_by_seed[s][(p[0], p[1])] != b3_keys_by_seed[s][(p[0], p[2])] else 0)

        macro_darc = statistics.mean([statistics.mean(v) for v in g_darc.values()]) if g_darc else 0.0
        macro_b4 = statistics.mean([statistics.mean(v) for v in g_b4.values()]) if g_b4 else 0.0
        macro_b3_list = [
            statistics.mean([statistics.mean(g_b3[s][gid]) for gid in gids if g_b3[s][gid]])
            for s in b3_seeds if any(g_b3[s][gid] for gid in gids)
        ]
        macro_b3 = statistics.mean(macro_b3_list) if macro_b3_list else 0.0

        d_vs_b3_per_group = [
            statistics.mean(g_darc[gid]) - statistics.mean([statistics.mean(g_b3[s][gid]) for s in range(len(b3_seeds))])
            for gid in g_darc
        ]
        ci_b3 = compute_paired_bootstrap(d_vs_b3_per_group, num_samples=2000, seed=20260912) if d_vs_b3_per_group else (0.0, 0.0, 0.0)

        equal_quota_10 = {
            "k": k10,
            "h": len(h_indices),
            "common_pairs": len(common_pairs),
            "group_macro_darc_flip": macro_darc,
            "group_macro_b4_flip": macro_b4,
            "group_macro_b3_flip": macro_b3,
            "gain_macro_vs_random_pp": (macro_b3 - macro_darc) * 100,
            "ci95_darc_minus_b3": [ci_b3[1], ci_b3[2]],
        }

    return {
        "cohort_name": cohort_name,
        "groups_count": len(gids),
        "utterances_count": len(items),
        "online_methods": online_results,
        "equal_quota_10pct": equal_quota_10,
    }


def evaluate_run(run_dir: Path, model_name: str) -> dict[str, Any]:
    group_files = sorted([f for f in run_dir.glob("test_*.json") if not f.name.endswith("_graph.json")])
    flat_utts = []
    graphs = {}

    for gf in group_files:
        gid = gf.stem
        graph_path = run_dir / f"{gid}_graph.json"
        graph = SyntheticGraph.load(graph_path)
        graphs[gid] = graph
        g_data = json.loads(gf.read_text(encoding="utf-8"))
        for u in g_data.get("utterances", []):
            flat_utts.append(u)

    for u in flat_utts:
        gid = u["group_id"]
        graph = graphs[gid]
        solver = ExactRouteSolver(graph)
        if u["routes"].get("review") is None and u["candidates"].get("review"):
            cand_rev = Intent.parse(u["candidates"]["review"])
            r_rev = solver.solve(**cand_rev.solver_args())
            u["routes"]["review"] = asdict(r_rev) if r_rev else None
        if not u["candidates"].get("review"):
            u["routes"]["review"] = u["routes"].get("A")

    utts_full160 = flat_utts
    utts_clean146 = [u for u in flat_utts if u["group_id"] not in DRIFT_14_GROUPS]

    full160_res = evaluate_cohort(utts_full160, graphs, "full_160_groups")
    clean146_res = evaluate_cohort(utts_clean146, graphs, "clean_146_groups")

    candidate_match_count = sum(1 for u in flat_utts if json.loads(u["calls"].get("review", {}).get("user_prompt", "{}")).get("candidate_A") is not None)
    review_valid_count = sum(1 for u in flat_utts if u["candidates"].get("review"))
    review_fallback_count = len(flat_utts) - review_valid_count

    summary = {
        "model": model_name,
        "run_dir": str(run_dir),
        "total_groups": len(group_files),
        "total_utterances": len(flat_utts),
        "audit_checks": {
            "candidate_match_count": candidate_match_count,
            "review_valid_count": review_valid_count,
            "review_fallback_count": review_fallback_count,
            "review_fallback_ratio": review_fallback_count / len(flat_utts) if flat_utts else 0.0,
        },
        "full_160_groups": full160_res,
        "clean_146_groups": clean146_res,
    }
    write_json(run_dir / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Full 160 Experiment for Claude Models")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/test/test_640_utterances.json")
    parser.add_argument("--pilot-groups", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8, help="Worker threads")
    parser.add_argument("--run-dir", type=Path, default=None, help="Existing run dir to resume into")
    args = parser.parse_args()

    base_config = load_config(args.config)
    model_name = base_config.model
    model_slug = model_name.replace(".", "_")

    if args.run_dir:
        run_dir = args.run_dir
    else:
        utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        pilot_tag = f"_pilot{args.pilot_groups}" if args.pilot_groups > 0 else ""
        run_id = f"{utc_now}_main_test_{model_slug}_full160{pilot_tag}"
        run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Initializing Claude Full 160 Test Experiment ===")
    print(f"Model:        {model_name}")
    print(f"Dataset:      {args.dataset}")
    print(f"Pilot Groups: {args.pilot_groups or 'Full 160'}")
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
    config = replace(base_config, retries=3, retry_sleep=2.0, timeout=max(base_config.timeout, 90))

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
                elapsed = time.time() - start_time
                avg_time = elapsed / completed_count
                rem_groups = len(selected_gids) - completed_count
                eta_s = rem_groups * avg_time / args.workers
                print(f"  [{completed_count:3d}/{len(selected_gids)}] Group {gid} done ({elapsed:.1f}s, ETA: {rem_groups*avg_time/min(completed_count, args.workers):.0f}s)")
            except Exception as e:
                print(f"  [ERROR] Group {gid} failed: {e}")

    print(f"\nCompleted collection in {time.time() - start_time:.1f}s. Evaluating results...")
    summary = evaluate_run(run_dir, model_name)
    print("\n=== Experiment Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
