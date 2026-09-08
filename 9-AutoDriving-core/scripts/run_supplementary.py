#!/usr/bin/env python3
"""Supplementary run for network failures in E1 Pilot.

Per EXPERIMENT_GUIDE.md Section 10:
"网络失败默认不自动重试；另开补测运行、关联原 attempt，主表保留首轮失败，补测表单列。不能把补测成功覆盖原失败。"

This script evaluates only the failed utterances from run `20260905T182600Z_pilot_e1`:
- pilot_03_v2
- pilot_06_v0
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route, compare_intents
from src.gating import resolve_review_fallback
from src.llm_client import LLM, load_config
from scripts.run_e1_pilot import run_utterance, PROMPTS, write_json


def main():
    orig_run_id = "20260905T182600Z_pilot_e1"
    orig_run_dir = ROOT / "results/runs" / orig_run_id
    if not orig_run_dir.exists():
        print(f"Error: Original run dir {orig_run_dir} not found", file=sys.stderr)
        sys.exit(1)

    supp_run_id = f"{orig_run_id}_supplementary"
    supp_run_dir = ROOT / "results/runs" / supp_run_id
    supp_run_dir.mkdir(parents=True, exist_ok=True)

    data_file = ROOT / "data/pilot/pilot_80_utterances.json"
    all_utterances = {u["utterance_id"]: u for u in json.loads(data_file.read_text(encoding="utf-8"))}

    target_uids = ["pilot_03_v2", "pilot_06_v0"]
    config = replace(load_config(ROOT / "configs/llm_config.json"), retries=0, timeout=45, max_output_tokens=1600)

    manifest = {
        "supplementary_run_id": supp_run_id,
        "original_run_id": orig_run_id,
        "purpose": "supplementary_run_for_network_failures",
        "target_utterances": target_uids,
        "timestamp_start": datetime.now(timezone.utc).isoformat(),
        "config": asdict(config),
    }
    write_json(supp_run_dir / "manifest.json", manifest)

    results = []
    for uid in target_uids:
        rec = all_utterances[uid]
        gid = rec["group_id"]
        # Load the exact frozen graph from the original run
        graph_path = orig_run_dir / f"{gid}_graph.json"
        graph = generate_synthetic_graph(graph_id=f"{gid}_graph", seed=4200 + int(gid.split("_")[-1]))
        if graph_path.exists():
            from src.graph import SyntheticGraph
            graph = SyntheticGraph.load(graph_path)
        solver = ExactRouteSolver(graph)

        print(f"Running supplementary evaluation for {uid} (group {gid})...")
        u_res = run_utterance(rec, graph, solver, config, supp_run_dir)
        u_res["original_run_id"] = orig_run_id
        u_res["is_supplementary"] = True
        results.append(u_res)

        b0_eval = u_res["evaluations"]["B0"]
        b6_eval = u_res["evaluations"]["B6"]
        print(f"  Result for {uid}: B0_success={b0_eval['task_success']}, B6_success={b6_eval['task_success']}")

    summary = {
        "supplementary_run_id": supp_run_id,
        "original_run_id": orig_run_id,
        "timestamp_end": datetime.now(timezone.utc).isoformat(),
        "evaluated_utterances": len(results),
        "results": [
            {
                "utterance_id": r["utterance_id"],
                "group_id": r["group_id"],
                "variant_type": r["variant_type"],
                "text": r["text"],
                "b0_task_success": r["evaluations"]["B0"]["task_success"],
                "b6_task_success": r["evaluations"]["B6"]["task_success"],
                "calls_issued": len(r["calls"]),
                "transport_errors": sum(1 for c in r["calls"].values() if "transport_error_type" in c),
            }
            for r in results
        ],
    }
    write_json(supp_run_dir / "summary.json", summary)
    write_json(supp_run_dir / "supplementary_results.json", results)
    print(f"\nSupplementary run completed. Results saved to {supp_run_dir}")


if __name__ == "__main__":
    main()
