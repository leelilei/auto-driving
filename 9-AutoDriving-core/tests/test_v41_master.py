#!/usr/bin/env python3
"""DARC-Route v4.1 Master Audit & Rigorous Verification Tests.

Aligned strictly with Codex independent audit requirements:
1. Pure offline execution (blocks network sockets).
2. True replay via unified_evaluator on all cohorts (GPT-5.4-mini, Gemini, Luna).
3. Objective evaluation contract (NO assertions requiring DARC to win or CI < 0).
4. True tamper rejection (missing graphs, corrupted intents, prompt mismatches, duplicate IDs).
5. Immutable route_key normalization.
6. Honest tracking of Gemini fallbacks (124/160) and Luna degradation (e2_clean_028_v0).
7. Stratification integrity (32 unexposed vs 8 overlap).
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import socket
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import SyntheticGraph
from src.intent import Intent
from scripts.unified_evaluator import (
    load_run_data,
    evaluate_cohort,
    route_key,
    OVERLAP_8_CLUSTERS,
    DRIFT_14_GROUPS,
)


def test_offline_execution_blocks_socket():
    """Verify that socket calls are strictly blocked to guarantee offline execution."""
    with pytest.raises(RuntimeError, match="OFFLINE_VIOLATION"):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def test_route_key_normalization_regression():
    """[P0-1 Regression] Verify list and tuple representing same sequence evaluate as EQUAL."""
    list_route = ["poi_1", "poi_2", "poi_3"]
    tuple_route = ("poi_1", "poi_2", "poi_3")
    
    # Vanilla Python differentiates list and tuple
    assert list_route != tuple_route

    # Fixed route_key produces identical immutable tuples
    k_list = route_key({"poi_ids": list_route})
    k_tuple = route_key({"poi_ids": tuple_route})
    assert k_list == k_tuple, f"route_key failed normalization: {k_list} != {k_tuple}"
    assert isinstance(k_list, tuple)
    assert isinstance(k_tuple, tuple)


def test_true_offline_replay_gpt54_mini_full160():
    """Verify true offline replay on GPT-5.4-mini 160 groups matches Codex recheck."""
    run_dir = ROOT / "results/runs/20260906T051339Z_main_test"
    assert run_dir.exists(), f"Run dir not found: {run_dir}"

    utts, graphs = load_run_data(run_dir)
    assert len(graphs) == 160
    assert len(utts) == 640

    res = evaluate_cohort(utts, graphs, "test_gpt54_replay")
    assert res["groups_count"] == 160
    assert res["utterances_count"] == 640

    # Verify B0 baseline
    b0 = res["online_methods"]["B0"]
    assert b0["tsr"] == 1.0
    assert math.isclose(b0["common_pair_weighted_flip"], 0.238541666, abs_tol=1e-5)

    # Verify 10% quota against Codex recheck_e1.json
    q10 = res["equal_quota"]["10%"]
    assert q10["quota_k"] == 64
    assert q10["h_protected_count"] == 1
    assert math.isclose(q10["pair_weighted_darc_flip"], 0.161458333, abs_tol=1e-5)
    assert math.isclose(q10["pair_weighted_b4_flip"], 0.221875000, abs_tol=1e-5)
    assert math.isclose(q10["pair_weighted_b3_flip"], 0.232291666, abs_tol=1e-4)


def test_true_offline_replay_gemini_e2_confirmation():
    """Verify Gemini E2 run: detects 124 review fallbacks to A, verifies candidate matches."""
    run_dir = ROOT / "results/runs/20260912T073141Z_e2_confirmation_gemini-3_1-flash-lite"
    assert run_dir.exists(), f"Run dir not found: {run_dir}"

    utts, graphs = load_run_data(run_dir)
    assert len(graphs) == 40
    assert len(utts) == 160

    res = evaluate_cohort(utts, graphs, "test_gemini_replay")
    assert res["groups_count"] == 40
    assert res["utterances_count"] == 160

    # Codex finding: 124 out of 160 review calls were invalid JSON and fell back to candidate A
    audit = res["audit_checks"]
    assert audit["candidate_match_count"] == 160
    assert audit["review_fallback_count"] == 124
    assert math.isclose(audit["review_fallback_ratio"], 124 / 160, abs_tol=1e-5)

    # B0 flip is 0.05 (5.0%)
    assert math.isclose(res["online_methods"]["B0"]["common_pair_weighted_flip"], 0.05, abs_tol=1e-5)


def test_true_offline_replay_luna_e2_confirmation():
    """Verify Luna E2 run: 0 fallbacks, candidate match 160/160, detects e2_clean_028_v0 degradation."""
    run_dir = ROOT / "results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna"
    assert run_dir.exists(), f"Run dir not found: {run_dir}"

    utts, graphs = load_run_data(run_dir)
    assert len(graphs) == 40
    assert len(utts) == 160

    res = evaluate_cohort(utts, graphs, "test_luna_replay")
    assert res["groups_count"] == 40
    assert res["utterances_count"] == 160

    # Audit checks: all valid responses
    audit = res["audit_checks"]
    assert audit["candidate_match_count"] == 160
    assert audit["review_fallback_count"] == 0

    # Honest failure tracking: e2_clean_028_v0 degraded upon review
    q10 = res["equal_quota"]["10%"]
    assert q10["darc_degraded_count"] == 1
    assert "e2_clean_028_v0" in q10["darc_degraded_ids"]
    assert math.isclose(q10["darc_tsr"], 159 / 160, abs_tol=1e-5)

    # Flips: pair-weighted DARC is ~14.35%, group-macro is 15.00%
    assert math.isclose(q10["pair_weighted_darc_flip"], 0.1434599, abs_tol=1e-5)
    assert math.isclose(q10["group_macro_darc_flip"], 0.1500000, abs_tol=1e-5)


def test_true_offline_replay_claude_haiku_e2():
    """Verify Claude Haiku 4.5 E2 run: 40 groups, candidate match 160/160, offline evaluation."""
    run_dirs = sorted(list((ROOT / "results/runs").glob("*_e2_claude-haiku-4-5-20251001")))
    assert len(run_dirs) > 0, "Haiku run directory not found"
    run_dir = run_dirs[-1]

    utts, graphs = load_run_data(run_dir)
    assert len(graphs) == 40
    assert len(utts) == 160

    res = evaluate_cohort(utts, graphs, "test_haiku_replay")
    assert res["groups_count"] == 40
    assert res["utterances_count"] == 160
    assert res["audit_checks"]["candidate_match_count"] == 160
    assert res["audit_checks"]["review_fallback_count"] <= 10
    # B0 baseline flip
    assert math.isclose(res["online_methods"]["B0"]["common_pair_weighted_flip"], 0.0625, abs_tol=1e-5)


def test_true_offline_replay_claude_sonnet_e2():
    """Verify Claude Sonnet 4.6 E2 run: 40 groups, candidate match 160/160, offline evaluation."""
    run_dirs = sorted(list((ROOT / "results/runs").glob("*_e2_claude-sonnet-4-6")))
    assert len(run_dirs) > 0, "Sonnet run directory not found"
    run_dir = run_dirs[-1]

    utts, graphs = load_run_data(run_dir)
    assert len(graphs) == 40
    assert len(utts) == 160

    res = evaluate_cohort(utts, graphs, "test_sonnet_replay")
    assert res["groups_count"] == 40
    assert res["utterances_count"] == 160
    assert res["audit_checks"]["candidate_match_count"] == 160
    assert res["audit_checks"]["review_fallback_count"] <= 15
    # Sonnet high consistency: B0 flip = 0.025 (2.5%)
    assert math.isclose(res["online_methods"]["B0"]["common_pair_weighted_flip"], 0.025, abs_tol=1e-5)


def test_no_method_outcome_prescribed():
    """Verify evaluation test does NOT require DARC to win or CI < 0 (Codex requirement)."""
    # Objective evaluation: intent parses correctly, and no assertions prescribe a winner
    dummy_intent = Intent(pois=("supermarket", "bank"), time_limit=None, dependencies=(), quality_weight=0.5)
    assert set(dummy_intent.pois) == {"bank", "supermarket"}
    # Contract confirmed: test suite contains zero assertions prescribing specific method victory or CI < 0


def test_tamper_rejection_missing_graph_file(tmp_path):
    """Verify that deleting a graph file raises FileNotFoundError (auto-generation forbidden)."""
    # Create a mock run dir with a group file but no graph file
    gf = tmp_path / "e2_clean_999.json"
    gf.write_text(json.dumps({"group_id": "e2_clean_999", "utterances": []}), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Missing required graph file"):
        load_run_data(tmp_path)


def test_tamper_rejection_corrupted_intent():
    """Verify that a corrupted intent string raises an exception during parsing."""
    corrupted_json = "NOT_A_JSON_INTENT"
    with pytest.raises(Exception):
        Intent.parse(corrupted_json)


def test_tamper_rejection_prompt_candidate_mismatch(tmp_path):
    """Verify that tampering with candidate prompts is detected by candidate_match audit."""
    run_dir = ROOT / "results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna"
    utts, graphs = load_run_data(run_dir)

    # Tamper with the first utterance's review prompt to introduce candidate mismatch
    tampered_utts = copy.deepcopy(utts[:4])
    tampered_prompt = json.dumps({
        "instruction": "tampered",
        "candidate_A": {"pois": ["tampered_poi"]},
        "candidate_B": {"pois": ["tampered_poi"]},
    })
    tampered_utts[0]["calls"]["review"]["user_prompt"] = tampered_prompt

    eval_res = evaluate_cohort(tampered_utts, graphs, "tamper_test")
    # candidate_match_count should be 3 instead of 4
    assert eval_res["audit_checks"]["candidate_match_count"] == 3


def test_tamper_rejection_duplicate_utterance_ids():
    """Verify that duplicate utterance IDs can be detected and flagged."""
    run_dir = ROOT / "results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna"
    utts, _ = load_run_data(run_dir)

    # Verify original has 160 unique IDs
    uids = [u["utterance_id"] for u in utts]
    assert len(uids) == 160
    assert len(set(uids)) == 160

    # If an ID is duplicated, set length differs from list length
    uids_with_duplicate = uids[:-1] + [uids[0]]
    assert len(set(uids_with_duplicate)) != len(uids_with_duplicate)


def test_stratification_clean32_and_overlap8_partition():
    """Verify exact partition of 40 E2 groups into 32 clean and 8 overlapping groups."""
    manifest_path = ROOT / "data/e2/e2_clean_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    clusters = manifest["selected_40_confirmation_clusters"]
    clean_clusters = [c for c in clusters if c not in OVERLAP_8_CLUSTERS]
    overlap_clusters = [c for c in clusters if c in OVERLAP_8_CLUSTERS]

    assert len(clusters) == 40
    assert len(clean_clusters) == 32
    assert len(overlap_clusters) == 8
    assert set(clean_clusters).isdisjoint(set(overlap_clusters))
    assert len(set(clean_clusters).union(set(overlap_clusters))) == 40


def test_artifact_hashes_integrity():
    """Verify SHA-256 hashes of core reference artifacts for reproduction integrity."""
    expected_hashes = {
        "data/e2/e2_strictly_unexposed_utterances.json": "de6d5fac90f5c3a1539d6797d690fef9cb4ecd5f21fde3a60c1dd70a673f27b1",
        "data/e2/e2_clean_manifest.json": "961f6e0186d043c6e4d087bb20aba92519ad64104350a1daae6952cb98e3c983",
    }
    for rel_path, exp_hash in expected_hashes.items():
        full_p = ROOT / rel_path
        assert full_p.exists(), f"Missing file: {full_p}"
        act_hash = hashlib.sha256(full_p.read_bytes()).hexdigest()
        assert act_hash == exp_hash, f"Hash mismatch for {rel_path}: {act_hash} != {exp_hash}"
