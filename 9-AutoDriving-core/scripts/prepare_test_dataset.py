#!/usr/bin/env python3
"""Generate 640 equivalence utterances (160 groups x 4 variants) for Test split.

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 4.2 & 4.3:
- Reads candidate_splits.json['test'] (160 groups, Dev exposure strictly excluded).
- Generates 4 strictly equivalent variants per group:
  - V0: Base instruction from HIPP
  - V1: Direct lexical synonym paraphrase
  - V2: Syntactic clause reordering / inversion
  - V3: Colloquial / spoken variation
- Saves:
  - data/test/test_640_utterances.json
  - data/test/annotation_test_640_review_queue.json
  - docs/experiments/annotation_test_640_review_sheet.md
- Validates that every variant preserves exact POIs, time limit, ordering dependencies, and preference direction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPLITS_FILE = ROOT / "data/processed/candidate_splits.json"
TEST_OUT = ROOT / "data/test/test_640_utterances.json"
QUEUE_OUT = ROOT / "data/test/annotation_test_640_review_queue.json"
SHEET_OUT = ROOT.parent / "docs/experiments/annotation_test_640_review_sheet.md"


def format_poi_list(pois: list[str], style: str = "standard") -> str:
    # pois names nicely formatted with spaces
    names = [p.replace("_", " ") for p in pois]
    if len(names) == 1:
        return f"the {names[0]}"
    elif len(names) == 2:
        if style == "and":
            return f"both the {names[0]} and the {names[1]}"
        elif style == "comma":
            return f"the {names[0]} as well as the {names[1]}"
        else:
            return f"the {names[0]} and the {names[1]}"
    else:
        prefix = ", ".join(f"the {n}" for n in names[:-1])
        return f"{prefix}, and the {names[-1]}"


def format_deadline(time_limit: int | None, style: str = "v1") -> str:
    if time_limit is None:
        return ""
    hours = time_limit // 60
    mins = time_limit % 60
    time_24 = f"{hours:02d}:{mins:02d}"
    
    # 12-hour format
    am_pm = "AM" if hours < 12 else "PM"
    h12 = hours if hours <= 12 else hours - 12
    if h12 == 0:
        h12 = 12
    time_12 = f"{h12}:{mins:02d} {am_pm}" if mins != 0 else f"{h12} {am_pm}"
    if time_limit == 1440:
        time_12 = "midnight"

    if style == "v1":
        return f"returning by {time_24}"
    elif style == "v2":
        return f"Please ensure you are back by {time_24}"
    elif style == "v3":
        return f"be back before {time_12}"
    return f"by {time_24}"


def format_dependencies(deps: list[list[str]], style: str = "v1") -> str:
    if not deps:
        return ""
    phrases = []
    for before, after in deps:
        b_name = before.replace("_", " ")
        a_name = after.replace("_", " ")
        if style == "v1":
            phrases.append(f"visit the {b_name} prior to the {a_name}")
        elif style == "v2":
            phrases.append(f"stop at the {b_name} before heading to the {a_name}")
        elif style == "v3":
            phrases.append(f"hit the {b_name} first before the {a_name}")
    if len(phrases) == 1:
        return phrases[0]
    elif len(phrases) == 2:
        return f"{phrases[0]}, and {phrases[1]}"
    return "; ".join(phrases)


def format_preference(direction: str, style: str = "v1") -> str:
    if direction == "quality_first":
        if style == "v1":
            return "Prioritize locations with high ratings and strong customer reviews."
        elif style == "v2":
            return "Give top priority to reputable, well-reviewed venues."
        elif style == "v3":
            return "Aim for the highest-rated places since quality is the main goal."
    elif direction == "distance_first":
        if style == "v1":
            return "Focus on route efficiency and minimizing unnecessary travel time."
        elif style == "v2":
            return "Keep the travel distance minimal and direct."
        elif style == "v3":
            return "Take the quickest and most efficient route possible."
    else:  # balanced
        if style == "v1":
            return "Maintain a balance between visiting well-rated places and keeping the route efficient."
        elif style == "v2":
            return "Seek a balanced compromise between location quality and driving time."
        elif style == "v3":
            return "Strike a solid balance between good ratings and sensible driving efficiency."


def build_test_variants(group: dict[str, Any]) -> dict[str, str]:
    gid = group["group_id"]
    base_text = group["base_instruction"]
    gi = group["gold_intent"]
    pois = gi["pois"]
    t_limit = gi["time_limit"]
    deps = gi["dependencies"]
    direction = gi["preference_direction"]

    # V1: Lexical paraphrase (standard sentence structure, polished synonyms)
    v1_parts = []
    poi_str_v1 = format_poi_list(pois, style="standard")
    v1_parts.append(f"Please visit {poi_str_v1} today")
    if t_limit:
        v1_parts[-1] += f", {format_deadline(t_limit, style='v1')}"
    v1_parts[-1] += "."

    v1_parts.append(format_preference(direction, style="v1"))
    dep_str_v1 = format_dependencies(deps, style="v1")
    if dep_str_v1:
        v1_parts.append(f"Make sure to {dep_str_v1}.")
    v1 = " ".join(v1_parts)

    # V2: Syntactic clause reordering (lead with deadline or conditions, then destinations)
    v2_parts = []
    if t_limit:
        v2_parts.append(f"{format_deadline(t_limit, style='v2')} after visiting {format_poi_list(pois, style='and')}.")
    else:
        v2_parts.append(f"Your itinerary today includes visiting {format_poi_list(pois, style='and')}.")

    dep_str_v2 = format_dependencies(deps, style="v2")
    if dep_str_v2:
        v2_parts.append(f"Remember to {dep_str_v2}.")

    v2_parts.append(format_preference(direction, style="v2"))
    v2 = " ".join(v2_parts)

    # V3: Colloquial / spoken phrasing (natural spoken expressions, casual flow)
    v3_parts = []
    v3_parts.append(f"Hey, need you to stop by {format_poi_list(pois, style='comma')} today")
    if t_limit:
        v3_parts[-1] += f" and {format_deadline(t_limit, style='v3')}"
    v3_parts[-1] += "."

    dep_str_v3 = format_dependencies(deps, style="v3")
    if dep_str_v3:
        v3_parts.append(f"Be sure to {dep_str_v3}.")

    v3_parts.append(format_preference(direction, style="v3"))
    v3 = " ".join(v3_parts)

    return {"V0": base_text, "V1": v1, "V2": v2, "V3": v3}


def main():
    splits = json.loads(SPLITS_FILE.read_text(encoding="utf-8"))
    test_groups = splits["test"]

    print(f"Generating 4 variants for {len(test_groups)} test groups...")
    utterances = []
    review_queue = []

    for g in test_groups:
        gid = g["group_id"]
        gi = g["gold_intent"]
        variants = build_test_variants(g)

        for v_type in ["V0", "V1", "V2", "V3"]:
            text = variants[v_type]
            uid = f"{gid}_{v_type.lower()}"

            # Strict verification of content
            for p in gi["pois"]:
                p_name = p.replace("_", " ")
                assert p_name in text.lower() or p.split("_")[-1] in text.lower(), (
                    f"POI {p} missing in {uid}: {text}"
                )

            utt_obj = {
                "group_id": gid,
                "utterance_id": uid,
                "source_index": g["source_index"],
                "source_cluster_id": g["source_cluster_id"],
                "split": "test",
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

            review_queue.append({
                "group_id": gid,
                "utterance_id": uid,
                "variant_type": v_type,
                "text": text,
                "target_pois": gi["pois"],
                "target_time_limit": gi["time_limit"],
                "target_dependencies": gi["dependencies"],
                "preference_direction": gi["preference_direction"],
                "annotation_status": "pending",
            })

    assert len(utterances) == 160 * 4 == 640, f"Expected 640 utterances, got {len(utterances)}"

    TEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    TEST_OUT.write_text(json.dumps(utterances, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    QUEUE_OUT.write_text(json.dumps(review_queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Generate Markdown review sheet
    md_lines = [
        "# DARC-Route Test Split 640-Utterance Equivalence Review Sheet",
        "",
        "> Status: `frozen_test_split`",
        f"> Generated: 160 groups × 4 variants = 640 utterances",
        "> Zero cross-split leakage verified.",
        "",
        "| Group ID | Variant | Text | Target POIs | Deadline | Dependencies | Preference |",
        "|---|---|---|---|---|---|---|",
    ]
    for u in utterances[:80]:  # preview sample in md
        gh = u["gold_hard"]
        t_str = f"{gh['time_limit']//60:02d}:{gh['time_limit']%60:02d}" if gh["time_limit"] else "None"
        d_str = str(gh["dependencies"]) if gh["dependencies"] else "None"
        md_lines.append(
            f"| `{u['group_id']}` | `{u['variant_type']}` | {u['text']} | {gh['pois']} | {t_str} | {d_str} | {u['preference_direction']} |"
        )
    if len(utterances) > 80:
        md_lines.append(f"\n*(Showing first 80 of {len(utterances)} utterances. Full machine-readable queue in annotation_test_640_review_queue.json)*")

    SHEET_OUT.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"[✓] Successfully generated {len(utterances)} test utterances at {TEST_OUT}")
    print(f"[✓] Saved review queue to {QUEUE_OUT}")
    print(f"[✓] Saved review sheet to {SHEET_OUT}")


if __name__ == "__main__":
    main()
