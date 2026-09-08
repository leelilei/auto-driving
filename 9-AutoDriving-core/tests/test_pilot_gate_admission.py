"""Unit and regression tests for Pilot Gate Admission programmatic logic.

Covers:
1. Leakage check returns 0 overlap between Dev and Test.
2. Pilot error diagnostics identifies Call A transport RuntimeError and rejects temporal window claims.
3. Compute transitions accurately calculates W2R, R2W, and net error correction.
4. Programmatic condition evaluation blocks admission when human review is pending or net gain is not met.
"""

import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.run_pilot_gate_admission import (
    audit_splits_leakage,
    diagnose_pilot_errors,
    compute_transitions,
    evaluate_gate_admission_conditions,
    evaluate_run_metric_v2,
)


def test_audit_splits_leakage():
    """Verify Dev and Test splits have strictly zero overlap."""
    res = audit_splits_leakage()
    assert res["leakage_clean"] is True
    assert res["cluster_overlap_count"] == 0
    assert res["index_overlap_count"] == 0
    assert res["test_exposed_leakage_count"] == 0


def test_diagnose_pilot_errors():
    """Verify pilot error cases are diagnosed as transport errors, not time windows."""
    pilot_run = ROOT / "results/runs/20260905T182600Z_pilot_e1"
    if not pilot_run.exists():
        pytest.skip("Pilot run not found")

    eval_res = evaluate_run_metric_v2(
        pilot_run, methods=["B0", "Ours", "B6"], tau=0.02, tau_sem=0.10, p_review=0.48
    )
    diagnostics = diagnose_pilot_errors(eval_res)

    assert len(diagnostics) == 2
    uids = {d["utterance_id"] for d in diagnostics}
    assert uids == {"pilot_03_v2", "pilot_06_v0"}

    for d in diagnostics:
        assert d["call_a_schema_valid"] is False
        assert d["call_a_transport_error"] == "RuntimeError"
        assert d["oracle_task_success"] is True
        assert d["is_temporal_window_conflict"] is False


def test_compute_transitions():
    """Verify error transition counting logic."""
    mock_preds = [
        {"utterance_id": "u1", "methods": {"B0": {"task_success": True}, "Ours": {"task_success": True}}},
        {"utterance_id": "u2", "methods": {"B0": {"task_success": False}, "Ours": {"task_success": True}}}, # W2R
        {"utterance_id": "u3", "methods": {"B0": {"task_success": True}, "Ours": {"task_success": False}}}, # R2W
        {"utterance_id": "u4", "methods": {"B0": {"task_success": False}, "Ours": {"task_success": False}}}, # SW
    ]
    trans = compute_transitions(mock_preds, "B0", "Ours")
    assert trans["wrong_to_right_count"] == 1
    assert trans["wrong_to_right_ids"] == ["u2"]
    assert trans["right_to_wrong_count"] == 1
    assert trans["right_to_wrong_ids"] == ["u3"]
    assert trans["net_correction"] == 0


def test_programmatic_admission_blocked():
    """Verify that overall admission is BLOCKED when human review is pending and net gain is 0."""
    pilot_run = ROOT / "results/runs/20260905T182600Z_pilot_e1"
    calib_run = ROOT / "results/runs/20260906T035711Z_calibration"
    if not pilot_run.exists() or not calib_run.exists():
        pytest.skip("Pilot or calibration run not found")

    p_eval = evaluate_run_metric_v2(pilot_run, methods=["B0", "B2", "B5", "B6", "Ours"], tau=0.02, tau_sem=0.10, p_review=0.48)
    c_eval = evaluate_run_metric_v2(calib_run, methods=["B0", "B2", "B3", "B4", "B5", "B6", "Ours"], tau=0.02, tau_sem=0.10, p_review=0.48)

    errors = diagnose_pilot_errors(p_eval)
    trans = compute_transitions(p_eval["predictions"], "B0", "Ours")
    leakage = audit_splits_leakage()

    admission = evaluate_gate_admission_conditions(p_eval, c_eval, errors, trans, leakage)

    assert admission["gate_a"]["verdict"] == "NOT_MET_TSR_NET_GAIN"
    assert admission["gate_b"]["verdict"] == "PASS_FLIP_REDUCTION"
    assert admission["data_leakage"]["verdict"] == "PASS"
    assert admission["overall_decision"] == "BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION"
    assert len(admission["blocking_reasons"]) > 0
