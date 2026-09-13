"""Prepare and freeze deterministic Dev (5) and Eval (40) datasets for LLMAP transfer.

Ensures:
1. Complete disjointness from historical 160 HIPP source indices.
2. Filtered by supported categories: shopping_mall, supermarket, pharmacy, bank, library.
3. Deterministic sequential selection by source_index.
4. Generates deterministic offline scenario snapshots (lat/lon, ratings, openings).
5. Generates 4 strictly audited variants per group (V0 original HIPP, V1 formal, V2 itinerary, V3 casual).
6. Outputs review queue markdown for audit transparency.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from src.graph import SyntheticGraph, generate_synthetic_graph

ROOT = Path(__file__).resolve().parents[1]
HIPP_PATH = ROOT / "tmp" / "llmap_repo_20260909" / "dataset" / "HIPP.json"
HIST_PATH = ROOT / "9-AutoDriving-core" / "data" / "test" / "test_640_utterances.json"
OUT_DATA_DIR = ROOT / "9-AutoDriving-core" / "data" / "llmap_transfer"
OUT_DOCS_DIR = ROOT / "docs" / "experiments" / "v41_next_action_20260913"

ALLOWED_CATEGORIES = ["shopping_mall", "supermarket", "pharmacy", "bank", "library"]


def synthetic_graph_to_llmap_scenario(
    graph: SyntheticGraph,
    base_lat: float = 39.9042,
    base_lon: float = 116.4074,
) -> dict[str, Any]:
    """Convert a SyntheticGraph into an LLMAP scenario snapshot dictionary."""
    def to_lat_lon(x_km: float, y_km: float) -> tuple[float, float]:
        lat = base_lat + y_km / 111.0
        lon = base_lon + x_km / (111.0 * math.cos(math.radians(base_lat)))
        return round(lat, 6), round(lon, 6)

    start_lat, start_lon = to_lat_lon(graph.origin[0], graph.origin[1])
    end_lat, end_lon = to_lat_lon(graph.destination[0], graph.destination[1])

    pois_data = []
    for poi in graph.pois:
        plat, plon = to_lat_lon(poi.x, poi.y)
        open_h = poi.open_time // 60
        open_m = poi.open_time % 60
        close_h = poi.close_time // 60
        close_m = poi.close_time % 60
        open_str = f"Monday: {open_h % 12 or 12}:{open_m:02d} {'AM' if open_h < 12 else 'PM'} – {close_h % 12 or 12}:{close_m:02d} {'AM' if close_h < 12 else 'PM'}"

        pois_data.append({
            "Place ID": poi.id,
            "Type": poi.category,
            "Rating": poi.rating,
            "Number Ratings": poi.reviews,
            "Latitude": plat,
            "Longitude": plon,
            "Opening": [open_str],
            "stay_duration": poi.stay_duration,
        })

    return {
        "start_location": {"latitude": start_lat, "longitude": start_lon},
        "end_location": {"latitude": end_lat, "longitude": end_lon},
        "pois": pois_data,
        "graph_id": graph.graph_id,
    }


def format_category_phrase(cats: list[str]) -> str:
    """Format a list of categories naturally, e.g. 'the bank and the library'."""
    items = [f"the {c.replace('_', ' ')}" for c in cats]
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def generate_paraphrase_variants(
    v0_text: str,
    pois: list[str],
    time_limit: str | None,
    dependencies: list[list[str]],
    quality_weight: float,
) -> dict[str, str]:
    """Generate 3 systematic, meaning-preserving paraphrase variants (V1, V2, V3)."""
    # 1. Determine preference direction
    if quality_weight > 0.5:
        pref_v1 = "Prioritize locations with high ratings and strong customer reviews."
        pref_v2 = "Give top priority to reputable, well-reviewed venues."
        pref_v3 = "Aim for the highest-rated places since quality is the main goal."
    elif quality_weight < 0.5:
        pref_v1 = "Focus on route efficiency and minimizing unnecessary travel time."
        pref_v2 = "Keep the travel distance minimal and direct."
        pref_v3 = "Take the quickest and most efficient route possible."
    else:
        pref_v1 = "Try to balance good quality with route efficiency."
        pref_v2 = "Maintain a fair balance between venue ratings and overall travel time."
        pref_v3 = "Balance quality and distance so we visit decent spots without taking too long."

    # 2. Time limit clauses
    time_v1 = f" Ensure that you return home by {time_limit}." if time_limit and time_limit != "None" else ""
    time_v2 = f" All visits must be completed with return by {time_limit}." if time_limit and time_limit != "None" else ""
    time_v3 = f" Make sure we are back by {time_limit}." if time_limit and time_limit != "None" else ""

    # 3. Dependency clauses
    deps_v1 = []
    deps_v2 = []
    deps_v3 = []
    for dep in dependencies:
        if len(dep) == 2:
            a, b = dep[0].replace("_", " "), dep[1].replace("_", " ")
            deps_v1.append(f"Make sure to visit the {a} prior to the {b}.")
            deps_v2.append(f"Remember to stop at the {a} before heading to the {b}.")
            deps_v3.append(f"Be sure to hit the {a} first before the {b}.")

    dep_v1_str = (" " + " ".join(deps_v1)) if deps_v1 else ""
    dep_v2_str = (" " + " ".join(deps_v2)) if deps_v2 else ""
    dep_v3_str = (" " + " ".join(deps_v3)) if deps_v3 else ""

    # 4. Assemble variants
    # V1: Formal request
    # V2: Structured itinerary
    # V3: Conversational
    poi_phrase = format_category_phrase(pois)

    v1 = f"Please visit {poi_phrase} today.{time_v1} {pref_v1}{dep_v1_str}".strip()
    v2 = f"Your itinerary today includes visiting {poi_phrase}.{dep_v2_str}{time_v2} {pref_v2}".strip()
    v3 = f"Hey, need you to stop by {poi_phrase} today.{dep_v3_str}{time_v3} {pref_v3}".strip()

    return {
        "V0": v0_text,
        "V1": v1,
        "V2": v2,
        "V3": v3,
    }


def main() -> None:
    OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Load historical exposure
    with open(HIST_PATH, "r", encoding="utf-8") as f:
        hist_data = json.load(f)
    hist_indices = set(item.get("source_index", item.get("group_id")) for item in hist_data)

    # Load HIPP dataset
    with open(HIPP_PATH, "r", encoding="utf-8") as f:
        hipp_data = json.load(f)

    # Filter unexposed candidates
    fresh_candidates = []
    for idx, sample in enumerate(hipp_data):
        if idx in hist_indices:
            continue
        label = sample.get("synthetic_label", {})
        pois = label.get("pois", [])
        if not pois or not all(p in ALLOWED_CATEGORIES for p in pois):
            continue
        deps = label.get("dependencies", [])
        if deps:
            if not all(
                isinstance(d, list) and len(d) == 2 and d[0] in ALLOWED_CATEGORIES and d[1] in ALLOWED_CATEGORIES
                for d in deps
            ):
                continue
        fresh_candidates.append((idx, sample))

    dev_candidates = fresh_candidates[:5]
    eval_candidates = fresh_candidates[5:45]

    print(f"Loaded {len(hipp_data)} HIPP samples.")
    print(f"Historical exposed indices count: {len(hist_indices)}")
    print(f"Fresh eligible candidates: {len(fresh_candidates)}")
    print(f"Selected Dev samples: {[c[0] for c in dev_candidates]}")
    print(f"Selected Eval samples: {[c[0] for c in eval_candidates]}")

    # Process Dev (5 samples)
    dev_utterances = []
    dev_scenarios = {}
    for i, (src_idx, sample) in enumerate(dev_candidates, start=1):
        gid = f"dev_{i:03d}"
        graph_id = f"{gid}_graph"
        # Generate synthetic graph and scenario snapshot
        synth_g = generate_synthetic_graph(graph_id=graph_id, seed=42 + src_idx)
        sc = synthetic_graph_to_llmap_scenario(synth_g)
        dev_scenarios[graph_id] = sc

        label = sample["synthetic_label"]
        pois = label["pois"]
        t_limit = label.get("time_limit")
        deps = label.get("dependencies", [])
        qw = float(label.get("quality_weight", 0.5))
        dw = float(label.get("distance_weight", 0.5))
        pref_dir = "quality_first" if qw > 0.5 else ("distance_first" if qw < 0.5 else "balanced")

        variants = generate_paraphrase_variants(
            v0_text=sample["human_instruction"],
            pois=pois,
            time_limit=t_limit if t_limit != "None" else None,
            dependencies=deps,
            quality_weight=qw,
        )

        for vtype, text in variants.items():
            dev_utterances.append({
                "group_id": gid,
                "utterance_id": f"{gid}_{vtype.lower()}",
                "source_index": src_idx,
                "split": "dev",
                "variant_type": vtype,
                "text": text,
                "gold_hard": {
                    "pois": pois,
                    "time_limit": t_limit if t_limit != "None" else None,
                    "dependencies": deps,
                },
                "preference_direction": pref_dir,
                "w_synthetic": qw,
                "distance_weight": dw,
                "graph_id": graph_id,
            })

    # Process Eval (40 samples)
    eval_utterances = []
    eval_scenarios = {}
    for i, (src_idx, sample) in enumerate(eval_candidates, start=1):
        gid = f"transfer_{i:03d}"
        graph_id = f"{gid}_graph"
        synth_g = generate_synthetic_graph(graph_id=graph_id, seed=100 + src_idx)
        sc = synthetic_graph_to_llmap_scenario(synth_g)
        eval_scenarios[graph_id] = sc

        label = sample["synthetic_label"]
        pois = label["pois"]
        t_limit = label.get("time_limit")
        deps = label.get("dependencies", [])
        qw = float(label.get("quality_weight", 0.5))
        dw = float(label.get("distance_weight", 0.5))
        pref_dir = "quality_first" if qw > 0.5 else ("distance_first" if qw < 0.5 else "balanced")

        variants = generate_paraphrase_variants(
            v0_text=sample["human_instruction"],
            pois=pois,
            time_limit=t_limit if t_limit != "None" else None,
            dependencies=deps,
            quality_weight=qw,
        )

        for vtype, text in variants.items():
            eval_utterances.append({
                "group_id": gid,
                "utterance_id": f"{gid}_{vtype.lower()}",
                "source_index": src_idx,
                "split": "eval",
                "variant_type": vtype,
                "text": text,
                "gold_hard": {
                    "pois": pois,
                    "time_limit": t_limit if t_limit != "None" else None,
                    "dependencies": deps,
                },
                "preference_direction": pref_dir,
                "w_synthetic": qw,
                "distance_weight": dw,
                "graph_id": graph_id,
            })

    # Save datasets
    dev_utt_file = OUT_DATA_DIR / "dev_5_utterances.json"
    dev_sc_file = OUT_DATA_DIR / "dev_5_scenarios.json"
    eval_utt_file = OUT_DATA_DIR / "eval_40_utterances.json"
    eval_sc_file = OUT_DATA_DIR / "eval_40_scenarios.json"

    with open(dev_utt_file, "w", encoding="utf-8") as f:
        json.dump(dev_utterances, f, indent=2, ensure_ascii=False)
    with open(dev_sc_file, "w", encoding="utf-8") as f:
        json.dump(dev_scenarios, f, indent=2, ensure_ascii=False)
    with open(eval_utt_file, "w", encoding="utf-8") as f:
        json.dump(eval_utterances, f, indent=2, ensure_ascii=False)
    with open(eval_sc_file, "w", encoding="utf-8") as f:
        json.dump(eval_scenarios, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(dev_utterances)} dev utterances to {dev_utt_file}")
    print(f"Wrote {len(dev_scenarios)} dev scenarios to {dev_sc_file}")
    print(f"Wrote {len(eval_utterances)} eval utterances to {eval_utt_file}")
    print(f"Wrote {len(eval_scenarios)} eval scenarios to {eval_sc_file}")

    # Generate Review Queue Markdown
    review_queue_file = OUT_DOCS_DIR / "REVIEW_QUEUE.md"
    lines = [
        "# LLMAP 迁移实验指令与改写审核队列 (REVIEW_QUEUE)",
        "",
        "- **审核日期**: `2026-09-13`",
        "- **执行环境**: `9-AutoDriving-core`",
        f"- **样本规模**: 5 组开发集 (20 句) + 40 组评估集 (160 句)",
        "- **历史暴露核验**: 所有选中源索引与历史 160 组完全正交（0 交集）",
        "",
        "---",
        "",
        "## 1. 5 组开发用例清单 (Dev 5 Groups / 20 Utterances)",
        "",
    ]

    for g_idx in range(1, 6):
        gid = f"dev_{g_idx:03d}"
        items = [u for u in dev_utterances if u["group_id"] == gid]
        first = items[0]
        lines.append(f"### 组 {gid} (HIPP Source Index: {first['source_index']})")
        lines.append(f"- **Gold POIs**: `{first['gold_hard']['pois']}`")
        lines.append(f"- **Time Limit**: `{first['gold_hard']['time_limit']}`")
        lines.append(f"- **Dependencies**: `{first['gold_hard']['dependencies']}`")
        lines.append(f"- **Quality Weight ($w$)**: `{first['w_synthetic']}` ({first['preference_direction']})")
        lines.append("- **4 变体文本**:")
        for it in items:
            lines.append(f"  - **{it['variant_type']}** (`{it['utterance_id']}`): {it['text']}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 2. 40 组评估用例清单 (Eval 40 Groups / 160 Utterances)",
        "",
    ])

    for g_idx in range(1, 41):
        gid = f"transfer_{g_idx:03d}"
        items = [u for u in eval_utterances if u["group_id"] == gid]
        first = items[0]
        lines.append(f"### 组 {gid} (HIPP Source Index: {first['source_index']})")
        lines.append(f"- **Gold POIs**: `{first['gold_hard']['pois']}`")
        lines.append(f"- **Time Limit**: `{first['gold_hard']['time_limit']}`")
        lines.append(f"- **Dependencies**: `{first['gold_hard']['dependencies']}`")
        lines.append(f"- **Quality Weight ($w$)**: `{first['w_synthetic']}` ({first['preference_direction']})")
        lines.append("- **4 变体文本**:")
        for it in items:
            lines.append(f"  - **{it['variant_type']}** (`{it['utterance_id']}`): {it['text']}")
        lines.append("")

    review_queue_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote review queue document to {review_queue_file}")


if __name__ == "__main__":
    main()
