#!/usr/bin/env python3
"""Run formal E1 Pilot (20 groups x 4 variants = 80 utterances, B0 and B6).

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 3, 10, 12:
- 80 utterances from data/pilot/pilot_80_utterances.json
- Concurrency max 3, timeout 45s, max_output_tokens 1600, retries 0
- Calls per utterance: A, B, review (up to 240 attempts total, budget <= 300)
- Shared frozen graph per group across all 4 variants
- Records raw responses, provider tokens, exact routes, independent gold evaluation
- Evaluates B0 and B6, computes TSR, GTSR, Route Flip, corrected/harmed tasks
- Emits Gate A evaluation report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from src.metrics import (
    compute_tsr,
    compute_gtsr,
    compute_variant_tsr,
    compute_route_flip,
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


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run_utterance(
    record: dict[str, Any],
    graph: Any,
    solver: ExactRouteSolver,
    config: Any,
    run_dir: Path,
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
        "oracle_route": asdict(oracle_route),
        "oracle_check": check_route(graph, oracle_route, gold),
        "calls": {},
        "evaluations": {},
    }

    llm = LLM(config)
    candidates: dict[str, Intent | None] = {}
    raw_candidates: dict[str, Any] = {}

    for method in ["A", "B", "review"]:
        if method != "review":
            user_msg = text
        else:
            user_msg = json.dumps({
                "instruction": text,
                "candidate_A": raw_candidates.get("A"),
                "candidate_B": raw_candidates.get("B"),
            }, ensure_ascii=False)

        call_record: dict[str, Any] = {
            "method": method,
            "system_prompt": PROMPTS[method],
            "user_prompt": user_msg,
        }

        try:
            raw = llm.complete(PROMPTS[method], user_msg)
            call_record["raw_response"] = raw
            try:
                parsed = json.loads(raw)
                cand = Intent.parse(parsed)
                candidates[method] = cand
                raw_candidates[method] = parsed
                call_record["schema_valid"] = True
            except (ValueError, TypeError) as parse_exc:
                candidates[method] = None
                raw_candidates[method] = {"invalid_response": raw, "error": str(parse_exc)}
                call_record["schema_valid"] = False
        except Exception as exc:
            call_record["transport_error_type"] = type(exc).__name__
            status_match = re.search(r"provider HTTP (\d{3})", str(exc))
            call_record["http_status"] = int(status_match.group(1)) if status_match else None
            call_record["schema_valid"] = False
            candidates[method] = None
            raw_candidates[method] = {"transport_failure": True}

        call_record["telemetry"] = llm.telemetry[-1] if llm.telemetry else None
        res["calls"][method] = call_record

        if "transport_error_type" in call_record:
            res["stopped_after_transport_failure"] = True
            break

    # Evaluate B0 (Single A)
    cand_b0 = candidates.get("A")
    route_b0 = solver.solve(**cand_b0.solver_args()) if cand_b0 is not None else None
    res["evaluations"]["B0"] = {
        "candidate": asdict(cand_b0) if cand_b0 else None,
        **compare_intents(cand_b0, gold),
        **check_route(graph, route_b0, gold),
        "route": asdict(route_b0) if route_b0 else None,
    }

    # Evaluate B6 (Review of A and B with fallback)
    cand_b6, b6_source = resolve_review_fallback(
        candidates.get("review"), candidates.get("A"), candidates.get("B")
    )
    route_b6 = solver.solve(**cand_b6.solver_args()) if cand_b6 is not None else None
    res["evaluations"]["B6"] = {
        "candidate": asdict(cand_b6) if cand_b6 else None,
        "source": b6_source,
        **compare_intents(cand_b6, gold),
        **check_route(graph, route_b6, gold),
        "route": asdict(route_b6) if route_b6 else None,
    }

    return res


def run_group(
    group_records: list[dict[str, Any]],
    config: Any,
    run_dir: Path,
) -> dict[str, Any]:
    gid = group_records[0]["group_id"]
    group_num = int(gid.split("_")[-1])
    seed = 4200 + group_num
    graph = generate_synthetic_graph(graph_id=f"{gid}_graph", seed=seed)
    graph_path = run_dir / f"{gid}_graph.json"
    graph.save(graph_path)
    # Load serialized graph to ensure exact equivalence
    graph = type(graph).load(graph_path)
    solver = ExactRouteSolver(graph)

    utterance_results = []
    for rec in group_records:
        u_res = run_utterance(rec, graph, solver, config, run_dir)
        utterance_results.append(u_res)

    group_data = {
        "group_id": gid,
        "utterances_count": len(utterance_results),
        "utterances": utterance_results,
    }
    write_json(run_dir / f"{gid}.json", group_data)
    return group_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-groups", type=int, default=20, help="Number of pilot groups (1..20)")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent group workers (1..3)")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/llm_config.json")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without calling API")
    args = parser.parse_args()

    data_file = ROOT / "data/pilot/pilot_80_utterances.json"
    if not data_file.exists():
        parser.error(f"Pilot utterances not found at {data_file}")

    all_utterances = json.loads(data_file.read_text(encoding="utf-8"))

    # Group by group_id
    by_group = defaultdict(list)
    for u in all_utterances:
        by_group[u["group_id"]].append(u)

    selected_gids = sorted(by_group.keys())[:args.limit_groups]
    total_utts = sum(len(by_group[g]) for g in selected_gids)
    total_planned_attempts = total_utts * 3

    print(f"=== Starting E1 Formal Pilot ===")
    print(f"Groups: {len(selected_gids)}, Utterances: {total_utts}, Max Attempts: {total_planned_attempts}")
    print(f"Budget Limit: 300 attempts (Planned: {total_planned_attempts})")

    if args.dry_run:
        print("[DRY RUN] Exiting successfully without calling API.")
        return

    if not os.environ.get("FHL_API_KEY"):
        parser.error("FHL_API_KEY must be set in environment")

    config = replace(load_config(args.config), retries=0, timeout=45, max_output_tokens=1600)
    if config.provider == "mock":
        parser.error("E1 Pilot requires real provider")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_pilot_e1"
    run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    manifest = {
        "run_id": run_id,
        "purpose": "pilot",
        "phase": "E1_pilot_gate_a",
        "selected_groups": selected_gids,
        "utterances_count": total_utts,
        "max_api_calls": total_planned_attempts,
        "workers": args.workers,
        "config": asdict(config),
        "timestamp_start": datetime.now(timezone.utc).isoformat(),
    }
    write_json(run_dir / "manifest.json", manifest)
    print(f"Run directory: {run_dir}")

    group_results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_group, by_group[gid], config, run_dir): gid
            for gid in selected_gids
        }
        for fut in as_completed(futures):
            gid = futures[fut]
            try:
                gres = fut.result()
                group_results.append(gres)
                b0_succ = sum(u["evaluations"]["B0"]["task_success"] for u in gres["utterances"])
                b6_succ = sum(u["evaluations"]["B6"]["task_success"] for u in gres["utterances"])
                print(f"  [{gid}] Complete: B0={b0_succ}/4, B6={b6_succ}/4", flush=True)
            except Exception as exc:
                print(f"  [ERROR] {gid} failed: {exc}", flush=True)

    # Flatten all utterance evaluations
    flat_utts = [u for g in group_results for u in g["utterances"]]

    # Collect calls telemetry
    all_calls = [c for u in flat_utts for c in u["calls"].values()]
    telemetry_list = [c["telemetry"] for c in all_calls if c.get("telemetry")]

    b0_recs = [{"group_id": u["group_id"], "variant_type": u["variant_type"],
                "task_success": u["evaluations"]["B0"]["task_success"],
                "route": u["evaluations"]["B0"]["route"]} for u in flat_utts]
    b6_recs = [{"group_id": u["group_id"], "variant_type": u["variant_type"],
                "task_success": u["evaluations"]["B6"]["task_success"],
                "route": u["evaluations"]["B6"]["route"]} for u in flat_utts]

    b0_tsr = compute_tsr(b0_recs)
    b6_tsr = compute_tsr(b6_recs)
    b0_gtsr = compute_gtsr(b0_recs)
    b6_gtsr = compute_gtsr(b6_recs)

    b0_v_tsr = compute_variant_tsr(b0_recs)
    b6_v_tsr = compute_variant_tsr(b6_recs)

    b0_flip = compute_route_flip(b0_recs)
    b6_flip = compute_route_flip(b6_recs)

    corrected = sum(1 for u in flat_utts if not u["evaluations"]["B0"]["task_success"] and u["evaluations"]["B6"]["task_success"])
    harmed = sum(1 for u in flat_utts if u["evaluations"]["B0"]["task_success"] and not u["evaluations"]["B6"]["task_success"])
    unchanged = sum(1 for u in flat_utts if u["evaluations"]["B0"]["task_success"] == u["evaluations"]["B6"]["task_success"])
    net_gain = corrected - harmed

    # Gate A evaluation
    # Requirement: B0 must have errors, and B6 must have net gain > 0
    b0_errors = len(flat_utts) - sum(1 for r in b0_recs if r["task_success"])
    gate_a_passed = (b0_errors > 0) and (net_gain > 0)

    summary = {
        "run_id": run_id,
        "timestamp_end": datetime.now(timezone.utc).isoformat(),
        "total_groups": len(group_results),
        "total_utterances": len(flat_utts),
        "total_calls_issued": len(all_calls),
        "schema_valid_calls": sum(1 for c in all_calls if c.get("schema_valid", False)),
        "transport_failures": sum(1 for c in all_calls if "transport_error_type" in c),
        "telemetry": {
            "provider_tokens_input": sum(t["input_tokens"] for t in telemetry_list),
            "provider_tokens_output": sum(t["output_tokens"] for t in telemetry_list),
            "provider_tokens_total": sum(t["total_tokens"] for t in telemetry_list),
            "total_latency_seconds": round(sum(t["latency_seconds"] for t in telemetry_list), 2),
        },
        "metrics": {
            "B0": {
                "TSR": round(b0_tsr, 4),
                "GTSR": round(b0_gtsr, 4),
                "variant_TSR": b0_v_tsr,
                "mean_route_flip": b0_flip["mean_route_flip"],
            },
            "B6": {
                "TSR": round(b6_tsr, 4),
                "GTSR": round(b6_gtsr, 4),
                "variant_TSR": b6_v_tsr,
                "mean_route_flip": b6_flip["mean_route_flip"],
            },
            "diagnostics": {
                "b0_errors": b0_errors,
                "corrected_tasks": corrected,
                "harmed_tasks": harmed,
                "net_gain": net_gain,
                "unchanged_tasks": unchanged,
            },
        },
        "gate_a": {
            "status": "PASS" if gate_a_passed else "FAIL_OR_INCONCLUSIVE",
            "b0_has_errors": b0_errors > 0,
            "b6_has_net_gain": net_gain > 0,
            "verdict_reason": (
                "Gate A PASSED: baseline shows errors and review achieves positive net correction."
                if gate_a_passed else
                f"Gate A NOT MET: b0_errors={b0_errors}, net_gain={net_gain}. " +
                ("Baseline is saturated (no errors to fix)." if b0_errors == 0 else "Review does not provide positive net gain.")
            ),
        },
    }

    write_json(run_dir / "summary.json", summary)

    b0_flip_str = f"{b0_flip['mean_route_flip']:.4f}" if b0_flip['mean_route_flip'] is not None else "NA"
    b6_flip_str = f"{b6_flip['mean_route_flip']:.4f}" if b6_flip['mean_route_flip'] is not None else "NA"
    report_lines = [
        f"# Gate A Pilot Execution Report (E1)",
        f"",
        f"- **Run ID**: `{run_id}`",
        f"- **Timestamp**: `{summary['timestamp_end']}`",
        f"- **Dataset**: {len(group_results)} groups × 4 variants = {len(flat_utts)} utterances",
        f"- **API Attempts**: {summary['total_calls_issued']} attempts",
        f"- **Provider Tokens**: Input: {summary['telemetry']['provider_tokens_input']}, Output: {summary['telemetry']['provider_tokens_output']}, Total: {summary['telemetry']['provider_tokens_total']}",
        f"",
        f"## 1. Key Metrics Comparison",
        f"",
        f"| Metric | B0 (Single A) | B6 (Always Review) | Delta (B6 - B0) |",
        f"|---|---|---|---|",
        f"| **TSR** | {b0_tsr:.4f} ({sum(r['task_success'] for r in b0_recs)}/{len(flat_utts)}) | {b6_tsr:.4f} ({sum(r['task_success'] for r in b6_recs)}/{len(flat_utts)}) | {b6_tsr - b0_tsr:+.4f} |",
        f"| **GTSR** | {b0_gtsr:.4f} | {b6_gtsr:.4f} | {b6_gtsr - b0_gtsr:+.4f} |",
        f"| **V0 TSR (原句)** | {b0_v_tsr.get('V0', 0):.4f} | {b6_v_tsr.get('V0', 0):.4f} | {b6_v_tsr.get('V0', 0) - b0_v_tsr.get('V0', 0):+.4f} |",
        f"| **V1 TSR (同义改写)** | {b0_v_tsr.get('V1', 0):.4f} | {b6_v_tsr.get('V1', 0):.4f} | {b6_v_tsr.get('V1', 0) - b0_v_tsr.get('V1', 0):+.4f} |",
        f"| **V2 TSR (语序变化)** | {b0_v_tsr.get('V2', 0):.4f} | {b6_v_tsr.get('V2', 0):.4f} | {b6_v_tsr.get('V2', 0) - b0_v_tsr.get('V2', 0):+.4f} |",
        f"| **V3 TSR (口语变化)** | {b0_v_tsr.get('V3', 0):.4f} | {b6_v_tsr.get('V3', 0):.4f} | {b6_v_tsr.get('V3', 0) - b0_v_tsr.get('V3', 0):+.4f} |",
        f"| **Route Flip** | {b0_flip_str} | {b6_flip_str} | - |",
        f"",
        f"## 2. Gate A Diagnostic Breakdown",
        f"",
        f"- **Baseline B0 Errors**: {b0_errors} / {len(flat_utts)}",
        f"- **Corrected by Review (改正)**: {corrected}",
        f"- **Harmed by Review (改坏)**: {harmed}",
        f"- **Net Gain (净收益)**: {net_gain}",
        f"- **Unchanged (未改变)**: {unchanged}",
        f"",
        f"## 3. Gate A Final Decision",
        f"",
        f"**Gate A Status**: `{summary['gate_a']['status']}`",
        f"",
        f"> **Verdict**: {summary['gate_a']['verdict_reason']}",
    ]
    (run_dir / "gate_a_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("\n=== E1 Pilot Completed ===")
    print(f"Summary: B0 TSR={b0_tsr:.4f}, B6 TSR={b6_tsr:.4f}, Net Gain={net_gain}")
    print(f"Gate A Status: {summary['gate_a']['status']}")
    print(f"Full report at: {run_dir / 'gate_a_report.md'}")


if __name__ == "__main__":
    main()
