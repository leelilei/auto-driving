"""Decision-aware Gating and Baselines (B0 to B6 + Ours) for DARC-Route.

Per Proposal v4 & EXPERIMENT_GUIDE.md Sections 6 & 7:
1. Structure extraction:
   H = (sorted(S), T, closure(D))
2. Protection trigger h:
   h = 1 if:
   - A or B is invalid (schema/type/constraint violation)
   - H(A) != H(B)
   - Either route has planning exception / is infeasible
   - Coverage count differs (cov(r_A) != cov(r_B))
   h = 0 otherwise.
3. Cross-utility difference delta_U:
   Only computed if h == 0 (both valid, same structure, same coverage):
   delta_U = max(|U_wA(rA) - U_wA(rB)|, |U_wB(rA) - U_wB(rB)|)
   where U_w(r) = w * Q(r) - (1 - w) * D_bar(r),
   D_bar(r) = total_dist / (6 * max_edge_distance).
   If routes are identical, delta_U = 0.0.
   If h == 1, delta_U is None.
4. Gating rule:
   g_DARC = h or (delta_U > tau)
5. Review fallback:
   Review candidate -> Candidate A -> Candidate B -> None.
6. Baseline execution:
   B0: Single A (1 call)
   B1: Medoid of {A, A2, A3} (3 calls)
   B2: Generates A and B, always outputs A (2 calls; identical output to B0)
   B3: Protection h, else probability p to review (2 + q calls)
   B4: Protection h or |wA - wB| > tau_sem (2 + q calls)
   B5: Only protection h (2 + q calls)
   B6: Always review after A and B (3 calls)
   Ours: g_DARC = h or delta_U > tau (2 + q calls)
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict
from typing import Any

from src.graph import SyntheticGraph
from src.intent import Intent, closure
from src.solver import ExactRouteSolver, RouteResult


def extract_structure(intent: Intent | None) -> tuple[tuple[str, ...], int | None, tuple[tuple[str, str], ...]] | None:
    """Extract hard structure H = (sorted(S), T, closure(D))."""
    if intent is None:
        return None
    return (
        tuple(sorted(intent.pois)),
        intent.time_limit,
        closure(intent.dependencies),
    )


def compute_protection_trigger(
    intent_a: Intent | None,
    intent_b: Intent | None,
    route_a: RouteResult | None,
    route_b: RouteResult | None,
) -> int:
    """Compute binary protection trigger h in {0, 1}.

    h = 1 if:
    - either intent is None
    - structural mismatch: H(A) != H(B)
    - either route is None or not valid
    - route coverage count differs
    """
    if intent_a is None or intent_b is None:
        return 1

    h_a = extract_structure(intent_a)
    h_b = extract_structure(intent_b)
    if h_a != h_b:
        return 1

    if route_a is None or route_b is None:
        return 1
    if not route_a.is_valid or not route_b.is_valid:
        return 1
    if route_a.coverage != route_b.coverage:
        return 1

    return 0


def compute_exact_route_distance(graph: SyntheticGraph, poi_ids: tuple[str, ...] | list[str]) -> float:
    """Compute exact unrounded travel distance from origin through visited POIs to destination."""
    lookup = {p.id: (p.x, p.y) for p in graph.pois}
    curr = graph.origin
    total_d = 0.0
    for pid in poi_ids:
        if pid in lookup:
            nxt = lookup[pid]
            total_d += graph.travel_distance(curr, nxt)
            curr = nxt
    total_d += graph.travel_distance(curr, graph.destination)
    return total_d


def calculate_route_utility(
    graph: SyntheticGraph,
    route: RouteResult | dict | None,
    quality_weight: float,
) -> float:
    """Compute exact unrounded utility U_w(r) = w * Q(r) - (1-w) * D_bar(r)."""
    if route is None:
        return -1.0

    if isinstance(route, dict):
        is_valid = route.get("is_valid", False)
        poi_ids = tuple(route.get("poi_ids", ()))
    else:
        is_valid = route.is_valid
        poi_ids = route.poi_ids

    if not is_valid:
        return -1.0

    scale_d = 6.0 * graph.max_edge_distance
    exact_dist = compute_exact_route_distance(graph, poi_ids)
    d_bar = exact_dist / scale_d if scale_d > 0 else 0.0

    if len(poi_ids) == 0:
        avg_q = 0.0
    else:
        lookup = {p.id: p.quality for p in graph.pois}
        visited_qualities = [lookup[pid] for pid in poi_ids if pid in lookup]
        avg_q = sum(visited_qualities) / len(visited_qualities) if visited_qualities else 0.0

    w = max(0.0, min(1.0, float(quality_weight)))
    return w * avg_q - (1.0 - w) * d_bar


def calculate_route_regret(
    graph: SyntheticGraph,
    oracle_route: RouteResult | dict | None,
    chosen_route: RouteResult | dict | None,
    gold_quality_weight: float,
) -> float:
    """Compute normalized decision regret on the same gold utility scale [0, 1].

    Both oracle route and chosen route are evaluated under the exact same gold quality weight.
    """
    if oracle_route is None or chosen_route is None:
        return 1.0

    chosen_is_valid = chosen_route.get("is_valid", False) if isinstance(chosen_route, dict) else chosen_route.is_valid
    if not chosen_is_valid:
        return 1.0

    oracle_u = calculate_route_utility(graph, oracle_route, gold_quality_weight)
    actual_u = calculate_route_utility(graph, chosen_route, gold_quality_weight)

    return max(0.0, (oracle_u - actual_u) / 2.0)


def compute_cross_utility_delta(
    graph: SyntheticGraph,
    intent_a: Intent | None,
    intent_b: Intent | None,
    route_a: RouteResult | None,
    route_b: RouteResult | None,
) -> float | None:
    """Compute cross-evaluation utility discrepancy delta_U.

    Returns None if protection trigger h == 1.
    If routes are identical in POI sequence, returns 0.0.
    """
    h = compute_protection_trigger(intent_a, intent_b, route_a, route_b)
    if h == 1 or intent_a is None or intent_b is None or route_a is None or route_b is None:
        return None

    # If both chose the exact same sequence of POI IDs, cross utility difference is zero
    if route_a.poi_ids == route_b.poi_ids:
        return 0.0

    w_a = intent_a.quality_weight
    w_b = intent_b.quality_weight

    u_wa_ra = calculate_route_utility(graph, route_a, w_a)
    u_wa_rb = calculate_route_utility(graph, route_b, w_a)
    u_wb_ra = calculate_route_utility(graph, route_a, w_b)
    u_wb_rb = calculate_route_utility(graph, route_b, w_b)

    diff_a = abs(u_wa_ra - u_wa_rb)
    diff_b = abs(u_wb_ra - u_wb_rb)

    return max(diff_a, diff_b)


def evaluate_darc_gate(
    graph: SyntheticGraph,
    intent_a: Intent | None,
    intent_b: Intent | None,
    route_a: RouteResult | None,
    route_b: RouteResult | None,
    tau: float = 0.05,
) -> tuple[bool, int, float | None, str]:
    """Evaluate DARC decision gate: g = h or (delta_U > tau).

    Returns: (triggered, h, delta_U, trigger_reason)
    """
    h = compute_protection_trigger(intent_a, intent_b, route_a, route_b)
    if h == 1:
        if intent_a is None or intent_b is None:
            reason = "h_invalid_intent"
        elif extract_structure(intent_a) != extract_structure(intent_b):
            reason = "h_structure_mismatch"
        elif route_a is None or route_b is None or not route_a.is_valid or not route_b.is_valid:
            reason = "h_infeasible_route"
        else:
            reason = "h_coverage_mismatch"
        return True, 1, None, reason

    delta_u = compute_cross_utility_delta(graph, intent_a, intent_b, route_a, route_b)
    if delta_u is not None and delta_u > tau:
        return True, 0, delta_u, "utility_discrepancy"

    return False, 0, delta_u, "no_trigger"


def resolve_review_fallback(
    review_intent: Intent | None,
    candidate_a: Intent | None,
    candidate_b: Intent | None,
) -> tuple[Intent | None, str]:
    """Fallback chain: review -> A -> B -> None."""
    if review_intent is not None:
        return review_intent, "adopted_review"
    if candidate_a is not None:
        return candidate_a, "fallback_to_A"
    if candidate_b is not None:
        return candidate_b, "fallback_to_B"
    return None, "all_candidates_invalid"


def intent_distance(i1: Intent, i2: Intent) -> float:
    """Distance between two valid intents for B1 medoid calculation.

    dist(c1, c2) = I(S1 != S2) + I(T1 != T2) + I(closure(D1) != closure(D2)) + |w1 - w2|
    """
    d_s = 1.0 if tuple(sorted(i1.pois)) != tuple(sorted(i2.pois)) else 0.0
    d_t = 1.0 if i1.time_limit != i2.time_limit else 0.0
    d_d = 1.0 if closure(i1.dependencies) != closure(i2.dependencies) else 0.0
    d_w = abs(i1.quality_weight - i2.quality_weight)
    return d_s + d_t + d_d + d_w


def select_medoid(candidates: list[tuple[str, Intent | None]]) -> tuple[Intent | None, str]:
    """Select medoid among valid candidates in [A, A2, A3].

    Ties broken by order in candidates.
    Returns: (selected_intent, chosen_label)
    """
    valid = [(label, intent) for label, intent in candidates if intent is not None]
    if not valid:
        return None, "no_valid_candidate"
    if len(valid) == 1:
        return valid[0][1], valid[0][0]

    best_label = valid[0][0]
    best_intent = valid[0][1]
    best_total_dist = math.inf

    for label_i, intent_i in valid:
        total_dist = sum(intent_distance(intent_i, intent_j) for _, intent_j in valid)
        if total_dist < best_total_dist - 1e-9:
            best_total_dist = total_dist
            best_label = label_i
            best_intent = intent_i

    return best_intent, best_label


def stable_pseudo_random(seed: int, group_id: str, utterance_id: str) -> float:
    """Deterministic, thread-independent pseudo-random float in [0, 1)."""
    key = f"{seed}_{group_id}_{utterance_id}".encode("utf-8")
    h = hashlib.sha256(key).hexdigest()
    # Use first 8 hex characters (32 bits)
    val = int(h[:8], 16)
    return val / float(0xFFFFFFFF)


def execute_method_decision(
    method: str,
    candidates: dict[str, Intent | None],
    routes: dict[str, RouteResult | None],
    graph: SyntheticGraph,
    solver: ExactRouteSolver,
    tau: float = 0.05,
    tau_sem: float = 0.1,
    p_review: float = 0.5,
    seed: int = 20260906,
    group_id: str = "group_000",
    utterance_id: str = "utt_000",
) -> tuple[Intent | None, RouteResult | None, dict[str, Any]]:
    """Execute decision rule for one of the methods (B0 to B6, Ours).

    Methods:
    - B0: Single A (1 call)
    - B1: Medoid of A, A2, A3 (3 calls)
    - B2: Generates A and B, always outputs A (2 calls, output == B0)
    - B3: Protection h, else review with prob p (2 + q calls)
    - B4: Protection h or |wA - wB| > tau_sem (2 + q calls)
    - B5: Only protection h (2 + q calls)
    - B6: Always review after A and B (3 calls)
    - Ours: Protection h or delta_U > tau (2 + q calls)

    Returns: (chosen_intent, chosen_route, meta_dict)
    """
    cand_a = candidates.get("A")
    cand_b = candidates.get("B")
    cand_rev = candidates.get("review")
    cand_a2 = candidates.get("A2")
    cand_a3 = candidates.get("A3")

    route_a = routes.get("A")
    route_b = routes.get("B")

    meta: dict[str, Any] = {
        "method": method,
        "calls_used": 0,
        "review_triggered": False,
        "trigger_reason": "none",
        "h": 0,
        "delta_u": None,
        "chosen_source": "",
    }

    # B0: Single A
    if method == "B0":
        meta["calls_used"] = 1
        meta["chosen_source"] = "A"
        return cand_a, route_a, meta

    # B1: Medoid of A, A2, A3
    elif method == "B1":
        meta["calls_used"] = 3
        pool = [("A", cand_a), ("A2", cand_a2), ("A3", cand_a3)]
        chosen, label = select_medoid(pool)
        meta["chosen_source"] = label
        chosen_route = routes.get(label)
        if chosen is not None and chosen_route is None:
            chosen_route = solver.solve(**chosen.solver_args())
        return chosen, chosen_route, meta

    # B2: Generate A and B, always output A (control check: must match B0 exactly)
    elif method == "B2":
        meta["calls_used"] = 2
        meta["chosen_source"] = "A"
        return cand_a, route_a, meta

    # B6: Always review
    elif method == "B6":
        meta["calls_used"] = 3
        meta["review_triggered"] = True
        meta["trigger_reason"] = "always_review"
        chosen, source = resolve_review_fallback(cand_rev, cand_a, cand_b)
        meta["chosen_source"] = source
        chosen_route = solver.solve(**chosen.solver_args()) if chosen is not None else None
        return chosen, chosen_route, meta

    # Gated methods: B3, B4, B5, Ours
    h = compute_protection_trigger(cand_a, cand_b, route_a, route_b)
    meta["h"] = h
    delta_u = compute_cross_utility_delta(graph, cand_a, cand_b, route_a, route_b)
    meta["delta_u"] = delta_u

    triggered = False
    reason = "no_trigger"

    if h == 1:
        triggered = True
        reason = "protection_h"
    else:
        if method == "B5":
            # Only protection h
            triggered = False
            reason = "no_trigger_b5_only_h"
        elif method == "B4":
            # Protection h or semantic weight difference > tau_sem
            diff_w = abs(cand_a.quality_weight - cand_b.quality_weight) if cand_a and cand_b else 0.0
            if diff_w > tau_sem:
                triggered = True
                reason = "weight_difference"
            else:
                reason = "no_trigger_b4"
        elif method == "B3":
            # Protection h or random probability p
            rand_val = stable_pseudo_random(seed, group_id, utterance_id)
            if rand_val < p_review:
                triggered = True
                reason = "random_probability"
            else:
                reason = "no_trigger_b3"
        elif method in {"Ours", "DARC"}:
            # Protection h or delta_U > tau
            if delta_u is not None and delta_u > tau:
                triggered = True
                reason = "utility_discrepancy"
            else:
                reason = "no_trigger_darc"
        else:
            raise ValueError(f"Unknown method: {method}")

    meta["review_triggered"] = triggered
    meta["trigger_reason"] = reason
    meta["calls_used"] = 3 if triggered else 2

    if triggered:
        chosen, source = resolve_review_fallback(cand_rev, cand_a, cand_b)
        meta["chosen_source"] = source
        chosen_route = solver.solve(**chosen.solver_args()) if chosen is not None else None
        return chosen, chosen_route, meta
    else:
        # Not triggered: adopt A if valid, else B, else None
        if cand_a is not None:
            return cand_a, route_a, meta
        elif cand_b is not None:
            return cand_b, route_b, meta
        else:
            return None, None, meta
