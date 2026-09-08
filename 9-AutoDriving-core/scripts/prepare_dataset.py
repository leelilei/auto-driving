#!/usr/bin/env python3
"""Dataset preparation, 200-group candidate partition, 80-utterance pilot construction, and audit materials.

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 4:
- Identifies and excludes all development exposed clusters and intents from Test.
- Generates stratified 200-group candidate split (Dev 40 [Pilot 20, Calibration 20], Test 160).
  Includes 1-category POI scenes to reflect true task diversity.
  Fixed split seed: 20260906.
  Verifies zero cross-split cluster or structural leakage.
- Constructs 20 groups x 4 variants = 80 equivalence utterances for Pilot (V0, V1, V2, V3).
- Generates human review queue (JSON) and fillable review sheet (Markdown) with pending status.
- Highlights specific adjudication cases: pilot_11, pilot_13, pilot_17.
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW_HIPP = ROOT / "data/raw/HIPP.json"
HIPP_CLUSTERS = ROOT / "data/processed/hipp_clusters.json"
PILOT_RAW = ROOT / "data/pilot/pilot_intents_raw.json"

DEV_EXPOSURE_OUT = ROOT / "data/processed/development_exposure.json"
SPLITS_OUT = ROOT / "data/processed/candidate_splits.json"
PILOT_80_OUT = ROOT / "data/pilot/pilot_80_utterances.json"
ANNOTATION_QUEUE_OUT = ROOT / "data/pilot/annotation_pilot_80_review_queue.json"
REVIEW_SHEET_MD = ROOT.parent / "docs/experiments/annotation_pilot_80_review_sheet.md"


# 20 groups x 3 paraphrases (V1, V2, V3) carefully created to maintain strict semantic equivalence
PILOT_PARAPHRASES = {
    "pilot_01": {
        "V1": "You will be stopping by the shopping mall and the supermarket today. Be sure to arrive back by 22:00. Prioritizing travel efficiency, keep the route as short and direct as feasible, and remember to visit the shopping mall prior to the supermarket.",
        "V2": "Ensure your return by 22:00 today after visiting the shopping mall and the supermarket. Because efficiency is paramount, choose the most direct path possible, stopping at the shopping mall before you head to the supermarket.",
        "V3": "Hey, need you to hit the shopping mall and supermarket today and get back by 22:00 sharp. Keep the driving distance minimal to save time, and definitely swing by the shopping mall first before going to the supermarket.",
    },
    "pilot_02": {
        "V1": "Please visit the supermarket and the pharmacy today. Keep a balance between selecting well-rated locations and maintaining route efficiency. Begin your stops at the supermarket prior to going to the pharmacy.",
        "V2": "Your itinerary today covers the supermarket and the pharmacy, starting at the supermarket before heading to the pharmacy. Aim for a balanced trade-off between customer ratings and total route distance.",
        "V3": "Make sure you stop at the supermarket and pharmacy today, starting off at the supermarket then hitting the pharmacy. Try to strike a good balance between decent reviews and not driving too far out of the way.",
    },
    "pilot_03": {
        "V1": "Please stop by the pharmacy and the shopping mall today. Seek a balance between high ratings and efficient travel distance. There is no required sequence between them, so choose whichever order suits you.",
        "V2": "Today you should visit both the shopping mall and the pharmacy in whichever order you prefer, balancing location quality with route efficiency.",
        "V3": "Today go visit the pharmacy and the shopping mall. No strict order needed between the two, just pick what works best while keeping a healthy balance between good ratings and travel efficiency.",
    },
    "pilot_04": {
        "V1": "Make sure to visit the bank and the library today, returning by 18:00. It is crucial to prioritize an efficient, quick route for these stops.",
        "V2": "Please return by 18:00 after stopping at the bank and the library. Focus on minimizing travel distance and keeping the journey as fast as possible.",
        "V3": "Need to stop by the bank and library today and be back before 18:00. Keep it super quick and take the most efficient route possible.",
    },
    "pilot_05": {
        "V1": "Please visit the bank, library, and pharmacy today. Give top priority to locations with the highest ratings, and make sure to visit the bank before the library.",
        "V2": "Today's stops include the bank, library, and pharmacy, going to the bank prior to the library. Focus on maximizing place quality and reviews above all.",
        "V3": "Go to the bank, library, and pharmacy today, making sure you hit the bank before heading to the library. Pick the top-rated spots since quality is the main priority.",
    },
    "pilot_06": {
        "V1": "You must visit the library, supermarket, and bank today, returning by 18:00. Select an efficient route to complete all visits promptly, and stop by the supermarket before going to the bank.",
        "V2": "Please be back by 18:00 after visiting the supermarket, bank, and library. Ensure the supermarket is visited before the bank, and prioritize travel efficiency.",
        "V3": "Got to visit the library, supermarket, and bank today and be back by 18:00. Make sure supermarket comes before the bank, and focus on the fastest, most efficient route.",
    },
    "pilot_07": {
        "V1": "Please visit the library, pharmacy, and supermarket today and return by 17:00. Prioritize locations with high ratings, even if it requires extra driving distance.",
        "V2": "Make sure to return by 17:00 after visiting the library, pharmacy, and supermarket. Quality is the key objective, so choose top-rated spots even if the route is longer.",
        "V3": "Head to the library, pharmacy, and supermarket today and be back by 17:00. Don't worry if the route takes a bit longer, just make sure to pick the best-rated places.",
    },
    "pilot_08": {
        "V1": "Please stop by the library, shopping mall, and supermarket today. Balance good ratings with route efficiency, and ensure you visit the shopping mall before the supermarket.",
        "V2": "Today's destination categories are the library, shopping mall, and supermarket. Head to the shopping mall prior to the supermarket, maintaining a balance between quality and distance.",
        "V3": "Let's visit the library, shopping mall, and supermarket today. Hit the shopping mall before heading to the supermarket, and keep a solid balance between good ratings and efficient travel.",
    },
    "pilot_09": {
        "V1": "Please visit the library, pharmacy, and bank today. Prioritize an efficient route with minimal travel time, and be sure to go to the library before heading to the pharmacy.",
        "V2": "Today you need to stop at the library, pharmacy, and bank, visiting the library before the pharmacy. Focus on route efficiency and minimizing driving time.",
        "V3": "Stop by the library, pharmacy, and bank today. Make sure library comes before pharmacy, and keep the route as fast and direct as possible.",
    },
    "pilot_10": {
        "V1": "The schedule today is to visit the supermarket, library, and pharmacy. Please choose a route that maximizes efficiency.",
        "V2": "Please visit the library, supermarket, and pharmacy today, focusing primarily on travel efficiency and directness.",
        "V3": "Plan for today is visiting the supermarket, library, and pharmacy. Just aim for the most efficient route you can find.",
    },
    "pilot_11": {
        "V1": "You need to stop by the library, shopping mall, supermarket, and bank today. While balancing worthwhile places and reasonable travel time, go to the library before the shopping mall, and visit the supermarket before the bank.",
        "V2": "Visit the library, shopping mall, supermarket, and bank today, maintaining a balance between quality and efficiency. Make sure the library precedes the shopping mall, and the supermarket precedes the bank.",
        "V3": "Need you to visit the library, shopping mall, supermarket, and bank today. Be sure to hit the library before the mall and the supermarket before the bank, balancing good places with sensible driving time.",
    },
    "pilot_12": {
        "V1": "Please visit the library, shopping mall, bank, and supermarket today. It is important to balance appealing locations with efficient travel time.",
        "V2": "Today's stops are the library, shopping mall, bank, and supermarket. Seek a balance between high-rated spots and route efficiency.",
        "V3": "Make sure to stop at the library, shopping mall, bank, and supermarket today, keeping a steady balance between place ratings and efficient driving.",
    },
    "pilot_13": {
        "V1": "You will visit the library, shopping mall, pharmacy, and bank today, returning by 23:00. Prioritize an efficient route; start at the library, proceed to the shopping mall, and visit the pharmacy after the mall.",
        "V2": "Be back by 23:00 after visiting the library, shopping mall, pharmacy, and bank. Focus on route efficiency, beginning at the library, then going to the shopping mall, and visiting the pharmacy following the mall.",
        "V3": "Hit the library, shopping mall, pharmacy, and bank today and be back by 23:00. Keep the route efficient, starting off at the library, then the shopping mall, and then the pharmacy after the mall.",
    },
    "pilot_14": {
        "V1": "Please stop by the shopping mall, bank, pharmacy, and library today. Aim to complete all visits efficiently to optimize your route.",
        "V2": "Your stops today are the shopping mall, bank, pharmacy, and library. Focus on route efficiency and minimizing unnecessary distance.",
        "V3": "Go visit the shopping mall, bank, pharmacy, and library today. Try to keep the route as efficient and streamlined as possible.",
    },
    "pilot_15": {
        "V1": "Please visit the library, supermarket, pharmacy, and shopping mall today. There is no specific deadline, but complete them efficiently, making sure to visit the supermarket before the pharmacy.",
        "V2": "Today you are visiting the library, supermarket, pharmacy, and shopping mall, going to the supermarket prior to the pharmacy. Focus on route efficiency.",
        "V3": "Please swing by the library, supermarket, pharmacy, and shopping mall today. No set return time, just keep it efficient and make sure you hit the supermarket before the pharmacy.",
    },
    "pilot_16": {
        "V1": "You need to visit the pharmacy, supermarket, library, shopping mall, and bank today. With no fixed return deadline, focus on covering the route efficiently, making sure to visit the library before the shopping mall.",
        "V2": "Today's itinerary includes the pharmacy, supermarket, library, shopping mall, and bank, heading to the library prior to the shopping mall. Prioritize an efficient route.",
        "V3": "Need to stop at the pharmacy, supermarket, library, shopping mall, and bank today. No fixed deadline, so just focus on efficiency, and remember library must come before shopping mall.",
    },
    "pilot_17": {
        "V1": "Please visit the library, pharmacy, bank, shopping mall, and supermarket today, completing everything by 23:00. Balance time at locations with travel efficiency, and visit the shopping mall before the supermarket.",
        "V2": "Ensure all visits to the library, pharmacy, bank, shopping mall, and supermarket are done by 23:00. Go to the shopping mall before the supermarket, balancing quality with efficient transit.",
        "V3": "Make sure you hit the library, pharmacy, bank, shopping mall, and supermarket today and finish by 11 PM. Balance good ratings with efficient driving, and stop by the shopping mall before the supermarket.",
    },
    "pilot_18": {
        "V1": "We need to visit the bank, pharmacy, shopping mall, library, and supermarket today, returning by 22:00. Focus on the quickest possible route, and make sure to stop by the library before the supermarket.",
        "V2": "Please return by 22:00 after visiting the bank, pharmacy, shopping mall, library, and supermarket. Prioritize travel speed and efficiency, visiting the library prior to the supermarket.",
        "V3": "Need to visit the bank, pharmacy, shopping mall, library, and supermarket today and get back by 22:00. Take the fastest, most direct route, making sure to visit the library before the supermarket.",
    },
    "pilot_19": {
        "V1": "Please visit the supermarket, pharmacy, bank, shopping mall, and library today. Prioritize highly-rated places for the best experience. Go to the supermarket before the pharmacy, and visit the shopping mall before the library.",
        "V2": "Today's stops include the supermarket, pharmacy, bank, shopping mall, and library. Focus on top-rated quality, ensuring the supermarket is visited before the pharmacy and the shopping mall before the library.",
        "V3": "Make sure to visit the supermarket, pharmacy, bank, shopping mall, and library today. Pick places with great ratings, and be sure to hit the supermarket before pharmacy, and the shopping mall before library.",
    },
    "pilot_20": {
        "V1": "You need to visit the pharmacy, shopping mall, bank, library, and supermarket today, returning by 23:00. Balance good ratings with travel efficiency. Stop by the pharmacy before the shopping mall, and the library before the supermarket.",
        "V2": "Please be back by 23:00 after visiting the pharmacy, shopping mall, bank, library, and supermarket. Maintain a balance between quality and route efficiency, visiting pharmacy before shopping mall and library before supermarket.",
        "V3": "Need to visit the pharmacy, shopping mall, bank, library, and supermarket today and be back by 11 PM. Balance high ratings with route efficiency, and make sure you do pharmacy before mall and library before supermarket.",
    },
}


def build_development_exposure() -> dict[str, Any]:
    """Identify all records and clusters exposed during development."""
    pilot_raw = json.loads(PILOT_RAW.read_text(encoding="utf-8"))
    clusters = json.loads(HIPP_CLUSTERS.read_text(encoding="utf-8"))
    cluster_map = {c["cluster_id"]: c for c in clusters}

    exposed_source_indices = [p["source_index"] for p in pilot_raw]
    exposed_cluster_ids = [p["source_cluster_id"] for p in pilot_raw]

    # Find all records in HIPP that belong to any of these 20 exposed clusters
    all_exposed_source_indices = set(exposed_source_indices)
    for cid in exposed_cluster_ids:
        if cid in cluster_map:
            for r in cluster_map[cid]["records"]:
                all_exposed_source_indices.add(r["source_index"])

    exposure_record = {
        "description": "All intent indices and clusters exposed during prompt development and exploratory smoke tests. Strictly excluded from Test.",
        "pilot_group_count": len(pilot_raw),
        "exposed_cluster_ids": sorted(set(exposed_cluster_ids)),
        "directly_exposed_source_indices": sorted(exposed_source_indices),
        "cluster_closure_exposed_source_indices": sorted(all_exposed_source_indices),
    }

    DEV_EXPOSURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEV_EXPOSURE_OUT.write_text(json.dumps(exposure_record, indent=2), encoding="utf-8")
    print(f"[✓] Saved development exposure list: {len(all_exposed_source_indices)} source indices across {len(exposed_cluster_ids)} clusters.")
    return exposure_record


def build_candidate_splits(exposure: dict[str, Any]) -> dict[str, Any]:
    """Generate 200 groups stratified split: Dev 40 (Pilot 20, Calibration 20), Test 160.

    Seed: 20260906.
    Includes 1-category POI scenes.
    Ensures zero cross-split leakage.
    """
    clusters = json.loads(HIPP_CLUSTERS.read_text(encoding="utf-8"))
    pilot_raw = json.loads(PILOT_RAW.read_text(encoding="utf-8"))

    exposed_clusters = set(exposure["exposed_cluster_ids"])

    # Build representative candidates from non-exposed clusters
    candidate_pool = []
    for c in clusters:
        cid = c["cluster_id"]
        if cid in exposed_clusters:
            continue
        k = c["intent_key"]
        rep = c["records"][0]
        candidate_pool.append({
            "source_cluster_id": cid,
            "source_index": rep["source_index"],
            "instruction": rep["instruction"],
            "intent_key": k,
            "synthetic_label": rep,
            "member_count": c["member_count"],
        })

    # Stratified sampling for Calibration 20 and Test 160 (total 180 non-exposed groups)
    # Stratify by POI count: 1, 2, 3, 4, 5
    # Target distribution across 180 groups:
    # 1 POI: 30
    # 2 POI: 38
    # 3 POI: 38
    # 4 POI: 37
    # 5 POI: 37
    rng = random.Random(20260906)

    by_poi = defaultdict(list)
    for cand in candidate_pool:
        by_poi[cand["intent_key"]["poi_count"]].append(cand)

    # Sort each bucket deterministically
    for n in by_poi:
        by_poi[n].sort(key=lambda x: (
            x["intent_key"]["direction"],
            x["intent_key"]["time_limit"] is not None,
            len(x["intent_key"]["closure"]) > 0,
            x["source_cluster_id"],
        ))
        rng.shuffle(by_poi[n])

    target_counts = {1: 30, 2: 38, 3: 38, 4: 37, 5: 37}
    selected_180 = []
    for n, target in target_counts.items():
        chosen = by_poi[n][:target]
        assert len(chosen) == target, f"Not enough clusters for POI count {n}: had {len(chosen)} vs {target}"
        selected_180.extend(chosen)

    # Shuffle the 180 selected groups
    rng.shuffle(selected_180)

    # Split into Calibration 20 and Test 160
    # Calibration target: 4 from 1-POI, 4 from 2-POI, 4 from 3-POI, 4 from 4-POI, 4 from 5-POI
    calib_groups = []
    test_groups = []

    calib_by_poi = defaultdict(list)
    remaining_for_test = []

    for item in selected_180:
        n = item["intent_key"]["poi_count"]
        if len(calib_by_poi[n]) < 4:
            calib_by_poi[n].append(item)
        else:
            remaining_for_test.append(item)

    for n in sorted(calib_by_poi):
        calib_groups.extend(calib_by_poi[n])
    test_groups = remaining_for_test

    assert len(calib_groups) == 20, f"Expected 20 calib groups, got {len(calib_groups)}"
    assert len(test_groups) == 160, f"Expected 160 test groups, got {len(test_groups)}"

    # Format into standard group structure
    # 1. Dev Pilot (the 20 existing pilot groups)
    pilot_entries = []
    for p in pilot_raw:
        pilot_entries.append({
            "group_id": p["pilot_group_id"],
            "split": "dev_pilot",
            "source_index": p["source_index"],
            "source_cluster_id": p["source_cluster_id"],
            "base_instruction": p["base_instruction"],
            "gold_intent": p["gold_intent"],
            "cluster_size": p["cluster_size"],
        })

    # 2. Dev Calibration
    calib_entries = []
    for idx, c in enumerate(calib_groups, start=1):
        k = c["intent_key"]
        rep = c["synthetic_label"]
        calib_entries.append({
            "group_id": f"calib_{idx:02d}",
            "split": "dev_calibration",
            "source_index": c["source_index"],
            "source_cluster_id": c["source_cluster_id"],
            "base_instruction": c["instruction"],
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

    # 3. Test (160 groups)
    test_entries = []
    for idx, c in enumerate(test_groups, start=1):
        k = c["intent_key"]
        rep = c["synthetic_label"]
        test_entries.append({
            "group_id": f"test_{idx:03d}",
            "split": "test",
            "source_index": c["source_index"],
            "source_cluster_id": c["source_cluster_id"],
            "base_instruction": c["instruction"],
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

    splits_data = {
        "metadata": {
            "seed": 20260906,
            "total_groups": len(pilot_entries) + len(calib_entries) + len(test_entries),
            "dev_pilot_count": len(pilot_entries),
            "dev_calibration_count": len(calib_entries),
            "test_count": len(test_entries),
            "annotation_status": "pending_human_verification",
        },
        "dev_pilot": pilot_entries,
        "dev_calibration": calib_entries,
        "test": test_entries,
    }

    # Verify zero leakage
    dev_clusters = set(p["source_cluster_id"] for p in pilot_entries) | set(c["source_cluster_id"] for c in calib_entries)
    test_clusters = set(t["source_cluster_id"] for t in test_entries)
    cluster_overlap = dev_clusters & test_clusters
    assert not cluster_overlap, f"Cluster leakage detected between Dev and Test: {cluster_overlap}"

    dev_indices = set(p["source_index"] for p in pilot_entries) | set(c["source_index"] for c in calib_entries)
    test_indices = set(t["source_index"] for t in test_entries)
    index_overlap = dev_indices & test_indices
    assert not index_overlap, f"Index leakage detected between Dev and Test: {index_overlap}"

    # Verify development exposure exclusion
    exposed_indices = set(exposure["cluster_closure_exposed_source_indices"])
    test_exposed = test_indices & exposed_indices
    assert not test_exposed, f"Development exposed indices present in Test: {test_exposed}"

    SPLITS_OUT.parent.mkdir(parents=True, exist_ok=True)
    SPLITS_OUT.write_text(json.dumps(splits_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Saved candidate splits (200 groups: Dev 40, Test 160). Zero cross-split leakage verified.")
    return splits_data


def build_pilot_80_utterances() -> list[dict[str, Any]]:
    """Build 80 utterances (20 groups x 4 variants) for Pilot."""
    pilot_raw = json.loads(PILOT_RAW.read_text(encoding="utf-8"))

    utterances = []
    review_queue = []

    for p in pilot_raw:
        gid = p["pilot_group_id"]
        gold = p["gold_intent"]
        base_text = p["base_instruction"]

        paraphrases = PILOT_PARAPHRASES[gid]

        variants = [
            ("V0", base_text),
            ("V1", paraphrases["V1"]),
            ("V2", paraphrases["V2"]),
            ("V3", paraphrases["V3"]),
        ]

        for v_type, text in variants:
            utt_id = f"{gid}_{v_type.lower()}"

            utt_obj = {
                "group_id": gid,
                "utterance_id": utt_id,
                "source_index": p["source_index"],
                "source_cluster_id": p["source_cluster_id"],
                "split": "dev_pilot",
                "variant_type": v_type,
                "text": text,
                "gold_hard": {
                    "pois": gold["pois"],
                    "time_limit": gold["time_limit"],
                    "dependencies": gold["dependencies"],
                },
                "preference_direction": gold["preference_direction"],
                "w_synthetic": gold["quality_weight_synthetic"],
                "annotation_status": "pending",
                "graph_id": f"{gid}_graph",
            }
            utterances.append(utt_obj)

            # Build review queue item
            special_note = ""
            if gid == "pilot_11":
                special_note = "DISPUTE NOTE: Text mentions 'balancing a good mix ... within reasonable timeframe'. Review if preference is balanced rather than quality_first (0.6)."
            elif gid == "pilot_13":
                special_note = "DISPUTE NOTE: Text mentions 'Start at the library'. Review if library is required global first stop or only library before shopping_mall."
            elif gid == "pilot_17":
                special_note = "DISPUTE NOTE: Text mentions 'good balance between spending time and navigating efficiently'. Review if balanced rather than quality_first (0.6)."

            review_queue.append({
                "group_id": gid,
                "utterance_id": utt_id,
                "variant_type": v_type,
                "text": text,
                "target_pois": gold["pois"],
                "target_time_limit": gold["time_limit"],
                "target_dependencies": gold["dependencies"],
                "preference_direction": gold["preference_direction"],
                "original_evidence": base_text if v_type != "V0" else "Original HIPP instruction",
                "annotator_a_status": "pending",
                "annotator_b_status": "pending",
                "adjudication_status": "pending",
                "dispute_flag": bool(special_note),
                "dispute_note": special_note,
            })

    PILOT_80_OUT.parent.mkdir(parents=True, exist_ok=True)
    PILOT_80_OUT.write_text(json.dumps(utterances, indent=2, ensure_ascii=False), encoding="utf-8")

    ANNOTATION_QUEUE_OUT.parent.mkdir(parents=True, exist_ok=True)
    ANNOTATION_QUEUE_OUT.write_text(json.dumps(review_queue, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[✓] Saved 80 Pilot utterances and review queue: {len(utterances)} entries.")
    return utterances


def build_review_sheet_md(utterances: list[dict[str, Any]]) -> None:
    """Generate human-fillable Markdown review sheet for the 80 Pilot utterances."""
    lines = [
        "# DARC-Route Pilot 80-Utterance Equivalence Human Review Sheet",
        "",
        "> Status: `pending_human_verification` (Gate A is `blocked_on_annotation`)",
        "> Date Generated: 2026-09-06",
        "> Protocol Reference: `docs/experiments/EXPERIMENT_GUIDE.md` Section 4.4",
        "",
        "## Instructions for Annotators",
        "1. **Annotator A**: Reviews all 80 utterances. Fill in `A_Verdict` (PASS / REVISE) and `A_Direction` (quality_first / balanced / distance_first).",
        "2. **Annotator B**: Independently reviews a stratified 25% sample (5 groups = 20 utterances) plus all disputed groups (pilot_11, pilot_13, pilot_17).",
        "3. **Adjudication**: Discrepancies are reconciled by consensus. All rows must be approved before marking status `human_verified`.",
        "",
        "### Key Prior Review Flags",
        "- **pilot_11**: Instruction states 'balancing a good mix of visiting worthwhile places within a reasonable timeframe'. Synthetic weight is 0.6, but text strongly suggests `balanced`.",
        "- **pilot_13**: Instruction states 'Start at the library'. Synthetic label encodes (library, shopping_mall). Review if library is required to be the absolute first stop of the trip.",
        "- **pilot_17**: Instruction states 'Aim for a good balance between spending time at each location and navigating efficiently'. Synthetic weight is 0.6, but text suggests `balanced`.",
        "",
        "## Review Table",
        "",
        "| ID | Var | Instruction Text | POIs | Time | Deps | Direction Hint | Notes/Disputes | A_Verdict | B_Verdict | Final Adjudication |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for u in utterances:
        gid = u["group_id"]
        uid = u["utterance_id"]
        v = u["variant_type"]
        text = u["text"].replace("|", "\\|")
        pois = ",".join(u["gold_hard"]["pois"])
        t = str(u["gold_hard"]["time_limit"]) if u["gold_hard"]["time_limit"] is not None else "None"
        deps = str(u["gold_hard"]["dependencies"]).replace("|", "\\|")
        pref = u["preference_direction"]

        note = ""
        if gid == "pilot_11":
            note = "Check balanced vs quality_first"
        elif gid == "pilot_13":
            note = "Check 'Start at library' scope"
        elif gid == "pilot_17":
            note = "Check balanced vs quality_first"

        lines.append(f"| {uid} | {v} | {text} | {pois} | {t} | {deps} | {pref} | {note} | pending | pending | pending |")

    REVIEW_SHEET_MD.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_SHEET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[✓] Generated human review sheet: {REVIEW_SHEET_MD.relative_to(ROOT.parent)}")


def main():
    print("=== DARC-Route Dataset Preparation & Partition ===")
    exposure = build_development_exposure()
    splits = build_candidate_splits(exposure)
    utterances = build_pilot_80_utterances()
    build_review_sheet_md(utterances)
    print("\n=== Dataset Preparation Complete ===")


if __name__ == "__main__":
    main()
