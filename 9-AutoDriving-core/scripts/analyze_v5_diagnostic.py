#!/usr/bin/env python3
"""Offline analysis of the frozen eight-group v5.1 development diagnostic."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.experiment_v5 import record_intent, weight_direction
from src.evaluation import check_route, compare_intents
from src.gating import calculate_route_regret
from src.graph import SyntheticGraph
from src.intent import Intent
from src.solver import ExactRouteSolver

BASE_ROLES = ("A", "B", "A2", "A3", "llmap_direct", "llmap_cot")
REVIEW_ROLES = ("review_plain", "review_fields", "review_constraints", "darc")
CONDITIONS = ("aligned", "tradeoff", "time_sensitive")


def parsed(record: dict | None) -> Intent | None:
    return Intent.parse(record["parsed_intent"]) if record and record.get("status") == "COMPLETE" else None


def intent_scores(candidate: Intent | None, gold: Intent) -> tuple[bool, bool]:
    hard = compare_intents(candidate, gold)["hard_exact"]
    direction = candidate is not None and weight_direction(candidate.quality_weight) == weight_direction(gold.quality_weight)
    return hard, direction


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    parser.add_argument("--graphs", type=Path, required=True)
    parser.add_argument("--runs", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    groups = {group for run in args.runs for group in json.loads((run / "summary.json").read_text())["groups"]}
    dataset = [row for row in json.loads(args.dataset.read_text()) if row["group_id"] in groups]
    if len(groups) != 8 or len(dataset) != 32:
        raise RuntimeError("analysis requires exactly eight groups and 32 utterances")

    attempts: dict[str, dict] = {}
    summaries = []
    for run in args.runs:
        summary = json.loads((run / "summary.json").read_text())
        summaries.append(summary)
        for path in (run / "attempts").glob("*.json"):
            record = json.loads(path.read_text())
            if record["call_id"] in attempts:
                raise RuntimeError(f"duplicate logical unit: {record['call_id']}")
            attempts[record["call_id"]] = record
    if len(attempts) != 576 or not all(item["collection_complete"] for item in summaries):
        raise RuntimeError("collection ledger is incomplete")

    role_metrics: dict[str, dict] = {}
    method_rows: dict[str, list[dict]] = defaultdict(list)
    for row in dataset:
        uid = row["utterance_id"]
        gold = record_intent(row)
        a = parsed(attempts.get(f"{uid}::A"))
        b = parsed(attempts.get(f"{uid}::B"))
        for condition in CONDITIONS:
            graph = SyntheticGraph.load(args.graphs / row["group_id"] / f"{condition}.json")
            solver = ExactRouteSolver(graph)
            oracle = solver.solve(**gold.solver_args())
            for role in (*BASE_ROLES, *REVIEW_ROLES):
                record = attempts.get(f"{uid}::{role}") if role in BASE_ROLES else attempts.get(f"{uid}::{condition}::{role}")
                raw_candidate = parsed(record)
                effective = raw_candidate if role in BASE_ROLES else (raw_candidate or a or b)
                route = solver.solve(**effective.solver_args()) if effective else None
                route_check = check_route(graph, route, gold)
                hard, direction = intent_scores(effective, gold)
                method_rows[role].append({
                    "group_id": row["group_id"], "utterance_id": uid, "condition": condition,
                    "raw_status": record.get("status") if record else "MISSING",
                    "fallback_used": role in REVIEW_ROLES and raw_candidate is None,
                    "hard_exact": hard, "direction_exact": direction,
                    "route": list(route.poi_ids) if route else None,
                    "oracle_route": list(oracle.poi_ids), "task_success": route_check["task_success"],
                    "regret": calculate_route_regret(graph, oracle, route, gold.quality_weight) if route_check["task_success"] else None,
                })

    for role, rows in method_rows.items():
        stable = 0
        for group in sorted(groups):
            for condition in CONDITIONS:
                block = [r for r in rows if r["group_id"] == group and r["condition"] == condition]
                stable += len({(tuple(r["route"]) if r["route"] else None, r["task_success"]) for r in block}) == 1
        regrets = [r["regret"] for r in rows if r["regret"] is not None]
        role_metrics[role] = {
            "n_route_cases": len(rows),
            "raw_schema_valid": sum(r["raw_status"] == "COMPLETE" for r in rows),
            "effective_hard_exact": sum(r["hard_exact"] for r in rows),
            "effective_direction_exact": sum(r["direction_exact"] for r in rows),
            "task_success": sum(r["task_success"] for r in rows),
            "oracle_route_exact": sum(r["route"] == r["oracle_route"] for r in rows),
            "stable_group_graphs": stable,
            "group_graphs": len(groups) * len(CONDITIONS),
            "mean_regret": sum(regrets) / len(regrets) if regrets else None,
            "fallback_cases": sum(r["fallback_used"] for r in rows),
        }

    # Intent accuracy has one unit per utterance for base roles and one per graph for reviewers.
    for role in BASE_ROLES:
        unique = [rows for rows in method_rows[role] if rows["condition"] == "aligned"]
        role_metrics[role]["n_intent_cases"] = len(unique)
        role_metrics[role]["hard_exact"] = sum(r["hard_exact"] for r in unique)
        role_metrics[role]["direction_exact"] = sum(r["direction_exact"] for r in unique)
    for role in REVIEW_ROLES:
        rows = method_rows[role]
        role_metrics[role]["n_intent_cases"] = len(rows)
        role_metrics[role]["hard_exact"] = sum(r["hard_exact"] for r in rows)
        role_metrics[role]["direction_exact"] = sum(r["direction_exact"] for r in rows)

    opportunity = {"utterances": len(dataset), "a_any_error": 0, "b_any_error": 0, "a_b_disagreements": 0}
    for row in dataset:
        uid, gold = row["utterance_id"], record_intent(row)
        a, b = parsed(attempts[f"{uid}::A"]), parsed(attempts[f"{uid}::B"])
        opportunity["a_any_error"] += not all(intent_scores(a, gold))
        opportunity["b_any_error"] += not all(intent_scores(b, gold))
        opportunity["a_b_disagreements"] += a is not None and b is not None and a != b

    result = {
        "protocol_version": "darc-v5.1-analysis-1",
        "scope": "development_diagnostic_not_confirmatory",
        "groups": sorted(groups), "utterances": len(dataset), "planned_logical_units": 576,
        "collection": {
            "logical_units_recorded": sum(x["logical_units_recorded"] for x in summaries),
            "physical_attempts": sum(x["physical_attempts"] for x in summaries),
            "complete_calls": sum(x["complete_calls"] for x in summaries),
            "schema_failures": sum(x["schema_failures"] for x in summaries),
            "skipped_upstream": sum(x["skipped_upstream"] for x in summaries),
            "transport_failures": sum(x["transport_failures"] for x in summaries),
            "provider_total_tokens": sum(x["provider_total_tokens"] for x in summaries),
        },
        "correction_opportunity": opportunity,
        "methods": role_metrics,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
