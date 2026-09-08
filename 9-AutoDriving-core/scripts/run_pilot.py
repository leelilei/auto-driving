#!/usr/bin/env python3
"""Bounded original-instruction DEVELOPMENT smoke run, NOT the audited 80-utterance Gate A.

Run from core: .venv/bin/python scripts/run_pilot.py --limit 20 --workers 3
Each group performs A, B, review (three calls, no retries), with raw outputs and usage.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route, compare_intents
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


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run_group(record, config, output):
    group_id = record["pilot_group_id"]
    graph = generate_synthetic_graph(graph_id=f"{group_id}_smoke_v1", seed=4200+int(group_id.split("_")[-1]))
    graph_path = output / f"{group_id}_graph.json"
    graph.save(graph_path)
    graph = type(graph).load(graph_path)  # Evaluate the actual serialized artifact.
    solver = ExactRouteSolver(graph)
    original = record["base_instruction"]
    label = record["gold_intent"]
    gold = Intent.parse({"pois": label["pois"], "time_limit": label["time_limit"],
                         "dependencies": label["dependencies"],
                         "quality_weight": label["quality_weight_synthetic"]})
    oracle = solver.solve(**gold.solver_args())
    result = {"group_id": group_id, "source_index": record["source_index"],
              "source_cluster_id": record["source_cluster_id"], "split": "development_only",
              "variant": "original", "instruction": original,
              "annotation_status": "human_review_pending", "gold_reference": asdict(gold),
              "oracle_route": asdict(oracle), "oracle_check": check_route(graph, oracle, gold),
              "calls": {}, "evaluations": {}}
    llm = LLM(config)
    candidates, raw_candidates = {}, {}
    for method in ["A", "B", "review"]:
        user = original if method != "review" else json.dumps({"instruction": original, "candidate_A": raw_candidates.get("A"), "candidate_B": raw_candidates.get("B")}, ensure_ascii=False)
        call = {"system_prompt": PROMPTS[method], "user_prompt": user}
        try:
            raw = llm.complete(PROMPTS[method], user)
            call["raw_response"] = raw
            try:
                parsed = json.loads(raw)
                candidate = Intent.parse(parsed)
                candidates[method] = candidate
                raw_candidates[method] = parsed
                call["schema_valid"] = True
            except (ValueError, TypeError):
                candidates[method] = None
                raw_candidates[method] = {"invalid_response": raw}
                call["schema_valid"] = False
        except Exception as exc:
            call["transport_error_type"] = type(exc).__name__
            # Record only status/type, not provider bodies that could contain credentials.
            status = re.search(r"provider HTTP (\d{3})", str(exc))
            call["http_status"] = int(status.group(1)) if status else None
            call["schema_valid"] = False
            candidates[method] = None
            raw_candidates[method] = {"transport_failure": True}
        call["telemetry"] = llm.telemetry[-1] if llm.telemetry else None
        result["calls"][method] = call
        write_json(output / f"{group_id}.json", result)  # Persist every completed call.
        if "transport_error_type" in call:
            result["stopped_after_transport_failure"] = True
            break
    for name, candidate in {"B0": candidates.get("A"),
                            "B6": candidates.get("review") or candidates.get("A") or candidates.get("B")}.items():
        started = time.perf_counter()
        route = solver.solve(**candidate.solver_args()) if candidate is not None else None
        result["evaluations"][name] = {**compare_intents(candidate, gold), **check_route(graph, route, gold),
                                           "route": asdict(route) if route else None,
                                           "solver_seconds": time.perf_counter()-started}
    result["telemetry_summary"] = llm.telemetry_summary()
    write_json(output / f"{group_id}.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/llm_config.json")
    args = parser.parse_args()
    if not 1 <= args.limit <= 20 or not 1 <= args.workers <= 3 or args.offset < 0:
        parser.error("Use limit 1..20, workers 1..3 and nonnegative offset")
    config = replace(load_config(args.config), retries=0, timeout=45, max_output_tokens=1600)
    if config.provider == "mock":
        parser.error("This script reports real-provider smoke results; mock is not allowed")
    records = json.loads((ROOT / "data/pilot/pilot_intents_raw.json").read_text())[args.offset:args.offset+args.limit]
    if not records:
        parser.error("No selected records")
    output = ROOT / "results/runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_original_smoke")
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"scope": "original_instruction_development_smoke_NOT_Gate_A", "config": asdict(config),
                "python": sys.version, "max_api_calls": 3*len(records), "workers": args.workers,
                "selected_source_indices": [r["source_index"] for r in records],
                "hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [*sorted((ROOT/"src").glob("*.py")), Path(__file__), ROOT/"data/pilot/pilot_intents_raw.json", ROOT/"data/raw/HIPP.json"]},
                "prompts": PROMPTS, "annotation_status": "human_review_pending"}
    write_json(output / "manifest.json", manifest)
    print(f"RUN_DIR={output}", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_group, r, config, output) for r in records]
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            print(f"{r['group_id']}: B0={r['evaluations']['B0']['task_success']} B6={r['evaluations']['B6']['task_success']} calls={len(r['calls'])}", flush=True)
    summary = {"scope": manifest["scope"], "groups": len(results), "annotation_status": "human_review_pending",
               "gold_reference_full_feasible": sum(r["oracle_check"]["task_success"] for r in results),
               "methods": {m: {k: sum(r["evaluations"][m][k] for r in results) for k in ["task_success", "hard_exact", "poi_exact", "time_exact", "dependency_exact"]} for m in ["B0", "B6"]},
               "corrected_tasks": sum(not r["evaluations"]["B0"]["task_success"] and r["evaluations"]["B6"]["task_success"] for r in results),
               "harmed_tasks": sum(r["evaluations"]["B0"]["task_success"] and not r["evaluations"]["B6"]["task_success"] for r in results)}
    calls = [c for r in results for c in r["calls"].values()]
    summary["calls"] = len(calls)
    summary["schema_valid_calls"] = sum(c["schema_valid"] for c in calls)
    summary["transport_failures"] = sum("transport_error_type" in c for c in calls)
    telemetry = [c["telemetry"] for c in calls if c["telemetry"]]
    summary["provider_usage_calls"] = sum(t["usage_source"] == "provider" for t in telemetry)
    for k in ["input_tokens", "output_tokens", "total_tokens", "latency_seconds"]:
        summary[k] = sum(t[k] for t in telemetry)
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
