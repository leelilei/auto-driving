"""Freeze the 12-case ChinaTravel baseline diagnostic before model calls."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
FIXED6 = CORE / "data/chinatravel_stage3_fixed6/public_inputs.json"
AUDIT = ROOT / "docs/experiments/chinatravel_setup/semantic_audit_20260911/results/audit.json"
MANIFEST = ROOT / "docs/experiments/chinatravel_setup/semantic_audit_20260911/results/manifest.json"
CANONICAL = ROOT / "external/ChinaTravel/chinatravel/data/dev_split"
OUT = CORE / "data/chinatravel_baseline12_20260912"


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise ValueError("Refuse overwrite: " + str(OUT))
    fixed = {item["uid"] for item in read(FIXED6)}
    manifest = read(MANIFEST)
    ordered = manifest["expected_ids"]
    assert len(ordered) == 60 and len(set(ordered)) == 60
    selected = [uid for uid in ordered if uid not in fixed][:12]
    assert len(selected) == 12 and not fixed.intersection(selected)

    public = []
    source_hashes = {}
    for uid in selected:
        source = CANONICAL / f"{uid}.json"
        item = read(source)
        public.append({"uid": uid, "nature_language": item["nature_language"]})
        source_hashes[str(source.relative_to(ROOT))] = sha(source)

    audit_rows = {row["uid"]: row for row in read(AUDIT)["rows"]}
    private_review = []
    for uid in selected:
        row = audit_rows[uid]
        private_review.append({
            "uid": uid,
            "tag": row["tag"],
            "request_fields": [req["field"] for req in row["requirements"]],
            "source_quotes": [{"field": req["field"], "quote": req["quote"]}
                              for req in row["requirements"]],
            "current_interface_gaps": row["current_interface_gaps"],
            "evaluation_issues": row["evaluation_issues"],
            "review_status": "pre_call_source_review_from_20260911_audit",
        })

    OUT.mkdir(parents=True)
    write(OUT / "public_inputs.json", public)
    write(OUT / "private_field_coverage_review.json", {
        "warning": "Contains source-audit annotations; never load in the model collector.",
        "rows": private_review,
    })
    write(OUT / "preregistration.json", {
        "status": "FROZEN_BEFORE_MODEL_CALLS",
        "date": "2026-09-12",
        "n": 12,
        "selection_rule": "First 12 UIDs in audited manifest expected_ids order after excluding fixed6; no outcome, difficulty, solvability, or tag filtering.",
        "selected_ids": selected,
        "excluded_prior_fixed6": sorted(fixed),
        "model_input_keys": ["uid", "nature_language"],
        "planned_model": "DeepSeek official API request model deepseek-v4-flash",
        "planned_calls": 12,
        "retries": "At most one retry for network/provider failure; never retry a semantic or structural response.",
        "planning": {"search_width": 10, "seconds_per_case": 30, "strategy": "unchanged Repair v1 backend"},
        "scope": "development baseline error-distribution diagnostic; not benchmark, SOTA, or DARC evidence",
        "source_hashes": source_hashes,
    })
    hashes = {name: sha(OUT / name) for name in (
        "public_inputs.json", "private_field_coverage_review.json", "preregistration.json")}
    write(OUT / "frozen_hashes.json", hashes)
    print(json.dumps({"status": "FROZEN", "n": len(selected), "ids": selected,
                      "public_inputs_sha256": hashes["public_inputs.json"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
