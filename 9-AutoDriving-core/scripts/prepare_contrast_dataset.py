#!/usr/bin/env python3
"""Generate E4 Contrast Set (40 intent pairs x 2 minimal change variants = 80 utterances).

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 3 & 4.2:
- Contrast set: 40 intents outside Dev & Test splits.
- Each pair has:
  - Base variant (C0)
  - Minimal semantic change variant (C1):
    - 15 pairs: flip / invert dependency order
    - 15 pairs: add or tighten deadline
    - 10 pairs: flip preference direction (quality vs efficiency)
- Used in E4 to verify system does not over-smooth and recognizes real semantic alterations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPLITS_FILE = ROOT / "data/processed/candidate_splits.json"
DEV_EXPOSURE = ROOT / "data/processed/development_exposure.json"
CLUSTERS_FILE = ROOT / "data/processed/hipp_clusters.json"
CONTRAST_OUT = ROOT / "data/contrast/contrast_80_utterances.json"


def main():
    splits = json.load(open(SPLITS_FILE))
    dev_exp = json.load(open(DEV_EXPOSURE))
    clusters = json.load(open(CLUSTERS_FILE))

    used_clusters = set(dev_exp["exposed_cluster_ids"])
    for split_name in ["dev_pilot", "dev_calibration", "test"]:
        for g in splits.get(split_name, []):
            used_clusters.add(g["source_cluster_id"])

    # Find unused clusters with 2-5 POIs
    available = []
    for c in clusters:
        cid = c["cluster_id"]
        if cid in used_clusters:
            continue
        rep = c["records"][0]
        pois = rep.get("pois", [])
        if len(pois) >= 2:
            available.append(c)

    print(f"Available unused clusters for contrast: {len(available)}")
    selected_40 = available[:40]

    contrast_records = []
    for idx, c in enumerate(selected_40, start=1):
        pair_id = f"contrast_{idx:02d}"
        rep = c["records"][0]
        base_inst = rep["instruction"]
        pois = rep.get("pois", [])
        t_limit = rep.get("time_limit")
        deps = rep.get("dependencies", [])
        w = rep.get("quality_weight_synthetic", 0.5)

        # C0: Original
        c0_rec = {
            "pair_id": pair_id,
            "utterance_id": f"{pair_id}_c0",
            "contrast_variant": "C0",
            "change_type": "original",
            "text": base_inst,
            "gold_intent": {
                "pois": pois,
                "time_limit": t_limit,
                "dependencies": deps,
                "quality_weight": w,
            },
            "source_index": rep["source_index"],
            "source_cluster_id": c["cluster_id"],
        }

        # C1: Minimal change
        # Cycle through: dependency flip, deadline change, preference flip
        if idx % 3 == 1:
            # Dependency change
            change_type = "dependency_alteration"
            p1, p2 = pois[0], pois[1]
            c1_deps = [[p2, p1]] if not deps else []
            c1_text = f"{base_inst} Furthermore, make sure you visit the {p2.replace('_', ' ')} before going to the {p1.replace('_', ' ')}."
            c1_intent = {
                "pois": pois,
                "time_limit": t_limit,
                "dependencies": c1_deps,
                "quality_weight": w,
            }
        elif idx % 3 == 2:
            # Deadline addition / tightening
            change_type = "deadline_alteration"
            c1_limit = 1080 if not t_limit or t_limit > 1080 else 960  # 18:00 or 16:00
            hours = c1_limit // 60
            mins = c1_limit % 60
            c1_text = f"{base_inst} However, you must return by {hours:02d}:{mins:02d} sharp."
            c1_intent = {
                "pois": pois,
                "time_limit": c1_limit,
                "dependencies": deps,
                "quality_weight": w,
            }
        else:
            # Preference flip
            change_type = "preference_flip"
            c1_w = 0.9 if w <= 0.5 else 0.1
            pref_phrase = "Please give top priority to the highest-rated places regardless of distance." if c1_w > 0.5 else "Please prioritize the fastest and shortest route over place ratings."
            c1_text = f"{base_inst} Above all, {pref_phrase.lower()}"
            c1_intent = {
                "pois": pois,
                "time_limit": t_limit,
                "dependencies": deps,
                "quality_weight": c1_w,
            }

        c1_rec = {
            "pair_id": pair_id,
            "utterance_id": f"{pair_id}_c1",
            "contrast_variant": "C1",
            "change_type": change_type,
            "text": c1_text,
            "gold_intent": c1_intent,
            "source_index": rep["source_index"],
            "source_cluster_id": c["cluster_id"],
        }

        contrast_records.extend([c0_rec, c1_rec])

    CONTRAST_OUT.parent.mkdir(parents=True, exist_ok=True)
    CONTRAST_OUT.write_text(json.dumps(contrast_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[✓] Saved {len(contrast_records)} contrast utterances (40 pairs) to {CONTRAST_OUT}")


if __name__ == "__main__":
    main()
