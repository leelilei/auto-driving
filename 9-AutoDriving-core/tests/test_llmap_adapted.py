"""Unit tests for MSGS-adapted solver and LLMAP evaluation module."""

import pytest
import networkx as nx

from src.baselines.llmap_adapted import (
    SEARCH_TYPE_MAPPING,
    build_llmap_graph,
    compute_composite_utility,
    compute_path_and_cost_adapted,
    evaluate_llmap_path,
    msgs_adapted,
    parse_time,
)


def test_parse_time():
    """Verify time range string parser."""
    assert parse_time("Closed") == []
    assert parse_time("Monday: Closed") == []
    assert parse_time("Open 24 hours") == [(0.0, 24.0)]
    ranges = parse_time("Monday: 9:00 AM – 5:00 PM")
    assert len(ranges) == 1
    assert ranges[0] == (9.0, 17.0)

    # Hyphen separator
    ranges2 = parse_time("Monday: 10:30 AM - 2:00 PM")
    assert len(ranges2) == 1
    assert abs(ranges2[0][0] - 10.5) < 1e-4
    assert ranges2[0][1] == 14.0


def test_negative_weight_bellman_ford_fix():
    """Verify Bellman-Ford resolves negative weights where Dijkstra crashes."""
    G = nx.DiGraph()
    G.add_edge("start", "poi_bad", weight=2.0)
    G.add_edge("start", "poi_good", weight=5.0)
    G.add_edge("poi_bad", "goal", weight=10.0)
    G.add_edge("poi_good", "poi_bad", weight=-4.0)

    # In networkx, Dijkstra on this graph with negative weight raises ValueError
    with pytest.raises(ValueError, match="Contradictory paths found"):
        nx.single_source_dijkstra(G, "start", "goal", weight="weight")

    # Bellman-Ford succeeds
    length, path = nx.single_source_bellman_ford(G, "start", "goal", weight="weight")
    assert path == ["start", "poi_good", "poi_bad", "goal"]
    assert length == 11.0


def test_single_node_groups_no_empty_range_crash():
    """Verify solver handles single-node groups without crashing on min()."""
    scenario = {
        "start_location": {"latitude": 39.90, "longitude": 116.40},
        "end_location": {"latitude": 39.91, "longitude": 116.41},
        "pois": [
            {
                "Place ID": "p1",
                "Type": "bank",
                "Rating": 4.5,
                "Number Ratings": 50,
                "Latitude": 39.905,
                "Longitude": 116.405,
                "Opening": ["Monday: 9:00 AM – 5:00 PM"],
            },
            {
                "Place ID": "p2",
                "Type": "supermarket",
                "Rating": 4.0,
                "Number Ratings": 120,
                "Latitude": 39.908,
                "Longitude": 116.408,
                "Opening": ["Monday: 9:00 AM – 9:00 PM"],
            },
        ],
    }

    graph = build_llmap_graph(
        scenario=scenario,
        requested_pois=["bank", "supermarket"],
        time_limit_str="18:00",
        dependencies=[["bank", "supermarket"]],
        quality_weight=0.7,
        distance_weight=0.3,
    )

    path, order, arrival = msgs_adapted(graph)
    assert len(path) == 4  # start, p1, p2, goal
    assert path[0] == graph.start_node
    assert path[-1] == graph.goal_node
    assert arrival < 18.0


def test_dependency_mapping_subset_groups():
    """Verify dependency constraints are enforced when only a subset of groups is present."""
    scenario = {
        "start_location": {"latitude": 39.90, "longitude": 116.40},
        "end_location": {"latitude": 39.91, "longitude": 116.41},
        "pois": [
            # Group bank = 3
            {"Place ID": "b1", "Type": "bank", "Rating": 4.8, "Number Ratings": 100, "Latitude": 39.902, "Longitude": 116.402, "Opening": ["Monday: 9:00 AM – 5:00 PM"]},
            {"Place ID": "b2", "Type": "bank", "Rating": 4.5, "Number Ratings": 50, "Latitude": 39.903, "Longitude": 116.403, "Opening": ["Monday: 9:00 AM – 5:00 PM"]},
            # Group supermarket = 1
            {"Place ID": "s1", "Type": "supermarket", "Rating": 4.2, "Number Ratings": 200, "Latitude": 39.907, "Longitude": 116.407, "Opening": ["Monday: 9:00 AM – 9:00 PM"]},
            {"Place ID": "s2", "Type": "supermarket", "Rating": 3.9, "Number Ratings": 80, "Latitude": 39.908, "Longitude": 116.408, "Opening": ["Monday: 9:00 AM – 9:00 PM"]},
        ],
    }

    # Dependency: supermarket before bank
    graph = build_llmap_graph(
        scenario=scenario,
        requested_pois=["supermarket", "bank"],
        time_limit_str="18:00",
        dependencies=[["supermarket", "bank"]],
        quality_weight=0.5,
        distance_weight=0.5,
    )

    path, order, arrival = msgs_adapted(graph)
    # Order must have supermarket (1) before bank (3)
    assert order == [SEARCH_TYPE_MAPPING["supermarket"], SEARCH_TYPE_MAPPING["bank"]]

    eval_res = evaluate_llmap_path(graph, path, order)
    assert eval_res["dependency_violations"] == 0
    assert eval_res["is_valid"] is True


def test_full_synthetic_scenario_evaluation():
    """Verify end-to-end planning and evaluation on a 10-POI scenario."""
    scenario = {
        "start_location": {"latitude": 39.90, "longitude": 116.40},
        "end_location": {"latitude": 39.90, "longitude": 116.40},
        "pois": [
            {"Place ID": "sm1", "Type": "shopping_mall", "Rating": 4.6, "Number Ratings": 300, "Latitude": 39.92, "Longitude": 116.42, "Opening": ["Monday: 10:00 AM – 10:00 PM"]},
            {"Place ID": "sm2", "Type": "shopping_mall", "Rating": 4.1, "Number Ratings": 150, "Latitude": 39.88, "Longitude": 116.38, "Opening": ["Monday: 10:00 AM – 10:00 PM"]},
            {"Place ID": "sp1", "Type": "supermarket", "Rating": 4.5, "Number Ratings": 220, "Latitude": 39.91, "Longitude": 116.41, "Opening": ["Monday: 8:00 AM – 10:00 PM"]},
            {"Place ID": "sp2", "Type": "supermarket", "Rating": 3.8, "Number Ratings": 60, "Latitude": 39.89, "Longitude": 116.39, "Opening": ["Monday: 8:00 AM – 10:00 PM"]},
            {"Place ID": "ph1", "Type": "pharmacy", "Rating": 4.9, "Number Ratings": 90, "Latitude": 39.905, "Longitude": 116.405, "Opening": ["Monday: 9:00 AM – 8:00 PM"]},
            {"Place ID": "ph2", "Type": "pharmacy", "Rating": 4.0, "Number Ratings": 30, "Latitude": 39.895, "Longitude": 116.395, "Opening": ["Monday: 9:00 AM – 8:00 PM"]},
            {"Place ID": "bk1", "Type": "bank", "Rating": 4.4, "Number Ratings": 110, "Latitude": 39.912, "Longitude": 116.402, "Opening": ["Monday: 9:00 AM – 5:00 PM"]},
            {"Place ID": "bk2", "Type": "bank", "Rating": 3.7, "Number Ratings": 40, "Latitude": 39.888, "Longitude": 116.408, "Opening": ["Monday: 9:00 AM – 5:00 PM"]},
            {"Place ID": "lb1", "Type": "library", "Rating": 4.7, "Number Ratings": 180, "Latitude": 39.93, "Longitude": 116.39, "Opening": ["Monday: 9:00 AM – 6:00 PM"]},
            {"Place ID": "lb2", "Type": "library", "Rating": 4.2, "Number Ratings": 75, "Latitude": 39.87, "Longitude": 116.41, "Opening": ["Monday: 9:00 AM – 6:00 PM"]},
        ],
    }

    graph = build_llmap_graph(
        scenario=scenario,
        requested_pois=["shopping_mall", "pharmacy", "bank"],
        time_limit_str="18:00",
        dependencies=[["bank", "shopping_mall"]],
        quality_weight=0.6,
        distance_weight=0.4,
    )

    path, order, arrival = msgs_adapted(graph)
    assert len(path) == 5  # start, 3 POIs, goal
    eval_res = evaluate_llmap_path(graph, path, order)

    assert eval_res["group_coverage"] == 100.0
    assert eval_res["dependency_violations"] == 0
    assert eval_res["time_violations_hours"] == 0.0
    assert eval_res["availability_violations"] == 0
    assert eval_res["is_valid"] is True

    utility = compute_composite_utility(eval_res, quality_weight=0.6, distance_weight=0.4)
    assert -1.0 <= utility <= 1.0
