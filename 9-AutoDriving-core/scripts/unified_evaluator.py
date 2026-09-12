#!/usr/bin/env python3
"""Unified Offline Evaluator for DARC-Route v4.1 Experiments.

Evaluates GPT-5.4-mini (E1), Gemini-3.1-flash-lite (E2), and GPT-5.6-luna (E2).
Strictly offline (blocks socket), computes full-denominator TSR, GTSR,
corrected/degraded counts, pair-weighted and group-macro flips,
all-pair flip-or-failure, unified utility, token ledger, and 8/32 stratification.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import socket
import statistics
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import SyntheticGraph
from src.solver import RouteResult, ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route
from src.gating import (
    compute_protection_trigger,
    compute_cross_utility_delta,
    calculate_route_utility,
    calculate_route_regret,
)
from src.metrics import compute_paired_bootstrap

# Block all network sockets to guarantee strict offline execution
def _block_network(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("[OFFLINE_VIOLATION] Unified evaluator must operate strictly offline.")

socket.socket = _block_network  # type: ignore

OVERLAP_8_CLUSTERS = {42, 56, 325, 345, 361, 369, 433, 501}
DRIFT_14_GROUPS = {
    "test_001", "test_007", "test_020", "test_080", "test_091", "test_100",
    "test_102", "test_108", "test_112", "test_115", "test_129", "test_141",
    "test_142", "test_147"
}

def route_key(r: Any) -> Tuple[str, ...]:
    """Strictly normalize poi_ids to immutable tuple of strings."""
    if r is None:
        return ()
    if isinstance(r, dict):
        return tuple(str(x) for x in r.get("poi_ids", ()))
    return tuple(str(x) for x in getattr(r, "poi_ids", ()))

def load_run_data(run_dir: Path) -> Tuple[List[Dict[str, Any]], Dict[str, SyntheticGraph]]:
    group_files = sorted([f for f in run_dir.glob("*.json")
                         if not f.name.endswith("_graph.json")
                         and f.name.startswith(("test_", "e2_clean_"))])
    if not group_files:
        raise FileNotFoundError(f"No group files found in {run_dir}")

    flat_utts: List[Dict[str, Any]] = []
    graphs: Dict[str, SyntheticGraph] = {}

    for gf in group_files:
        gid = gf.stem
        graph_path = run_dir / f"{gid}_graph.json"
        if not graph_path.exists():
            raise FileNotFoundError(f"Missing required graph file: {graph_path}. Auto-generation is strictly forbidden.")
        graph = SyntheticGraph.load(graph_path)
        graphs[gid] = graph

        g_data = json.loads(gf.read_text(encoding="utf-8"))
        utts = g_data.get("utterances", [])
        for u in utts:
            flat_utts.append(u)

    # Pre-solve review routes if missing
    for u in flat_utts:
        gid = u["group_id"]
        graph = graphs[gid]
        solver = ExactRouteSolver(graph)
        if u["routes"].get("review") is None and u["candidates"].get("review"):
            cand_rev = Intent.parse(u["candidates"]["review"])
            r_rev = solver.solve(**cand_rev.solver_args())
            u["routes"]["review"] = asdict(r_rev) if r_rev else None
        if not u["candidates"].get("review"):
            # Formal fallback to A when review candidate is invalid
            u["routes"]["review"] = u["routes"].get("A")

    return flat_utts, graphs

def evaluate_cohort(
    utts: List[Dict[str, Any]],
    graphs: Dict[str, SyntheticGraph],
    cohort_name: str,
    b3_seeds: List[int] = list(range(20)),
) -> Dict[str, Any]:
    n_total = len(utts)
    if n_total == 0:
        return {"error": "EMPTY_COHORT"}

    solver_cache = {gid: ExactRouteSolver(graphs[gid]) for gid in graphs}
    gids = sorted(list(set(u["group_id"] for u in utts)))
    pair_variants = [("V0", "V1"), ("V0", "V2"), ("V0", "V3"), ("V1", "V2"), ("V1", "V3"), ("V2", "V3")]

    # 1. Audit checks
    review_fallback_count = sum(1 for u in utts if not u["candidates"].get("review"))
    candidate_match_count = 0
    usage_missing_count = 0
    for u in utts:
        rev_call = u["calls"].get("review", {})
        prompt_str = rev_call.get("user_prompt", "")
        if prompt_str:
            try:
                pj = json.loads(prompt_str)
                if pj.get("candidate_A") == u["candidates"].get("A") and pj.get("candidate_B") == u["candidates"].get("B"):
                    candidate_match_count += 1
            except Exception:
                pass
        for c in u["calls"].values():
            if c.get("usage") is None:
                usage_missing_count += 1

    # 2. Score items
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

        h = compute_protection_trigger(cand_a, cand_b, r_a, r_b)
        delta_u = compute_cross_utility_delta(graph, cand_a, cand_b, r_a, r_b) if h == 0 else 0.0
        delta_sem = abs(cand_a.quality_weight - cand_b.quality_weight) if (h == 0 and cand_a and cand_b) else 0.0

        succ_a = check_route(graph, r_a, gold)["task_success"] if r_a else False
        succ_rev = check_route(graph, r_rev, gold)["task_success"] if r_rev else False

        # Oracle route for regret
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
        })

    h_indices = set(it["index"] for it in items if it["h"] == 1)
    non_h_items = [it for it in items if it["h"] == 0]

    # Evaluate online methods
    online_results = {}
    for om_name in ["B0", "B4_online", "DARC_online", "B6"]:
        method_choices = {}
        for it in items:
            idx = it["index"]
            if om_name == "B0":
                ch = False
            elif om_name == "B6":
                ch = True
            elif om_name == "B4_online":
                ch = (it["h"] == 1) or (it["delta_sem"] > 0.10)
            elif om_name == "DARC_online":
                ch = (it["h"] == 1) or (it["delta_u"] > 0.02)
            method_choices[idx] = ch

        succs = [it["succ_rev"] if method_choices[it["index"]] else it["succ_a"] for it in items]
        keys = {(it["gid"], it["v_type"]): (it["key_rev"] if method_choices[it["index"]] else it["key_a"]) for it in items}
        succ_map = {(it["gid"], it["v_type"]): (it["succ_rev"] if method_choices[it["index"]] else it["succ_a"]) for it in items}
        utils = [it["u_rev"] if method_choices[it["index"]] else it["u_a"] for it in items]
        regrets = [it["reg_rev"] if method_choices[it["index"]] else it["reg_a"] for it in items]

        # Corrected vs Degraded compared to B0 (choice A)
        corr_uids = [it["uid"] for it in items if not it["succ_a"] and (it["succ_rev"] if method_choices[it["index"]] else it["succ_a"])]
        degr_uids = [it["uid"] for it in items if it["succ_a"] and not (it["succ_rev"] if method_choices[it["index"]] else it["succ_a"])]

        # Group task success rate (GTSR)
        g_succs = defaultdict(list)
        for it in items:
            g_succs[it["gid"]].append(it["succ_rev"] if method_choices[it["index"]] else it["succ_a"])
        gtsr = sum(1 for gid, res in g_succs.items() if len(res) == 4 and all(res)) / len(g_succs)

        # Flips across common pairs where this method succeeds
        # Also compute full flip-or-failure
        all_pairs = [(gid, v1, v2) for gid in gids for v1, v2 in pair_variants if (gid, v1) in keys and (gid, v2) in keys]
        common_pairs = [p for p in all_pairs if succ_map[(p[0], p[1])] and succ_map[(p[0], p[2])]]

        diff_common = [1 if keys[(p[0], p[1])] != keys[(p[0], p[2])] else 0 for p in common_pairs]
        pair_weighted_flip = statistics.mean(diff_common) if diff_common else 0.0

        g_diffs = defaultdict(list)
        for p in common_pairs:
            g_diffs[p[0]].append(1 if keys[(p[0], p[1])] != keys[(p[0], p[2])] else 0)
        group_macro_flip = statistics.mean([statistics.mean(v) for v in g_diffs.values()]) if g_diffs else 0.0

        flip_or_fail = sum(1 for p in all_pairs if (keys[(p[0], p[1])] != keys[(p[0], p[2])]) or not succ_map[(p[0], p[1])] or not succ_map[(p[0], p[2])]) / len(all_pairs) if all_pairs else 0.0

        calls_per_utt = sum(3 if method_choices[it["index"]] else (1 if om_name == "B0" else 2) for it in items) / len(items)
        rev_rate = sum(1 for it in items if method_choices[it["index"]]) / len(items)

        online_results[om_name] = {
            "tsr": sum(succs) / len(succs),
            "gtsr": gtsr,
            "failed_count": len(items) - sum(succs),
            "failed_ids": [it["uid"] for it in items if not (it["succ_rev"] if method_choices[it["index"]] else it["succ_a"])],
            "corrected_count": len(corr_uids),
            "degraded_count": len(degr_uids),
            "degraded_ids": degr_uids,
            "review_rate": rev_rate,
            "calls_per_utterance": calls_per_utt,
            "common_pairs_count": len(common_pairs),
            "common_pair_weighted_flip": pair_weighted_flip,
            "common_group_macro_flip": group_macro_flip,
            "all_pair_flip_or_failure": flip_or_fail,
            "mean_route_utility": statistics.mean(utils),
            "mean_regret": statistics.mean(regrets),
        }

    # Evaluate Equal Quotas
    equal_quota_results = {}
    for q in [0.05, 0.10, 0.20]:
        k = math.floor(q * n_total)
        q_label = f"{int(q*100)}%"

        rem_k = k - len(h_indices)
        if rem_k < 0:
            equal_quota_results[q_label] = {"error": "INFEASIBLE_BUDGET", "h_count": len(h_indices), "k": k}
            continue

        darc_sorted = sorted(non_h_items, key=lambda x: (x["delta_u"], -x["index"]), reverse=True)
        darc_sel = h_indices.union(set(it["index"] for it in darc_sorted[:rem_k]))

        b4_sorted = sorted(non_h_items, key=lambda x: (x["delta_sem"], -x["index"]), reverse=True)
        b4_sel = h_indices.union(set(it["index"] for it in b4_sorted[:rem_k]))

        b3_sel_by_seed = {}
        for s in b3_seeds:
            rng = random.Random(s)
            shf = list(non_h_items)
            rng.shuffle(shf)
            b3_sel_by_seed[s] = h_indices.union(set(it["index"] for it in shf[:rem_k]))

        def get_map(sel_set: Set[int]):
            return {(it["gid"], it["v_type"]): (
                it["key_rev"] if it["index"] in sel_set else it["key_a"],
                it["succ_rev"] if it["index"] in sel_set else it["succ_a"]
            ) for it in items}

        darc_map = get_map(darc_sel)
        b4_map = get_map(b4_sel)
        b3_maps = [get_map(b3_sel_by_seed[s]) for s in b3_seeds]

        # Common successful pairs across DARC, B4, and all B3 seeds
        all_pairs = [(gid, v1, v2) for gid in gids for v1, v2 in pair_variants]
        common_pairs = [p for p in all_pairs if (
            darc_map[(p[0], p[1])][1] and darc_map[(p[0], p[2])][1] and
            b4_map[(p[0], p[1])][1] and b4_map[(p[0], p[2])][1] and
            all(m[(p[0], p[1])][1] and m[(p[0], p[2])][1] for m in b3_maps)
        )]

        # Flips
        darc_diffs = [1 if darc_map[(p[0], p[1])][0] != darc_map[(p[0], p[2])][0] else 0 for p in common_pairs]
        b4_diffs = [1 if b4_map[(p[0], p[1])][0] != b4_map[(p[0], p[2])][0] else 0 for p in common_pairs]
        b3_diffs_by_seed = [[1 if m[(p[0], p[1])][0] != m[(p[0], p[2])][0] else 0 for p in common_pairs] for m in b3_maps]

        pair_darc = statistics.mean(darc_diffs) if darc_diffs else 0.0
        pair_b4 = statistics.mean(b4_diffs) if b4_diffs else 0.0
        b3_seed_pair_means = [statistics.mean(d) for d in b3_diffs_by_seed] if b3_diffs_by_seed and b3_diffs_by_seed[0] else [0.0]
        pair_b3 = statistics.mean(b3_seed_pair_means)

        # Group-macro flips
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
        b3_seed_macro_means = [statistics.mean([statistics.mean(v) for v in g_b3[s].values()]) for s in range(len(b3_seeds))]
        macro_b3 = statistics.mean(b3_seed_macro_means) if b3_seed_macro_means else 0.0

        # TSR for DARC and B4
        tsr_darc = sum(1 for it in items if (it["succ_rev"] if it["index"] in darc_sel else it["succ_a"])) / len(items)
        tsr_b4 = sum(1 for it in items if (it["succ_rev"] if it["index"] in b4_sel else it["succ_a"])) / len(items)
        degraded_darc = [it["uid"] for it in items if it["succ_a"] and not (it["succ_rev"] if it["index"] in darc_sel else it["succ_a"])]

        # Bootstrap on paired group differences
        d_vs_b3_per_group = [
            statistics.mean(g_darc[gid]) - statistics.mean([statistics.mean(g_b3[s][gid]) for s in range(len(b3_seeds))])
            for gid in g_darc
        ]
        d_vs_b4_per_group = [
            statistics.mean(g_darc[gid]) - statistics.mean(g_b4[gid])
            for gid in g_darc
        ]

        ci_b3 = compute_paired_bootstrap(d_vs_b3_per_group, num_samples=2000, seed=20260912) if d_vs_b3_per_group else (0.0, 0.0, 0.0)
        ci_b4 = compute_paired_bootstrap(d_vs_b4_per_group, num_samples=2000, seed=20260912) if d_vs_b4_per_group else (0.0, 0.0, 0.0)

        equal_quota_results[q_label] = {
            "quota_pct": q_label,
            "quota_k": k,
            "h_protected_count": len(h_indices),
            "common_pairs_count": len(common_pairs),
            "total_pairs_count": len(all_pairs),
            "darc_tsr": tsr_darc,
            "b4_tsr": tsr_b4,
            "darc_degraded_count": len(degraded_darc),
            "darc_degraded_ids": degraded_darc,
            # Pair-weighted
            "pair_weighted_darc_flip": pair_darc,
            "pair_weighted_b4_flip": pair_b4,
            "pair_weighted_b3_flip": pair_b3,
            "gain_pair_weighted_vs_random_pct": (pair_b3 - pair_darc) * 100,
            "gain_pair_weighted_vs_b4_pct": (pair_b4 - pair_darc) * 100,
            # Group-macro
            "group_macro_darc_flip": macro_darc,
            "group_macro_b4_flip": macro_b4,
            "group_macro_b3_flip": macro_b3,
            "gain_group_macro_vs_random_pct": (macro_b3 - macro_darc) * 100,
            "gain_group_macro_vs_b4_pct": (macro_b4 - macro_darc) * 100,
            # 95% CI on group-macro
            "ci95_darc_minus_b3": [ci_b3[1], ci_b3[2]],
            "ci95_darc_minus_b4": [ci_b4[1], ci_b4[2]],
        }

    # Token stats
    total_prompt_tok = sum(c.get("usage", {}).get("prompt_tokens", 0) for it in items for c in it["calls_dict"].values() if c.get("usage"))
    total_comp_tok = sum(c.get("usage", {}).get("completion_tokens", 0) for it in items for c in it["calls_dict"].values() if c.get("usage"))
    total_cached_tok = sum(c.get("usage", {}).get("prompt_tokens_details", {}).get("cached_tokens", 0) for it in items for c in it["calls_dict"].values() if c.get("usage"))

    return {
        "cohort_name": cohort_name,
        "groups_count": len(gids),
        "utterances_count": len(items),
        "audit_checks": {
            "candidate_match_count": candidate_match_count,
            "candidate_match_ratio": candidate_match_count / len(items) if items else 0.0,
            "review_fallback_count": review_fallback_count,
            "review_fallback_ratio": review_fallback_count / len(items) if items else 0.0,
            "usage_missing_count": usage_missing_count,
        },
        "tokens_ledger": {
            "total_prompt_tokens": total_prompt_tok,
            "total_completion_tokens": total_comp_tok,
            "total_cached_tokens": total_cached_tok,
            "mean_tokens_per_utterance": (total_prompt_tok + total_comp_tok) / len(items) if items else 0.0,
        },
        "online_methods": online_results,
        "equal_quota": equal_quota_results,
    }

def main():
    parser = argparse.ArgumentParser(description="Unified Offline Evaluator for DARC Experiments")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "docs/experiments/v41_codex_audit_20260912/unified_audit_metrics.json")
    args = parser.parse_args()

    print("=== DARC-Route v4.1 Unified Offline Evaluator ===")
    print("Socket network is blocked. Performing pure offline evaluation.")

    runs_to_eval = {
        "gpt54_mini_historical": ROOT / "results/runs/20260906T051339Z_main_test",
        "gemini31_flash_lite_e2": ROOT / "results/runs/20260912T073141Z_e2_confirmation_gemini-3_1-flash-lite",
        "gpt56_luna_e2": ROOT / "results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna",
        "claude_haiku_4_5_e2": ROOT / "results/runs/20260912T090152Z_e2_claude-haiku-4-5-20251001",
        "claude_sonnet_4_6_e2": ROOT / "results/runs/20260912T092122Z_e2_claude-sonnet-4-6",
    }

    full_report = {}

    for run_key, run_path in runs_to_eval.items():
        if not run_path.exists():
            print(f"[SKIP] Path not found: {run_path}")
            continue

        print(f"\nProcessing {run_key} from {run_path.name}...")
        utts, graphs = load_run_data(run_path)

        if "e2" in run_key:
            # Evaluate all 40, clean 32, and overlap 8
            utts_all = utts
            utts_clean32 = [u for u in utts if u.get("source_cluster_id") not in OVERLAP_8_CLUSTERS]
            utts_overlap8 = [u for u in utts if u.get("source_cluster_id") in OVERLAP_8_CLUSTERS]

            full_report[run_key] = {
                "all_40_groups": evaluate_cohort(utts_all, graphs, f"{run_key}_all40"),
                "stratified_32_unexposed": evaluate_cohort(utts_clean32, graphs, f"{run_key}_clean32"),
                "stratified_8_overlap": evaluate_cohort(utts_overlap8, graphs, f"{run_key}_overlap8"),
            }
        else:
            # GPT-5.4-mini: full160 and clean146
            utts_full160 = utts
            utts_clean146 = [u for u in utts if u["group_id"] not in DRIFT_14_GROUPS]

            full_report[run_key] = {
                "full_160_groups": evaluate_cohort(utts_full160, graphs, f"{run_key}_full160"),
                "clean_146_groups": evaluate_cohort(utts_clean146, graphs, f"{run_key}_clean146"),
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(full_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n[✓] Unified audit metrics saved to: {args.output}")

if __name__ == "__main__":
    main()
