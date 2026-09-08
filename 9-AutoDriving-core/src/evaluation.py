"""Independent gold route checker: deliberately does not call the planning evaluator."""
from __future__ import annotations
import math
from src.intent import Intent, closure


def check_route(graph, result, gold: Intent):
    reasons = []
    if result is None or not result.is_valid:
        return {"task_success": False, "reasons": ["no_valid_route"]}
    lookup = {p.id: p for p in graph.pois}
    if len(set(result.poi_ids)) != len(result.poi_ids) or any(i not in lookup for i in result.poi_ids):
        return {"task_success": False, "reasons": ["invalid_node_sequence"]}
    nodes = [lookup[i] for i in result.poi_ids]
    cats = [p.category for p in nodes]
    if set(cats) != set(gold.pois) or len(cats) != len(set(cats)):
        reasons.append("requested_POIs_mismatch")
    for a, b in gold.dependencies:
        if a not in cats or b not in cats or cats.index(a) >= cats.index(b):
            reasons.append("gold_dependency_violation")
            break
    current, position = float(graph.departure_time), graph.origin
    distance = 0.0
    for node in nodes:
        leg = math.dist(position, (node.x, node.y))
        distance += leg
        current = max(current + leg * 60 / graph.speed_km_h, node.open_time) + node.stay_duration
        if current > node.close_time + 1e-4:
            reasons.append("opening_hours_violation")
        position = (node.x, node.y)
    leg = math.dist(position, graph.destination)
    distance += leg
    current += leg * 60 / graph.speed_km_h
    if gold.time_limit is not None and current > gold.time_limit + 1e-4:
        reasons.append("gold_deadline_violation")
    return {"task_success": not reasons, "reasons": sorted(set(reasons)),
            "arrival_minutes": current, "distance_km": distance}


def compare_intents(predicted, gold):
    if predicted is None:
        return {"hard_exact": False, "poi_exact": False, "time_exact": False, "dependency_exact": False}
    fields = {"poi_exact": predicted.pois == gold.pois,
              "time_exact": predicted.time_limit == gold.time_limit,
              "dependency_exact": closure(predicted.dependencies) == closure(gold.dependencies)}
    return {**fields, "hard_exact": all(fields.values())}
