"""Unit and integration tests for recomputed transfer metrics and replay integrity."""

from pathlib import Path
import json
import sys
import pytest

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "9-AutoDriving-core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from scripts.recompute_transfer_metrics import (
    DEFAULT_CLUSTERS_FILE,
    DEFAULT_DATA_DIR,
    DEFAULT_OUT_DIR,
    DEFAULT_RAW_DIR,
    compute_invariant_utility,
    compute_proposal_delta_u,
    evaluate_route_against_gold,
    get_canonical_route,
    load_json,
    parse_intent_audited,
    run_tamper_rejection_tests,
    verify_replay,
)


def test_canonical_route_mapping():
    """Verify that node indices accurately map to Place IDs in canonical route."""
    filtered_pois = [
        {"Place ID": "poi_A", "Type": "bank"},
        {"Place ID": "poi_B", "Type": "supermarket"},
        {"Place ID": "poi_C", "Type": "pharmacy"},
    ]
    # Path [0, 2, 3, 4] -> intermediate nodes 2 and 3 -> poi_B, poi_C
    path = [0, 2, 3, 4]
    route = get_canonical_route(path, filtered_pois, goal_node=4)
    assert route == ("poi_B", "poi_C")

    # Empty intermediate path
    empty_route = get_canonical_route([0, 4], filtered_pois, goal_node=4)
    assert empty_route == ()

    # None path
    assert get_canonical_route(None, filtered_pois) is None


def test_proposal_delta_u_zero_when_identical_routes():
    """Verify Proposal contract: Delta U == 0.0 when routes are identical, even if weights differ."""
    eval_a = {"is_valid": True, "avg_rating": 4.5, "total_dist_km": 20.0}
    eval_b = {"is_valid": True, "avg_rating": 4.5, "total_dist_km": 20.0}

    # Weight A = 0.9, Weight B = 0.1
    du = compute_proposal_delta_u(eval_a, eval_b, w_a=0.9, w_b=0.1)
    assert du == 0.0

    # Weight A = 1.0, Weight B = 0.0
    du2 = compute_proposal_delta_u(eval_a, eval_b, w_a=1.0, w_b=0.0)
    assert du2 == 0.0


def test_proposal_delta_u_positive_when_different_routes():
    """Verify Delta U > 0 when routes have different ratings or distances."""
    eval_a = {"is_valid": True, "avg_rating": 5.0, "total_dist_km": 10.0}
    eval_b = {"is_valid": True, "avg_rating": 3.0, "total_dist_km": 50.0}

    du = compute_proposal_delta_u(eval_a, eval_b, w_a=0.5, w_b=0.5)
    assert du > 0.0

    # Invalid route yields Delta U = 1.0
    eval_invalid = {"is_valid": False, "avg_rating": 1.0, "total_dist_km": 0.0}
    du_inv = compute_proposal_delta_u(eval_a, eval_invalid, w_a=0.5, w_b=0.5)
    assert du_inv == 1.0


def test_invariant_utility_scale():
    """Verify utility uses invariant w_gold and penalizes invalid routes."""
    eval_valid = {"is_valid": True, "avg_rating": 5.0, "total_dist_km": 0.0}
    # Rating 5.0 normalized = 1.0, Distance 0 normalized = 0.0 -> w_gold * 1.0 = 0.7
    u = compute_invariant_utility(eval_valid, w_gold=0.7)
    assert abs(u - 0.7) < 1e-4

    # Invalid route gives -1.0
    eval_invalid = {"is_valid": False, "avg_rating": 5.0, "total_dist_km": 0.0}
    assert compute_invariant_utility(eval_invalid, w_gold=0.7) == -1.0


def test_gold_hard_constraint_enforcement():
    """Verify evaluate_route_against_gold rejects missing categories and opening hour violations."""
    scenario = {
        "start_location": {"latitude": 39.90, "longitude": 116.40},
        "end_location": {"latitude": 39.91, "longitude": 116.41},
        "pois": [
            {
                "Place ID": "poi_1",
                "Type": "bank",
                "Rating": 4.5,
                "Number Ratings": 50,
                "Latitude": 39.905,
                "Longitude": 116.405,
                "Opening": ["Monday: 9:00 AM – 5:00 PM"],
            },
            {
                "Place ID": "poi_2",
                "Type": "supermarket",
                "Rating": 4.0,
                "Number Ratings": 120,
                "Latitude": 39.908,
                "Longitude": 116.408,
                "Opening": ["Monday: 9:00 AM – 5:00 PM"],
            },
        ],
    }

    # Gold expects bank AND supermarket
    gold = {
        "pois": ["bank", "supermarket"],
        "time_limit": "23:00",
        "dependencies": [],
    }

    # Route visits only bank -> missing supermarket -> is_valid False
    res_partial = evaluate_route_against_gold(("poi_1",), gold, scenario)
    assert not res_partial["is_valid"]
    assert "missing_categories" in (res_partial["failure_reason"] or "")

    # Route visits both -> valid
    res_full = evaluate_route_against_gold(("poi_1", "poi_2"), gold, scenario)
    assert res_full["is_valid"]


def test_review_parse_error_auditing():
    """Verify that 'today' deadline in review response is captured as schema failure."""
    raw = '{"intent": {"pois": ["library", "bank"], "time_limit": "today", "dependencies": [], "quality_weight": 0.9}}'
    intent, raw_dict, err = parse_intent_audited(raw)
    assert intent is None
    assert raw_dict is not None
    assert err is not None
    assert "Deadline must be HH:MM or minutes" in err


def test_recomputed_metrics_exist_and_sane():
    """Verify the recomputed metrics JSON exists and has verified structure."""
    metrics_file = DEFAULT_OUT_DIR / "joint_metrics.json"
    assert metrics_file.exists(), f"Missing {metrics_file}"
    m = load_json(metrics_file)

    assert m["metadata"]["utterances_count"] == 160
    assert m["metadata"]["groups_count"] == 40
    assert m["audit_summary"]["review_fail"] == 32
    assert m["audit_summary"]["parse_a_fail"] == 0
    assert m["audit_summary"]["parse_b_fail"] == 0

    # Check 10% budget metrics
    b10 = m["budgets"]["budget_10pct"]
    assert b10["budget_feasible"] is True
    assert b10["policies"]["B0_no_review"]["TSR_pct"] == 100.0
    assert b10["policies"]["B0_no_review"]["pairwise_route_diff_rate_pct"] == 11.25
    assert b10["policies"]["B0_no_review"]["diff_route_pairs"] == 27
    assert b10["policies"]["B0_no_review"]["mutually_valid_pairs"] == 240

    # Check B3 20 seeds
    assert b10["policies"]["B3_random_20seeds"]["seeds_evaluated"] == 20

    # Check Bootstrap CIs cross zero
    assert b10["cluster_bootstrap_35clusters"]["delta_darc_minus_b4_utility"]["crosses_zero"] is True
    assert b10["cluster_bootstrap_35clusters"]["delta_darc_minus_b0_utility"]["crosses_zero"] is True


def test_replay_verification():
    """Verify that replay verification succeeds with exit code 0."""
    code = verify_replay(DEFAULT_OUT_DIR, DEFAULT_DATA_DIR, DEFAULT_RAW_DIR, DEFAULT_CLUSTERS_FILE)
    assert code == 0


def test_tamper_rejection():
    """Verify that tamper rejection suite passes 4/4 tests."""
    code = run_tamper_rejection_tests(DEFAULT_OUT_DIR, DEFAULT_RAW_DIR, DEFAULT_DATA_DIR, DEFAULT_CLUSTERS_FILE)
    assert code == 0
