"""Generate deterministic decision-contrast reports without gold access."""
from __future__ import annotations

from dataclasses import asdict

from src.evaluation import check_route
from src.graph import SyntheticGraph
from src.intent import Intent, closure
from src.solver import ExactRouteSolver, RouteResult


FIELDS = ("pois", "time_limit", "dependencies", "quality_weight")


def intent_dict(intent: Intent) -> dict[str, object]:
    return {
        "pois": list(intent.pois),
        "time_limit": intent.time_limit,
        "dependencies": [list(pair) for pair in intent.dependencies],
        "quality_weight": intent.quality_weight,
    }


def differing_fields(a: Intent, b: Intent) -> list[str]:
    values_a = intent_dict(a)
    values_b = intent_dict(b)
    return [field for field in FIELDS if values_a[field] != values_b[field]]


def _swap(base: Intent, donor: Intent, field: str) -> Intent:
    data = intent_dict(base)
    data[field] = intent_dict(donor)[field]
    return Intent.parse(data)


def _route_summary(graph: SyntheticGraph, route: RouteResult) -> dict[str, object]:
    qualities = [graph.get_poi(poi_id).quality for poi_id in route.poi_ids if graph.get_poi(poi_id)]
    return {
        "poi_ids": list(route.poi_ids),
        "categories": list(route.categories),
        "coverage_count": route.coverage,
        "is_valid": route.is_valid,
        "is_full_coverage": route.is_full_coverage,
        "average_quality": sum(qualities) / len(qualities) if qualities else None,
        "distance_km": route.total_distance,
        "duration_minutes": route.total_time,
        "arrival_minutes": route.final_arrival_time,
        "utility_under_own_candidate": route.raw_utility,
        "status": route.status,
    }


def _cross_check(graph: SyntheticGraph, route: RouteResult, intent: Intent) -> dict[str, object]:
    checked = check_route(graph, route, intent)
    reasons = [reason.replace("gold_", "candidate_") for reason in checked["reasons"]]
    return {"task_success": checked["task_success"], "reasons": reasons}


def build_contrast_report(
    instruction: str,
    candidate_a: Intent,
    candidate_b: Intent,
    graph: SyntheticGraph,
    evidence_a: dict[str, str] | None = None,
    evidence_b: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build report E from normal scenario data and candidates only."""
    solver = ExactRouteSolver(graph)
    route_a = solver.solve(**candidate_a.solver_args())
    route_b = solver.solve(**candidate_b.solver_args())
    differences = differing_fields(candidate_a, candidate_b)
    swaps: list[dict[str, object]] = []
    for field in differences:
        for base_name, base, donor in (("A", candidate_a, candidate_b), ("B", candidate_b, candidate_a)):
            item: dict[str, object] = {"base": base_name, "field_from_other": field}
            try:
                hybrid = _swap(base, donor, field)
                item["hybrid_intent"] = intent_dict(hybrid)
                item["route"] = _route_summary(graph, solver.solve(**hybrid.solver_args()))
            except ValueError as exc:
                item.update(status="invalid_hybrid", reason=str(exc))
            swaps.append(item)
    return {
        "report_version": "darc-v5.1-contrast-2",
        "instruction": instruction,
        "candidate_A": intent_dict(candidate_a),
        "candidate_B": intent_dict(candidate_b),
        "candidate_evidence": {"A": evidence_a or {}, "B": evidence_b or {}},
        "differing_fields": differences,
        "routes": {"A": _route_summary(graph, route_a), "B": _route_summary(graph, route_b)},
        "cross_constraints": {
            "route_A_under_A": _cross_check(graph, route_a, candidate_a),
            "route_A_under_B": _cross_check(graph, route_a, candidate_b),
            "route_B_under_A": _cross_check(graph, route_b, candidate_a),
            "route_B_under_B": _cross_check(graph, route_b, candidate_b),
        },
        "single_field_swaps": swaps,
        "limitations": [
            "The report does not identify the user's true intent.",
            "Both candidates may share the same error.",
            "Single-field swaps do not identify higher-order interactions.",
        ],
    }
