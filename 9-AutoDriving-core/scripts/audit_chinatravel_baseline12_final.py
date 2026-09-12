"""Audit frozen baseline12 collection/planning without changing any artifacts."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
RUN = CORE / "data/chinatravel_baseline12_20260912"
sys.path.insert(0, str(CORE / "scripts"))
import chinatravel_pipeline_v3 as ct


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prereg = ct.read(RUN / "preregistration.json")
    public = ct.read(RUN / "public_inputs.json")
    collection = ct.read(RUN / "collection_retry1.json")
    planning = ct.read(RUN / "planning/summary.json")
    ids = prereg["selected_ids"]
    assert len(ids) == 12 and [x["uid"] for x in public] == ids
    assert collection["logical_model_calls"] == 12 and collection["complete"] == 12
    assert len(collection["records"]) == 12
    for record, item in zip(collection["records"], public):
        user = json.loads(record["request"]["messages"][1]["content"])
        assert user == item and set(user) == {"uid", "nature_language"}
        assert "hard_logic_py" not in json.dumps(record["request"], ensure_ascii=False)
        assert record["status"] == "COMPLETE"
    assert [row["uid"] for row in planning["cases"]] == ids
    assert all(row["status"] == "search_success" for row in planning["cases"])
    assert all(row["raw_schema_valid"] and row["adapted_schema_valid"] for row in planning["cases"])
    assert all(row["schema_changes"] == 0 for row in planning["cases"])
    assert all(row["prediction_accepted"] for row in planning["cases"])
    assert all(row["official_all_pass_rate"] == 100.0 for row in planning["cases"])
    result = {
        "status": "PASS", "n_expected": 12, "source_model_calls": 12,
        "complete_parses": 12, "search_successes": 12, "search_failures": 0,
        "raw_schema_valid": 12, "adapted_schema_valid": 12, "schema_adapter_changes": 0,
        "invented_values": 0, "official_all_pass": 12,
        "full_denominator_all_pass_rate": 100.0,
        "semantic_error_candidate": False,
        "scope": "development baseline diagnostic; simple non-fixed6 ordered slice; not benchmark or DARC evidence",
        "next_action": "Do not start stage 5; retain 12-case diagnostic and reassess whether a harder audited slice is justified.",
        "ids": ids,
        "artifact_hashes": {name: sha(RUN / name) for name in ("public_inputs.json", "preregistration.json", "collection_retry1.json")},
    }
    ct.write(RUN / "final_audit.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
