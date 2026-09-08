#!/usr/bin/env python3
"""Build 80 equivalence utterances (20 groups x 4 variants) for Calibration.

Per EXPERIMENT_GUIDE.md Section 8:
- Groups: calib_01 to calib_20 from candidate_splits.json['dev_calibration']
- 4 variants per group:
  - V0: Base instruction from HIPP
  - V1: Direct lexical paraphrase
  - V2: Syntactic structure / order variation
  - V3: Colloquial / spoken variation
- Saves to data/calibration/calibration_80_utterances.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPLITS_FILE = ROOT / "data/processed/candidate_splits.json"
CALIB_OUT = ROOT / "data/calibration/calibration_80_utterances.json"

CALIB_PARAPHRASES = {
    "calib_01": {
        "V1": "Please make sure to visit the shopping mall today. High-quality destinations are quite important to us, so prioritize a location with great ratings. The visit sequence has no specific constraints, giving us complete schedule flexibility.",
        "V2": "Our visit has flexible timing with no required sequence, but be sure to visit the shopping mall today. Because destination quality is paramount, focus on a top-rated venue for a superior experience.",
        "V3": "Hey, let's hit the shopping mall today. Aim for a spot with really high reviews since quality matters a lot, and don't worry about any strict timing or order.",
    },
    "calib_02": {
        "V1": "You need to stop by the supermarket today. Please strike a balance between finding a well-regarded place and keeping your travel route efficient.",
        "V2": "Keep a steady balance between a good reputation and an efficient driving route while visiting the supermarket today.",
        "V3": "Need you to swing by the supermarket today. Try to find a happy medium between a solid place and a quick, efficient drive.",
    },
    "calib_03": {
        "V1": "Please visit the library today, ensuring your return by 21:00. Prioritizing highly-rated spots is essential, so enjoy your time at a well-reviewed location.",
        "V2": "Make sure you are back by 21:00 after visiting the library today. Top-rated places are the primary priority, so choose a well-regarded venue.",
        "V3": "Head to the library today and be back before 9 PM. Definitely pick a place with great reviews since quality comes first.",
    },
    "calib_04": {
        "V1": "You must visit the supermarket today and return by 17:00. It is vital to maintain an efficient and rapid itinerary.",
        "V2": "Please ensure you return by 17:00 after stopping at the supermarket. Keep the journey quick, direct, and efficient.",
        "V3": "Go to the supermarket today and get back by 5:00 PM. Take the fastest and most efficient route possible.",
    },
    "calib_05": {
        "V1": "We need to visit the bank and the shopping mall today, returning by 17:00. Focus on visiting high-quality locations during the outing.",
        "V2": "Ensure our return by 17:00 after visiting both the shopping mall and the bank. Our goal is to select stops with the highest quality.",
        "V3": "Need to visit the bank and shopping mall today and wrap up by 5 PM. Focus on hitting top-notch spots with great ratings.",
    },
    "calib_06": {
        "V1": "You should visit the supermarket and the bank today. Balance high-quality locations with travel efficiency, and make sure to stop by the supermarket prior to the bank.",
        "V2": "Visit the supermarket before heading to the bank today, seeking a balanced compromise between location quality and driving efficiency.",
        "V3": "Hit the supermarket and bank today, doing the supermarket first before the bank. Keep a good balance between decent reviews and efficient travel.",
    },
    "calib_07": {
        "V1": "Please visit the library and the shopping mall today, returning by 23:00 at the latest. Focus on places with top reviews, starting at the library before proceeding to the shopping mall.",
        "V2": "Be back no later than 11 PM after visiting the library and the shopping mall. Begin with the library then head to the shopping mall, giving top priority to excellent ratings.",
        "V3": "Need you to visit the library and shopping mall today, finishing up before 11 PM. Start off at the library then hit the mall, and pick the highest-rated places.",
    },
    "calib_08": {
        "V1": "We must visit the pharmacy and the bank today. An efficient route is paramount; be sure to go to the pharmacy prior to the bank.",
        "V2": "Go to the pharmacy before visiting the bank today, focusing strictly on route efficiency and minimizing driving distance.",
        "V3": "Stop by the pharmacy and bank today, making sure you do pharmacy first before the bank. Keep the route as short and efficient as you can.",
    },
    "calib_09": {
        "V1": "You need to visit the library, supermarket, and pharmacy today, returning by 22:00. Balance selecting reputable spots with keeping transit efficient.",
        "V2": "Return by 10 PM after stopping at the library, supermarket, and pharmacy. Maintain a balanced approach between good ratings and route efficiency.",
        "V3": "Hit the library, supermarket, and pharmacy today and be back by 10 PM. Strike a balance between well-rated places and not driving all over the place.",
    },
    "calib_10": {
        "V1": "Please visit the shopping mall, bank, and pharmacy today, returning by 22:00. Prioritize top-rated locations for quality, and ensure the bank is visited prior to the pharmacy.",
        "V2": "Ensure your return by 22:00 after visiting the bank, shopping mall, and pharmacy. Visit the bank before the pharmacy, focusing primarily on high ratings.",
        "V3": "Go to the shopping mall, bank, and pharmacy today and finish by 10 PM. Head to the bank before the pharmacy, and aim for the best-rated spots.",
    },
    "calib_11": {
        "V1": "You need to visit the bank, shopping mall, and pharmacy today, returning by 17:00. Prioritize transit efficiency to ensure the quickest possible journey.",
        "V2": "Please return by 5:00 PM after visiting the bank, shopping mall, and pharmacy. Focus entirely on travel efficiency and minimal transit time.",
        "V3": "Need to hit the bank, shopping mall, and pharmacy today and be back by 5 PM. Take the most direct, efficient route to get it done fast.",
    },
    "calib_12": {
        "V1": "We need to visit the supermarket, shopping mall, and pharmacy today, returning by 21:00. Route efficiency is key to save time; visit the supermarket before the shopping mall.",
        "V2": "Return by 21:00 after visiting the supermarket, shopping mall, and pharmacy. Begin at the supermarket before the shopping mall, prioritizing an efficient route.",
        "V3": "Stop by the supermarket, shopping mall, and pharmacy today and get back by 9 PM. Make sure supermarket comes before mall, and keep the driving efficient.",
    },
    "calib_13": {
        "V1": "Please visit the shopping mall, pharmacy, library, and supermarket today. Prioritize an efficient, short route. Start at the shopping mall, then go to the pharmacy, and visit the library afterward.",
        "V2": "Travel efficiently to the shopping mall, pharmacy, library, and supermarket today. Follow the sequence of shopping mall first, then pharmacy, and then library.",
        "V3": "Hit the shopping mall, pharmacy, library, and supermarket today on a quick route. Start at the mall, head to pharmacy next, then the library after that.",
    },
    "calib_14": {
        "V1": "We need to visit the shopping mall, supermarket, library, and pharmacy today without a set return time. Prioritize travel speed: visit the shopping mall before the supermarket, and the library before the pharmacy.",
        "V2": "With no fixed deadline, focus on the fastest route across the shopping mall, supermarket, library, and pharmacy. Stop at the shopping mall prior to the supermarket, and the library prior to the pharmacy.",
        "V3": "Visit the shopping mall, supermarket, library, and pharmacy today. No return time limit, just keep it super efficient, hitting mall before supermarket and library before pharmacy.",
    },
    "calib_15": {
        "V1": "You need to visit the supermarket, bank, shopping mall, and library today. Prioritize well-rated spots while maintaining reasonable travel efficiency. Visit the supermarket before heading to the bank.",
        "V2": "Stop by the supermarket before the bank while visiting the shopping mall and library as well. Aim for high place ratings combined with sensible route efficiency.",
        "V3": "Need you to hit the supermarket, bank, shopping mall, and library today. Do supermarket before bank, and pick well-rated spots while keeping the drive sensible.",
    },
    "calib_16": {
        "V1": "Please visit the shopping mall, library, supermarket, and pharmacy today, returning by 18:00. Prioritize route efficiency and brevity, visiting the library before the supermarket.",
        "V2": "Return by 18:00 after visiting the library, supermarket, shopping mall, and pharmacy. Keep the path as direct as possible, stopping at the library before the supermarket.",
        "V3": "Hit the shopping mall, library, supermarket, and pharmacy today and be back by 6 PM. Visit library before supermarket, and take the shortest, most efficient route.",
    },
    "calib_17": {
        "V1": "Today's visits cover the bank, supermarket, shopping mall, library, and pharmacy, returning by 18:00. Balance decent ratings with sensible transit; visit the bank before the supermarket and the library before the pharmacy.",
        "V2": "Be back by 6 PM after visiting the bank, supermarket, shopping mall, library, and pharmacy. Head to the bank prior to the supermarket and the library prior to the pharmacy, balancing quality and efficiency.",
        "V3": "Need to visit the bank, supermarket, shopping mall, library, and pharmacy today, getting back by 6 PM. Do bank before supermarket and library before pharmacy, balancing good ratings with a smooth drive.",
    },
    "calib_18": {
        "V1": "Please visit the bank, pharmacy, supermarket, shopping mall, and library today. Prioritize locations with strong reputations and reviews, visiting the bank before the pharmacy.",
        "V2": "Focus on highly-rated quality while visiting the bank, pharmacy, supermarket, shopping mall, and library today. Ensure the bank is visited before the pharmacy.",
        "V3": "Make sure you hit the bank, pharmacy, supermarket, shopping mall, and library today. Stop by the bank before pharmacy, and pick top-rated spots since quality is priority.",
    },
    "calib_19": {
        "V1": "You need to visit the shopping mall, bank, pharmacy, supermarket, and library today. Prioritize a swift and efficient route. Visit the bank before the pharmacy, and the supermarket before the library.",
        "V2": "Focus on route efficiency across the shopping mall, bank, pharmacy, supermarket, and library today. Ensure bank precedes pharmacy and supermarket precedes library.",
        "V3": "Head to the shopping mall, bank, pharmacy, supermarket, and library today. Keep it fast and efficient, doing bank before pharmacy and supermarket before library.",
    },
    "calib_20": {
        "V1": "Please visit the library, pharmacy, bank, shopping mall, and supermarket today, returning by 17:00. Balance visiting well-rated places with maintaining an efficient route.",
        "V2": "Ensure your return by 17:00 after visiting the library, pharmacy, bank, shopping mall, and supermarket. Seek a balanced trade-off between location ratings and travel efficiency.",
        "V3": "Visit the library, pharmacy, bank, shopping mall, and supermarket today and be back by 5 PM. Keep a solid balance between good ratings and efficient driving.",
    },
}


def build_calibration_80_utterances() -> list[dict[str, Any]]:
    splits = json.loads(SPLITS_FILE.read_text(encoding="utf-8"))
    calib_groups = splits["dev_calibration"]

    utterances = []
    for g in calib_groups:
        gid = g["group_id"]
        gi = g["gold_intent"]
        base_text = g["base_instruction"]
        paraphrases = CALIB_PARAPHRASES[gid]

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
                "source_index": g["source_index"],
                "source_cluster_id": g["source_cluster_id"],
                "split": "dev_calibration",
                "variant_type": v_type,
                "text": text,
                "gold_hard": {
                    "pois": gi["pois"],
                    "time_limit": gi["time_limit"],
                    "dependencies": gi["dependencies"],
                },
                "preference_direction": gi["preference_direction"],
                "w_synthetic": gi["quality_weight_synthetic"],
                "graph_id": f"{gid}_graph",
            }
            utterances.append(utt_obj)

    CALIB_OUT.parent.mkdir(parents=True, exist_ok=True)
    CALIB_OUT.write_text(json.dumps(utterances, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[✓] Saved 80 Calibration utterances to {CALIB_OUT} ({len(utterances)} records).")
    return utterances


if __name__ == "__main__":
    build_calibration_80_utterances()
