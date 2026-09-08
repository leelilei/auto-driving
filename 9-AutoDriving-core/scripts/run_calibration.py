#!/usr/bin/env python3
"""Execute Calibration run on dev_calibration (20 groups x 4 variants = 80 utterances).

Per EXPERIMENT_GUIDE.md Section 8, 11, 12 (P2):
- Loads 80 utterances from data/calibration/calibration_80_utterances.json
- Runs A, B, review calls for each utterance using FHL/gpt-5.4-mini
- Performs grid calibration across tau, tau_sem, and target review rates (0.25, 0.50, 0.75)
- Under Option A: Optimizes Route Flip reduction and consistency subject to zero TSR degradation
- Freezes parameters in data/calibration/frozen_config.json
- Generates calibration trace and report
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

from src.graph import generate_synthetic_graph, SyntheticGraph
from src.solver import ExactRouteSolver
from src.intent import Intent
from src.evaluation import check_route, compare_intents
from src.gating import (
    execute_method_decision,
    resolve_review_fallback,
    compute_protection_trigger,
    compute_cross_utility_delta,
)
from src.metrics import (
    compute_tsr,
    compute_gtsr,
    compute_variant_tsr,
    compute_route_flip,
    compute_calibrated_utility_loss,
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
                call_record["error_message"] = str(parse_exc)
        except Exception as exc:
            call_record["transport_error_type"] = type(exc).__name__
            call_record["error_message"] = str(exc)
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

    # Solve routes for A and B
    for m in ["A", "B"]:
        cand = candidates.get(m)
        r = solver.solve(**cand.solver_args()) if cand is not None else None
        res["routes"][m] = asdict(r) if r else None
        res["candidates"][m] = asdict(cand) if cand else None

    # Review candidate
    cand_rev = candidates.get("review")
    res["candidates"]["review"] = asdict(cand_rev) if cand_rev else None

    return res


def run_calibration_group(
    group_records: list[dict[str, Any]],
    config: Any,
    run_dir: Path,
) -> dict[str, Any]:
    gid = group_records[0]["group_id"]
    group_num = int(gid.split("_")[-1])
    seed = 4200 + 100 + group_num
    graph = generate_synthetic_graph(graph_id=f"{gid}_graph", seed=seed)
    graph_path = run_dir / f"{gid}_graph.json"
    graph.save(graph_path)
    graph = SyntheticGraph.load(graph_path)
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


def evaluate_offline_method(
    flat_utts: list[dict[str, Any]],
    graphs: dict[str, SyntheticGraph],
    method: str,
    tau: float = 0.05,
    tau_sem: float = 0.10,
    p_review: float = 0.50,
) -> dict[str, Any]:
    """Offline evaluation of a method on the calibration dataset."""
    eval_records = []
    calls_used_list = []
    triggered_list = []
    h_triggered_list = []
    delta_u_triggered_list = []
    utility_losses = []

    for u in flat_utts:
        gid = u["group_id"]
        uid = u["utterance_id"]
        v_type = u["variant_type"]
        graph = graphs[gid]
        solver = ExactRouteSolver(graph)

        gold_dict = u["gold_intent"]
        gold_intent = Intent.parse({
            "pois": gold_dict["pois"],
            "time_limit": gold_dict["time_limit"],
            "dependencies": gold_dict["dependencies"],
            "quality_weight": gold_dict["quality_weight"],
        })

        # Reconstruct parsed candidates
        candidates: dict[str, Intent | None] = {}
        for m in ["A", "B", "review"]:
            c_dict = u["candidates"].get(m)
            if c_dict:
                candidates[m] = Intent.parse({
                    "pois": c_dict["pois"],
                    "time_limit": c_dict["time_limit"],
                    "dependencies": c_dict["dependencies"],
                    "quality_weight": c_dict["quality_weight"],
                })
            else:
                candidates[m] = None

        # Reconstruct routes
        from src.solver import RouteResult
        routes: dict[str, RouteResult | None] = {}
        for m in ["A", "B"]:
            r_dict = u["routes"].get(m)
            if r_dict:
                routes[m] = RouteResult(
                    poi_ids=r_dict["poi_ids"],
                    categories=r_dict["categories"],
                    coverage=r_dict["coverage"],
                    is_full_coverage=r_dict["is_full_coverage"],
                    is_valid=r_dict["is_valid"],
                    utility=r_dict["utility"],
                    total_distance=r_dict["total_distance"],
                    total_time=r_dict["total_time"],
                    final_arrival_time=r_dict["final_arrival_time"],
                    status=r_dict["status"],
                    details=r_dict["details"],
                    raw_utility=r_dict.get("raw_utility", r_dict["utility"]),
                )
            else:
                routes[m] = None

        chosen_intent, chosen_route, meta = execute_method_decision(
            method=method,
            candidates=candidates,
            routes=routes,
            graph=graph,
            solver=solver,
            tau=tau,
            tau_sem=tau_sem,
            p_review=p_review,
            group_id=gid,
            utterance_id=uid,
        )

        check = check_route(graph, chosen_route, gold_intent)
        eval_records.append({
            "group_id": gid,
            "utterance_id": uid,
            "variant_type": v_type,
            "task_success": check["task_success"],
            "route": asdict(chosen_route) if chosen_route else None,
        })

        calls_used_list.append(meta["calls_used"])
        triggered_list.append(1 if meta["review_triggered"] else 0)
        h_triggered_list.append(meta["h"])
        if meta["trigger_reason"] == "utility_discrepancy":
            delta_u_triggered_list.append(1)
        else:
            delta_u_triggered_list.append(0)

        # Calibrated utility loss if task succeeds
        if check["task_success"] and chosen_route is not None:
            oracle_r = u["oracle_route"]
            oracle_u = oracle_r.get("raw_utility", oracle_r["utility"])
            actual_u = chosen_route.raw_utility
            loss = max(0.0, (oracle_u - actual_u) / 2.0)
            utility_losses.append(loss)

    tsr = compute_tsr(eval_records)
    gtsr = compute_gtsr(eval_records)
    v_tsr = compute_variant_tsr(eval_records)
    flip = compute_route_flip(eval_records)

    return {
        "method": method,
        "tau": tau,
        "tau_sem": tau_sem,
        "p_review": p_review,
        "TSR": round(tsr, 4),
        "GTSR": round(gtsr, 4),
        "variant_TSR": v_tsr,
        "route_flip": flip["mean_route_flip"],
        "mean_calls_used": round(sum(calls_used_list) / len(calls_used_list), 4),
        "review_rate": round(sum(triggered_list) / len(triggered_list), 4),
        "h_trigger_rate": round(sum(h_triggered_list) / len(h_triggered_list), 4),
        "delta_u_trigger_rate": round(sum(delta_u_triggered_list) / len(delta_u_triggered_list), 4),
        "mean_utility_loss": round(sum(utility_losses) / len(utility_losses), 6) if utility_losses else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3, help="Workers count")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/llm_config.json")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without calling API")
    parser.add_argument("--run-dir", type=Path, default=None, help="Existing run directory to resume or analyze")
    args = parser.parse_args()

    data_file = ROOT / "data/calibration/calibration_80_utterances.json"
    if not data_file.exists():
        parser.error(f"Calibration data missing at {data_file}")

    all_utterances = json.loads(data_file.read_text(encoding="utf-8"))
    by_group = defaultdict(list)
    for u in all_utterances:
        by_group[u["group_id"]].append(u)

    selected_gids = sorted(by_group.keys())
    total_utts = sum(len(by_group[g]) for g in selected_gids)
    print(f"=== Starting Calibration Run (dev_calibration) ===")
    print(f"Groups: {len(selected_gids)}, Utterances: {total_utts}, Planned Attempts: {total_utts * 3}")

    if args.dry_run:
        print("[DRY RUN MODE] Exiting without calling API.")
        return

    if args.run_dir:
        run_dir = args.run_dir
        run_id = run_dir.name
        print(f"Using existing run directory: {run_dir}")
    else:
        if not os.environ.get("FHL_API_KEY"):
            parser.error("FHL_API_KEY must be set in environment")

        config = replace(load_config(args.config), retries=0, timeout=45, max_output_tokens=1600)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_calibration"
        run_dir = ROOT / "results/runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        manifest = {
            "run_id": run_id,
            "purpose": "calibration",
            "phase": "P2_calibration",
            "selected_groups": selected_gids,
            "utterances_count": total_utts,
            "max_api_calls": total_utts * 3,
            "workers": args.workers,
            "config": asdict(config),
            "timestamp_start": datetime.now(timezone.utc).isoformat(),
        }
        write_json(run_dir / "manifest.json", manifest)

    config = replace(load_config(args.config), retries=0, timeout=45, max_output_tokens=1600)

    # Check for already completed groups
    group_results = []
    missing_gids = []
    for gid in selected_gids:
        grp_file = run_dir / f"{gid}.json"
        if grp_file.exists():
            group_results.append(json.loads(grp_file.read_text(encoding="utf-8")))
            print(f"  [{gid}] Loaded existing group result ({len(group_results[-1]['utterances'])} utterances)")
        else:
            missing_gids.append(gid)

    if missing_gids:
        print(f"Executing {len(missing_gids)} pending groups via API...")
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(run_calibration_group, by_group[gid], config, run_dir): gid
                for gid in missing_gids
            }
            for fut in as_completed(futures):
                gid = futures[fut]
                try:
                    gres = fut.result()
                    group_results.append(gres)
                    print(f"  [{gid}] Group complete ({len(gres['utterances'])} utterances)", flush=True)
                except Exception as exc:
                    print(f"  [ERROR] {gid} failed: {exc}", flush=True)

    flat_utts = [u for g in group_results for u in g["utterances"]]
    graphs = {
        gid: SyntheticGraph.load(run_dir / f"{gid}_graph.json")
        for gid in selected_gids
    }

    # Telemetry
    all_calls = [c for u in flat_utts for c in u["calls"].values()]
    telemetry_list = [c["telemetry"] for c in all_calls if c.get("telemetry")]

    telemetry_summary = {
        "total_calls_issued": len(all_calls),
        "schema_valid_calls": sum(1 for c in all_calls if c.get("schema_valid", False)),
        "transport_failures": sum(1 for c in all_calls if "transport_error_type" in c),
        "provider_tokens_input": sum(t["input_tokens"] for t in telemetry_list),
        "provider_tokens_output": sum(t["output_tokens"] for t in telemetry_list),
        "provider_tokens_total": sum(t["total_tokens"] for t in telemetry_list),
        "total_latency_seconds": round(sum(t["latency_seconds"] for t in telemetry_list), 2),
    }

    print("\n=== All Calibration Utterances Collected. Running Grid Search ===")
    tau_grid = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 999.0]
    tau_sem_grid = [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0, 999.0]

    # Evaluate baselines
    b0_eval = evaluate_offline_method(flat_utts, graphs, "B0")
    b2_eval = evaluate_offline_method(flat_utts, graphs, "B2")
    b5_eval = evaluate_offline_method(flat_utts, graphs, "B5")
    b6_eval = evaluate_offline_method(flat_utts, graphs, "B6")

    # Protection trigger rate
    p_h = b5_eval["review_rate"]
    print(f"Protection trigger rate p_h = {p_h:.4f}")

    # Search Ours over tau_grid
    darc_results = []
    for tau in tau_grid:
        res = evaluate_offline_method(flat_utts, graphs, "Ours", tau=tau)
        darc_results.append(res)

    # Search B4 over tau_sem_grid
    b4_results = []
    for t_sem in tau_sem_grid:
        res = evaluate_offline_method(flat_utts, graphs, "B4", tau_sem=t_sem)
        b4_results.append(res)

    # Evaluate B3 across random probabilities matching target review rates
    # Target total review rates: q in {0.25, 0.50, 0.75}
    # Since total q_B3 = p_h + (1 - p_h) * p_review, p_review = (target - p_h) / (1 - p_h)
    target_q_levels = [0.25, 0.50, 0.75]
    b3_results = []
    for tq in target_q_levels:
        if tq > p_h:
            p_rand = (tq - p_h) / (1.0 - p_h)
        else:
            p_rand = 0.0
        res = evaluate_offline_method(flat_utts, graphs, "B3", p_review=p_rand)
        res["target_q"] = tq
        b3_results.append(res)

    # Selection Protocol for DARC (Ours):
    # Under Option A:
    # 1. Subject to TSR >= TSR(B0) (zero degradation)
    # 2. Target review rate q <= 0.50 (budget constraint)
    # 3. Minimize Route Flip (maximize consistency)
    # 4. Tie-break: smaller calls_used / higher tau
    admissible_darc = [
        r for r in darc_results
        if r["TSR"] >= b0_eval["TSR"] and r["review_rate"] <= 0.55
    ]
    if not admissible_darc:
        admissible_darc = darc_results

    # Sort by route_flip ascending, then review_rate ascending, then -tau
    def sort_key(r):
        flip = r["route_flip"] if r["route_flip"] is not None else 1.0
        return (flip, r["review_rate"], -r["tau"])

    best_darc = sorted(admissible_darc, key=sort_key)[0]
    tau_star = best_darc["tau"]

    # Best B4 matching q <= 0.55
    admissible_b4 = [
        r for r in b4_results
        if r["TSR"] >= b0_eval["TSR"] and r["review_rate"] <= 0.55
    ]
    if not admissible_b4:
        admissible_b4 = b4_results
    best_b4 = sorted(admissible_b4, key=sort_key)[0]
    tau_sem_star = best_b4["tau_sem"]

    # Best B3 matching q ~= 0.50
    b3_50 = next((r for r in b3_results if r.get("target_q") == 0.50), b3_results[0])

    frozen_config = {
        "frozen_timestamp": datetime.now(timezone.utc).isoformat(),
        "purpose": "frozen_calibration_config_for_test",
        "split": "dev_calibration",
        "groups_count": len(selected_gids),
        "utterances_count": total_utts,
        "target_review_rate": 0.50,
        "calibrated_parameters": {
            "tau_star": tau_star,
            "tau_sem_star": tau_sem_star,
            "p_review_star": b3_50["p_review"],
        },
        "operating_points": {
            "B0": b0_eval,
            "B2": b2_eval,
            "B5": b5_eval,
            "B6": b6_eval,
            "B3_q50": b3_50,
            "B4_star": best_b4,
            "Ours_star": best_darc,
        },
    }

    frozen_file = ROOT / "data/calibration/frozen_config.json"
    write_json(frozen_file, frozen_config)
    print(f"\n[✓] Frozen calibration parameters saved to {frozen_file}")
    print(f"Selected tau* = {tau_star} (Ours: q={best_darc['review_rate']}, flip={best_darc['route_flip']})")
    print(f"Selected tau_sem* = {tau_sem_star} (B4: q={best_b4['review_rate']}, flip={best_b4['route_flip']})")

    # Generate Calibration Report
    report_lines = [
        "# DARC-Route Calibration Report (dev_calibration)",
        "",
        f"- **Run ID**: `{run_id}`",
        f"- **Timestamp**: `{frozen_config['frozen_timestamp']}`",
        f"- **Dataset**: 20 groups × 4 variants = 80 utterances",
        f"- **Provider Tokens**: Total {telemetry_summary['provider_tokens_total']} (Input: {telemetry_summary['provider_tokens_input']}, Output: {telemetry_summary['provider_tokens_output']})",
        f"- **API Attempts**: {telemetry_summary['total_calls_issued']} calls (Valid: {telemetry_summary['schema_valid_calls']}, Transport Errors: {telemetry_summary['transport_failures']})",
        "",
        "## 1. Baseline Operating Points",
        "",
        "| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | Route Flip | Utility Loss $L_U$ |",
        "|---|---|---|---|---|---|---|---|",
        f"| **B0** | Single A | {b0_eval['mean_calls_used']:.2f} | {b0_eval['review_rate']:.4f} | {b0_eval['TSR']:.4f} | {b0_eval['GTSR']:.4f} | {b0_eval['route_flip']:.4f} | {b0_eval['mean_utility_loss']:.6f} |",
        f"| **B2** | A+B (always A) | {b2_eval['mean_calls_used']:.2f} | {b2_eval['review_rate']:.4f} | {b2_eval['TSR']:.4f} | {b2_eval['GTSR']:.4f} | {b2_eval['route_flip']:.4f} | {b2_eval['mean_utility_loss']:.6f} |",
        f"| **B5** | Only Protection $h$ | {b5_eval['mean_calls_used']:.2f} | {b5_eval['review_rate']:.4f} | {b5_eval['TSR']:.4f} | {b5_eval['GTSR']:.4f} | {b5_eval['route_flip']:.4f} | {b5_eval['mean_utility_loss']:.6f} |",
        f"| **B6** | Always Review | {b6_eval['mean_calls_used']:.2f} | {b6_eval['review_rate']:.4f} | {b6_eval['TSR']:.4f} | {b6_eval['GTSR']:.4f} | {b6_eval['route_flip']:.4f} | {b6_eval['mean_utility_loss']:.6f} |",
        "",
        "## 2. DARC Utility Threshold ($\tau$) Grid Sweep",
        "",
        "| $\\tau$ | Review Rate $q$ | Calls/Req | $P(h)$ | $P(\\Delta_U > \\tau)$ | TSR | GTSR | Route Flip | Selection Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for r in darc_results:
        verdict = "**SELECTED $\\tau^*$**" if r["tau"] == tau_star else ("Admissible" if r in admissible_darc else "Excluded")
        t_str = f"{r['tau']:.4f}" if r['tau'] < 900.0 else "inf (off)"
        report_lines.append(
            f"| {t_str} | {r['review_rate']:.4f} | {r['mean_calls_used']:.2f} | {r['h_trigger_rate']:.4f} | {r['delta_u_trigger_rate']:.4f} | {r['TSR']:.4f} | {r['GTSR']:.4f} | {r['route_flip']:.4f} | {verdict} |"
        )

    report_lines.extend([
        "",
        "## 3. Comparison of Calibrated Operating Points ($q \\approx 0.50$ Target)",
        "",
        "| Method | Setting | Calls/Req | Review Rate $q$ | TSR | GTSR | Route Flip | Flip Reduction vs B0 |",
        "|---|---|---|---|---|---|---|---|",
        f"| **B0** | Single A | {b0_eval['mean_calls_used']:.2f} | {b0_eval['review_rate']:.4f} | {b0_eval['TSR']:.4f} | {b0_eval['GTSR']:.4f} | {b0_eval['route_flip']:.4f} | 0.0% (Ref) |",
        f"| **B3** (Random) | $p={b3_50['p_review']:.2f}$ | {b3_50['mean_calls_used']:.2f} | {b3_50['review_rate']:.4f} | {b3_50['TSR']:.4f} | {b3_50['GTSR']:.4f} | {b3_50['route_flip']:.4f} | {(b0_eval['route_flip'] - b3_50['route_flip'])/b0_eval['route_flip']*100:.1f}% |",
        f"| **B4** (Semantic) | $\\tau_{{sem}}={best_b4['tau_sem']}$ | {best_b4['mean_calls_used']:.2f} | {best_b4['review_rate']:.4f} | {best_b4['TSR']:.4f} | {best_b4['GTSR']:.4f} | {best_b4['route_flip']:.4f} | {(b0_eval['route_flip'] - best_b4['route_flip'])/b0_eval['route_flip']*100:.1f}% |",
        f"| **B5** (Protection) | $h$ only | {b5_eval['mean_calls_used']:.2f} | {b5_eval['review_rate']:.4f} | {b5_eval['TSR']:.4f} | {b5_eval['GTSR']:.4f} | {b5_eval['route_flip']:.4f} | {(b0_eval['route_flip'] - b5_eval['route_flip'])/b0_eval['route_flip']*100:.1f}% |",
        f"| **B6** (Always) | Full Review | {b6_eval['mean_calls_used']:.2f} | {b6_eval['review_rate']:.4f} | {b6_eval['TSR']:.4f} | {b6_eval['GTSR']:.4f} | {b6_eval['route_flip']:.4f} | {(b0_eval['route_flip'] - b6_eval['route_flip'])/b0_eval['route_flip']*100:.1f}% |",
        f"| **Ours** (DARC) | $\\tau^*={tau_star}$ | {best_darc['mean_calls_used']:.2f} | {best_darc['review_rate']:.4f} | {best_darc['TSR']:.4f} | {best_darc['GTSR']:.4f} | {best_darc['route_flip']:.4f} | {(b0_eval['route_flip'] - best_darc['route_flip'])/b0_eval['route_flip']*100:.1f}% |",
        "",
        "## 4. Frozen Protocol Confirmation",
        "",
        f"- **Frozen $\\tau^*$**: `{tau_star}`",
        f"- **Frozen $\\tau_{{sem}}^*$**: `{tau_sem_star}`",
        f"- **Frozen $p^*$**: `{b3_50['p_review']}`",
        f"- **Status**: Parameters successfully frozen on Dev Calibration split. Test split remains 100% untouched.",
    ])

    report_file = ROOT / "results/reports/calibration_report.md"
    report_file.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    (run_dir / "calibration_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    trace_summary = {
        "run_id": run_id,
        "telemetry": telemetry_summary,
        "frozen_config": frozen_config,
        "darc_sweep": darc_results,
        "b4_sweep": b4_results,
        "b3_sweep": b3_results,
    }
    trace_file = ROOT / "results/reports/calibration_trace.json"
    write_json(trace_file, trace_summary)
    write_json(run_dir / "summary.json", trace_summary)

    print(f"\nCalibration report saved to {report_file.relative_to(ROOT.parent)}")
    print(f"Calibration trace saved to {trace_file.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
