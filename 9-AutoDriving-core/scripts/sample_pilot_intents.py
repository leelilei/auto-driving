#!/usr/bin/env python3
"""Sample 20 stratified pilot intent groups from preprocessed HIPP clusters.

Per Proposal v4 Section 5.2:
- Stratified across POI count (2, 3, 4, 5 POIs)
- Balanced across time limits, dependencies, and preference directions
- Seed-fixed, reproducible selection
"""

import json
import random
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]  # 9-AutoDriving-core
CLUSTERS_FILE = ROOT_DIR / "data" / "processed" / "hipp_clusters.json"
PILOT_OUTPUT_FILE = ROOT_DIR / "data" / "pilot" / "pilot_intents_raw.json"


def main():
    if not CLUSTERS_FILE.exists():
        raise FileNotFoundError(f"Clusters file not found at {CLUSTERS_FILE}")

    clusters = json.loads(CLUSTERS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(clusters)} semantic clusters.")

    # Filter out 1-POI clusters for route planning (routes need at least 2 POIs to have ordering/dependencies)
    valid_clusters = [c for c in clusters if c["intent_key"]["poi_count"] >= 2]
    print(f"Clusters with >= 2 POIs: {len(valid_clusters)}")

    # Target counts:
    # 2 POIs: 4
    # 3 POIs: 6
    # 4 POIs: 5
    # 5 POIs: 5
    target_poi_counts = {2: 4, 3: 6, 4: 5, 5: 5}
    rng = random.Random(42)

    by_poi = {k: [] for k in target_poi_counts}
    for c in valid_clusters:
        n = c["intent_key"]["poi_count"]
        if n in by_poi:
            by_poi[n].append(c)

    selected_clusters = []

    for poi_count, target_num in target_poi_counts.items():
        candidates = list(by_poi[poi_count])
        # Sort candidates deterministically to ensure reproducibility before random shuffle
        candidates.sort(key=lambda x: (
            x["intent_key"]["direction"],
            x["intent_key"]["time_limit"] is not None,
            len(x["intent_key"]["closure"]) > 0,
            x["cluster_id"]
        ))
        rng.shuffle(candidates)

        # Pick diverse candidates across direction, deadline, and dependencies
        picked = []
        seen_combos = set()
        for c in candidates:
            k = c["intent_key"]
            combo = (k["direction"], k["time_limit"] is not None, len(k["closure"]) > 0)
            if combo not in seen_combos:
                seen_combos.add(combo)
                picked.append(c)
                if len(picked) == target_num:
                    break
        # If still need more, pick remaining
        if len(picked) < target_num:
            for c in candidates:
                if c not in picked:
                    picked.append(c)
                    if len(picked) == target_num:
                        break

        selected_clusters.extend(picked)

    print(f"Selected {len(selected_clusters)} pilot intent groups.")

    # Format into pilot raw records
    pilot_records = []
    for g_idx, c in enumerate(selected_clusters, start=1):
        k = c["intent_key"]
        rep = c["records"][0]
        pilot_records.append({
            "pilot_group_id": f"pilot_{g_idx:02d}",
            "source_cluster_id": c["cluster_id"],
            "source_index": rep["source_index"],
            "base_instruction": rep["instruction"],
            "gold_intent": {
                "pois": k["pois"],
                "poi_count": k["poi_count"],
                "time_limit": k["time_limit"],
                "dependencies": rep["dependencies"],
                "dependency_closure": k["closure"],
                "preference_direction": k["direction"],
                "quality_weight_synthetic": rep["quality_weight"],
                "distance_weight_synthetic": rep["distance_weight"],
            },
            "cluster_size": c["member_count"],
        })

    PILOT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PILOT_OUTPUT_FILE.write_text(json.dumps(pilot_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Saved pilot dataset to {PILOT_OUTPUT_FILE.relative_to(ROOT_DIR.parent)}")

    # Summary
    poi_c = Counter(p["gold_intent"]["poi_count"] for p in pilot_records)
    dir_c = Counter(p["gold_intent"]["preference_direction"] for p in pilot_records)
    time_c = Counter(p["gold_intent"]["time_limit"] is not None for p in pilot_records)
    dep_c = Counter(len(p["gold_intent"]["dependency_closure"]) > 0 for p in pilot_records)

    print("\nPilot Stratification Summary:")
    print("  POI counts:", dict(poi_c))
    print("  Directions:", dict(dir_c))
    print("  Has deadline:", dict(time_c))
    print("  Has dependencies:", dict(dep_c))


if __name__ == "__main__":
    main()
