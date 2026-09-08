"""Controlled synthetic graph scenario profiles for DARC-Route.

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 5.1:
Three scenario distributions:
1. 'loose' (default/current):
   - Departure 09:00 (540 min), bank/library close at 18:00 (1080 min), others at 21:00 (1260 min).
   - Generous time windows for testing feasibility and basic routing.
2. 'time_sensitive':
   - Departure 14:00 (840 min), bank/library close at 17:00 (1020 min), others at 19:00 (1140 min).
   - Speed 25 km/h, tighter closing hours and deadlines.
3. 'tradeoff':
   - Sharp contrast between close/low-quality and far/high-quality POIs.
   - Candidate 1: r=1.0-2.5 km, quality~0.2-0.35.
   - Candidate 2: r=5.0-8.0 km, quality~0.8-0.95.
   - Distinct trade-off between travel distance and POI quality.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.graph import POI, POI_CATEGORIES, DEFAULT_STAY_DURATIONS, SyntheticGraph


SCENARIO_PROFILES = {
    "loose": {
        "description": "Loose time windows, departure 09:00, bank/library close 18:00, others 21:00",
        "departure_time": 540,
        "speed_km_h": 30.0,
        "area_km": 10.0,
        "early_open": 480,
        "std_open": 540,
        "early_close": 1080,
        "std_close": 1260,
    },
    "time_sensitive": {
        "description": "Afternoon departure 14:00, early closing 17:00/19:00, speed 25 km/h",
        "departure_time": 840,
        "speed_km_h": 25.0,
        "area_km": 10.0,
        "early_open": 840,
        "std_open": 840,
        "early_close": 1020,  # 17:00
        "std_close": 1140,   # 19:00
    },
    "tradeoff": {
        "description": "Sharp distance vs quality trade-off, area 15 km",
        "departure_time": 540,
        "speed_km_h": 30.0,
        "area_km": 15.0,
        "early_open": 480,
        "std_open": 540,
        "early_close": 1080,
        "std_close": 1260,
    },
}


def generate_scenario_graph(
    graph_id: str,
    scenario_type: str = "loose",
    seed: int = 42,
) -> SyntheticGraph:
    """Generate a controlled SyntheticGraph configured for a specific scenario type."""
    if scenario_type not in SCENARIO_PROFILES:
        raise ValueError(f"Unknown scenario profile: {scenario_type}. Expected one of {list(SCENARIO_PROFILES.keys())}")

    prof = SCENARIO_PROFILES[scenario_type]
    rng = random.Random(seed)

    area_km = prof["area_km"]
    origin = (area_km / 2.0, area_km / 2.0)
    destination = (area_km / 2.0, area_km / 2.0)
    dep_time = prof["departure_time"]
    speed = prof["speed_km_h"]

    pois = []
    for cat in POI_CATEGORIES:
        stay = DEFAULT_STAY_DURATIONS[cat]

        if scenario_type == "tradeoff":
            # Candidate 1: close, low quality
            angle1 = rng.uniform(0, 2 * math.pi)
            r1 = rng.uniform(1.0, 2.5)
            x1 = origin[0] + r1 * math.cos(angle1)
            y1 = origin[1] + r1 * math.sin(angle1)
            rating1 = round(rng.uniform(3.0, 3.6), 1)
            reviews1 = rng.randint(15, 60)

            # Candidate 2: far, high quality
            angle2 = rng.uniform(0, 2 * math.pi)
            r2 = rng.uniform(5.0, 7.5)
            x2 = origin[0] + r2 * math.cos(angle2)
            y2 = origin[1] + r2 * math.sin(angle2)
            rating2 = round(rng.uniform(4.7, 5.0), 1)
            reviews2 = rng.randint(600, 1000)
        else:
            # Standard two-tier candidate distribution
            angle1 = rng.uniform(0, 2 * math.pi)
            r1 = rng.uniform(1.0, 3.5)
            x1 = origin[0] + r1 * math.cos(angle1)
            y1 = origin[1] + r1 * math.sin(angle1)
            rating1 = round(rng.uniform(3.5, 4.2), 1)
            reviews1 = rng.randint(30, 200)

            angle2 = rng.uniform(0, 2 * math.pi)
            r2 = rng.uniform(3.5, 6.0)
            x2 = origin[0] + r2 * math.cos(angle2)
            y2 = origin[1] + r2 * math.sin(angle2)
            rating2 = round(rng.uniform(4.3, 5.0), 1)
            reviews2 = rng.randint(250, 950)

        # Store hours based on scenario
        open_time = prof["early_open"] if cat in {"supermarket", "pharmacy"} else prof["std_open"]
        close_time = prof["early_close"] if cat in {"bank", "library"} else prof["std_close"]

        for cand_idx, (x, y, rat, rev) in enumerate([(x1, y1, rating1, reviews1), (x2, y2, rating2, reviews2)], start=1):
            norm_rating = max(0.0, min(1.0, (rat - 3.0) / 2.0))
            norm_reviews = max(0.0, min(1.0, math.log(max(10, rev)) / math.log(1000.0)))
            q = round(0.5 * norm_rating + 0.5 * norm_reviews, 4)

            poi = POI(
                id=f"{cat}_{cand_idx}",
                category=cat,
                x=round(x, 3),
                y=round(y, 3),
                rating=rat,
                reviews=rev,
                quality=q,
                open_time=open_time,
                close_time=close_time,
                stay_duration=stay,
            )
            pois.append(poi)

    all_points = [origin] + [(p.x, p.y) for p in pois]
    max_d = 0.0
    for i in range(len(all_points)):
        for j in range(i + 1, len(all_points)):
            d = math.hypot(all_points[i][0] - all_points[j][0], all_points[i][1] - all_points[j][1])
            if d > max_d:
                max_d = d

    return SyntheticGraph(
        graph_id=graph_id,
        origin=origin,
        destination=destination,
        departure_time=dep_time,
        speed_km_h=speed,
        pois=pois,
        max_edge_distance=max_d,
    )
