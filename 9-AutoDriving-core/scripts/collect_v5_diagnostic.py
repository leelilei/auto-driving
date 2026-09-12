#!/usr/bin/env python3
"""Bounded, resumable v5.1 diagnostic collector."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import SyntheticGraph
from src.intent import Intent
from src.llm_client import LLM, load_config
from src.v5.contrast import build_contrast_report, differing_fields, intent_dict


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_response(raw: str) -> tuple[Intent, dict]:
    value = json.loads(raw)
    outer = value if isinstance(value, dict) else {}
    body = outer.get("intent", outer)
    return Intent.parse(body), {"evidence": outer.get("evidence", {}), "changes": outer.get("changes", [])}


def render(template: str, **values: object) -> str:
    result = template
    for name, value in values.items():
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
        result = result.replace("{{" + name + "}}", str(text))
    if re.search(r"\{\{[a-z_]+\}\}", result):
        raise ValueError("unresolved prompt placeholder")
    return result


def execute_call(llm: LLM, path: Path, call_id: str, role: str, system: str, user: str,
                 graph_condition: str | None = None, resume: bool = False) -> dict:
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("status") in {"COMPLETE", "SCHEMA_FAILED", "NOT_RUN_UPSTREAM_SCHEMA_FAILED"}:
            return existing
        if existing.get("status") != "TRANSPORT_FAILED" or not resume:
            raise RuntimeError(f"refusing to overwrite or retry recorded attempt: {path}")
        attempt = 2
        while path.with_name(f"{path.stem}.attempt{attempt}{path.suffix}").exists():
            candidate = path.with_name(f"{path.stem}.attempt{attempt}{path.suffix}")
            recorded = json.loads(candidate.read_text(encoding="utf-8"))
            if recorded.get("status") == "COMPLETE":
                return recorded
            attempt += 1
        path = path.with_name(f"{path.stem}.attempt{attempt}{path.suffix}")
    record = {"call_id": call_id, "role": role, "graph_condition": graph_condition, "started_at": stamp(),
              "request": {"system": system, "user": user}}
    try:
        raw = llm.complete(system, user)
        record["raw_response"] = raw
        intent, extra = parse_response(raw)
        record.update(status="COMPLETE", schema_valid=True, parsed_intent=intent_dict(intent), **extra)
    except Exception as exc:
        record.update(status="TRANSPORT_FAILED" if not llm.telemetry or not llm.telemetry[-1]["success"] else "SCHEMA_FAILED",
                      schema_valid=False, error_type=type(exc).__name__, error_message=str(exc))
    record["finished_at"] = stamp()
    record["telemetry"] = llm.telemetry[-1] if llm.telemetry else None
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def record_upstream_skip(path: Path, call_id: str, role: str, graph_condition: str,
                         upstream_status: dict[str, str]) -> dict:
    """Record a planned unit that cannot call the reviewer because A or B is invalid."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    now = stamp()
    record = {
        "call_id": call_id,
        "role": role,
        "graph_condition": graph_condition,
        "started_at": now,
        "finished_at": now,
        "status": "NOT_RUN_UPSTREAM_SCHEMA_FAILED",
        "schema_valid": False,
        "reason": "review requires schema-valid A and B candidates",
        "upstream_status": upstream_status,
        "telemetry": None,
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def summarize_collection(records: list[dict], planned: int, model: str, gids: list[str],
                         phase: str = "full") -> dict:
    terminal = {"COMPLETE", "SCHEMA_FAILED", "NOT_RUN_UPSTREAM_SCHEMA_FAILED"}
    logical_ids = {x["call_id"] for x in records if x.get("status") in terminal}
    valid_ids = {x["call_id"] for x in records if x.get("status") == "COMPLETE"}
    transport_ids = {x["call_id"] for x in records if x.get("status") == "TRANSPORT_FAILED"}
    collection_complete = len(logical_ids) == planned and not (transport_ids - logical_ids)
    return {
        "protocol_version": "darc-v5.1-collection-2",
        "model": model,
        "phase": phase,
        "groups": gids,
        "planned_calls": planned,
        "attempt_files": len(records),
        "logical_units_recorded": len(logical_ids),
        "complete_calls": len(valid_ids),
        "physical_attempts": sum(x.get("status") != "NOT_RUN_UPSTREAM_SCHEMA_FAILED" for x in records),
        "schema_failures": sum(x.get("status") == "SCHEMA_FAILED" for x in records),
        "skipped_upstream": sum(x.get("status") == "NOT_RUN_UPSTREAM_SCHEMA_FAILED" for x in records),
        "transport_failures": sum(x.get("status") == "TRANSPORT_FAILED" for x in records),
        "provider_total_tokens": sum(
            (x.get("telemetry") or {}).get("total_tokens", 0)
            for x in records
            if (x.get("telemetry") or {}).get("usage_source") == "provider"
        ),
        "collection_complete": collection_complete,
        "all_model_calls_schema_valid": not any(x.get("status") == "SCHEMA_FAILED" for x in records),
        "finished_at": stamp(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", type=Path, default=ROOT / "data/pilot/pilot_80_utterances.json")
    p.add_argument("--graphs", type=Path, required=True)
    p.add_argument("--admission", type=Path, required=True)
    p.add_argument("--config", type=Path, default=ROOT / "configs/llm_config_gpt56_terra.json")
    p.add_argument("--groups", type=int, default=1)
    p.add_argument("--group-start", type=int, default=0, help="zero-based offset in sorted group IDs")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--transport", choices=["urllib", "curl"])
    p.add_argument("--phase", choices=["candidates", "ab_reviews", "full"], default="full",
                   help="8, 56, or 72 logical units per group; later phases may expand the same immutable run")
    args = p.parse_args()
    admission = json.loads(args.admission.read_text())
    if not admission.get("collection_allowed"):
        raise RuntimeError("human review admission is not PASS")
    if admission.get("scope") == "author_constructed_candidate_only_design_smoke":
        allowed_dataset = ROOT / admission["allowed_dataset"]
        if args.phase != admission.get("allowed_phase") or args.dataset.resolve() != allowed_dataset.resolve():
            raise RuntimeError("design-smoke authorization is restricted to its candidate-only dataset and phase")
    records = json.loads(args.dataset.read_text())
    all_gids = sorted({str(x["group_id"]) for x in records})
    gids = all_gids[args.group_start:args.group_start + args.groups]
    if len(gids) != args.groups:
        raise RuntimeError("requested group range exceeds dataset")
    selected = sorted((x for x in records if x["group_id"] in gids), key=lambda x: x["utterance_id"])
    if len(selected) != args.groups * 4:
        raise RuntimeError("expected four utterances per group")
    prompt_dir = ROOT / "prompts/v5"
    prompts = {p.stem: p.read_text() for p in prompt_dir.glob("*.txt")}
    args.run_dir.mkdir(parents=True, exist_ok=True)
    attempt_dir = args.run_dir / "attempts"
    attempt_dir.mkdir(exist_ok=True)
    base = load_config(args.config)
    config = replace(base, retries=0, max_concurrency=1, max_output_tokens=1600,
                     transport=args.transport or base.transport)
    llm = LLM(config)
    calls: list[dict] = []
    stop_collection = False
    for item in selected:
        uid, instruction = item["utterance_id"], item["text"]
        candidates: dict[str, Intent] = {}
        extras: dict[str, dict] = {}
        roles = {
            "A": ("parse_a", prompts["parse_a"], instruction),
            "B": ("parse_b", prompts["parse_b"], instruction),
            "A2": ("parse_a", prompts["parse_a"], instruction),
            "A3": ("parse_a", prompts["parse_a"], instruction),
            "llmap_direct": ("llmap_direct_original", prompts["llmap_direct_original"], render(prompts["llmap_user_original"], instruction=instruction)),
            "llmap_cot": ("llmap_cot_original", prompts["llmap_cot_original"], render(prompts["llmap_user_original"], instruction=instruction)),
        }
        selected_roles = ("A", "B") if args.phase in {"candidates", "ab_reviews"} else tuple(roles)
        for role in selected_roles:
            _, system, user = roles[role]
            rec = execute_call(llm, attempt_dir / f"{uid}__{role}.json", f"{uid}::{role}", role, system, user,
                               resume=args.resume)
            calls.append(rec)
            if rec.get("schema_valid"):
                candidates[role] = Intent.parse(rec["parsed_intent"])
                extras[role] = rec
            if rec.get("status") == "TRANSPORT_FAILED":
                stop_collection = True
                break
        if stop_collection:
            break
        if args.phase == "candidates":
            continue
        if "A" not in candidates or "B" not in candidates:
            upstream_status = {
                role: next(x.get("status", "UNKNOWN") for x in reversed(calls) if x.get("call_id") == f"{uid}::{role}")
                for role in ("A", "B")
            }
            for condition in ("aligned", "tradeoff", "time_sensitive"):
                for role in ("review_plain", "review_fields", "review_constraints", "darc"):
                    rec = record_upstream_skip(
                        attempt_dir / f"{uid}__{condition}__{role}.json",
                        f"{uid}::{condition}::{role}", role, condition, upstream_status,
                    )
                    calls.append(rec)
            continue
        for condition in ("aligned", "tradeoff", "time_sensitive"):
            graph = SyntheticGraph.load(args.graphs / item["group_id"] / f"{condition}.json")
            report = build_contrast_report(instruction, candidates["A"], candidates["B"], graph,
                                           extras["A"].get("evidence"), extras["B"].get("evidence"))
            review_values = {
                "instruction": instruction,
                "candidate_a": intent_dict(candidates["A"]),
                "candidate_b": intent_dict(candidates["B"]),
                "field_differences": {"fields": differing_fields(candidates["A"], candidates["B"])},
                "cross_constraints": report["cross_constraints"],
                "decision_contrast_report": report,
            }
            for role, prompt_name in (("review_plain", "review_plain"), ("review_fields", "review_fields"),
                                      ("review_constraints", "review_constraints"), ("darc", "review_darc")):
                user = render(prompts[prompt_name], **review_values)
                rec = execute_call(llm, attempt_dir / f"{uid}__{condition}__{role}.json",
                                   f"{uid}::{condition}::{role}", role, "Return only the requested JSON object.", user,
                                   graph_condition=condition, resume=args.resume)
                calls.append(rec)
                if rec.get("status") == "TRANSPORT_FAILED":
                    stop_collection = True
                    break
            if stop_collection:
                break
        if stop_collection:
            break
    files = sorted(attempt_dir.glob("*.json"))
    all_records = [json.loads(path.read_text()) for path in files]
    planned_per_group = {"candidates": 8, "ab_reviews": 56, "full": 72}[args.phase]
    planned = args.groups * planned_per_group
    summary = summarize_collection(all_records, planned, config.model, gids, args.phase)
    (args.run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["collection_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
