#!/usr/bin/env python3
"""Bounded concurrency probe with one physical request per planned unit."""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.llm_client import LLM, load_config
from src.scene_policy import decode_response_object


def one(config, level: int, index: int) -> dict:
    llm = LLM(config)
    started = time.perf_counter()
    raw = None
    try:
        raw = llm.complete("Return exactly one JSON object. Do not use Markdown fences or explanatory text.", f'Return {{"ok":true,"level":{level},"index":{index}}}.')
        value = decode_response_object(raw)
        valid = value == {"ok": True, "level": level, "index": index}
        return {"index": index, "status": "PASS" if valid else "SCHEMA_FAILED", "raw_response": raw,
                "latency_seconds": time.perf_counter() - started, "telemetry": llm.telemetry[-1]}
    except Exception as exc:
        return {"index": index, "status": "SCHEMA_FAILED" if raw is not None else "TRANSPORT_FAILED", "raw_response":raw,"error_type": type(exc).__name__,
                "error_message": str(exc), "latency_seconds": time.perf_counter() - started,
                "telemetry": llm.telemetry[-1] if llm.telemetry else None}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--levels", type=int, nargs="+", default=[4, 8, 12, 16, 20])
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--transport", choices=["urllib", "curl"])
    args = p.parse_args()
    base = load_config(args.config)
    config = replace(base, retries=0, max_output_tokens=100, transport=args.transport or base.transport)
    report = {"protocol_version": "darc-v5.1-concurrency-probe-1", "model": config.model,
              "config": asdict(config), "started_at": datetime.now(timezone.utc).isoformat(), "levels": []}
    for level in args.levels:
        begun = time.perf_counter()
        with ThreadPoolExecutor(max_workers=level) as pool:
            futures = [pool.submit(one, config, level, index) for index in range(level)]
            attempts = [future.result() for future in as_completed(futures)]
        passed = sum(item["status"] == "PASS" for item in attempts)
        item = {"concurrency": level, "planned": level, "passed": passed,
                "failed": level - passed, "wall_seconds": time.perf_counter() - begun,
                "attempts": sorted(attempts, key=lambda x: x["index"])}
        report["levels"].append(item)
        print(json.dumps({k: item[k] for k in ("concurrency", "planned", "passed", "failed", "wall_seconds")}, indent=2))
        if passed != level:
            break
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["levels"][-1]["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
