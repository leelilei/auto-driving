"""Targeted unit tests for R1 remediation addressing Codex audit findings.

Covers:
1. Direction weights strictly alter route evaluation order (w=0.25 vs w=0.75).
2. Identical physical routes evaluated under the same gold weight produce identical utility (regret == 0.0).
3. Contrast pairs where both sides fail do NOT count as valid appropriate responses.
4. Protection trigger h=1 budget consumption and fallback consistency.
5. 429 rate limit retry preserves attempts count (attempts == 2).
6. cmd_replay raises error / exits non-zero on missing group or graph files.
7. cmd_replay detects tampered inputs and exits non-zero.
8. Property C01 holds: B0 and B2 produce identical node sequences and task success.
9. Missing preference_direction in ablation lookup strictly raises KeyError.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph import SyntheticGraph, generate_synthetic_graph
from src.solver import ExactRouteSolver, RouteResult
from src.intent import Intent
from src.gating import (
    calculate_route_utility,
    calculate_route_regret,
    compute_exact_route_distance,
    compute_protection_trigger,
    execute_method_decision,
)
from src.llm_client import LLM, LLMConfig
from scripts.experiment import cmd_replay


# ----------------------------------------------------------------------
# 1. Direction weights strictly alter route evaluation order
# ----------------------------------------------------------------------
def test_direction_weights_change_evaluation():
    """Non-zero direction weights strictly alter route evaluation order."""
    # Controlled 10-POI synthetic graph
    graph = generate_synthetic_graph(seed=42)
    solver = ExactRouteSolver(graph)

    # Category 'shopping_mall' has two candidates in graph:
    # shopping_mall_1 (closer, lower quality) and shopping_mall_2 (farther, higher quality)
    route_dist = solver.solve(requested_pois=["shopping_mall"], quality_weight=0.1)
    route_qual = solver.solve(requested_pois=["shopping_mall"], quality_weight=0.9)

    assert route_dist.is_valid and route_qual.is_valid
    # The solver must choose different candidates under different preference weights
    assert route_dist.poi_ids != route_qual.poi_ids
    assert route_dist.poi_ids == ("shopping_mall_1",)
    assert route_qual.poi_ids == ("shopping_mall_2",)

    # Utilities must differ across weights
    u_dist_eval = calculate_route_utility(graph, route_dist, quality_weight=0.1)
    u_qual_eval = calculate_route_utility(graph, route_qual, quality_weight=0.9)
    assert u_dist_eval != u_qual_eval


# ----------------------------------------------------------------------
# 2. Identical physical routes under same weight get identically 0.0 regret
# ----------------------------------------------------------------------
def test_identical_physical_routes_same_weight_zero_regret():
    """Identical physical routes under same weight yield 0.0 regret without rounding drift."""
    graph = generate_synthetic_graph(seed=123)
    solver = ExactRouteSolver(graph)

    route = solver.solve(requested_pois=["shopping_mall", "supermarket"], quality_weight=0.5)
    assert route.is_valid

    for w in [0.0, 0.25, 0.5, 0.75, 1.0]:
        regret = calculate_route_regret(graph, route, route, gold_quality_weight=w)
        assert regret == 0.0, f"Expected 0.0 regret for identical route under weight {w}, got {regret}"

        # Dict representation should also work identically
        route_dict = {
            "poi_ids": route.poi_ids,
            "is_valid": route.is_valid,
            "utility": route.utility,
            "total_distance": route.total_distance,
        }
        regret_dict = calculate_route_regret(graph, route_dict, route_dict, gold_quality_weight=w)
        assert regret_dict == 0.0


# ----------------------------------------------------------------------
# 3. Contrast pairs where both sides fail do NOT count as appropriate
# ----------------------------------------------------------------------
def test_contrast_both_fail_not_appropriate():
    """Production evaluate_contrast_pair_validity strictly requires both sides to succeed."""
    from scripts.run_contrast_experiment import evaluate_contrast_pair_validity

    # Case 1: Both fail -> valid_appropriate MUST be False, even if change patterns match
    res_both_fail = evaluate_contrast_pair_validity(
        succ_c0=False, succ_c1=False, route_changed=False, oracle_changed=False
    )
    assert res_both_fail["both_valid"] is False
    assert res_both_fail["change_pattern_agreement"] is True
    assert res_both_fail["valid_appropriate"] is False

    # Case 2: One fails -> valid_appropriate MUST be False
    res_one_fail = evaluate_contrast_pair_validity(
        succ_c0=True, succ_c1=False, route_changed=True, oracle_changed=True
    )
    assert res_one_fail["both_valid"] is False
    assert res_one_fail["valid_appropriate"] is False

    # Case 3: Both succeed and route change matches oracle change -> valid_appropriate is True
    res_success = evaluate_contrast_pair_validity(
        succ_c0=True, succ_c1=True, route_changed=True, oracle_changed=True
    )
    assert res_success["both_valid"] is True
    assert res_success["change_pattern_agreement"] is True
    assert res_success["valid_appropriate"] is True


# ----------------------------------------------------------------------
# 4. Protection trigger h=1 budget consumption and fallback consistency
# ----------------------------------------------------------------------
def test_protection_h_budget_and_fallback_consistency():
    """When h=1, calls_used and chosen fallback route are consistent."""
    graph = generate_synthetic_graph(seed=42)
    solver = ExactRouteSolver(graph)

    # Use actual valid categories
    p0 = graph.pois[0].category
    p1 = graph.pois[1].category
    p2 = graph.pois[2].category
    cand_a = Intent(pois=(p0, p1), time_limit=None, dependencies=(), quality_weight=0.5)
    cand_b = Intent(pois=(p0, p2), time_limit=None, dependencies=(), quality_weight=0.5)

    route_a = solver.solve(**cand_a.solver_args())
    route_b = solver.solve(**cand_b.solver_args())

    # Review intent resolves the conflict
    cand_rev = Intent(pois=(p0, p1, p2), time_limit=None, dependencies=(), quality_weight=0.5)

    candidates = {"A": cand_a, "B": cand_b, "review": cand_rev, "A2": None, "A3": None}
    routes = {"A": route_a, "B": route_b, "A2": None, "A3": None}

    # Protection trigger should be 1 due to POI mismatch
    h = compute_protection_trigger(cand_a, cand_b, route_a, route_b)
    assert h == 1

    chosen_intent, chosen_route, meta = execute_method_decision(
        method="Ours",
        candidates=candidates,
        routes=routes,
        graph=graph,
        solver=solver,
        tau=0.02,
        group_id="test_001",
        utterance_id="u_001",
    )

    assert meta["h"] == 1
    assert meta["review_triggered"] is True
    assert meta["calls_used"] == 3
    assert chosen_intent == cand_rev


# ----------------------------------------------------------------------
# 5. 429 rate limit retry preserves attempts count (attempts == 2)
# ----------------------------------------------------------------------
def test_rate_limit_429_retry_records_two_attempts():
    """429 retry preserves attempt count in telemetry."""
    call_count = 0

    class Mock429Client:
        last_usage = {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150}

        def complete(self, prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("429 Too Many Requests: Rate limit exceeded")
            return '{"pois": ["shopping_mall"], "time_limit": null, "dependencies": [], "quality_weight": 0.5}'

    config = LLMConfig(
        provider="mock",
        model="mock-429",
        retries=2,
        retry_sleep=0.001,
    )
    client = LLM(config)
    client.client = Mock429Client()

    resp = client.complete(system="test_sys", user="test_user")
    assert "shopping_mall" in resp
    assert len(client.telemetry) == 1
    telemetry = client.telemetry[0]
    assert telemetry["attempts"] == 2
    assert telemetry["success"] is True


# ----------------------------------------------------------------------
# 6. cmd_replay raises error / exits non-zero on missing group or graph files
# ----------------------------------------------------------------------
def test_replay_missing_file_raises_error():
    """cmd_replay exits non-zero if graph file is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a group json without corresponding graph json
        group_file = tmp_path / "test_001.json"
        group_file.write_text(json.dumps({
            "group_id": "test_001",
            "utterances": []
        }))

        args = Namespace(
            run_dir=str(tmp_path),
            tau=0.02,
            tau_sem=0.10,
            p_review=0.48,
            limit=None,
            output_dir=str(tmp_path / "out"),
            no_verify_summary=True,
            allow_partial=True,
            allow_missing_summary=True,
            no_dataset_check=True,
        )

        with pytest.raises(SystemExit) as exc_info:
            cmd_replay(args)
        assert exc_info.value.code != 0


# ----------------------------------------------------------------------
# 7. cmd_replay detects tampered inputs and exits non-zero
# ----------------------------------------------------------------------
def test_replay_tampered_input_detected():
    """cmd_replay detects tampered candidate and exits non-zero."""
    real_run = ROOT / "results/runs/20260906T051339Z_main_test"
    if not (real_run / "test_001.json").exists():
        pytest.skip("Main test run directory not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        shutil.copy(real_run / "test_001.json", tmp_path / "test_001.json")
        shutil.copy(real_run / "test_001_graph.json", tmp_path / "test_001_graph.json")

        # Tamper with the raw response of call A in the first utterance
        data = json.loads((tmp_path / "test_001.json").read_text(encoding="utf-8"))
        first_call = data["utterances"][0]["calls"]["A"]
        first_call["raw_response"] = '{"pois": ["tampered_poi_999"], "time_limit": null, "dependencies": [], "quality_weight": 0.5}'
        (tmp_path / "test_001.json").write_text(json.dumps(data), encoding="utf-8")

        args = Namespace(
            run_dir=str(tmp_path),
            tau=0.02,
            tau_sem=0.10,
            p_review=0.48,
            limit=1,
            output_dir=str(tmp_path / "out"),
            no_verify_summary=True,
            allow_partial=True,
            allow_missing_summary=True,
            no_dataset_check=True,
        )

        with pytest.raises(SystemExit) as exc_info:
            cmd_replay(args)
        assert exc_info.value.code != 0


# ----------------------------------------------------------------------
# 8. Property C01: B0 and B2 produce identical node sequences and task success
# ----------------------------------------------------------------------
def test_b0_b2_identity_property_c01():
    """Property C01: B0 and B2 return identical node sequences and validity on non-empty valid routes."""
    graph = generate_synthetic_graph(seed=99)
    solver = ExactRouteSolver(graph)

    # Use real categories from the graph so solver solves valid feasible routes
    all_categories = list(dict.fromkeys(p.category for p in graph.pois))
    for i in range(1, min(4, len(all_categories) + 1)):
        cats = all_categories[:i]
        cand_a = Intent(pois=tuple(cats), time_limit=None, dependencies=(), quality_weight=0.5)
        cand_b = Intent(pois=tuple(reversed(cats)), time_limit=None, dependencies=(), quality_weight=0.5)
        route_a = solver.solve(**cand_a.solver_args())
        route_b = solver.solve(**cand_b.solver_args())

        candidates = {"A": cand_a, "B": cand_b, "review": None, "A2": None, "A3": None}
        routes = {"A": route_a, "B": route_b, "A2": None, "A3": None}

        _, route_b0, _ = execute_method_decision("B0", candidates, routes, graph, solver)
        _, route_b2, _ = execute_method_decision("B2", candidates, routes, graph, solver)

        assert route_b0.is_valid is True
        assert route_b2.is_valid is True
        assert len(route_b0.poi_ids) == len(cats)
        assert route_b0.poi_ids == route_b2.poi_ids
        assert route_b0.total_distance == route_b2.total_distance


# ----------------------------------------------------------------------
# 9. Missing preference_direction strictly raises KeyError via production lookup
# ----------------------------------------------------------------------
def test_missing_preference_direction_raises_keyerror():
    """Production lookup_preference_direction raises KeyError when utterance_id is missing."""
    from scripts.run_ablation_experiment import lookup_preference_direction

    lookup_table = {"test_001_v0": "distance_first"}
    assert lookup_preference_direction(lookup_table, "test_001_v0") == "distance_first"

    with pytest.raises(KeyError) as exc_info:
        lookup_preference_direction(lookup_table, "missing_utterance_v0")
    assert "missing_utterance_v0" in str(exc_info.value)


# ----------------------------------------------------------------------
# 10. Replay fails if incomplete group files without explicit partial flag
# ----------------------------------------------------------------------
def test_replay_incomplete_groups_fails():
    """cmd_replay fails if fewer than expected groups exist."""
    real_run = ROOT / "results/runs/20260906T051339Z_main_test"
    if not (real_run / "test_001.json").exists():
        pytest.skip("Main test run directory not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Copy only 1 group out of 160
        shutil.copy(real_run / "test_001.json", tmp_path / "test_001.json")
        shutil.copy(real_run / "test_001_graph.json", tmp_path / "test_001_graph.json")
        shutil.copy(real_run / "summary.json", tmp_path / "summary.json")

        args = Namespace(
            run_dir=str(tmp_path),
            tau=0.02,
            tau_sem=0.10,
            p_review=0.48,
            limit=None,
            output_dir=str(tmp_path / "out"),
            no_verify_summary=True,
            allow_partial=False,  # default strict
            allow_missing_summary=False,
            no_dataset_check=True,
        )

        with pytest.raises(SystemExit) as exc_info:
            cmd_replay(args)
        assert exc_info.value.code != 0


# ----------------------------------------------------------------------
# 11. Replay fails if mandatory summary.json is missing
# ----------------------------------------------------------------------
def test_replay_missing_summary_fails():
    """cmd_replay fails if summary.json is missing and not explicitly waived."""
    real_run = ROOT / "results/runs/20260906T051339Z_main_test"
    if not (real_run / "test_001.json").exists():
        pytest.skip("Main test run directory not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        shutil.copy(real_run / "test_001.json", tmp_path / "test_001.json")
        shutil.copy(real_run / "test_001_graph.json", tmp_path / "test_001_graph.json")

        args = Namespace(
            run_dir=str(tmp_path),
            tau=0.02,
            tau_sem=0.10,
            p_review=0.48,
            limit=1,
            output_dir=str(tmp_path / "out"),
            no_verify_summary=False,
            allow_partial=True,
            allow_missing_summary=False,  # default strict
            no_dataset_check=True,
        )

        with pytest.raises(SystemExit) as exc_info:
            cmd_replay(args)
        assert exc_info.value.code != 0


# ----------------------------------------------------------------------
# 12. Replay fails if cached candidates or routes are stripped
# ----------------------------------------------------------------------
def test_replay_missing_cached_candidates_routes_fails():
    """cmd_replay fails if cached candidates or routes are empty/missing."""
    real_run = ROOT / "results/runs/20260906T051339Z_main_test"
    if not (real_run / "test_001.json").exists():
        pytest.skip("Main test run directory not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        shutil.copy(real_run / "test_001.json", tmp_path / "test_001.json")
        shutil.copy(real_run / "test_001_graph.json", tmp_path / "test_001_graph.json")
        shutil.copy(real_run / "summary.json", tmp_path / "summary.json")

        # Strip candidates and routes
        d = json.loads((tmp_path / "test_001.json").read_text(encoding="utf-8"))
        for u in d["utterances"]:
            u["candidates"] = {}
            u["routes"] = {}
        (tmp_path / "test_001.json").write_text(json.dumps(d), encoding="utf-8")

        args = Namespace(
            run_dir=str(tmp_path),
            tau=0.02,
            tau_sem=0.10,
            p_review=0.48,
            limit=1,
            output_dir=str(tmp_path / "out"),
            no_verify_summary=True,
            allow_partial=True,
            allow_missing_summary=True,
            no_dataset_check=True,
        )

        with pytest.raises(SystemExit) as exc_info:
            cmd_replay(args)
        assert exc_info.value.code != 0


# ----------------------------------------------------------------------
# 13. NetworkBlocker blocks socket and restores cleanly
# ----------------------------------------------------------------------
def test_network_blocker_blocks_and_restores():
    """NetworkBlocker prevents connections and restores original socket."""
    import socket
    from scripts.experiment import NetworkBlocker

    orig_connect = socket.socket.connect
    with NetworkBlocker():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with pytest.raises(RuntimeError) as exc_info:
            s.connect(("127.0.0.1", 80))
        assert "NETWORK ATTEMPT DETECTED" in str(exc_info.value)
        s.close()

    # Verify socket.connect is cleanly restored
    assert socket.socket.connect == orig_connect
