"""Bounded local planning for the frozen baseline12 DeepSeek parses."""
import contextlib
import copy
import io
import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
RUN = CORE / "data/chinatravel_baseline12_20260912"
SOURCE = RUN / "collection_retry1.json"
OUT = RUN / "planning"
CANONICAL = ROOT / "external/ChinaTravel/chinatravel/data/dev_split"
sys.path.insert(0, str(CORE / "scripts"))
import chinatravel_parse_plan_v4 as v4
import chinatravel_pipeline_v3 as ct
from chinatravel_plan_schema_adapter import adapt
from chinatravel_symbolic_backend import MealStateRuleAgent, NoModel, TracedWorldEnv


def score(query, plan):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return ct.json_safe(ct.v1.evaluate({query['uid']: query}, {query['uid']: plan}))


def main():
    if OUT.exists():
        raise ValueError("Refuse overwrite: " + str(OUT))
    OUT.mkdir()
    source = ct.read(SOURCE)
    assert source["complete"] == 12
    rows = []
    for record in source["records"]:
        uid = record["uid"]
        case = OUT / uid
        case.mkdir()
        intent = v4.validate(record["parsed_intent"], "")
        constraints = v4.compile_extended(intent)
        query = {key: intent[key] for key in ("start_city", "target_city", "days", "people_number")}
        query.update(uid=uid, hard_logic_py=constraints)
        ct.write(case / "intent.json", intent)
        ct.write(case / "compiled_query.json", query)
        started = time.monotonic(); raw = {}; success = False
        with (case / "search.log").open("w") as log, (case / "tool_trace.jsonl").open("w") as trace, ct.offline(), contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            env = TracedWorldEnv(trace)
            agent = MealStateRuleAgent(env=env, backbone_llm=NoModel(), cache_dir=str(case / "cache"), log_dir=str(case / "logs"), search_width=10, debug=False)
            agent.TIME_CUT = 30
            try:
                with ct.deadline(30):
                    success, raw = agent.symbolic_search(copy.deepcopy(query))
                status = "search_success" if success else "search_failed"
            except Exception as exc:
                status = "search_error:" + type(exc).__name__
                (case / "error.txt").write_text(str(exc))
        adapted, changes = adapt(raw)
        accepted = adapted if success and ct.valid_plan(adapted) else {}
        ct.write(case / "raw_search_return.json", raw)
        ct.write(case / "adapted_plan.json", adapted)
        ct.write(case / "schema_changes.json", changes)
        ct.write(case / "prediction.json", accepted)
        official = ct.read(CANONICAL / f"{uid}.json")
        official_score = score(official, accepted)
        ct.write(case / "official_score.json", official_score)
        row = {"uid": uid, "status": status, "seconds": time.monotonic() - started,
               "tool_calls": len(env.results), "tool_errors": sum(not x["success"] for x in env.results),
               "raw_schema_valid": ct.valid_plan(raw), "adapted_schema_valid": ct.valid_plan(adapted),
               "schema_changes": len(changes), "prediction_accepted": bool(accepted),
               "official_all_pass_rate": official_score["all_pass_rate"]}
        ct.write(case / "summary.json", row); rows.append(row)
    ct.write(OUT / "summary.json", {"status": "BASELINE12_PLANNING_COMPLETE", "model_api_calls": 0,
        "search_seconds_per_case": 30, "search_width": 10, "adapter": "room_type numeric-string coercion only", "cases": rows})
    print(json.dumps({"status": "BASELINE12_PLANNING_COMPLETE", "cases": rows}, ensure_ascii=False))


if __name__ == "__main__":
    main()
