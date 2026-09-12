"""Controlled paired graphs for the HIPP-DC development protocol."""
from __future__ import annotations

import itertools
import math
from dataclasses import replace

from src.graph import DEFAULT_STAY_DURATIONS, POI, POI_CATEGORIES, SyntheticGraph
from src.intent import Intent
from src.solver import ExactRouteSolver


BASE_COORDINATES = {
    "shopping_mall": ((0.8, 0.4), (4.8, 1.0)),
    "supermarket": ((0.6, 1.1), (2.8, 4.4)),
    "pharmacy": ((-0.5, 0.9), (-3.8, 3.5)),
    "bank": ((-1.0, -0.3), (-4.5, -2.0)),
    "library": ((0.4, -1.0), (2.4, -4.6)),
}


def _max_edge_distance(pois: list[POI]) -> float:
    points = [(0.0, 0.0), *((p.x, p.y) for p in pois)]
    return max(math.dist(a, b) for a, b in itertools.combinations(points, 2))


def _graph(graph_id: str, qualities: tuple[float, float], far_close: int = 1440) -> SyntheticGraph:
    pois: list[POI] = []
    for category in POI_CATEGORIES:
        for candidate, (x, y) in enumerate(BASE_COORDINATES[category], start=1):
            quality = qualities[candidate - 1]
            pois.append(
                POI(
                    id=f"{category}_{candidate}",
                    category=category,
                    x=x,
                    y=y,
                    rating=4.0,
                    reviews=100 if candidate == 1 else 900,
                    quality=quality,
                    open_time=540,
                    close_time=far_close if candidate == 2 else 1440,
                    stay_duration=DEFAULT_STAY_DURATIONS[category],
                )
            )
    return SyntheticGraph(
        graph_id=graph_id,
        origin=(0.0, 0.0),
        destination=(0.0, 0.0),
        departure_time=540,
        speed_km_h=30.0,
        pois=pois,
        max_edge_distance=_max_edge_distance(pois),
    )


def build_graph_family(group_id: str) -> dict[str, SyntheticGraph]:
    """Return graphs whose documented parent-child differences are field-local."""
    aligned = _graph(f"{group_id}_aligned", (0.5, 0.5))
    tradeoff = _graph(f"{group_id}_tradeoff", (0.2, 0.9))
    time_sensitive = _graph(f"{group_id}_time_sensitive", (0.2, 0.9), far_close=550)
    return {"aligned": aligned, "tradeoff": tradeoff, "time_sensitive": time_sensitive}


def graph_field_diff(left: SyntheticGraph, right: SyntheticGraph) -> set[str]:
    """Return graph fields that differ, ignoring graph_id."""
    changed: set[str] = set()
    for field in ("origin", "destination", "departure_time", "speed_km_h", "max_edge_distance"):
        if getattr(left, field) != getattr(right, field):
            changed.add(field)
    lpois = {p.id: p for p in left.pois}
    rpois = {p.id: p for p in right.pois}
    if lpois.keys() != rpois.keys():
        changed.add("poi_ids")
        return changed
    for poi_id in lpois:
        for field in ("category", "x", "y", "rating", "reviews", "quality", "open_time", "close_time", "stay_duration"):
            if getattr(lpois[poi_id], field) != getattr(rpois[poi_id], field):
                changed.add(f"pois.{field}")
    return changed


def enumerate_full_feasible(graph: SyntheticGraph, intent: Intent) -> list[tuple[str, ...]]:
    """Enumerate the exact full-coverage feasible route domain for structural checks."""
    solver = ExactRouteSolver(graph)
    if not intent.pois:
        ok, *_ = solver.evaluate_sequence((), intent.time_limit, list(intent.dependencies), intent.quality_weight)
        return [()] if ok else []
    choices = [[p for p in graph.pois if p.category == category] for category in intent.pois]
    routes: list[tuple[str, ...]] = []
    for selected in itertools.product(*choices):
        for sequence in itertools.permutations(selected):
            ok, *_ = solver.evaluate_sequence(sequence, intent.time_limit, list(intent.dependencies), intent.quality_weight)
            if ok:
                routes.append(tuple(p.id for p in sequence))
    return sorted(set(routes))


def _route_attributes(graph: SyntheticGraph, intent: Intent, route: tuple[str, ...]) -> tuple[float, float]:
    lookup = {poi.id: poi for poi in graph.pois}
    sequence = tuple(lookup[poi_id] for poi_id in route)
    solver = ExactRouteSolver(graph)
    ok, _, distance, *_ = solver.evaluate_sequence(
        sequence, intent.time_limit, list(intent.dependencies), intent.quality_weight
    )
    if not ok:
        raise ValueError("route is not feasible under the supplied intent")
    quality = sum(poi.quality for poi in sequence) / len(sequence) if sequence else 0.0
    return quality, distance


def _extreme_sets(graph: SyntheticGraph, intent: Intent, routes: list[tuple[str, ...]]) -> tuple[set[tuple[str, ...]], set[tuple[str, ...]]]:
    values = {route: _route_attributes(graph, intent, route) for route in routes}
    max_quality = max((quality for quality, _ in values.values()), default=0.0)
    min_distance = min((distance for _, distance in values.values()), default=0.0)
    quality_set = {route for route, (quality, _) in values.items() if abs(quality - max_quality) <= 1e-9}
    distance_set = {route for route, (_, distance) in values.items() if abs(distance - min_distance) <= 1e-9}
    return quality_set, distance_set


def validate_graph_family(graphs: dict[str, SyntheticGraph], intent: Intent) -> dict[str, object]:
    aligned, tradeoff, time_sensitive = (graphs[k] for k in ("aligned", "tradeoff", "time_sensitive"))
    aligned_routes = enumerate_full_feasible(aligned, intent)
    tradeoff_routes = enumerate_full_feasible(tradeoff, intent)
    time_routes = enumerate_full_feasible(time_sensitive, intent)
    aligned_quality, aligned_distance = _extreme_sets(aligned, intent, aligned_routes)
    tradeoff_quality, tradeoff_distance = _extreme_sets(tradeoff, intent, tradeoff_routes)
    report = {
        "aligned_to_tradeoff_diff": sorted(graph_field_diff(aligned, tradeoff)),
        "tradeoff_to_time_diff": sorted(graph_field_diff(tradeoff, time_sensitive)),
        "full_feasible_counts": {
            "aligned": len(aligned_routes),
            "tradeoff": len(tradeoff_routes),
            "time_sensitive": len(time_routes),
        },
        "time_is_strict_subset": bool(time_routes) and set(time_routes) < set(tradeoff_routes),
        "aligned_extreme_sets_intersect": bool(aligned_quality & aligned_distance),
        "tradeoff_extreme_sets_disjoint": bool(tradeoff_quality) and bool(tradeoff_distance)
        and not bool(tradeoff_quality & tradeoff_distance),
    }
    report["valid"] = (
        report["aligned_to_tradeoff_diff"] == ["pois.quality"]
        and report["tradeoff_to_time_diff"] == ["pois.close_time"]
        and bool(aligned_routes)
        and bool(tradeoff_routes)
        and report["aligned_extreme_sets_intersect"]
        and report["tradeoff_extreme_sets_disjoint"]
        and report["time_is_strict_subset"]
    )
    return report
