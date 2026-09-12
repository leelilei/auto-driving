#!/usr/bin/env python3
"""Generate strictly unexposed E2 confirmation and control datasets (Zero overlap with any history)."""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
clusters = json.loads((ROOT / "data/processed/hipp_clusters.json").read_text())
all_cids = {c["cluster_id"]: c for c in clusters}

dev_exp = json.loads((ROOT / "data/processed/development_exposure.json").read_text()).get("exposed_cluster_ids", [])
splits = json.loads((ROOT / "data/processed/candidate_splits.json").read_text())
split_cids = set()
for s in splits.values():
    for row in s:
        if "source_cluster_id" in row:
            split_cids.add(row["source_cluster_id"])
test_raw = json.loads((ROOT / "data/test/test_640_utterances.json").read_text())
test_cids = {u.get("source_cluster_id") for u in test_raw if u.get("source_cluster_id") is not None}

total_exposed = set(dev_exp) | split_cids | test_cids
truly_unexposed = sorted(list(set(all_cids.keys()) - total_exposed))

random.seed(20260912)
selected_50 = random.sample(truly_unexposed, 50)
selected_40_confirm = selected_50[:40]
selected_10_control = selected_50[40:]

import sys
sys.path.insert(0, str(ROOT))
from scripts.prepare_e2_confirmation_data import build_variants

weight_map = {
    "quality_first": 0.75,
    "balanced": 0.50,
    "distance_first": 0.25,
}

confirm_utterances = []
for idx, cid in enumerate(selected_40_confirm):
    c_info = all_cids[cid]
    rec = c_info["records"][0]
    gid = f"e2_clean_{idx+1:03d}"
    base_inst = rec["instruction"]
    ik = c_info["intent_key"]
    pois = ik["pois"]
    t_limit = ik["time_limit"]
    deps = ik["closure"]
    direction = rec.get("direction") or ik.get("direction", "balanced")
    w_syn = weight_map.get(direction, 0.50)

    variants = build_variants(base_inst, pois, t_limit, deps, direction)
    for v_type in ["V0", "V1", "V2", "V3"]:
        confirm_utterances.append({
            "group_id": gid,
            "utterance_id": f"{gid}_{v_type.lower()}",
            "variant_type": v_type,
            "source_index": rec["source_index"],
            "source_cluster_id": cid,
            "text": variants[v_type],
            "gold_hard": {
                "pois": pois,
                "time_limit": t_limit,
                "dependencies": deps,
            },
            "preference_direction": direction,
            "w_synthetic": w_syn,
        })

out_file = ROOT / "data/e2/e2_strictly_unexposed_utterances.json"
out_file.write_text(json.dumps(confirm_utterances, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

manifest = {
    "total_hipp_clusters": len(all_cids),
    "total_exposed_excluded": len(total_exposed),
    "truly_unexposed_pool": len(truly_unexposed),
    "selected_40_confirmation_clusters": selected_40_confirm,
    "selected_10_control_clusters": selected_10_control,
    "sampling_seed": 20260912,
}
(ROOT / "data/e2/e2_clean_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"[✓] Generated {len(confirm_utterances)} strictly unexposed utterances to {out_file}")
