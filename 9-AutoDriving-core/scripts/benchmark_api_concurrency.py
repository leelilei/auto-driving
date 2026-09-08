#!/usr/bin/env python3
"""Benchmark maximum concurrent request capacity for the FHL API endpoint.

Tests increasing concurrency levels (4, 8, 12, 16, 20, 25, 30) with lightweight JSON requests.
Measures:
- Success rate (% HTTP 200)
- Error types (429 Rate Limit, 502/503 Gateway, TLS resets, Timeouts)
- Latency distribution (Mean, P50, P90, P95)
- Actual throughput (Requests/sec)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ENDPOINT = "https://www.fhl.mom/v1/chat/completions"
RESOLVE = "www.fhl.mom:443:104.21.224.5"
MODEL = "gpt-5.4-mini"


@dataclass
class CallResult:
    status_code: int
    latency: float
    error: str | None = None
    tokens: int = 0


def make_single_call(api_key: str, prompt_id: int, timeout: int = 30) -> CallResult:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a test agent. Output JSON only."},
            {"role": "user", "content": f'{{"test_id": {prompt_id}, "prompt": "Reply with ok:true in JSON."}}'},
        ],
        "response_format": {"type": "json_object"},
    }
    body_str = json.dumps(payload)

    cmd = [
        "curl",
        "-s",
        "-k",
        "--resolve",
        RESOLVE,
        "-X",
        "POST",
        ENDPOINT,
        "-H",
        f"Authorization: Bearer {api_key}",
        "-H",
        "Content-Type: application/json",
        "-d",
        body_str,
        "-w",
        "\n%{http_code}",
        "--max-time",
        str(timeout),
    ]

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            check=False,
        )
        latency = time.perf_counter() - t0
        if proc.returncode != 0:
            return CallResult(
                status_code=0,
                latency=latency,
                error=f"curl_rc_{proc.returncode}: {proc.stderr.strip()[:80]}",
            )
        stdout = proc.stdout.strip()
        body, sep, code_str = stdout.rpartition("\n")
        if not sep or not code_str.isdigit():
            return CallResult(
                status_code=0,
                latency=latency,
                error=f"malformed_status: {stdout[:80]}",
            )
        code = int(code_str)
        tokens = 0
        if code == 200:
            try:
                data = json.loads(body)
                tokens = data.get("usage", {}).get("total_tokens", 0)
            except Exception:
                pass
            return CallResult(status_code=200, latency=latency, tokens=tokens)
        else:
            return CallResult(
                status_code=code,
                latency=latency,
                error=f"HTTP_{code}: {body[:100]}",
            )
    except subprocess.TimeoutExpired:
        return CallResult(status_code=408, latency=timeout, error="client_timeout")
    except Exception as exc:
        return CallResult(status_code=0, latency=time.perf_counter() - t0, error=str(exc))


def test_concurrency_tier(
    api_key: str,
    concurrency: int,
    total_requests: int,
    timeout: int = 30,
) -> dict[str, Any]:
    print(f"\n--- Testing Concurrency Level: {concurrency} (Sending {total_requests} requests) ---", flush=True)
    results: list[CallResult] = []
    t_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(make_single_call, api_key, i, timeout)
            for i in range(total_requests)
        ]
        for fut in as_completed(futures):
            results.append(fut.result())

    total_time = time.perf_counter() - t_start
    successes = [r for r in results if r.status_code == 200]
    errors = [r for r in results if r.status_code != 200]
    latencies = sorted(r.latency for r in successes) if successes else [0.0]

    p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
    p90 = latencies[int(len(latencies) * 0.90)] if latencies else 0.0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    mean_lat = sum(latencies) / len(latencies) if latencies else 0.0
    rps = len(successes) / total_time if total_time > 0 else 0.0

    err_summary = {}
    for r in errors:
        key = r.error or f"status_{r.status_code}"
        err_summary[key] = err_summary.get(key, 0) + 1

    tier_res = {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "success_count": len(successes),
        "error_count": len(errors),
        "success_rate": round(len(successes) / total_requests, 4),
        "total_time_seconds": round(total_time, 2),
        "rps": round(rps, 2),
        "mean_latency": round(mean_lat, 2),
        "p50_latency": round(p50, 2),
        "p90_latency": round(p90, 2),
        "p95_latency": round(p95, 2),
        "errors": err_summary,
    }

    print(f"  Success Rate: {tier_res['success_rate']*100:.1f}% ({len(successes)}/{total_requests})")
    print(f"  Throughput: {tier_res['rps']} req/sec | Mean Latency: {tier_res['mean_latency']}s | P95: {tier_res['p95_latency']}s")
    if err_summary:
        print(f"  Errors: {err_summary}")

    return tier_res


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--levels",
        type=int,
        nargs="+",
        default=[4, 8, 12, 16, 20, 25, 30],
        help="Concurrency levels to test",
    )
    parser.add_argument("--requests-multiplier", type=int, default=1, help="Requests per concurrency worker (default: 1)")
    parser.add_argument("--timeout", type=int, default=30, help="Per-request timeout")
    args = parser.parse_args()

    api_key = os.environ.get("FHL_API_KEY")
    if not api_key:
        print("Error: FHL_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    print("=== Starting FHL API Concurrency Stress Benchmark ===")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Model: {MODEL}")
    print(f"Levels to test: {args.levels}")

    tier_results = []
    for c in args.levels:
        n_req = max(c, c * args.requests_multiplier)
        res = test_concurrency_tier(api_key, c, n_req, timeout=args.timeout)
        tier_results.append(res)
        # If error rate > 30%, stop ascending
        if res["error_count"] / res["total_requests"] > 0.30:
            print(f"\n[!] Severe degradation at concurrency {c} (Error rate: {res['error_count']/res['total_requests']*100:.1f}%). Stopping higher levels.")
            break
        time.sleep(2)  # Cooldown between tiers

    print("\n" + "=" * 80)
    print("=== FINAL CONCURRENCY BENCHMARK RESULTS TABLE ===")
    print("=" * 80)
    print(f"{'Concurrency':<12} | {'Success':<10} | {'Throughput':<12} | {'Mean Lat (s)':<12} | {'P95 Lat (s)':<12} | {'Errors'}")
    print("-" * 80)
    for t in tier_results:
        err_str = "None" if not t["errors"] else str(t["errors"])
        print(f"{t['concurrency']:<12} | {t['success_count']}/{t['total_requests']:<8} | {t['rps']:<6} req/s | {t['mean_latency']:<12} | {t['p95_latency']:<12} | {err_str}")


if __name__ == "__main__":
    main()
