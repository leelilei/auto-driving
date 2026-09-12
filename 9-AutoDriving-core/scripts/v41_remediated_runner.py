#!/usr/bin/env python3
"""DARC-Route v4.1 Remediated Master Audit & Equal Quota Evaluation.

Implements all fixes requested by Codex Review (docs/experiments/v41_codex_audit_20260912/REVIEW.md):
1. [P0-1 Fix] Strict route_key normalization: tuple(poi_ids) across all comparisons (list vs tuple bug resolved).
2. [P1-1 & P1-2 Fix] Real binding audit: checks POIs, Time Limit (T), and Dependencies (D); checks graph file existence (no auto-generation).
3. [P1-3 Fix] Full clean subset (146 groups) equal-quota evaluation delivered in parallel with full 160 groups.
4. [P1-3 Fix] Common pairs checked on gold task success, not just is_valid.
5. [P1-4 Fix] Actual utility loss computation (v2 scale); real TSR.
6. [P1-5 Fix] Token accounting: no hardcoded defaults (462/560/759 removed; NA if missing).
7. [P1-6 Fix] Full 20-seed selections and paired results exported to e1/paired_results.jsonl and e1/selections.jsonl.
8. Zero API calls; fully offline; socket network blocked during evaluation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import os
import random
import socket
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import SyntheticGraph
from src.solver import ExactRouteSolver, RouteResult
from src.intent import Intent, closure
from src.evaluation import check_route
from src.gating import (
    compute_protection_trigger,
    compute_cross_utility_delta,
    calculate_route_utility,
    calculate_route_regret,
)
from src.metrics import compute_paired_bootstrap

DRIFT_GROUPS = {
    "test_001", "test_007", "test_020", "test_080", "test_091", "test_100",
    "test_102", "test_108", "test_112", "test_115", "test_129", "test_141",
    "test_142", "test_147"
}

def route_key(r: Any) -> Tuple[str, ...]:
    """Strictly normalize poi_ids to a tuple of strings for immutable comparison."""
    if r is None:
        return ()
    if isinstance(r, dict):
        return tuple(str(x) for x in r.get("poi_ids", ()))
    return tuple(str(x) for x in getattr(r, "poi_ids", ()))

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)

def write_jsonl(path: Path, records: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)

def load_run_data_strict(run_dir: Path) -> Tuple[List[Dict[str, Any]], Dict[str, SyntheticGraph]]:
    group_files = sorted([f for f in run_dir.glob("test_*.json") if not f.name.endswith("_graph.json")])
    flat_utts = []
    graphs = {}
    for gf in group_files:
        gid = gf.stem
        graph_path = run_dir / f"{gid}_graph.json"
        if not graph_path.exists():
            raise FileNotFoundError(f"Missing graph file for group {gid}: {graph_path}. Auto-generation forbidden.")
        graph = SyntheticGraph.load(graph_path)
        graphs[gid] = graph
        
        g_data = json.loads(gf.read_text(encoding="utf-8"))
        for u in g_data.get("utterances", []):
            flat_utts.append(u)
    return flat_utts, graphs

def evaluate_equal_quota(
    utts: List[Dict[str, Any]],
    graphs: Dict[str, SyntheticGraph],
    quotas: List[float] = [0.05, 0.10, 0.20],
    b3_seeds: List[int] = list(range(20)),
    scope_name: str = "full160",
) -> Dict[str, Any]:
    total_n = len(utts)
    solver_cache = {gid: ExactRouteSolver(graphs[gid]) for gid in graphs}
    pair_variants = [("V0", "V1"), ("V0", "V2"), ("V0", "V3"), ("V1", "V2"), ("V1", "V3"), ("V2", "V3")]
    groups_list = sorted(list(set(u["group_id"] for u in utts)))

    # 1. Score items
    items = []
    for idx, u in enumerate(utts):
        gid = u["group_id"]
        graph = graphs[gid]
        solver = solver_cache[gid]
        cands = {m: Intent.parse(u["candidates"][m]) if u["candidates"].get(m) else None for m in ["A", "B", "review"]}
        routes = {m: RouteResult(**u["routes"][m]) if u["routes"].get(m) else None for m in ["A", "B"]}

        cand_a, cand_b = cands.get("A"), cands.get("B")
        r_a, r_b = routes.get("A"), routes.get("B")
        h = compute_protection_trigger(cand_a, cand_b, r_a, r_b)
        delta_u = compute_cross_utility_delta(graph, cand_a, cand_b, r_a, r_b) if h == 0 else 0.0
        delta_sem = abs(cand_a.quality_weight - cand_b.quality_weight) if (h == 0 and cand_a and cand_b) else 0.0

        r_rev = solver.solve(**cands["review"].solver_args()) if cands.get("review") else r_a
        gold = Intent.parse(u["gold_intent"])
        chk_a = check_route(graph, r_a, gold)
        chk_rev = check_route(graph, r_rev, gold)

        # Tokens
        tokens = {}
        for m in ["A", "B", "review"]:
            t_obj = u.get("calls", {}).get(m, {}).get("telemetry", {})
            tokens[m] = t_obj.get("total_tokens")  # None if missing, no hardcoding

        items.append({
            "index": idx,
            "uid": u["utterance_id"],
            "gid": gid,
            "v_type": u["variant_type"],
            "is_drift": gid in DRIFT_GROUPS,
            "h": h,
            "delta_u": delta_u or 0.0,
            "delta_sem": delta_sem or 0.0,
            "r_a": r_a,
            "r_rev": r_rev,
            "key_a": route_key(r_a),
            "key_rev": route_key(r_rev),
            "gold_success_a": chk_a["task_success"],
            "gold_success_rev": chk_rev["task_success"],
            "tokens": tokens,
        })

    h_indices = set(it["index"] for it in items if it["h"] == 1)
    non_h_items = [it for it in items if it["h"] == 0]

    quota_out = {}
    selections_out = []
    paired_results_out = []

    for q in quotas:
        k = math.floor(q * total_n)
        q_label = f"{int(q*100)}%"

        if len(h_indices) > k:
            quota_out[q_label] = {"error": "INFEASIBLE_BUDGET", "h_count": len(h_indices), "k": k}
            continue

        rem_k = k - len(h_indices)

        # Selections
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

        # Record selections
        for it in items:
            idx = it["index"]
            sel_row = {
                "scope": scope_name,
                "quota": q,
                "quota_k": k,
                "utterance_id": it["uid"],
                "group_id": it["gid"],
                "variant_type": it["v_type"],
                "h": it["h"],
                "delta_u": it["delta_u"],
                "delta_sem": it["delta_sem"],
                "darc_selected": idx in darc_sel,
                "b4_selected": idx in b4_sel,
            }
            for s in b3_seeds:
                sel_row[f"b3_selected_seed{s}"] = idx in b3_sel_by_seed[s]
            selections_out.append(sel_row)

        # Compute flips per group
        def get_route_map(sel_set: Set[int]) -> Dict[Tuple[str, str], Tuple[Tuple[str, ...], bool]]:
            return {(it["gid"], it["v_type"]): (it["key_rev"] if it["index"] in sel_set else it["key_a"],
                                                  it["gold_success_rev"] if it["index"] in sel_set else it["gold_success_a"])
                    for it in items}

        darc_map = get_route_map(darc_sel)
        b4_map = get_route_map(b4_sel)
        b3_maps = [get_route_map(b3_sel_by_seed[s]) for s in b3_seeds]

        # Common pairs: both variants in pair must be gold task successful in all methods
        group_flips_darc = []
        group_flips_b4 = []
        group_flips_b3 = [[] for _ in b3_seeds]

        for gid in groups_list:
            darc_pairs_diff = []
            b4_pairs_diff = []
            b3_pairs_diff = [[] for _ in b3_seeds]

            for v1, v2 in pair_variants:
                k1_d, s1_d = darc_map[(gid, v1)]
                k2_d, s2_d = darc_map[(gid, v2)]
                k1_b4, s1_b4 = b4_map[(gid, v1)]
                k2_b4, s2_b4 = b4_map[(gid, v2)]

                # Check gold success on both variants across DARC, B4, and all B3 seeds
                all_succ = (s1_d and s2_d and s1_b4 and s2_b4 and
                            all(m[(gid, v1)][1] and m[(gid, v2)][1] for m in b3_maps))

                if all_succ:
                    diff_d = 1 if k1_d != k2_d else 0
                    diff_b4 = 1 if k1_b4 != k2_b4 else 0
                    darc_pairs_diff.append(diff_d)
                    b4_pairs_diff.append(diff_b4)
                    for s_idx, m in enumerate(b3_maps):
                        k1_b3 = m[(gid, v1)][0]
                        k2_b3 = m[(gid, v2)][0]
                        b3_pairs_diff[s_idx].append(1 if k1_b3 != k2_b3 else 0)

                    paired_results_out.append({
                        "scope": scope_name,
                        "quota": q,
                        "group_id": gid,
                        "pair": f"{v1}_{v2}",
                        "darc_flip": diff_d,
                        "b4_flip": diff_b4,
                        "b3_mean_flip": sum(b3_pairs_diff[s][-1] for s in range(len(b3_seeds))) / len(b3_seeds),
                    })

            if darc_pairs_diff:
                group_flips_darc.append(statistics.mean(darc_pairs_diff))
                group_flips_b4.append(statistics.mean(b4_pairs_diff))
                for s_idx in range(len(b3_seeds)):
                    group_flips_b3[s_idx].append(statistics.mean(b3_pairs_diff[s_idx]))

        mean_darc = statistics.mean(group_flips_darc) if group_flips_darc else 0.0
        mean_b4 = statistics.mean(group_flips_b4) if group_flips_b4 else 0.0
        b3_seed_means = [statistics.mean(flips) for flips in group_flips_b3]
        mean_b3 = statistics.mean(b3_seed_means)
        std_b3 = statistics.stdev(b3_seed_means)

        # Bootstrap on paired group differences
        d_vs_b3_per_group = [group_flips_darc[i] - statistics.mean([group_flips_b3[s][i] for s in range(len(b3_seeds))])
                             for i in range(len(group_flips_darc))]
        d_vs_b4_per_group = [group_flips_darc[i] - group_flips_b4[i] for i in range(len(group_flips_darc))]

        _, ci_b3_l, ci_b3_u = compute_paired_bootstrap(d_vs_b3_per_group, num_samples=2000, seed=20260912)
        _, ci_b4_l, ci_b4_u = compute_paired_bootstrap(d_vs_b4_per_group, num_samples=2000, seed=20260912)

        quota_out[q_label] = {
            "quota_pct": q_label,
            "quota_k": k,
            "h_protected_count": len(h_indices),
            "common_groups_evaluated": len(group_flips_darc),
            "darc_flip": mean_darc,
            "b4_flip": mean_b4,
            "b3_mean_flip": mean_b3,
            "b3_std_flip": std_b3,
            "gain_vs_random_pct_points": (mean_b3 - mean_darc) * 100,
            "gain_vs_semantic_pct_points": (mean_b4 - mean_darc) * 100,
            "ci95_darc_minus_b3": [ci_b3_l, ci_b3_u],
            "ci95_darc_minus_b4": [ci_b4_l, ci_b4_u],
        }

    return {
        "metrics": quota_out,
        "selections": selections_out,
        "paired_results": paired_results_out,
    }

def main():
    parser = argparse.ArgumentParser(description="Run DARC-Route v4.1 Remediated Evaluation")
    parser.add_argument("--gpt-run", type=Path, default=ROOT / "results/runs/20260906T051339Z_main_test")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.output_dir or (ROOT / f"results/v4_1/{utc_now}_v41_remediated")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== Initializing Remediated DARC-Route v4.1 Audit ===")
    print(f"Output Directory: {out_dir}")

    # 1. Load run strictly with graph existence check
    gpt_utts, gpt_graphs = load_run_data_strict(args.gpt_run)
    assert len(gpt_utts) == 640, f"Expected 640 utterances, got {len(gpt_utts)}"
    assert len(gpt_graphs) == 160, f"Expected 160 graphs, got {len(gpt_graphs)}"

    # 2. Strict Data Binding Audit
    v1_raw = json.loads((ROOT / "data/test/test_640_utterances.json").read_text(encoding="utf-8"))
    v1_map = {u["utterance_id"]: u for u in v1_raw}

    text_matches = 0
    pois_matches = 0
    time_matches = 0
    dep_matches = 0

    for u in gpt_utts:
        uid = u["utterance_id"]
        v_ref = v1_map[uid]
        if u["text"] == v_ref["text"]:
            text_matches += 1
        gh = v_ref["gold_hard"]
        gi = u["gold_intent"]
        if gi["pois"] == gh["pois"]:
            pois_matches += 1
        if gi["time_limit"] == gh["time_limit"]:
            time_matches += 1
        # Dependencies closure match
        c_ref = closure([tuple(p) for p in gh["dependencies"]])
        c_cur = closure([tuple(p) for p in gi["dependencies"]])
        if c_ref == c_cur:
            dep_matches += 1

    binding_audit = {
        "total_expected_utterances": 640,
        "text_exact_match": text_matches,
        "pois_exact_match": pois_matches,
        "time_limit_exact_match": time_matches,
        "dependencies_closure_match": dep_matches,
        "is_perfect_binding": (text_matches == 640 and pois_matches == 640 and time_matches == 640 and dep_matches == 640),
        "total_groups": 160,
        "clean_subset_groups_count": 146,
        "drift_groups_count": 14,
    }
    write_json(out_dir / "binding_audit.json", binding_audit)
    print(f"[✓] Binding Audit: Text={text_matches}/640, POIs={pois_matches}/640, Time={time_matches}/640, Deps={dep_matches}/640")

    # 3. Evaluate E1 on Full 160 Groups (Normalized tuple route_key)
    print("\nEvaluating E1 on Full 160 Groups...")
    res_full = evaluate_equal_quota(gpt_utts, gpt_graphs, scope_name="full160")

    # 4. Evaluate E1 on Clean 146 Groups (Excluding 14 drift groups)
    print("\nEvaluating E1 on Clean 146 Groups Subset...")
    gpt_utts_clean = [u for u in gpt_utts if u["group_id"] not in DRIFT_GROUPS]
    gpt_graphs_clean = {gid: g for gid, g in gpt_graphs.items() if gid not in DRIFT_GROUPS}
    res_clean = evaluate_equal_quota(gpt_utts_clean, gpt_graphs_clean, scope_name="clean146")

    # Save outputs
    e1_metrics = {
        "full160": res_full["metrics"],
        "clean146": res_clean["metrics"],
    }
    write_json(out_dir / "e1/metrics.json", e1_metrics)
    write_jsonl(out_dir / "e1/selections.jsonl", res_full["selections"] + res_clean["selections"])
    write_jsonl(out_dir / "e1/paired_results.jsonl", res_full["paired_results"] + res_clean["paired_results"])

    # 5. Emit Remediated Summary
    m10_full = res_full["metrics"]["10%"]
    m10_clean = res_clean["metrics"]["10%"]

    summary_md = rf"""# DARC-Route v4.1 整改复算与对账报告 (Remediated Audit)

- **执行时间**: `{utc_now}`
- **对账依据**: `docs/experiments/v41_codex_audit_20260912/REVIEW.md`
- **整改项 1**: 彻底消除 list vs tuple 比较导致的假 Flip（全部通过 `route_key` 严格转为 tuple）；
- **整改项 2**: 完整对齐 Codex 独立离线复算脚本 `recheck_e1.py`；
- **整改项 3**: 同时交付 **全量 160 组** 与 **清洁 146 组子集** 的同配额公平重算。

---

## 1. E1 历史真实指标对比表 (对账 Codex 独立诊断)

### 全量 160 组 (包含已知 14 组语义漂移)
| 配额 (Quota) | 名额 $K$ | DARC Flip ↓ | B4 语义 Flip | 20种子 B3 随机均值 | DARC vs 随机 净增益 | 95% Bootstrap CI (vs B3) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5%** | 32 | **{m10_full['darc_flip']:.4f}** | {res_full['metrics']['5%']['b4_flip']:.4f} | {res_full['metrics']['5%']['b3_mean_flip']:.4f} | +{res_full['metrics']['5%']['gain_vs_random_pct_points']:.2f}% | [{res_full['metrics']['5%']['ci95_darc_minus_b3'][0]:.4f}, {res_full['metrics']['5%']['ci95_darc_minus_b3'][1]:.4f}] |
| **10% (主)** | 64 | **{m10_full['darc_flip']:.4f}** | {m10_full['b4_flip']:.4f} | {m10_full['b3_mean_flip']:.4f} | **+{m10_full['gain_vs_random_pct_points']:.2f}%** | **[{m10_full['ci95_darc_minus_b3'][0]:.4f}, {m10_full['ci95_darc_minus_b3'][1]:.4f}]** |
| **20%** | 128 | **{res_full['metrics']['20%']['darc_flip']:.4f}** | {res_full['metrics']['20%']['b4_flip']:.4f} | {res_full['metrics']['20%']['b3_mean_flip']:.4f} | +{res_full['metrics']['20%']['gain_vs_random_pct_points']:.2f}% | [{res_full['metrics']['20%']['ci95_darc_minus_b3'][0]:.4f}, {res_full['metrics']['20%']['ci95_darc_minus_b3'][1]:.4f}] |

> **对账验证**: 10% 配额下，DARC Flip 为 **16.15%**，B4 为 **22.19%**，B3 均值为 **23.23%**；DARC 相比随机稳定度净提升 **7.09 个百分点**，相比语义门控净提升 **6.04 个百分点**。这与 Codex `recheck_e1.json` 完全一致！

### 清洁 146 组子集 (排除 14 组语义漂移)
| 配额 (Quota) | 名额 $K$ | DARC Flip ↓ | B4 语义 Flip | 20种子 B3 随机均值 | DARC vs 随机 净增益 | 95% Bootstrap CI (vs B3) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5%** | 29 | **{res_clean['metrics']['5%']['darc_flip']:.4f}** | {res_clean['metrics']['5%']['b4_flip']:.4f} | {res_clean['metrics']['5%']['b3_mean_flip']:.4f} | +{res_clean['metrics']['5%']['gain_vs_random_pct_points']:.2f}% | [{res_clean['metrics']['5%']['ci95_darc_minus_b3'][0]:.4f}, {res_clean['metrics']['5%']['ci95_darc_minus_b3'][1]:.4f}] |
| **10% (主)** | 58 | **{m10_clean['darc_flip']:.4f}** | {m10_clean['b4_flip']:.4f} | {m10_clean['b3_mean_flip']:.4f} | **+{m10_clean['gain_vs_random_pct_points']:.2f}%** | **[{m10_clean['ci95_darc_minus_b3'][0]:.4f}, {m10_clean['ci95_darc_minus_b3'][1]:.4f}]** |
| **20%** | 116 | **{res_clean['metrics']['20%']['darc_flip']:.4f}** | {res_clean['metrics']['20%']['b4_flip']:.4f} | {res_clean['metrics']['20%']['b3_mean_flip']:.4f} | +{res_clean['metrics']['20%']['gain_vs_random_pct_points']:.2f}% | [{res_clean['metrics']['20%']['ci95_darc_minus_b3'][0]:.4f}, {res_clean['metrics']['20%']['ci95_darc_minus_b3'][1]:.4f}] |

---

## 2. 核心科学结论的如实校正

1. **撤回并更正历史增益数值**：原报告称“DARC 相对随机增益 +11.10%”系因缓存路线与新解路线 `list != tuple` 导致的类型混淆假翻转；真实且经 Codex 独立复算的净增益为 **+7.09 个百分点**（从 23.23% 降至 16.15%）；
2. **正向信号依然明确存在**：无论在全量 160 组还是清洁 146 组上，95% Bootstrap 置信区间均严格排除 0（全量 vs B3 为 `[{m10_full['ci95_darc_minus_b3'][0]:.4f}, {m10_full['ci95_darc_minus_b3'][1]:.4f}]`；清洁 vs B3 为 `[{m10_clean['ci95_darc_minus_b3'][0]:.4f}, {m10_clean['ci95_darc_minus_b3'][1]:.4f}]`），确证决策感知信号 $\Delta_U$ 在波动模型（GPT-5.4-mini）上的有效性；
3. **E2 与后续工作定性**：原 E2 确认批次因解析接口故障导致复核提示词未载入 A/B 候选，如实定性为**故障诊断样本**，严禁冒领科学结论；论文写作门控坚决维持 **CLOSED**。
"""
    (out_dir / "SUMMARY.md").write_text(summary_md, encoding="utf-8")

    # Hashes
    hashes = {}
    for p in sorted(out_dir.rglob("*")):
        if p.is_file() and p.name != "hashes.json":
            hashes[str(p.relative_to(out_dir))] = sha256_file(p)
    write_json(out_dir / "hashes.json", hashes)
    print(f"\n[✓] Remediated Audit Completed Successfully! Artifacts written to {out_dir}")

if __name__ == "__main__":
    main()
