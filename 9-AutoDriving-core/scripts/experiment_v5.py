#!/usr/bin/env python3
"""DARC-Route v5.1 staged experiment interface.

Only ``probe`` performs a network call. Other implemented commands are offline.
Collection and confirmatory analysis remain blocked until their contracts exist.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.intent import Intent
from src.llm_client import LLM, load_config
from src.evaluation import compare_intents
from src.v5.contrast import build_contrast_report
from src.v5.graph_family import build_graph_family, validate_graph_family


WEIGHTS = {"quality_first": 0.75, "balanced": 0.5, "distance_first": 0.25}
MODEL_SMOKE_FIXTURES = [
    {
        "id": "quality_and_order",
        "text": "Visit a bank and then a pharmacy. Choose the best-rated places even if the trip is longer.",
        "gold": {"pois": ["bank", "pharmacy"], "time_limit": None,
                 "dependencies": [["bank", "pharmacy"]], "quality_weight": 0.75},
        "direction": "quality_first",
    },
    {
        "id": "distance_and_deadline",
        "text": "Go to a library and a supermarket, return by 18:30, and keep the route as short as possible.",
        "gold": {"pois": ["library", "supermarket"], "time_limit": 1110,
                 "dependencies": [], "quality_weight": 0.25},
        "direction": "distance_first",
    },
    {
        "id": "balanced",
        "text": "Stop at a shopping mall and a bank. Balance good ratings with a manageable travel distance.",
        "gold": {"pois": ["shopping_mall", "bank"], "time_limit": None,
                 "dependencies": [], "quality_weight": 0.5},
        "direction": "balanced",
    },
    {
        "id": "three_step_dependency",
        "text": "Visit the supermarket before the pharmacy, then go to the library. I care more about a quick route.",
        "gold": {"pois": ["supermarket", "pharmacy", "library"], "time_limit": None,
                 "dependencies": [["supermarket", "pharmacy"], ["pharmacy", "library"]],
                 "quality_weight": 0.25},
        "direction": "distance_first",
    },
    {
        "id": "no_preference_with_time",
        "text": "Visit a pharmacy before 20:00. No preference between rating and travel distance.",
        "gold": {"pois": ["pharmacy"], "time_limit": 1200,
                 "dependencies": [], "quality_weight": 0.5},
        "direction": "balanced",
    },
]
REVIEW_SMOKE_FIXTURES = [
    {
        "id": "resist_route_preference",
        "text": "Visit the bank before the pharmacy and keep the route short.",
        "gold": {"pois": ["bank", "pharmacy"], "time_limit": None,
                 "dependencies": [["bank", "pharmacy"]], "quality_weight": 0.25},
        "a": {"pois": ["bank", "pharmacy"], "time_limit": None,
              "dependencies": [["bank", "pharmacy"]], "quality_weight": 0.25},
        "b": {"pois": ["bank", "pharmacy"], "time_limit": None,
              "dependencies": [["pharmacy", "bank"]], "quality_weight": 0.75},
        "direction": "distance_first",
    },
    {
        "id": "select_text_supported_quality",
        "text": "Visit a library and a supermarket before 20:00. Choose the best-rated places even if the trip is longer; there is no required order.",
        "gold": {"pois": ["library", "supermarket"], "time_limit": 1200,
                 "dependencies": [], "quality_weight": 0.75},
        "a": {"pois": ["library", "supermarket"], "time_limit": 1200,
              "dependencies": [], "quality_weight": 0.25},
        "b": {"pois": ["library", "supermarket"], "time_limit": 1200,
              "dependencies": [], "quality_weight": 0.75},
        "direction": "quality_first",
    },
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def load_records(path: Path) -> list[dict[str, object]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("dataset must be a JSON list")
    return value


def split_groups(value: dict[str, object]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for key in ("dev_pilot", "dev_calibration", "test"):
        part = value.get(key, [])
        if isinstance(part, list):
            records.extend(item for item in part if isinstance(item, dict))
    return records


def record_intent(record: dict[str, object]) -> Intent:
    direction = record.get("preference_direction")
    if direction not in WEIGHTS:
        raise ValueError(f"unsupported preference direction: {direction!r}")
    return Intent.parse({**record["gold_hard"], "quality_weight": WEIGHTS[direction]})


def cmd_preflight(args: argparse.Namespace) -> int:
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = {
        "status": "PASS",
        "offline": True,
        "network_calls": 0,
        "python": sys.version,
        "platform": platform.platform(),
        "protocol_version": config["protocol_version"],
        "config_sha256": sha256(args.config),
        "hipp_sha256": sha256(ROOT / "data/raw/HIPP.json"),
        "implemented_commands": ["preflight", "audit-data", "build-graphs", "contrast-smoke", "plan-diagnostic", "validate-review", "probe", "model-smoke", "review-smoke"],
        "not_implemented": ["plan", "collect", "analyze", "replay", "package"],
        "confirmatory_collection_allowed": False,
    }
    if args.out:
        write_new(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_audit_data(args: argparse.Namespace) -> int:
    splits = json.loads(args.splits.read_text(encoding="utf-8"))
    clusters = json.loads(args.clusters.read_text(encoding="utf-8"))
    pilot = load_records(args.pilot)
    selected = split_groups(splits)
    exposed_indices = {int(item["source_index"]) for item in selected}
    exposed_clusters = {int(item["source_cluster_id"]) for item in selected}
    eligible_clusters = [
        item for item in clusters
        if int(item["cluster_id"]) not in exposed_clusters
        and any(int(record["source_index"]) not in exposed_indices for record in item.get("records", []))
    ]
    annotation_counts: dict[str, int] = {}
    for record in pilot:
        status = str(record.get("annotation_status", "missing"))
        annotation_counts[status] = annotation_counts.get(status, 0) + 1
    result = {
        "status": "BLOCKED_ON_ANNOTATION" if annotation_counts.get("pending") else "READY_FOR_REVIEW",
        "scope": "qualification count only; no new test split selected",
        "candidate_split_groups_exposed": len(selected),
        "direct_source_indices_exposed": len(exposed_indices),
        "semantic_clusters_exposed": len(exposed_clusters),
        "remaining_candidate_clusters": len(eligible_clusters),
        "remaining_candidate_records": sum(len(item.get("records", [])) for item in eligible_clusters),
        "pilot_annotation_counts": annotation_counts,
        "pilot_groups": len({str(record["group_id"]) for record in pilot}),
        "test_selection_performed": False,
        "warning": "The historical 200-group candidate split is development-exposed and cannot be reused as an untouched v5 test.",
        "inputs": {
            "splits_sha256": sha256(args.splits),
            "clusters_sha256": sha256(args.clusters),
            "pilot_sha256": sha256(args.pilot),
        },
    }
    write_new(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_build_graphs(args: argparse.Namespace) -> int:
    records = load_records(args.dataset)
    group_first: dict[str, dict[str, object]] = {}
    for record in records:
        group_first.setdefault(str(record["group_id"]), record)
    selected = sorted(group_first)[: args.groups]
    output = args.out
    output.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, object] = {
        "protocol_version": "darc-v5.1-graphs-1",
        "dataset": str(args.dataset.resolve()),
        "dataset_sha256": sha256(args.dataset),
        "groups": [],
        "development_only": True,
    }
    for group_id in selected:
        intent = record_intent(group_first[group_id])
        graphs = build_graph_family(group_id)
        validation = validate_graph_family(graphs, intent)
        if not validation["valid"]:
            raise RuntimeError(f"graph family failed for {group_id}: {validation}")
        group_dir = output / group_id
        files: dict[str, dict[str, str]] = {}
        for condition, graph in graphs.items():
            graph_path = group_dir / f"{condition}.json"
            write_new(graph_path, graph.to_dict())
            files[condition] = {
                "path": str(graph_path.relative_to(output)),
                "sha256": sha256(graph_path),
            }
        manifest["groups"].append(
            {"group_id": group_id, "intent": asdict(intent), "validation": validation, "files": files}
        )
    write_new(output / "manifest.json", manifest)
    print(json.dumps({"status": "PASS", "groups": len(selected), "out": str(output)}, indent=2))
    return 0


def cmd_contrast_smoke(args: argparse.Namespace) -> int:
    a = Intent.parse({"pois": ["bank", "pharmacy"], "time_limit": None,
                      "dependencies": [["bank", "pharmacy"]], "quality_weight": 0.25})
    b = Intent.parse({"pois": ["bank", "pharmacy"], "time_limit": None,
                      "dependencies": [["pharmacy", "bank"]], "quality_weight": 0.75})
    graph = build_graph_family("manual_fixture")["tradeoff"]
    report = build_contrast_report(
        "Visit the bank before the pharmacy and keep the route short.", a, b, graph,
        evidence_a={"dependencies": "bank before the pharmacy", "quality_weight": "keep the route short"},
        evidence_b={"dependencies": "bank before the pharmacy", "quality_weight": "keep the route short"},
    )
    write_new(args.out, report)
    print(json.dumps({"status": "PASS", "swaps": len(report["single_field_swaps"]), "out": str(args.out)}, indent=2))
    return 0


def cmd_plan_diagnostic(args: argparse.Namespace) -> int:
    records = load_records(args.dataset)
    groups = sorted({str(record["group_id"]) for record in records})[: args.groups]
    selected = [record for record in records if str(record["group_id"]) in groups]
    if len(selected) != args.groups * 4:
        raise ValueError("diagnostic plan requires exactly four utterances per selected group")
    args.out.mkdir(parents=True, exist_ok=False)
    units: list[dict[str, object]] = []
    shared_roles = ("A", "B", "A2", "A3", "llmap_direct", "llmap_cot")
    review_roles = ("review_plain", "review_fields", "review_constraints", "darc")
    for record in sorted(selected, key=lambda item: str(item["utterance_id"])):
        uid = str(record["utterance_id"])
        for role in shared_roles:
            units.append({"unit_id": f"{uid}::{role}", "utterance_id": uid, "group_id": record["group_id"],
                          "graph_condition": None, "role": role, "status": "PLANNED"})
        for condition in ("aligned", "tradeoff", "time_sensitive"):
            for role in review_roles:
                units.append({"unit_id": f"{uid}::{condition}::{role}", "utterance_id": uid,
                              "group_id": record["group_id"], "graph_condition": condition,
                              "role": role, "status": "PLANNED"})
    with (args.out / "expected_units.jsonl").open("x", encoding="utf-8") as handle:
        for unit in units:
            handle.write(json.dumps(unit, ensure_ascii=False) + "\n")
    annotation_counts: dict[str, int] = {}
    for record in selected:
        status = str(record.get("annotation_status", "missing"))
        annotation_counts[status] = annotation_counts.get(status, 0) + 1
    plan = {
        "protocol_version": "darc-v5.1-diagnostic-plan-1",
        "stage": "S2_diagnostic8",
        "dataset": str(args.dataset.resolve()),
        "dataset_sha256": sha256(args.dataset),
        "selected_groups": groups,
        "utterances": len(selected),
        "graph_instances": len(selected) * 3,
        "planned_calls": len(units),
        "expected_calls_formula": "groups * 4 utterances * (6 shared + 3 graphs * 4 reviews)",
        "annotation_counts": annotation_counts,
        "collection_allowed": not annotation_counts.get("pending") and not annotation_counts.get("missing"),
        "blocker": "pilot annotations are pending" if annotation_counts.get("pending") else None,
        "retries": 0,
        "method_gating": False,
        "hash_used_for_decisions": False,
    }
    write_new(args.out / "plan.json", plan)
    write_new(args.out / "budget.json", {
        "planned_calls": len(units), "input_token_estimate": None, "output_token_estimate": None,
        "price_source": None, "estimated_currency_cost": None,
        "status": "token and price estimate pending prompt freeze",
    })
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


def validate_human_review(dataset: Path, review_path: Path, groups: int) -> dict[str, object]:
    records = load_records(dataset)
    selected_groups = sorted({str(item["group_id"]) for item in records})[:groups]
    selected = [item for item in records if str(item["group_id"]) in selected_groups]
    expected = {str(item["utterance_id"]) for item in selected}
    review = json.loads(review_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    if review.get("protocol_version") != "darc-v5.1-human-review-1":
        issues.append("unexpected protocol_version")
    if not str(review.get("reviewer", "")).strip():
        issues.append("missing reviewer identity")
    if not str(review.get("reviewed_at", "")).strip():
        issues.append("missing reviewed_at")
    rows = review.get("records")
    if not isinstance(rows, list):
        rows = []
        issues.append("records must be a list")
    ids = [str(item.get("utterance_id")) for item in rows if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        issues.append("duplicate utterance_id")
    if set(ids) != expected:
        issues.append("review scope does not exactly match selected utterances")
    nonpass: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            issues.append("non-object review row")
            continue
        uid = str(item.get("utterance_id"))
        for field in ("equivalence", "label_support"):
            if item.get(field) not in {"yes", "no", "unclear"}:
                issues.append(f"{uid}: invalid {field}")
        if item.get("equivalence") != "yes" or item.get("label_support") != "yes":
            nonpass.append(uid)
    admitted = not issues and not nonpass and len(rows) == groups * 4
    return {
        "protocol_version": "darc-v5.1-review-admission-1",
        "status": "PASS" if admitted else "BLOCKED",
        "collection_allowed": admitted,
        "dataset": str(dataset.resolve()),
        "dataset_sha256": sha256(dataset),
        "review": str(review_path.resolve()),
        "review_sha256": sha256(review_path),
        "reviewer": review.get("reviewer"),
        "reviewed_at": review.get("reviewed_at"),
        "expected_utterances": len(expected),
        "reviewed_utterances": len(rows),
        "issues": issues,
        "nonpassing_utterances": sorted(set(nonpass)),
    }


def cmd_validate_review(args: argparse.Namespace) -> int:
    result = validate_human_review(args.dataset, args.review, args.groups)
    write_new(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["collection_allowed"] else 2


def cmd_attest_review(args: argparse.Namespace) -> int:
    if args.attestation != "ALL_UTTERANCES_REVIEWED_AND_PASSED":
        raise ValueError("explicit all-pass attestation phrase is required")
    records = load_records(args.dataset)
    group_ids = sorted({str(item["group_id"]) for item in records})[:args.groups]
    selected = [item for item in records if str(item["group_id"]) in group_ids]
    payload = {
        "protocol_version": "darc-v5.1-human-review-1",
        "reviewer": args.reviewer,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "source": str(args.dataset.resolve()),
        "attestation_basis": args.basis,
        "scope_groups": group_ids,
        "records": [{"group_id": item["group_id"], "utterance_id": item["utterance_id"],
                     "equivalence": "yes", "label_support": "yes",
                     "note": "covered by explicit all-pass attestation"} for item in selected],
    }
    write_new(args.out, payload)
    print(json.dumps({"status": "RECORDED", "groups": len(group_ids),
                      "utterances": len(selected), "out": str(args.out)}, ensure_ascii=False))
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    """Perform exactly one bounded provider request and preserve its evidence."""
    base = load_config(args.config)
    if base.provider == "mock":
        raise ValueError("probe requires a non-mock provider")
    if not base.api_key_env or not os.environ.get(base.api_key_env):
        raise ValueError("configured API key environment variable is absent")
    config = replace(
        base,
        retries=0,
        max_concurrency=1,
        timeout=min(base.timeout, 45),
        max_output_tokens=200,
        transport=args.transport or base.transport,
    )
    model_slug = "".join(char if char.isalnum() else "_" for char in config.model)
    run_dir = args.out / f"{utc_stamp()}_{model_slug}_probe"
    run_dir.mkdir(parents=True, exist_ok=False)
    public_config = asdict(config)
    system = "Return only a JSON object with keys status and capability."
    user = "Connectivity probe for DARC-Route v5.1. Set status to ok and capability to json."
    started = datetime.now(timezone.utc).isoformat()
    llm = LLM(config)
    record: dict[str, object] = {
        "protocol_version": "darc-v5.1-probe-1",
        "started_at": started,
        "planned_calls": 1,
        "config": public_config,
        "request": {"system": system, "user": user},
    }
    exit_code = 0
    try:
        raw = llm.complete(system, user)
        record["raw_response"] = raw
        try:
            parsed = json.loads(raw)
            record["json_valid"] = isinstance(parsed, dict)
            record["parsed_response"] = parsed
        except json.JSONDecodeError as exc:
            record.update(json_valid=False, parse_error=str(exc))
            exit_code = 2
    except Exception as exc:
        record.update(error_type=type(exc).__name__, error_message=str(exc), json_valid=False)
        exit_code = 2
    record.update(finished_at=datetime.now(timezone.utc).isoformat(), telemetry=llm.telemetry[-1])
    write_new(run_dir / "probe.json", record)
    write_new(run_dir / "manifest.json", {"probe_sha256": sha256(run_dir / "probe.json")})
    print(json.dumps({"status": "PASS" if exit_code == 0 else "FAIL", "run_dir": str(run_dir),
                      "usage_source": record["telemetry"]["usage_source"]}, indent=2))
    return exit_code


def weight_direction(weight: float) -> str:
    if weight > 0.6:
        return "quality_first"
    if weight < 0.4:
        return "distance_first"
    return "balanced"


def cmd_model_smoke(args: argparse.Namespace) -> int:
    """Evaluate a candidate model on five hand-authored development fixtures."""
    base = load_config(args.config)
    if base.provider == "mock":
        raise ValueError("model-smoke requires a non-mock provider")
    config = replace(base, retries=0, max_concurrency=1, timeout=min(base.timeout, 60),
                     max_output_tokens=800, json_mode=True, omit_temperature=True,
                     transport=args.transport or base.transport)
    model_slug = "".join(char if char.isalnum() else "_" for char in config.model)
    run_dir = args.out / f"{utc_stamp()}_{model_slug}_model_smoke"
    run_dir.mkdir(parents=True, exist_ok=False)
    system = (
        "Parse a route request. Return only JSON with exactly these keys: pois, time_limit, "
        "dependencies, quality_weight. Allowed POIs: shopping_mall, supermarket, pharmacy, "
        "bank, library. time_limit is HH:MM or null. dependencies is an array of [before, after]. "
        "quality_weight is in [0,1]: above 0.6 for quality-first, below 0.4 for distance-first, "
        "and 0.5 when explicitly balanced or no preference. Do not add unstated constraints."
    )
    llm = LLM(config)
    records: list[dict[str, object]] = []
    for fixture in MODEL_SMOKE_FIXTURES:
        call: dict[str, object] = {"fixture_id": fixture["id"], "text": fixture["text"],
                                  "gold": fixture["gold"], "started_at": datetime.now(timezone.utc).isoformat()}
        try:
            raw = llm.complete(system, str(fixture["text"]))
            call["raw_response"] = raw
            try:
                predicted = Intent.parse(json.loads(raw))
                gold = Intent.parse(fixture["gold"])
                call.update(schema_valid=True, predicted=asdict(predicted),
                            hard=compare_intents(predicted, gold),
                            direction_predicted=weight_direction(predicted.quality_weight),
                            direction_exact=weight_direction(predicted.quality_weight) == fixture["direction"])
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                call.update(schema_valid=False, parse_error=str(exc), hard={"hard_exact": False},
                            direction_exact=False)
        except Exception as exc:
            call.update(schema_valid=False, transport_error_type=type(exc).__name__,
                        error_message=str(exc), hard={"hard_exact": False}, direction_exact=False)
        call.update(finished_at=datetime.now(timezone.utc).isoformat(), telemetry=llm.telemetry[-1])
        write_new(run_dir / f"{fixture['id']}.json", call)
        records.append(call)
        if "transport_error_type" in call:
            break
    completed = len(records) == len(MODEL_SMOKE_FIXTURES) and not any("transport_error_type" in r for r in records)
    summary = {
        "scope": "hand-authored development model selection; not a paper result",
        "model": config.model,
        "transport": config.transport,
        "planned_calls": len(MODEL_SMOKE_FIXTURES),
        "attempted_calls": len(records),
        "collection_complete": completed,
        "schema_valid": sum(bool(r.get("schema_valid")) for r in records),
        "hard_exact": sum(bool((r.get("hard") or {}).get("hard_exact")) for r in records),
        "direction_exact": sum(bool(r.get("direction_exact")) for r in records),
        "provider_usage_calls": sum((r["telemetry"]["usage_source"] == "provider") for r in records),
        "provider_total_tokens": sum(r["telemetry"]["total_tokens"] for r in records
                                     if r["telemetry"]["usage_source"] == "provider"),
        "mean_latency_seconds": sum(r["telemetry"]["latency_seconds"] for r in records) / len(records),
    }
    write_new(run_dir / "summary.json", summary)
    write_new(run_dir / "manifest.json", {
        "config": asdict(config), "system_prompt": system,
        "fixture_version": "v5.1-model-smoke-1", "summary_sha256": sha256(run_dir / "summary.json"),
    })
    print(json.dumps({**summary, "run_dir": str(run_dir)}, ensure_ascii=False, indent=2))
    return 0 if completed else 2


def cmd_review_smoke(args: argparse.Namespace) -> int:
    """Check whether a model uses decision reports without overriding the text."""
    base = load_config(args.config)
    config = replace(base, retries=0, max_concurrency=1, timeout=min(base.timeout, 60),
                     max_output_tokens=800, json_mode=True, omit_temperature=True,
                     transport=args.transport or base.transport)
    model_slug = "".join(char if char.isalnum() else "_" for char in config.model)
    run_dir = args.out / f"{utc_stamp()}_{model_slug}_review_smoke"
    run_dir.mkdir(parents=True, exist_ok=False)
    system = (
        "Review two candidate route intents using the original instruction as the only evidence of user intent. "
        "The decision report shows consequences, not truth. Never change a preference merely because one route "
        "looks more efficient. Return only JSON with pois, time_limit, dependencies, quality_weight."
    )
    llm = LLM(config)
    records: list[dict[str, object]] = []
    for fixture in REVIEW_SMOKE_FIXTURES:
        candidate_a, candidate_b = Intent.parse(fixture["a"]), Intent.parse(fixture["b"])
        report = build_contrast_report(str(fixture["text"]), candidate_a, candidate_b,
                                       build_graph_family(str(fixture["id"]))["tradeoff"])
        user = json.dumps({"instruction": fixture["text"], "decision_report": report}, ensure_ascii=False)
        call: dict[str, object] = {"fixture_id": fixture["id"], "text": fixture["text"],
                                  "gold": fixture["gold"], "decision_report": report,
                                  "started_at": datetime.now(timezone.utc).isoformat()}
        try:
            raw = llm.complete(system, user)
            call["raw_response"] = raw
            try:
                predicted, gold = Intent.parse(json.loads(raw)), Intent.parse(fixture["gold"])
                call.update(schema_valid=True, predicted=asdict(predicted), hard=compare_intents(predicted, gold),
                            direction_predicted=weight_direction(predicted.quality_weight),
                            direction_exact=weight_direction(predicted.quality_weight) == fixture["direction"])
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                call.update(schema_valid=False, parse_error=str(exc), hard={"hard_exact": False}, direction_exact=False)
        except Exception as exc:
            call.update(schema_valid=False, transport_error_type=type(exc).__name__, error_message=str(exc),
                        hard={"hard_exact": False}, direction_exact=False)
        call.update(finished_at=datetime.now(timezone.utc).isoformat(), telemetry=llm.telemetry[-1])
        write_new(run_dir / f"{fixture['id']}.json", call)
        records.append(call)
        if "transport_error_type" in call:
            break
    complete = len(records) == len(REVIEW_SMOKE_FIXTURES) and not any("transport_error_type" in r for r in records)
    summary = {
        "scope": "hand-authored decision-report development check; not a paper result",
        "model": config.model, "planned_calls": 2, "attempted_calls": len(records),
        "collection_complete": complete,
        "schema_valid": sum(bool(r.get("schema_valid")) for r in records),
        "hard_exact": sum(bool((r.get("hard") or {}).get("hard_exact")) for r in records),
        "direction_exact": sum(bool(r.get("direction_exact")) for r in records),
        "provider_total_tokens": sum(r["telemetry"]["total_tokens"] for r in records
                                     if r["telemetry"]["usage_source"] == "provider"),
        "mean_latency_seconds": sum(r["telemetry"]["latency_seconds"] for r in records) / len(records),
    }
    write_new(run_dir / "summary.json", summary)
    write_new(run_dir / "manifest.json", {"config": asdict(config), "system_prompt": system,
                                            "summary_sha256": sha256(run_dir / "summary.json")})
    print(json.dumps({**summary, "run_dir": str(run_dir)}, ensure_ascii=False, indent=2))
    return 0 if complete else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    common_config = ROOT / "configs/v5/development.json"
    p = sub.add_parser("preflight")
    p.add_argument("--config", type=Path, default=common_config)
    p.add_argument("--out", type=Path)
    p.set_defaults(func=cmd_preflight)
    p = sub.add_parser("build-graphs")
    p.add_argument("--dataset", type=Path, required=True)
    p.add_argument("--groups", type=int, default=8)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_build_graphs)
    p = sub.add_parser("audit-data")
    p.add_argument("--splits", type=Path, default=ROOT / "data/processed/candidate_splits.json")
    p.add_argument("--clusters", type=Path, default=ROOT / "data/processed/hipp_clusters.json")
    p.add_argument("--pilot", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_audit_data)
    p = sub.add_parser("contrast-smoke")
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_contrast_smoke)
    p = sub.add_parser("plan-diagnostic")
    p.add_argument("--dataset", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    p.add_argument("--groups", type=int, default=8)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_plan_diagnostic)
    p = sub.add_parser("validate-review")
    p.add_argument("--dataset", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--groups", type=int, default=8)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_validate_review)
    p = sub.add_parser("attest-review")
    p.add_argument("--dataset", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    p.add_argument("--groups", type=int, default=8)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--basis", required=True)
    p.add_argument("--attestation", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(func=cmd_attest_review)
    p = sub.add_parser("probe")
    p.add_argument("--config", type=Path, default=ROOT / "configs/llm_config.json")
    p.add_argument("--out", type=Path, default=ROOT / "results/v5/probes")
    p.add_argument("--transport", choices=["curl", "urllib"], help="bounded diagnostic override")
    p.set_defaults(func=cmd_probe)
    p = sub.add_parser("model-smoke")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT / "results/v5/model_selection")
    p.add_argument("--transport", choices=["curl", "urllib"])
    p.set_defaults(func=cmd_model_smoke)
    p = sub.add_parser("review-smoke")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT / "results/v5/model_selection")
    p.add_argument("--transport", choices=["curl", "urllib"])
    p.set_defaults(func=cmd_review_smoke)
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
