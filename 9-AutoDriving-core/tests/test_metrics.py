"""Unit tests for evaluation metrics, route flip, and bootstrap estimation."""

import pytest
from src.metrics import (
    compute_tsr,
    compute_gtsr,
    compute_variant_tsr,
    compute_route_flip,
    compute_intent_f1,
    compute_calibrated_utility_loss,
    compute_gating_diagnostics,
    compute_paired_bootstrap,
)


def test_tsr_and_gtsr():
    # 2 groups x 4 variants = 8 records
    # Group 1: all 4 succeed -> GTSR=1, TSR=1.0
    # Group 2: 3 succeed, 1 fails -> GTSR=0, TSR=0.75
    recs = [
        {"group_id": "g1", "variant_type": "V0", "task_success": True},
        {"group_id": "g1", "variant_type": "V1", "task_success": True},
        {"group_id": "g1", "variant_type": "V2", "task_success": True},
        {"group_id": "g1", "variant_type": "V3", "task_success": True},
        {"group_id": "g2", "variant_type": "V0", "task_success": True},
        {"group_id": "g2", "variant_type": "V1", "task_success": True},
        {"group_id": "g2", "variant_type": "V2", "task_success": True},
        {"group_id": "g2", "variant_type": "V3", "task_success": False},
    ]

    assert compute_tsr(recs) == 7.0 / 8.0
    assert compute_gtsr(recs) == 0.5

    var_tsr = compute_variant_tsr(recs)
    assert var_tsr["V0"] == 1.0
    assert var_tsr["V3"] == 0.5


def test_route_flip_calculation():
    # Group 1: V0 and V1 have different valid POI sequence
    recs = [
        {"group_id": "g1", "variant_type": "V0", "route": {"is_valid": True, "poi_ids": ["p1", "p2"]}},
        {"group_id": "g1", "variant_type": "V1", "route": {"is_valid": True, "poi_ids": ["p2", "p1"]}},
        {"group_id": "g1", "variant_type": "V2", "route": {"is_valid": True, "poi_ids": ["p1", "p2"]}},
        {"group_id": "g1", "variant_type": "V3", "route": {"is_valid": False, "poi_ids": []}},
    ]

    flip_res = compute_route_flip(recs)
    assert flip_res["valid_groups_count"] == 1
    # Pairs among V0, V1, V2: (V0,V1: flip), (V0,V2: same), (V1,V2: flip) => 2/3 flip
    assert flip_res["valid_pairs_count"] == 3
    assert flip_res["invalid_pairs_ratio"] == 0.5
    assert abs(flip_res["mean_route_flip"] - (2.0 / 3.0)) < 1e-3


def test_intent_f1_exact():
    recs = [{
        "predicted_intent": {
            "pois": ["bank", "library"],
            "time_limit": 1000,
            "dependencies": [["bank", "library"]],
        },
        "gold_intent": {
            "pois": ["bank", "library"],
            "time_limit": 1000,
            "dependencies": [["bank", "library"]],
        },
    }]
    f1 = compute_intent_f1(recs)
    assert f1["poi_f1"] == 1.0
    assert f1["dependency_f1"] == 1.0
    assert f1["time_exact_match"] == 1.0


def test_paired_bootstrap():
    diffs = [0.05, 0.05, 0.05, 0.05, 0.05]
    mean_val, lower, upper = compute_paired_bootstrap(diffs, num_samples=100)
    assert abs(mean_val - 0.05) < 1e-4
    assert abs(lower - 0.05) < 1e-4
    assert abs(upper - 0.05) < 1e-4
