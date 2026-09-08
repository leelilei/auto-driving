"""Unit tests for controlled synthetic graph and exact solver."""

import time
from src.graph import generate_synthetic_graph
from src.solver import ExactRouteSolver


def test_graph_generation():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    assert len(graph.pois) == 10
    assert graph.max_edge_distance > 0.0
    cats = {p.category for p in graph.pois}
    assert len(cats) == 5


def test_solver_feasible_route():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Request 2 POIs with no tight deadline
    res = solver.solve(
        requested_pois=["supermarket", "pharmacy"],
        time_limit=1200,  # 20:00
        dependencies=[],
        quality_weight=0.5,
    )
    assert res.is_valid
    assert res.is_full_coverage
    assert res.coverage == 2
    assert len(res.poi_ids) == 2
    assert res.status == "SUCCESS"
    assert res.final_arrival_time <= 1200


def test_solver_dependency_order():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Enforce pharmacy before supermarket
    res = solver.solve(
        requested_pois=["supermarket", "pharmacy"],
        time_limit=1200,
        dependencies=[("pharmacy", "supermarket")],
        quality_weight=0.5,
    )
    assert res.is_valid
    assert res.is_full_coverage
    assert res.categories.index("pharmacy") < res.categories.index("supermarket")


def test_solver_circular_dependency():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Cycle between bank and library
    res = solver.solve(
        requested_pois=["bank", "library"],
        dependencies=[("bank", "library"), ("library", "bank")],
    )
    assert not res.is_valid
    assert res.status == "CYCLE_DEPENDENCY_ERROR"


def test_solver_impossible_deadline():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Deadline is 5 minutes after departure (departure is 540)
    res = solver.solve(
        requested_pois=["shopping_mall", "supermarket", "pharmacy"],
        time_limit=545,
    )
    # Impossible to visit all 3 in 5 minutes
    assert not res.is_full_coverage


def test_solver_preference_weight_sensitivity():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Solve with high quality weight
    res_quality = solver.solve(
        requested_pois=["shopping_mall"],
        quality_weight=0.95,
    )
    # Solve with high distance weight (low quality weight)
    res_distance = solver.solve(
        requested_pois=["shopping_mall"],
        quality_weight=0.05,
    )
    assert res_quality.is_valid and res_distance.is_valid
    # Candidate 2 has higher quality and is farther; Candidate 1 has lower distance
    # With w=0.95, quality matters most; with w=0.05, distance matters most.
    # The selected POI should reflect this trade-off
    q_poi = graph.get_poi(res_quality.poi_ids[0])
    d_poi = graph.get_poi(res_distance.poi_ids[0])
    assert q_poi.quality >= d_poi.quality


def test_solver_full_enumeration_performance():
    graph = generate_synthetic_graph(graph_id="test_001", seed=42)
    solver = ExactRouteSolver(graph)

    # Full 5 categories requested (maximum search space)
    t0 = time.perf_counter()
    res = solver.solve(
        requested_pois=["shopping_mall", "supermarket", "pharmacy", "bank", "library"],
        time_limit=1400,
        dependencies=[("supermarket", "pharmacy")],
        quality_weight=0.5,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"5-POI exact solve time: {elapsed_ms:.2f} ms, status={res.status}, route={res.poi_ids}")
    assert res.is_valid
    assert elapsed_ms < 100.0  # Must be well under 100ms
