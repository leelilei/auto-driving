"""Controlled synthetic POI graph environment for DARC-Route.

Per Proposal v4 Section 6.2:
- Fixed 10 POIs: 5 categories x 2 candidates each
  (shopping_mall, supermarket, pharmacy, bank, library)
- Origin and Destination (Home / Start-End node)
- 2D Euclidean coordinates, fixed driving speed (e.g., 30 km/h = 0.5 km/min)
- Attributes per POI: coordinates, normalized quality Q(poi), open_time, close_time, stay_duration
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

POI_CATEGORIES = ["shopping_mall", "supermarket", "pharmacy", "bank", "library"]

# Default stay duration in minutes per category
DEFAULT_STAY_DURATIONS = {
    "shopping_mall": 60,
    "supermarket": 40,
    "pharmacy": 15,
    "bank": 30,
    "library": 45,
}


@dataclass(frozen=True)
class POI:
    id: str
    category: str
    x: float
    y: float
    rating: float  # raw rating, e.g. 3.0 - 5.0
    reviews: int   # raw review count, e.g. 10 - 1000
    quality: float # normalized quality in [0, 1]
    open_time: int # minutes from 00:00 (e.g. 540 = 09:00)
    close_time: int # minutes from 00:00 (e.g. 1260 = 21:00)
    stay_duration: int # minutes


@dataclass
class SyntheticGraph:
    graph_id: str
    origin: tuple[float, float]
    destination: tuple[float, float]
    departure_time: int # minutes from 00:00 (default 540 = 09:00)
    speed_km_h: float   # default 30.0 km/h
    pois: list[POI]
    max_edge_distance: float

    @property
    def speed_km_min(self) -> float:
        return self.speed_km_h / 60.0

    def get_poi(self, poi_id: str) -> POI | None:
        for p in self.pois:
            if p.id == poi_id:
                return p
        return None

    def travel_distance(self, p1: tuple[float, float], p2: tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def travel_time(self, p1: tuple[float, float], p2: tuple[float, float]) -> float:
        dist = self.travel_distance(p1, p2)
        return dist / self.speed_km_min

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "origin": list(self.origin),
            "destination": list(self.destination),
            "departure_time": self.departure_time,
            "speed_km_h": self.speed_km_h,
            "max_edge_distance": self.max_edge_distance,
            "pois": [asdict(p) for p in self.pois],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SyntheticGraph":
        pois = [POI(**p) for p in data["pois"]]
        return cls(
            graph_id=data["graph_id"],
            origin=tuple(data["origin"]),
            destination=tuple(data["destination"]),
            departure_time=data["departure_time"],
            speed_km_h=data["speed_km_h"],
            pois=pois,
            max_edge_distance=data["max_edge_distance"],
        )

    def save(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> "SyntheticGraph":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def generate_synthetic_graph(
    graph_id: str = "graph_default_001",
    seed: int = 42,
    area_km: float = 10.0,
    departure_time: int = 540, # 09:00 AM
    speed_km_h: float = 30.0,
) -> SyntheticGraph:
    """Generate a reproducible, controlled 10-POI synthetic graph."""
    rng = random.Random(seed)

    origin = (area_km / 2.0, area_km / 2.0)
    destination = (area_km / 2.0, area_km / 2.0) # start and end at origin (round-trip)

    pois = []
    # Two candidates per category: one closer/lower-quality, one farther/higher-quality (trade-off)
    for cat in POI_CATEGORIES:
        stay = DEFAULT_STAY_DURATIONS[cat]

        # Candidate 1: Closer to center (r = 1.0 - 3.5 km)
        angle1 = rng.uniform(0, 2 * math.pi)
        r1 = rng.uniform(1.0, 3.5)
        x1 = origin[0] + r1 * math.cos(angle1)
        y1 = origin[1] + r1 * math.sin(angle1)
        rating1 = round(rng.uniform(3.5, 4.2), 1)
        reviews1 = rng.randint(30, 200)

        # Candidate 2: Farther from center (r = 3.5 - 6.0 km), higher quality
        angle2 = rng.uniform(0, 2 * math.pi)
        r2 = rng.uniform(3.5, 6.0)
        x2 = origin[0] + r2 * math.cos(angle2)
        y2 = origin[1] + r2 * math.sin(angle2)
        rating2 = round(rng.uniform(4.3, 5.0), 1)
        reviews2 = rng.randint(250, 950)

        # Store open hours: 09:00 - 21:00 (540 to 1260), pharmacy/supermarket may open earlier
        open_time = 540 if cat not in {"supermarket", "pharmacy"} else 480  # 08:00
        close_time = 1260 if cat not in {"bank", "library"} else 1080       # Bank/Library close at 18:00

        for cand_idx, (x, y, rat, rev) in enumerate([(x1, y1, rating1, reviews1), (x2, y2, rating2, reviews2)], start=1):
            # Quality formula: 0.5 * (rating-3.0)/2.0 + 0.5 * log(reviews)/log(1000)
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

    # Compute max edge distance across all points (origin + 10 POIs)
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
        departure_time=departure_time,
        speed_km_h=speed_km_h,
        pois=pois,
        max_edge_distance=max_d,
    )
