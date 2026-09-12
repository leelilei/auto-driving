"""Freeze a 100-call-per-model ChinaTravel cross-model diagnostic.

Coverage is the independently audited 60-case dev slice. Calls 61--100 are
pre-registered repeats, not additional independent cases.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
AUDIT = ROOT / "docs/experiments/chinatravel_setup/semantic_audit_20260911/results/audit.json"
UPSTREAM = ROOT / "external/ChinaTravel/chinatravel/data/dev_split"
OUT = CORE / "data/chinatravel_crossmodel100_20260912"

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, x): Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2) + "\n")

def main():
    if OUT.exists(): raise ValueError(f"Refuse overwrite: {OUT}")
    audit = read(AUDIT)
    rows = sorted(audit["rows"], key=lambda r: r["uid"])
    assert len(rows) == 60
    public = [{"uid": r["uid"], "nature_language": r["nature_language"]} for r in rows]
    source_hashes = {f"external/ChinaTravel/chinatravel/data/dev_split/{r['uid']}.json":
                     sha(UPSTREAM / f"{r['uid']}.json") for r in rows}
    calls = []
    for i in range(100):
        item = public[i] if i < 60 else public[i - 60]
        calls.append({"call_index": i + 1, "uid": item["uid"],
                      "independent_case": i < 60, "repeat_index": 0 if i < 60 else 1})
    OUT.mkdir(parents=True)
    write(OUT / "public_inputs.json", public)
    write(OUT / "call_schedule.json", calls)
    write(OUT / "preregistration.json", {
        "status": "FROZEN_BEFORE_MODEL_CALLS", "date": "2026-09-12",
        "unique_cases": 60, "planned_calls_per_model": 100,
        "models": ["deepseek-v4-flash", "claude-haiku-4-5-20251001"],
        "coverage": "all 60 independently source-audited ChinaTravel dev cases",
        "repeat_policy": "calls 61-100 repeat calls 1-40; repeats are stability diagnostics, not independent denominator cases",
        "input_keys": ["uid", "nature_language"],
        "retry_policy": "at most one separately logged provider retry; no semantic/structural retry",
        "planner": {"search_width": 10, "seconds_per_case": 30, "backend": "unchanged Repair v1"},
        "scope": "cross-model development diagnostic; not benchmark, SOTA, or stage-5 evidence",
        "source_hashes": source_hashes,
    })
    write(OUT / "private_audit_notice.json", {
        "warning": "Audit annotations are not model inputs.",
        "audit_source": str(AUDIT.relative_to(ROOT)),
        "audited_cases": 60,
        "model_input_keys": ["uid", "nature_language"],
    })
    write(OUT / "manifest.json", {
        "public_inputs_sha256": sha(OUT / "public_inputs.json"),
        "call_schedule_sha256": sha(OUT / "call_schedule.json"),
        "source_script_sha256": sha(Path(__file__)),
    })
    print(json.dumps({"status":"FROZEN", "unique_cases":60, "calls_per_model":100,
                      "total_calls":200, "repeated_calls_per_model":40}, ensure_ascii=False))

if __name__ == "__main__": main()
