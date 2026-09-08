"""Unit tests for dataset splits, cluster isolation, and development exposure exclusion."""

import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_splits_and_leakage():
    splits_file = ROOT / "data/processed/candidate_splits.json"
    exposure_file = ROOT / "data/processed/development_exposure.json"
    pilot_80_file = ROOT / "data/pilot/pilot_80_utterances.json"

    assert splits_file.exists(), "candidate_splits.json missing"
    assert exposure_file.exists(), "development_exposure.json missing"
    assert pilot_80_file.exists(), "pilot_80_utterances.json missing"

    splits = json.loads(splits_file.read_text(encoding="utf-8"))
    exposure = json.loads(exposure_file.read_text(encoding="utf-8"))
    pilot_80 = json.loads(pilot_80_file.read_text(encoding="utf-8"))

    dev_pilot = splits["dev_pilot"]
    dev_calib = splits["dev_calibration"]
    test = splits["test"]

    # 1. Size checks
    assert len(dev_pilot) == 20
    assert len(dev_calib) == 20
    assert len(test) == 160
    assert len(pilot_80) == 80

    # 2. Zero cluster overlap between Dev and Test
    dev_clusters = {p["source_cluster_id"] for p in dev_pilot} | {c["source_cluster_id"] for c in dev_calib}
    test_clusters = {t["source_cluster_id"] for t in test}
    assert not (dev_clusters & test_clusters), "Cross-split cluster overlap found!"

    # 3. Zero index overlap between Dev and Test
    dev_indices = {p["source_index"] for p in dev_pilot} | {c["source_index"] for c in dev_calib}
    test_indices = {t["source_index"] for t in test}
    assert not (dev_indices & test_indices), "Cross-split index overlap found!"

    # 4. Development exposure exclusion
    exposed_closure = set(exposure["cluster_closure_exposed_source_indices"])
    assert not (test_indices & exposed_closure), "Exposed development indices leaked into Test!"

    # 5. 1-POI scenes present in Test
    test_1poi = sum(1 for t in test if t["gold_intent"]["poi_count"] == 1)
    assert test_1poi > 0, "No 1-POI scenes in Test set!"
