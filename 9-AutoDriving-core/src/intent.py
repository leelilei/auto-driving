"""Strict intent boundary; normalize known aliases, never erase unknown constraints."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from src.graph import POI_CATEGORIES


def category(value):
    if not isinstance(value, str):
        raise ValueError("POI category must be a string")
    result = value.strip().lower().replace(" ", "_")
    if result not in POI_CATEGORIES:
        raise ValueError(f"Unknown POI category: {value!r}")
    return result


def deadline(value):
    if value is None or value == "None":
        return None
    if isinstance(value, str):
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", value)
        if not match:
            raise ValueError("Deadline must be HH:MM or minutes")
        hour, minute = map(int, match.groups())
        if minute >= 60 or hour > 24 or (hour == 24 and minute != 0):
            raise ValueError("Invalid clock time")
        value = hour * 60 + minute
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 1440:
        raise ValueError("Deadline outside [0,1440] minutes")
    return value


def closure(edges):
    reach = set(map(tuple, edges))
    while True:
        updated = reach | {(a, d) for a, b in reach for c, d in reach if b == c}
        if updated == reach:
            return tuple(sorted(reach))
        reach = updated


@dataclass(frozen=True)
class Intent:
    pois: tuple[str, ...]
    time_limit: int | None
    dependencies: tuple[tuple[str, str], ...]
    quality_weight: float

    @classmethod
    def parse(cls, data):
        if not isinstance(data, dict):
            raise ValueError("Intent must be an object")
        required = {"pois", "time_limit", "dependencies", "quality_weight"}
        if not required <= data.keys():
            raise ValueError("Missing intent fields")
        if not isinstance(data["pois"], (list, tuple)) or not isinstance(data["dependencies"], (list, tuple)):
            raise ValueError("POIs and dependencies must be lists or tuples")
        pois = tuple(sorted({category(p) for p in data["pois"]}))
        deps = []
        for pair in data["dependencies"]:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("Invalid dependency pair")
            a, b = map(category, pair)
            if a not in pois or b not in pois:
                raise ValueError("Dependency endpoint absent from requested POIs")
            deps.append((a, b))
        if any(a == b for a, b in closure(deps)):
            raise ValueError("Cyclic dependencies")
        w = data["quality_weight"]
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or not 0 <= w <= 1:
            raise ValueError("Invalid quality weight")
        if "distance_weight" in data:
            dw = data["distance_weight"]
            if isinstance(dw, bool) or not isinstance(dw, (int, float)) or not math.isfinite(dw) or abs(w + dw - 1) > 1e-6:
                raise ValueError("Weights must sum to one")
        return cls(pois, deadline(data["time_limit"]), tuple(sorted(set(deps))), float(w))

    def solver_args(self):
        return {"requested_pois": list(self.pois), "time_limit": self.time_limit,
                "dependencies": list(self.dependencies), "quality_weight": self.quality_weight}
