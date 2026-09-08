"""Unit tests for decision-aware gating, baselines (B0 to B6 + Ours), and review fallback."""

import pytest
from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver, RouteResult
from src.intent import Intent
from src.gating import (
    extract_structure,
    compute_protection_trigger,
    calculate_route_utility,
    compute_cross_utility_delta,
    evaluate_darc_gate,
    resolve_review_fallback,
    intent_distance,
    select_medoid,
    execute_method_decision,
)


def test_structure_extraction():
    intent = Intent.parse({
        "pois": ["shopping_mall", "supermarket"],
        "time_limit": 1200,
        "dependencies": [["shopping mall", "supermarket"]],
        "quality_weight": 0.5,
    })
    h = extract_structure(intent)
    assert h == (("shopping_mall", "supermarket"), 1200, (("shopping_mall", "supermarket"),))
    assert extract_structure(None) is None


def test_protection_trigger_cases():
    graph = generate_synthetic_graph()
    solver = ExactRouteSolver(graph)

    intent_a = Intent.parse({"pois": ["bank"], "time_limit": 1000, "dependencies": [], "quality_weight": 0.5})
    intent_b = Intent.parse({"pois": ["bank"], "time_limit": 1000, "dependencies": [], "quality_weight": 0.8})
    intent_mismatch = Intent.parse({"pois": ["library"], "time_limit": 1000, "dependencies": [], "quality_weight": 0.5})

    route_a = solver.solve(**intent_a.solver_args())
    route_b = solver.solve(**intent_b.solver_args())

    # Case 1: Matching structures, valid routes -> h = 0
    assert compute_protection_trigger(intent_a, intent_b, route_a, route_b) == 0

    # Case 2: Structural mismatch -> h = 1
    assert compute_protection_trigger(intent_a, intent_mismatch, route_a, route_b) == 1

    # Case 3: None intent or route -> h = 1
    assert compute_protection_trigger(None, intent_b, route_a, route_b) == 1
    assert compute_protection_trigger(intent_a, intent_b, None, route_b) == 1

    # Case 4: Infeasible route -> h = 1
    infeasible_route = RouteResult((), (), 0, False, False, -1.0, 0.0, 0.0, 540, "NO_FEASIBLE_ROUTE")
    assert compute_protection_trigger(intent_a, intent_b, infeasible_route, route_b) == 1


def test_cross_utility_delta():
    graph = generate_synthetic_graph()
    solver = ExactRouteSolver(graph)

    # High quality vs high distance weight
    intent_a = Intent.parse({"pois": ["shopping_mall"], "time_limit": None, "dependencies": [], "quality_weight": 0.95})
    intent_b = Intent.parse({"pois": ["shopping_mall"], "time_limit": None, "dependencies": [], "quality_weight": 0.05})

    route_a = solver.solve(**intent_a.solver_args())
    route_b = solver.solve(**intent_b.solver_args())

    delta_u = compute_cross_utility_delta(graph, intent_a, intent_b, route_a, route_b)
    assert delta_u is not None
    # Because candidate 2 is chosen by route_a and candidate 1 by route_b, delta_u > 0
    if route_a.poi_ids != route_b.poi_ids:
        assert delta_u > 0.0
    else:
        assert delta_u == 0.0


def test_review_fallback_resolution():
    intent_a = Intent.parse({"pois": ["bank"], "time_limit": None, "dependencies": [], "quality_weight": 0.5})
    intent_b = Intent.parse({"pois": ["library"], "time_limit": None, "dependencies": [], "quality_weight": 0.5})
    intent_rev = Intent.parse({"pois": ["pharmacy"], "time_limit": None, "dependencies": [], "quality_weight": 0.5})

    # Review valid -> adopts review
    chosen, reason = resolve_review_fallback(intent_rev, intent_a, intent_b)
    assert chosen == intent_rev and reason == "adopted_review"

    # Review None -> fallback to A
    chosen, reason = resolve_review_fallback(None, intent_a, intent_b)
    assert chosen == intent_a and reason == "fallback_to_A"

    # Review None and A None -> fallback to B
    chosen, reason = resolve_review_fallback(None, None, intent_b)
    assert chosen == intent_b and reason == "fallback_to_B"

    # All None -> failure
    chosen, reason = resolve_review_fallback(None, None, None)
    assert chosen is None and reason == "all_candidates_invalid"


def test_medoid_selection_b1():
    i_a = Intent.parse({"pois": ["bank"], "time_limit": None, "dependencies": [], "quality_weight": 0.5})
    i_a2 = Intent.parse({"pois": ["bank"], "time_limit": None, "dependencies": [], "quality_weight": 0.52})
    i_a3 = Intent.parse({"pois": ["library"], "time_limit": None, "dependencies": [], "quality_weight": 0.9})

    candidates = [("A", i_a), ("A2", i_a2), ("A3", i_a3)]
    chosen, label = select_medoid(candidates)
    # i_a and i_a2 are close to each other; i_a3 is distant from both
    assert label in {"A", "A2"}


def test_b2_equals_b0_strictly():
    graph = generate_synthetic_graph()
    solver = ExactRouteSolver(graph)

    intent_a = Intent.parse({"pois": ["bank", "supermarket"], "time_limit": 1000, "dependencies": [], "quality_weight": 0.5})
    intent_b = Intent.parse({"pois": ["bank", "supermarket"], "time_limit": 1000, "dependencies": [], "quality_weight": 0.8})

    route_a = solver.solve(**intent_a.solver_args())
    route_b = solver.solve(**intent_b.solver_args())

    candidates = {"A": intent_a, "B": intent_b}
    routes = {"A": route_a, "B": route_b}

    chosen_b0, route_b0, meta_b0 = execute_method_decision("B0", candidates, routes, graph, solver)
    chosen_b2, route_b2, meta_b2 = execute_method_decision("B2", candidates, routes, graph, solver)

    assert chosen_b0 == chosen_b2
    assert route_b0 == route_b2
    assert meta_b0["calls_used"] == 1
    assert meta_b2["calls_used"] == 2
