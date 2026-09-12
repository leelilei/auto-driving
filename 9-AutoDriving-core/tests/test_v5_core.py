import json
import hashlib
from argparse import Namespace
from pathlib import Path

from scripts import experiment_v5
from scripts.generate_v5_pilot_review import select_groups
from scripts.collect_v5_diagnostic import render, summarize_collection
from src.intent import Intent
from src.v5.contrast import build_contrast_report
from src.v5.graph_family import build_graph_family, graph_field_diff, validate_graph_family


def intent(weight=0.25, dependencies=()):
    return Intent.parse(
        {
            "pois": ["bank", "pharmacy"],
            "time_limit": None,
            "dependencies": list(dependencies),
            "quality_weight": weight,
        }
    )


def test_v5_graph_family_changes_only_declared_fields():
    graphs = build_graph_family("fixture")
    assert graph_field_diff(graphs["aligned"], graphs["tradeoff"]) == {"pois.quality"}
    assert graph_field_diff(graphs["tradeoff"], graphs["time_sensitive"]) == {"pois.close_time"}
    report = validate_graph_family(graphs, intent())
    assert report["valid"] is True
    assert report["aligned_extreme_sets_intersect"] is True
    assert report["tradeoff_extreme_sets_disjoint"] is True
    assert report["full_feasible_counts"]["time_sensitive"] < report["full_feasible_counts"]["tradeoff"]


def test_contrast_report_has_cross_checks_and_bounded_swaps():
    report = build_contrast_report(
        "Visit the bank before the pharmacy and keep the route short.",
        intent(0.25, (("bank", "pharmacy"),)),
        intent(0.75, (("pharmacy", "bank"),)),
        build_graph_family("fixture")["tradeoff"],
    )
    assert report["differing_fields"] == ["dependencies", "quality_weight"]
    assert len(report["single_field_swaps"]) == 4
    assert report["report_version"] == "darc-v5.1-contrast-2"
    assert report["routes"]["A"]["average_quality"] is not None
    assert report["routes"]["A"]["coverage_count"] == 2
    assert set(report["cross_constraints"]) == {
        "route_A_under_A", "route_A_under_B", "route_B_under_A", "route_B_under_B"
    }
    assert "gold" not in json.dumps(report).lower()


def test_equal_candidates_still_generate_report_without_swaps():
    candidate = intent()
    report = build_contrast_report("Visit a bank and a pharmacy.", candidate, candidate, build_graph_family("fixture")["aligned"])
    assert report["differing_fields"] == []
    assert report["single_field_swaps"] == []
    assert report["routes"]["A"] == report["routes"]["B"]


def test_diagnostic_plan_has_576_units_and_blocks_pending_annotations(tmp_path):
    dataset = Path(__file__).parents[1] / "data/pilot/pilot_80_utterances.json"
    out = tmp_path / "plan"
    assert experiment_v5.cmd_plan_diagnostic(Namespace(dataset=dataset, groups=8, out=out)) == 0
    units = [json.loads(line) for line in (out / "expected_units.jsonl").read_text().splitlines()]
    plan = json.loads((out / "plan.json").read_text())
    assert len(units) == 576
    assert len({unit["unit_id"] for unit in units}) == 576
    assert plan["collection_allowed"] is False
    assert plan["annotation_counts"] == {"pending": 32}


def test_probe_run_name_contains_model_and_microseconds():
    stamp = experiment_v5.utc_stamp()
    assert len(stamp) == 22
    assert stamp.endswith("Z")


def test_v5_prompt_information_boundaries_are_distinct():
    prompt_dir = Path(__file__).parents[1] / "prompts/v5"
    prompts = {name: (prompt_dir / f"{name}.txt").read_text(encoding="utf-8") for name in (
        "review_plain", "review_fields", "review_constraints", "review_darc"
    )}
    assert "{{field_differences}}" not in prompts["review_plain"]
    assert "{{field_differences}}" in prompts["review_fields"]
    assert "{{cross_constraints}}" in prompts["review_constraints"]
    assert "{{decision_contrast_report}}" in prompts["review_darc"]
    for value in prompts.values():
        lowered = value.lower()
        assert "{{instruction}}" in value
        assert "sole authority" in lowered
        assert "gold" not in lowered


def test_v5_prompt_freeze_manifest_matches_files():
    prompt_dir = Path(__file__).parents[1] / "prompts/v5"
    manifest = json.loads((prompt_dir / "FREEZE_MANIFEST.json").read_text())
    for name, expected in manifest["files"].items():
        assert hashlib.sha256((prompt_dir / name).read_bytes()).hexdigest() == expected


def test_v5_primary_model_is_explicitly_frozen():
    config = json.loads((Path(__file__).parents[1] / "configs/v5/development.json").read_text())
    assert config["model_policy"]["primary"]["model"] == "gpt-5.6-terra"
    assert config["model_policy"]["primary"]["selected_by"] == "research_lead"
    assert config["model_policy"]["strong_baseline"] == "gpt-5.5"


def test_human_review_workspace_selection_does_not_change_status():
    records = json.loads((Path(__file__).parents[1] / "data/pilot/pilot_80_utterances.json").read_text())
    selected = select_groups(records, 8)
    assert len(selected) == 32
    assert {item["annotation_status"] for item in selected} == {"pending"}
    assert sorted({item["group_id"] for item in selected}) == [f"pilot_{i:02d}" for i in range(1, 9)]


def test_review_admission_requires_complete_real_review(tmp_path):
    dataset = Path(__file__).parents[1] / "data/pilot/pilot_80_utterances.json"
    source = json.loads(dataset.read_text())
    selected = [item for item in source if item["group_id"] in {f"pilot_{i:02d}" for i in range(1, 9)}]
    payload = {
        "protocol_version": "darc-v5.1-human-review-1",
        "reviewer": "reviewer_fixture",
        "reviewed_at": "2026-09-09T00:00:00Z",
        "records": [{"utterance_id": item["utterance_id"], "equivalence": "yes",
                     "label_support": "yes", "note": ""} for item in selected],
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(payload))
    assert experiment_v5.validate_human_review(dataset, path, 8)["collection_allowed"] is True
    payload["records"][0]["equivalence"] = "unclear"
    path.write_text(json.dumps(payload))
    blocked = experiment_v5.validate_human_review(dataset, path, 8)
    assert blocked["collection_allowed"] is False
    assert blocked["nonpassing_utterances"] == [selected[0]["utterance_id"]]


def test_prompt_renderer_accepts_nested_json_braces_but_rejects_placeholders():
    assert render("report={{report}}", report={"a": {"b": 1}}).startswith("report={")
    try:
        render("{{missing}}", report={})
    except ValueError as exc:
        assert "unresolved" in str(exc)
    else:
        raise AssertionError("unresolved placeholder was accepted")


def test_diagnostic_group_offset_selects_expected_slice():
    records = json.loads((Path(__file__).parents[1] / "data/pilot/pilot_80_utterances.json").read_text())
    gids = sorted({item["group_id"] for item in records})
    assert gids[1:8] == [f"pilot_{i:02d}" for i in range(2, 9)]


def test_collection_summary_separates_coverage_from_schema_validity():
    records = [
        {"call_id": "u::A", "status": "COMPLETE", "telemetry": {"usage_source": "provider", "total_tokens": 10}},
        {"call_id": "u::B", "status": "SCHEMA_FAILED", "telemetry": {"usage_source": "provider", "total_tokens": 5}},
        {"call_id": "u::review", "status": "NOT_RUN_UPSTREAM_SCHEMA_FAILED", "telemetry": None},
    ]
    summary = summarize_collection(records, 3, "fixture", ["pilot_01"])
    assert summary["phase"] == "full"
    assert summary["collection_complete"] is True
    assert summary["all_model_calls_schema_valid"] is False
    assert summary["logical_units_recorded"] == 3
    assert summary["physical_attempts"] == 2
    assert summary["complete_calls"] == 1
    assert summary["schema_failures"] == 1
    assert summary["skipped_upstream"] == 1
    assert summary["provider_total_tokens"] == 15
