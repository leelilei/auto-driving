"""LLMAP-adapted backend and MSGS solver.

Implements the LLMAP baseline solver with explicit bug fixes and safeguards:
1. Fixes NetworkX Dijkstra crash on negative edge weights by using Bellman-Ford / DAG shortest path.
2. Safeguards min-max normalization against empty intra-group distances.
3. Fixes dependency category mapping bug in permutation validation.
4. Provides composite utility calculation for DARC cross-utility delta U gating.

Strictly designated as 'LLMAP-adapted' per TRANSFER_FEASIBILITY.md.
"""

from __future__ import annotations

import itertools
import math
import re
from dataclasses import dataclass, field
from typing import Any

from haversine import haversine
import networkx as nx
import numpy as np

# Official LLMAP mappings and parameters
SEARCH_TYPE_MAPPING = {
    "shopping_mall": 0,
    "supermarket": 1,
    "pharmacy": 2,
    "bank": 3,
    "library": 4,
}

REVERSE_SEARCH_TYPE_MAPPING = {v: k for k, v in SEARCH_TYPE_MAPPING.items()}

STAY_TIME_MAPPING = {
    0: 120,  # shopping_mall: 120 min
    1: 30,   # supermarket: 30 min
    2: 15,   # pharmacy: 15 min
    3: 20,   # bank: 20 min
    4: 60,   # library: 60 min
}

AVERAGE_SPEED = 0.5  # km/min = 30 km/h
DISTANCE_FACTOR = 1.5

DAY_TO_INDEX = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

CURRENT_DAY = "Monday"
DEPARTURE_TIME = 10.0  # 10:00 AM in hours


def parse_time(time_str: str) -> list[tuple[float, float]]:
    """Parse opening hours string into list of (start_hour, end_hour) tuples."""
    if not time_str or time_str.endswith("Closed"):
        return []
    if "Open 24 hours" in time_str:
        return [(0.0, 24.0)]

    time_ranges = []
    for time_range in time_str.split(","):
        time_range = time_range.strip()
        if "–" not in time_range and "-" not in time_range:
            continue
        sep = "–" if "–" in time_range else "-"
        parts = time_range.split(sep)
        if len(parts) != 2:
            continue
        start_time_str, end_time_str = parts[0].strip(), parts[1].strip()
        pattern = r"(\d+):(\d+)\s*(AM|PM)"
        start_match = re.search(pattern, start_time_str, re.IGNORECASE)
        end_match = re.search(pattern, end_time_str, re.IGNORECASE)
        if not (start_match and end_match):
            continue

        def convert_to_hours(match: re.Match[str]) -> float:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            period = match.group(3).upper()
            if period == "PM" and hours != 12:
                hours += 12
            elif period == "AM" and hours == 12:
                hours = 0
            return hours + minutes / 60.0

        time_ranges.append((convert_to_hours(start_match), convert_to_hours(end_match)))
    return time_ranges


def check_path_availability(
    path: list[int],
    groups: list[int],
    goal_node: int,
    positions: list[tuple[float, float]],
    openings: list[Any],
    start_time: float = DEPARTURE_TIME,
) -> bool:
    """Check if all POIs in path are visited within their opening hours."""
    current_time = start_time
    for i in range(len(path) - 1):
        node1, node2 = path[i], path[i + 1]
        travel_time = (
            haversine(positions[node1], positions[node2])
            * DISTANCE_FACTOR
            / AVERAGE_SPEED
            / 60.0
        )
        current_time += travel_time
        if node2 != goal_node:
            node_openings = openings[node2]
            if isinstance(node_openings, list) and len(node_openings) > DAY_TO_INDEX[CURRENT_DAY]:
                day_opening_hours = node_openings[DAY_TO_INDEX[CURRENT_DAY]]
            elif isinstance(node_openings, str):
                day_opening_hours = node_openings
            else:
                day_opening_hours = "Monday: 9:00 AM – 5:00 PM"

            def is_available(time_val: float, opening_times: list[tuple[float, float]]) -> bool:
                if not opening_times:
                    return False
                for s_time, e_time in opening_times:
                    if s_time <= time_val <= e_time:
                        return True
                return False

            parsed_intervals = parse_time(day_opening_hours)
            if not is_available(current_time, parsed_intervals):
                return False
            grp = groups[node2]
            current_time += (STAY_TIME_MAPPING[grp] / 60.0) if grp != -1 else 0.0
    return True


def min_max_normalize(value: float, value_range: tuple[float, float], zero_case: float = 0.0) -> float:
    """Normalize value into [0, 1] range."""
    if value_range[0] == value_range[1]:
        return zero_case
    return (value - value_range[0]) / (value_range[1] - value_range[0])


@dataclass
class LLMAPGraph:
    """Represents a graph instance for LLMAP / MSGS."""
    positions: list[tuple[float, float]]
    edge_indices: list[list[int]]
    edge_weights: list[float]
    start_node: int
    goal_node: int
    groups: list[int]
    time_constraint: float  # In hours, e.g. 14.0 or inf
    ratings: list[float]
    num_ratings: list[int]
    dependencies: list[list[str]]
    openings: list[Any]
    alpha: float  # quality_weight / 2
    beta: float   # distance_weight


def build_llmap_graph(
    scenario: dict[str, Any],
    requested_pois: list[str],
    time_limit_str: str | None,
    dependencies: list[list[str]],
    quality_weight: float = 0.5,
    distance_weight: float = 0.5,
) -> LLMAPGraph:
    """Construct an LLMAPGraph from scenario data and extracted parameters."""
    req_set = set(requested_pois)
    all_pois = scenario.get("pois", [])

    # Filter to requested POI types
    filtered_pois = [p for p in all_pois if p.get("Type") in req_set]

    num_nodes = len(filtered_pois) + 2
    nodes = list(range(num_nodes))
    start_node = 0
    goal_node = num_nodes - 1

    positions: dict[int, tuple[float, float]] = {}
    positions[start_node] = (
        scenario["start_location"]["latitude"],
        scenario["start_location"]["longitude"],
    )
    positions[goal_node] = (
        scenario["end_location"]["latitude"],
        scenario["end_location"]["longitude"],
    )

    groups = [-1] * num_nodes
    ratings = [-1.0] * num_nodes
    num_ratings = [-1] * num_nodes
    openings = [""] * num_nodes

    for idx, poi in enumerate(filtered_pois, start=1):
        positions[idx] = (poi["Latitude"], poi["Longitude"])
        ptype = poi.get("Type", "")
        groups[idx] = SEARCH_TYPE_MAPPING.get(ptype, -1)
        r_val = poi.get("Rating", 1.0)
        ratings[idx] = 1.0 if r_val == "N/A" or r_val is None else float(r_val)
        nr_val = poi.get("Number Ratings", 1)
        num_ratings[idx] = 1 if nr_val == "N/A" or nr_val is None else int(nr_val)
        op_val = poi.get("Opening", ["Monday: 9:00 AM – 5:00 PM"])
        openings[idx] = op_val

    positions_list = [positions[i] for i in nodes]

    edge_indices: list[list[int]] = []
    edge_weights: list[float] = []
    for i in nodes:
        for j in nodes:
            if i != j and groups[i] != groups[j]:
                edge_indices.append([i, j])
                edge_weights.append(haversine(positions_list[i], positions_list[j]))

    if [start_node, goal_node] not in edge_indices:
        edge_indices.append([start_node, goal_node])
        edge_weights.append(haversine(positions_list[start_node], positions_list[goal_node]))

    # Parse time constraint
    t_limit = float("inf")
    if time_limit_str and time_limit_str != "None":
        hour_part = str(time_limit_str).split(":")[0].strip()
        if hour_part.isdigit():
            t_limit = float(hour_part)

    return LLMAPGraph(
        positions=positions_list,
        edge_indices=edge_indices,
        edge_weights=edge_weights,
        start_node=start_node,
        goal_node=goal_node,
        groups=groups,
        time_constraint=t_limit,
        ratings=ratings,
        num_ratings=num_ratings,
        dependencies=dependencies or [],
        openings=openings,
        alpha=float(quality_weight) / 2.0,
        beta=float(distance_weight),
    )


def compute_path_and_cost_adapted(
    graph: LLMAPGraph,
    selected_group_indices: tuple[int, ...],
    node_in_groups: list[list[int]],
    travel_time_range: tuple[float, float],
    num_ratings_range: tuple[float, float],
    use_bellman_ford: bool = True,
) -> tuple[float, list[int]]:
    """Compute shortest path and arrival time for a specific permutation of groups.
    
    Fixes negative-weight crash using Bellman-Ford / DAG shortest path.
    """
    start_node = graph.start_node
    goal_node = graph.goal_node
    positions = graph.positions
    groups = graph.groups
    ratings = graph.ratings
    num_ratings = graph.num_ratings
    openings = graph.openings
    alpha = graph.alpha
    beta = graph.beta

    rating_range = (1.0, 5.0)
    stay_time_range = (15.0, 120.0)

    def calculate_real_time(node1: int, node2: int) -> float:
        travel_time = (
            haversine(positions[node1], positions[node2])
            * DISTANCE_FACTOR
            / AVERAGE_SPEED
            / 60.0
        )
        stay_time = (STAY_TIME_MAPPING[groups[node2]] / 60.0) if groups[node2] != -1 else 0.0
        return travel_time + stay_time

    def calculate_weight(node1: int, node2: int) -> float:
        travel_time = min_max_normalize(
            haversine(positions[node1], positions[node2]) * DISTANCE_FACTOR / AVERAGE_SPEED / 60.0,
            travel_time_range,
            zero_case=0.0,
        )
        stay_time = min_max_normalize(
            (STAY_TIME_MAPPING[groups[node2]] / 60.0) if groups[node2] != -1 else 0.0,
            stay_time_range,
            zero_case=0.0,
        )
        if node2 == goal_node:
            return travel_time + stay_time
        node_rating = min_max_normalize(ratings[node2], rating_range, zero_case=1.0)
        node_num_ratings = min_max_normalize(float(num_ratings[node2]), num_ratings_range, zero_case=1.0)
        return - (alpha * node_rating + alpha * node_num_ratings) + beta * (travel_time + stay_time)

    edges = [(start_node, node, calculate_weight(start_node, node)) for node in node_in_groups[selected_group_indices[0]]]
    edges.extend([
        (prev_node, next_node, calculate_weight(prev_node, next_node))
        for prev_group, next_group in zip(selected_group_indices[:-1], selected_group_indices[1:])
        for prev_node in node_in_groups[prev_group]
        for next_node in node_in_groups[next_group]
    ])
    edges.extend([(node, goal_node, calculate_weight(node, goal_node)) for node in node_in_groups[selected_group_indices[-1]]])

    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)

    try:
        if use_bellman_ford:
            _, path = nx.single_source_bellman_ford(G, source=start_node, target=goal_node, weight="weight")
        else:
            _, path = nx.single_source_dijkstra(G, source=start_node, target=goal_node, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound, ValueError):
        return float("inf"), []

    if not check_path_availability(path, groups, goal_node, positions, openings):
        return float("inf"), path

    real_time = DEPARTURE_TIME + sum(
        calculate_real_time(path[k], path[k + 1]) for k in range(len(path) - 1)
    )
    return real_time, path


def msgs_adapted(
    graph: LLMAPGraph,
    search_mode: str = "first_feasible",  # "first_feasible" (official heuristic) or "best_feasible"
) -> tuple[list[int], list[int], float]:
    """MSGS-adapted route planning.

    Args:
        graph: LLMAPGraph instance.
        search_mode: 'first_feasible' matches official LLMAP early termination on first valid permutation.
                     'best_feasible' searches all valid permutations of maximum size for minimum cost.

    Returns:
        (best_path, best_group_order, best_arrival_time)
    """
    start_node = graph.start_node
    goal_node = graph.goal_node
    groups = graph.groups
    time_constraint = graph.time_constraint
    dependencies = graph.dependencies

    # Extract distinct non-negative group IDs
    actual_group_ids = sorted(list(set(g for g in groups if g >= 0)))
    if not actual_group_ids:
        return [start_node, goal_node], [], DEPARTURE_TIME

    node_in_groups: list[list[int]] = []
    for gid in actual_group_ids:
        indices = [idx for idx, g in enumerate(groups) if g == gid and idx not in (start_node, goal_node)]
        node_in_groups.append(indices)

    # Pre-calculate ranges with safeguard against empty intra-group pairs
    travel_times = [
        haversine(graph.positions[n1], graph.positions[n2]) * DISTANCE_FACTOR / AVERAGE_SPEED / 60.0
        for group in node_in_groups for n1 in group for n2 in group if n1 != n2
    ]
    if not travel_times:
        all_poi_nodes = [node for group in node_in_groups for node in group]
        travel_times = [
            haversine(graph.positions[n1], graph.positions[n2]) * DISTANCE_FACTOR / AVERAGE_SPEED / 60.0
            for n1 in all_poi_nodes for n2 in all_poi_nodes if n1 != n2
        ]
    if not travel_times:
        travel_time_range = (0.0, 1.0)
    else:
        min_t, max_t = min(travel_times), max(travel_times)
        travel_time_range = (min_t, max_t if max_t > min_t else min_t + 1.0)

    num_ratings_list = [graph.num_ratings[node] for group in node_in_groups for node in group]
    if not num_ratings_list:
        num_ratings_range = (1.0, 100.0)
    else:
        min_nr, max_nr = float(min(num_ratings_list)), float(max(num_ratings_list))
        num_ratings_range = (min_nr, max_nr if max_nr > min_nr else min_nr + 1.0)

    # Dependency validation fixing group ID mapping
    def is_valid_order(perm: tuple[int, ...]) -> bool:
        for dep in dependencies:
            if len(dep) != 2:
                continue
            cat_a, cat_b = dep[0], dep[1]
            if cat_a in SEARCH_TYPE_MAPPING and cat_b in SEARCH_TYPE_MAPPING:
                gid_a = SEARCH_TYPE_MAPPING[cat_a]
                gid_b = SEARCH_TYPE_MAPPING[cat_b]
                if gid_a in actual_group_ids and gid_b in actual_group_ids:
                    idx_a = actual_group_ids.index(gid_a)
                    idx_b = actual_group_ids.index(gid_b)
                    if idx_a in perm and idx_b in perm:
                        if perm.index(idx_a) > perm.index(idx_b):
                            return False
        return True

    best_weight = float("inf")
    best_path: list[int] | None = None
    best_order: list[int] | None = None

    group_indices = list(range(len(node_in_groups)))

    # Search from largest subset to smallest
    for num_groups in range(len(group_indices), 0, -1):
        for groups_subset in itertools.combinations(group_indices, num_groups):
            for perm in itertools.permutations(groups_subset):
                if is_valid_order(perm):
                    w, p = compute_path_and_cost_adapted(
                        graph=graph,
                        selected_group_indices=perm,
                        node_in_groups=node_in_groups,
                        travel_time_range=travel_time_range,
                        num_ratings_range=num_ratings_range,
                        use_bellman_ford=True,
                    )
                    if w <= time_constraint and w < best_weight:
                        best_weight = w
                        best_path = p
                        best_order = [actual_group_ids[idx] for idx in perm]
                        if search_mode == "first_feasible":
                            break
            if best_path is not None and search_mode == "first_feasible":
                break
        if best_path is not None and search_mode == "first_feasible":
            break

    if best_path is None:
        return [start_node, goal_node], [], DEPARTURE_TIME

    return best_path, best_order or [], best_weight


def evaluate_llmap_path(
    graph: LLMAPGraph,
    path: list[int],
    group_order: list[int],
) -> dict[str, Any]:
    """Evaluate path according to official LLMAP evaluation metrics."""
    goal_node = graph.goal_node
    positions = graph.positions
    groups = graph.groups
    ratings = graph.ratings
    num_ratings = graph.num_ratings
    time_constraint = graph.time_constraint
    dependencies = graph.dependencies
    openings = graph.openings

    # 1. Group coverage
    covered_groups = set(groups[node] for node in path if groups[node] >= 0)
    total_groups = set(g for g in groups if g >= 0)
    group_coverage_rate = (len(covered_groups) / len(total_groups) * 100.0) if total_groups else 0.0

    # 2. Ratings and number of ratings
    path_ratings = [ratings[node] for node in path[1:-1] if node != goal_node]
    path_num_ratings = [num_ratings[node] for node in path[1:-1] if node != goal_node]
    avg_rating = sum(path_ratings) / len(path_ratings) if path_ratings else 0.0
    avg_num_ratings = sum(path_num_ratings) / len(path_num_ratings) if path_num_ratings else 0.0

    # 3. Path length
    path_length = 0.0
    for u, v in zip(path[:-1], path[1:]):
        path_length += haversine(positions[u], positions[v]) * DISTANCE_FACTOR

    # 4. Real time and time violations
    def calc_seg_time(n1: int, n2: int) -> float:
        t_time = haversine(positions[n1], positions[n2]) * DISTANCE_FACTOR / AVERAGE_SPEED / 60.0
        s_time = (STAY_TIME_MAPPING[groups[n2]] / 60.0) if groups[n2] != -1 else 0.0
        return t_time + s_time

    real_time = DEPARTURE_TIME + sum(calc_seg_time(path[i], path[i + 1]) for i in range(len(path) - 1))
    time_violation = max(0.0, real_time - time_constraint)

    # 5. Dependency violations
    dep_violation = 0
    for dep in dependencies:
        if len(dep) != 2:
            continue
        cat_a, cat_b = dep[0], dep[1]
        if cat_a in SEARCH_TYPE_MAPPING and cat_b in SEARCH_TYPE_MAPPING:
            gid_a = SEARCH_TYPE_MAPPING[cat_a]
            gid_b = SEARCH_TYPE_MAPPING[cat_b]
            if gid_a in group_order and gid_b in group_order:
                if group_order.index(gid_a) > group_order.index(gid_b):
                    dep_violation = 1
                    break

    # 6. Availability violations
    avail_violation = 0 if check_path_availability(path, groups, goal_node, positions, openings) else 1

    is_valid = (time_violation == 0.0 and dep_violation == 0 and avail_violation == 0)

    return {
        "path": path,
        "group_order": group_order,
        "group_coverage": group_coverage_rate,
        "avg_rating": avg_rating,
        "avg_num_ratings": avg_num_ratings,
        "path_length_km": path_length,
        "real_time_hours": real_time,
        "time_violations_hours": time_violation,
        "dependency_violations": dep_violation,
        "availability_violations": avail_violation,
        "is_valid": is_valid,
    }


def compute_composite_utility(
    eval_result: dict[str, Any],
    quality_weight: float,
    distance_weight: float,
    max_path_length_km: float = 100.0,
) -> float:
    """Compute normalized composite utility U_w(r) in [0, 1] for DARC delta U gating.

    U_w(r) = w * Q(r) - (1-w) * D_bar(r)
    If path violates hard constraints, utility is penalized to 0.0 or negative.
    """
    if not eval_result.get("is_valid", False):
        return -1.0

    avg_rating = eval_result.get("avg_rating", 1.0)
    norm_quality = min_max_normalize(avg_rating, (1.0, 5.0), zero_case=0.0)

    path_length = eval_result.get("path_length_km", 0.0)
    norm_dist = min(1.0, path_length / max_path_length_km)

    w = quality_weight
    utility = w * norm_quality - (1.0 - w) * norm_dist
    return utility
