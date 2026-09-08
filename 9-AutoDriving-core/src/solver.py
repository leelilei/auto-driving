"""Exact deterministic route solver for DARC-Route.

Per Proposal v4 Section 6.3:
- Exhaustively evaluates all candidate routes on the controlled 10-POI graph.
- First satisfies hard constraints (closing times, deadline T, dependencies D).
- Then maximizes requested POI coverage.
- Then maximizes controlled quality-distance utility:
    U_w(r) = w * Q(r) - (1-w) * D_bar(r)
- Deterministic tie-breaking on (coverage, utility, lexicographical POI IDs).
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any

from src.graph import POI, POI_CATEGORIES, SyntheticGraph


@dataclass(frozen=True)
class RouteResult:
    poi_ids: tuple[str, ...]
    categories: tuple[str, ...]
    coverage: int
    is_full_coverage: bool
    is_valid: bool
    utility: float
    total_distance: float
    total_time: float
    final_arrival_time: int
    status: str
    details: dict[str, Any] = field(default_factory=dict)
    raw_utility: float = 0.0


def has_cycle(categories: list[str], dependencies: list[tuple[str, str]]) -> bool:
    """Check if directed dependencies contain a cycle among categories."""
    adj = {c: set() for c in categories}
    in_degree = {c: 0 for c in categories}
    for u, v in dependencies:
        if u in adj and v in adj:
            if v not in adj[u]:
                adj[u].add(v)
                in_degree[v] += 1

    queue = [c for c in categories if in_degree[c] == 0]
    visited_count = 0
    while queue:
        curr = queue.pop(0)
        visited_count += 1
        for nxt in adj[curr]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)
    return visited_count < len(categories)


class ExactRouteSolver:
    def __init__(self, graph: SyntheticGraph):
        self.graph = graph
        # Map category -> list of POIs in this graph
        self.cat_to_pois: dict[str, list[POI]] = {cat: [] for cat in POI_CATEGORIES}
        for p in graph.pois:
            if p.category in self.cat_to_pois:
                self.cat_to_pois[p.category].append(p)

    def evaluate_sequence(
        self,
        poi_seq: tuple[POI, ...],
        time_limit: int | None,
        dependencies: list[tuple[str, str]],
        quality_weight: float,
    ) -> tuple[bool, float, float, float, int, str]:
        """Simulate execution of a specific sequence of POIs.

        Returns: (is_valid, utility, total_dist, total_time, final_arr_time, reason)
        """
        # 1. Dependency check
        visited_cats = [p.category for p in poi_seq]
        cat_pos = {cat: idx for idx, cat in enumerate(visited_cats)}
        for u, v in dependencies:
            if u in cat_pos and v in cat_pos:
                if cat_pos[u] > cat_pos[v]:
                    return False, -1.0, 0.0, 0.0, 0, f"Dependency violated: {u} appeared after {v}"

        # 2. Path simulation
        curr_loc = self.graph.origin
        curr_time = float(self.graph.departure_time)
        total_dist = 0.0

        for poi in poi_seq:
            next_loc = (poi.x, poi.y)
            d = self.graph.travel_distance(curr_loc, next_loc)
            total_dist += d
            arr_time = curr_time + (d / self.graph.speed_km_min)
            start_service = max(arr_time, float(poi.open_time))
            finish_service = start_service + float(poi.stay_duration)

            if finish_service > poi.close_time + 1e-4:
                return False, -1.0, total_dist, 0.0, int(finish_service), f"Store closed at {poi.id}"

            curr_loc = next_loc
            curr_time = finish_service

        # Travel to destination
        dest_d = self.graph.travel_distance(curr_loc, self.graph.destination)
        total_dist += dest_d
        final_time = curr_time + (dest_d / self.graph.speed_km_min)

        if time_limit is not None and final_time > time_limit + 1e-4:
            return False, -1.0, total_dist, final_time - self.graph.departure_time, int(round(final_time)), f"Exceeded deadline {time_limit}"

        # 3. Utility calculation
        if len(poi_seq) == 0:
            avg_q = 0.0
        else:
            avg_q = sum(p.quality for p in poi_seq) / len(poi_seq)

        # Scale distance: (5 + 1) * max_edge_distance
        scale_d = 6.0 * self.graph.max_edge_distance
        d_bar = total_dist / scale_d if scale_d > 0 else 0.0

        w = max(0.0, min(1.0, quality_weight))
        utility = w * avg_q - (1.0 - w) * d_bar

        total_duration = final_time - self.graph.departure_time
        return True, utility, total_dist, total_duration, int(round(final_time)), "OK"

    def solve(
        self,
        requested_pois: list[str],
        time_limit: int | None = None,
        dependencies: list[tuple[str, str]] | None = None,
        quality_weight: float = 0.5,
    ) -> RouteResult:
        """Find the globally optimal feasible route for the structured intent."""
        from src.intent import Intent
        dependencies = [] if dependencies is None else dependencies
        try:
            intent = Intent.parse({"pois": requested_pois, "time_limit": time_limit,
                                   "dependencies": dependencies, "quality_weight": quality_weight})
        except ValueError as exc:
            return RouteResult((), (), 0, False, False, -1.0, 0.0, 0.0,
                               self.graph.departure_time,
                               "CYCLE_DEPENDENCY_ERROR" if "Cyclic" in str(exc) else "INVALID_INTENT",
                               {"reason": str(exc)},
                               raw_utility=-1.0)
        valid_cats = list(intent.pois)
        dependencies = list(intent.dependencies)
        time_limit = intent.time_limit
        quality_weight = intent.quality_weight
        num_requested = len(valid_cats)

        if num_requested == 0:
            # Direct routes must also satisfy the deadline.
            ok, u, d, dur, fin, reason = self.evaluate_sequence((), time_limit, dependencies, quality_weight)
            return RouteResult(
                poi_ids=(),
                categories=(),
                coverage=0,
                is_full_coverage=ok,
                is_valid=ok,
                utility=round(u, 4),
                total_distance=round(d, 3),
                total_time=round(dur, 1),
                final_arrival_time=fin,
                status="EMPTY_REQUEST_DIRECT" if ok else "NO_FEASIBLE_ROUTE",
                details={"reason": reason},
                raw_utility=u if ok else -1.0,
            )

        # Cycle check in dependencies
        if has_cycle(valid_cats, dependencies):
            return RouteResult(
                poi_ids=(),
                categories=(),
                coverage=0,
                is_full_coverage=False,
                is_valid=False,
                utility=-1.0,
                total_distance=0.0,
                total_time=0.0,
                final_arrival_time=self.graph.departure_time,
                status="CYCLE_DEPENDENCY_ERROR",
                details={"reason": "Circular dependency detected among requested POIs"},
                raw_utility=-1.0,
            )

        best_result: RouteResult | None = None
        best_utility = -math.inf
        best_ids: tuple[str, ...] | None = None

        # Search descending from full coverage down to length 1
        for k in range(num_requested, 0, -1):
            for cat_subset in itertools.combinations(valid_cats, k):
                # Candidate choices: for each cat in cat_subset, pick 1 of the 2 candidate POIs
                cand_options = [self.cat_to_pois[c] for c in cat_subset]
                for chosen_pois in itertools.product(*cand_options):
                    # Permutations of order
                    for perm in itertools.permutations(chosen_pois):
                        is_val, u, dist, dur, fin_arr, reason = self.evaluate_sequence(
                            perm, time_limit, dependencies, quality_weight
                        )
                        if is_val:
                            cov = len(perm)
                            poi_ids = tuple(p.id for p in perm)
                            if (u > best_utility + 1e-9 or
                                (abs(u - best_utility) <= 1e-9 and (best_ids is None or poi_ids < best_ids))):
                                best_utility, best_ids = u, poi_ids
                                best_result = RouteResult(
                                    poi_ids=poi_ids,
                                    categories=tuple(p.category for p in perm),
                                    coverage=cov,
                                    is_full_coverage=(cov == num_requested),
                                    is_valid=True,
                                    utility=round(u, 4),
                                    total_distance=round(dist, 3),
                                    total_time=round(dur, 1),
                                    final_arrival_time=fin_arr,
                                    status="SUCCESS" if cov == num_requested else "PARTIAL_COVERAGE",
                                    details={"reason": reason, "evaluated_pois": poi_ids},
                                    raw_utility=u,
                                )
            # If we found at least one feasible route with coverage k, we do not accept lower coverage
            if best_result is not None:
                break

        if best_result is None:
            # Completely infeasible
            return RouteResult(
                poi_ids=(),
                categories=(),
                coverage=0,
                is_full_coverage=False,
                is_valid=False,
                utility=-1.0,
                total_distance=0.0,
                total_time=0.0,
                final_arrival_time=self.graph.departure_time,
                status="NO_FEASIBLE_ROUTE",
                details={"reason": "No candidate route satisfies time or dependency constraints"},
                raw_utility=-1.0,
            )

        return best_result
