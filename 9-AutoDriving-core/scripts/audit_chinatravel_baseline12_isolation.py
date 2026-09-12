"""Audit input isolation and denominator integrity for the frozen ChinaTravel baseline12 run.

This is an offline audit.  It does not call a model, search service, or evaluator.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
RUN = CORE / "data/chinatravel_baseline12_20260912"
CANONICAL = ROOT / "external/ChinaTravel/chinatravel/data/dev_split"
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
    assert collection["logical_model_calls"] == 12
    assert collection["complete"] == 12 and len(collection["records"]) == 12

    forbidden_request_markers = (
        "hard_logic_py", "official_score", "oracle_translation", "gold DSL",
        "canonical constraint", "target constraints",
    )
    request_checks = []
    for record, item in zip(collection["records"], public):
        messages = record["request"]["messages"]
        user_payload = json.loads(messages[1]["content"])
        assert user_payload == item and set(user_payload) == {"uid", "nature_language"}
        request_text = json.dumps(messages, ensure_ascii=False)
        leaked = [marker for marker in forbidden_request_markers if marker in request_text]
        assert not leaked, (record["uid"], leaked)
        assert record["status"] == "COMPLETE"
        request_checks.append({"uid": record["uid"], "public_keys": sorted(user_payload), "forbidden_markers": leaked})

    rows = planning["cases"]
    assert [row["uid"] for row in rows] == ids
    assert all(row["status"] == "search_success" for row in rows)
    assert all(row["prediction_accepted"] for row in rows)
    assert all(row["official_all_pass_rate"] == 100.0 for row in rows)
    trace_checks = []
    for uid in ids:
        case = RUN / "planning" / uid
        compiled = ct.read(case / "compiled_query.json")
        intent = ct.read(case / "intent.json")
        assert compiled["uid"] == uid
        assert all(compiled[key] == intent[key] for key in ("start_city", "target_city", "days", "people_number"))
        # Predicted constraints are allowed in the symbolic planner trace; private
        # official score/source records must not be present in the search trace.
        trace = (case / "tool_trace.jsonl").read_text()
        leaked = [marker for marker in ("official_score", "oracle_translation") if marker in trace]
        assert not leaked, (uid, leaked)
        assert (case / "official_score.json").exists()  # written only after search output
        trace_checks.append({"uid": uid, "compiled_query_keys": sorted(compiled), "private_markers": leaked})

    result = {
        "status": "PASS",
        "scope": "frozen 12-case development baseline; input/denominator audit only",
        "model_calls": 12,
        "public_input_cases": len(request_checks),
        "public_input_keys_only": True,
        "collection_complete": 12,
        "planning_cases": len(rows),
        "planning_search_successes": sum(r["status"] == "search_success" for r in rows),
        "accepted_predictions": sum(r["prediction_accepted"] for r in rows),
        "official_all_pass_cases": sum(r["official_all_pass_rate"] == 100.0 for r in rows),
        "full_denominator": 12,
        "excluded_from_denominator": [],
        "request_private_marker_hits": 0,
        "search_trace_private_marker_hits": 0,
        "request_checks": request_checks,
        "trace_checks": trace_checks,
        "conclusion": "No input leakage or denominator omission observed; 100% is 12/12 for this diagnostic slice, not benchmark evidence.",
        "artifact_hashes": {name: sha(RUN / name) for name in (
            "preregistration.json", "public_inputs.json", "collection_retry1.json",
            "final_audit.json", "planning/summary.json")},
    }
    ct.write(RUN / "input_isolation_audit.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
