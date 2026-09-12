"""Collect one frozen ten-field DeepSeek parse for each baseline12 input."""
import json
import os
import argparse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "9-AutoDriving-core/data/chinatravel_baseline12_20260912"
INPUTS = RUN / "public_inputs.json"
FIELDS = ("start_city", "target_city", "days", "people_number", "budget", "room_count",
          "room_type", "cuisine", "intercity_mode", "attraction_category")
SYSTEM = """Extract the explicitly requested travel constraints and return exactly one JSON object.
Required keys: start_city,target_city,days,people_number,budget,room_count,room_type,cuisine,intercity_mode,attraction_category.
Use null only when the query does not specify a field. Do not plan an itinerary.
Dataset party convention: 我计划/我打算/我想 without a companion means 1; 我和朋友/男朋友/女朋友 means 2; 我们N个人 means N.
room_type is 1 for 单床房 and 2 for 双床房. intercity_mode is train or airplane.
Only extract an explicit cuisine or attraction category; do not invent proxies. No markdown or commentary."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-failed", action="store_true",
                        help="retry provider failures into collection_retry1.json")
    args = parser.parse_args()
    out = RUN / ("collection_retry1.json" if args.retry_failed else "collection.json")
    if out.exists():
        raise ValueError("Refuse overwrite: " + str(out))
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY unavailable")
    public = json.loads(INPUTS.read_text())
    assert len(public) == 12 and all(set(item) == {"uid", "nature_language"} for item in public)
    records = []
    for item in public:
        body = {"model": "deepseek-v4-flash", "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(item, ensure_ascii=False)}],
            "temperature": 0, "max_tokens": 700, "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"}}
        record = {"uid": item["uid"], "request": body, "logical_request": 1, "status": "STARTED"}
        try:
            request = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
                data=json.dumps(body, ensure_ascii=False).encode(), method="POST",
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=60) as response:
                envelope = json.loads(response.read().decode())
            record["provider_response"] = envelope
            parsed = json.loads(envelope["choices"][0]["message"]["content"])
            if set(parsed) != set(FIELDS):
                raise ValueError("JSON keys mismatch")
            record.update(status="COMPLETE", parsed_intent=parsed)
        except Exception as exc:
            record.update(status="FAILED", error_type=type(exc).__name__, error=str(exc))
        records.append(record)
    report = {
        "status": "COLLECTED",
        "provider": "official DeepSeek",
        "request_model": "deepseek-v4-flash",
        "logical_model_calls": len(records),
        "complete": sum(row["status"] == "COMPLETE" for row in records),
        "retry_policy": "No retry for semantic/structural output; provider failures eligible for one separately logged retry.",
        "prompt_policy": "Frozen Repair v1 ten-field prompt with disclosed dataset party convention",
        "records": records,
    }
    report["retry_of"] = "collection.json" if args.retry_failed else None
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"logical_model_calls": len(records), "complete": report["complete"],
                      "statuses": [(row["uid"], row["status"]) for row in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
