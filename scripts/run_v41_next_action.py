#!/usr/bin/env python3
"""Runner for LLMAP transfer experiment and multi-model next actions.

Implements P0 through P4 per docs/guides/AGY_NEXT_ACTION_DS_QWEN_TRANSFER_20260913.md:
- preflight: verify keys, models, configs, inputs, frozen prompts
- health_check: run 5 Dev samples (20 logical calls) for API/schema/solver validation
- collect: run 40 Eval samples (480 mechanism calls + 40 system baseline calls = 520 calls)
- evaluate: compute joint metrics (system level + mechanism level B0/B3/B4/DARC/B6)
- replay: true offline re-computation and hash integrity check
- status: inspect execution progress and budget counters
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.baselines.llmap_adapted import (
    build_llmap_graph,
    compute_composite_utility,
    evaluate_llmap_path,
    msgs_adapted,
)
from src.intent import Intent

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "9-AutoDriving-core" / "data" / "llmap_transfer"
PROMPTS_DIR = ROOT / "9-AutoDriving-core" / "prompts" / "v5"
CONFIGS_DIR = ROOT / "9-AutoDriving-core" / "configs" / "v5"
RESULTS_BASE = ROOT / "9-AutoDriving-core" / "results" / "v4_1" / "next_action_20260913"


def get_git_commit() -> str:
    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"


def load_json(path: Path | str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path | str, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(f".tmp_{int(time.time() * 1000)}")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(p)


import threading
import concurrent.futures

class LLMCaller:
    """Performs HTTP LLM calls with strict attempt logging, 1-retry limit, and circuit breaker."""

    def __init__(self, config_path: Path, run_dir: Path):
        self.config_path = config_path
        self.run_dir = run_dir
        self.attempts_dir = run_dir / "attempts"
        self.attempts_dir.mkdir(parents=True, exist_ok=True)

        with open(config_path, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.api_key_env = self.cfg.get("api_key_env", "DEEPSEEK_API_KEY")
        self.api_key = os.environ.get(self.api_key_env, "")
        if not self.api_key:
            raise ValueError(f"Environment variable {self.api_key_env} is not set!")

        self.base_url = self.cfg.get("base_url", "https://api.deepseek.com").rstrip("/")
        self.model = self.cfg.get("model", "deepseek-v4-flash")
        self.timeout = self.cfg.get("timeout", 60)
        self.temperature = self.cfg.get("temperature", 0.0)

        self.lock = threading.Lock()
        self.recent_attempts: list[bool] = []  # True for success, False for transmission error

    def call(self, call_id: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Execute a single logical call with max 1 transmission retry and attempt logging."""
        with self.lock:
            if len(self.recent_attempts) >= 20:
                fail_rate = self.recent_attempts[-20:].count(False) / 20.0
                if fail_rate >= 0.20:
                    raise RuntimeError(f"Circuit breaker triggered: transmission failure rate {fail_rate*100:.1f}% >= 20%!")

        max_attempts = 2  # 1 initial + max 1 transmission retry
        last_error = None
        attempt_record: dict[str, Any] = {}

        for attempt_idx in range(1, max_attempts + 1):
            attempt_file = self.attempts_dir / f"{call_id}_attempt_{attempt_idx}.json"
            if attempt_file.exists():
                attempt_record = load_json(attempt_file)
                if attempt_record.get("status") == "success":
                    self.recent_attempts.append(True)
                    return attempt_record

            t0 = time.time()
            iso_start = datetime.now(timezone.utc).isoformat()
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
            }

            req_bytes = json.dumps(payload).encode("utf-8")
            url = f"{self.base_url}/chat/completions"
            req = urllib.request.Request(
                url,
                data=req_bytes,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    duration = time.time() - t0
                    choice = resp_data.get("choices", [{}])[0]
                    content = choice.get("message", {}).get("content", "")

                    attempt_record = {
                        "call_id": call_id,
                        "attempt_idx": attempt_idx,
                        "status": "success",
                        "start_time": iso_start,
                        "duration_sec": duration,
                        "status_code": resp.status,
                        "requested_model": self.model,
                        "returned_model": resp_data.get("model", ""),
                        "raw_response": content,
                        "usage": resp_data.get("usage", {}),
                        "request_payload": {
                            "model": self.model,
                            "temperature": self.temperature,
                            "messages": payload["messages"],
                        },
                    }
                    save_json(attempt_file, attempt_record)
                    self.recent_attempts.append(True)
                    return attempt_record

            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
                duration = time.time() - t0
                status_code = getattr(exc, "code", None)
                error_msg = str(exc)
                attempt_record = {
                    "call_id": call_id,
                    "attempt_idx": attempt_idx,
                    "status": "transmission_error",
                    "start_time": iso_start,
                    "duration_sec": duration,
                    "status_code": status_code,
                    "error_message": error_msg,
                    "requested_model": self.model,
                }
                save_json(attempt_file, attempt_record)
                self.recent_attempts.append(False)
                last_error = exc
                if attempt_idx < max_attempts:
                    time.sleep(1.0)
                    continue

        raise RuntimeError(f"Logical call {call_id} failed after {max_attempts} attempts: {last_error}")


def extract_json_object(raw_text: str) -> dict[str, Any] | None:
    """Extract a JSON object from raw response string safely."""
    if not raw_text:
        return None
    raw = raw_text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def parse_intent_safe(data: dict[str, Any] | None) -> Intent | None:
    """Parse intent safely, returning None on schema/semantic error."""
    if not data or not isinstance(data, dict):
        return None
    # If nested under 'intent'
    candidate = data.get("intent", data)
    try:
        return Intent.parse(candidate)
    except Exception:
        return None


def run_preflight() -> int:
    print("=== PREFLIGHT CHECK ===")
    commit = get_git_commit()
    print(f"Git Commit: {commit}")

    # Check data files
    for fname in ["dev_5_utterances.json", "dev_5_scenarios.json", "eval_40_utterances.json", "eval_40_scenarios.json"]:
        p = DATA_DIR / fname
        if not p.exists():
            print(f"ERROR: Missing data file {p}")
            return 1
        data = load_json(p)
        print(f"Loaded {fname}: {len(data)} items")

    # Check prompts
    for pname in ["parse_a.txt", "parse_b.txt", "review_plain.txt", "llmap_direct_original.txt", "llmap_user_original.txt"]:
        p = PROMPTS_DIR / pname
        if not p.exists():
            print(f"ERROR: Missing prompt file {p}")
            return 1
        print(f"Prompt {pname}: {p.stat().st_size} bytes")

    # Check config
    cfg_file = CONFIGS_DIR / "deepseek_official_v4_flash.json"
    if not cfg_file.exists():
        print(f"ERROR: Missing config {cfg_file}")
        return 1
    cfg = load_json(cfg_file)
    api_key_set = bool(os.environ.get(cfg.get("api_key_env", ""), ""))
    print(f"Model config: provider={cfg.get('provider')}, model={cfg.get('model')}, base_url={cfg.get('base_url')}")
    print(f"API Key present ({cfg.get('api_key_env')}): {api_key_set}")
    if not api_key_set:
        print("ERROR: API key environment variable is not set!")
        return 1

    print("Preflight SUCCESS! All required assets verified.")
    return 0


def execute_pipeline(
    split: str,  # 'dev' or 'eval'
    run_dir: Path,
    caller: LLMCaller,
    prompt_a: str,
    prompt_b: str,
    prompt_rev: str,
    prompt_llmap_sys: str,
    prompt_llmap_user: str,
    concurrency: int = 4,
) -> dict[str, Any]:
    """Run extraction, review, and solver pipeline for the given dataset split."""
    run_dir.mkdir(parents=True, exist_ok=True)
    records_dir = run_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    utt_file = DATA_DIR / f"{split}_{5 if split == 'dev' else 40}_utterances.json"
    sc_file = DATA_DIR / f"{split}_{5 if split == 'dev' else 40}_scenarios.json"

    utterances = load_json(utt_file)
    scenarios = load_json(sc_file)

    # For dev split, strictly use the 5 original V0 instructions (5 x 4 = 20 calls) per Section 6.2
    if split == "dev":
        utterances = [u for u in utterances if u["variant_type"] == "V0"]

    expected_ids = [u["utterance_id"] for u in utterances]
    save_json(run_dir / "expected_ids.json", expected_ids)

    # Save manifest
    manifest = {
        "split": split,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "model": caller.model,
        "base_url": caller.base_url,
        "utterances_count": len(utterances),
        "scenarios_count": len(scenarios),
        "concurrency": concurrency,
    }
    save_json(run_dir / "manifest.json", manifest)

    results_by_id: dict[str, Any] = {}

    print(f"Starting {split} execution on {len(utterances)} utterances (concurrency={concurrency})...", flush=True)

    def process_single_utterance(utt: dict[str, Any]) -> dict[str, Any]:
        uid = utt["utterance_id"]
        gid = utt["group_id"]
        text = utt["text"]
        vtype = utt["variant_type"]
        sc = scenarios[utt["graph_id"]]
        record_file = records_dir / f"{uid}.json"

        if record_file.exists():
            return load_json(record_file)

        # 1. Candidate A call
        call_id_a = f"{uid}_parse_a"
        user_msg_a = prompt_a.replace("{{instruction}}", text)
        resp_a = caller.call(call_id_a, system_prompt="You extract route-planning intent.", user_prompt=user_msg_a)
        data_a = extract_json_object(resp_a.get("raw_response", ""))
        intent_a = parse_intent_safe(data_a)

        # 2. Candidate B call
        call_id_b = f"{uid}_parse_b"
        user_msg_b = prompt_b.replace("{{instruction}}", text)
        resp_b = caller.call(call_id_b, system_prompt="You extract route-planning intent.", user_prompt=user_msg_b)
        data_b = extract_json_object(resp_b.get("raw_response", ""))
        intent_b = parse_intent_safe(data_b)

        # 3. Review call
        call_id_rev = f"{uid}_review"
        rev_user = prompt_rev.replace("{{instruction}}", text)
        rev_user = rev_user.replace("{{candidate_a}}", json.dumps(data_a or {}, ensure_ascii=False))
        rev_user = rev_user.replace("{{candidate_b}}", json.dumps(data_b or {}, ensure_ascii=False))
        resp_rev = caller.call(call_id_rev, system_prompt="Resolve two candidate interpretations.", user_prompt=rev_user)
        data_rev = extract_json_object(resp_rev.get("raw_response", ""))
        intent_rev = parse_intent_safe(data_rev)

        # 4. LLMAP original parser call (only on V0)
        data_llmap = None
        intent_llmap = None
        if vtype == "V0":
            call_id_llmap = f"{uid}_llmap_orig"
            user_msg_llmap = prompt_llmap_user.replace("{{instruction}}", text)
            resp_llmap = caller.call(call_id_llmap, system_prompt=prompt_llmap_sys, user_prompt=user_msg_llmap)
            data_llmap = extract_json_object(resp_llmap.get("raw_response", ""))
            intent_llmap = parse_intent_safe(data_llmap)

        # 5. Solver evaluations
        def solve_and_eval(intent: Intent | None) -> tuple[dict[str, Any] | None, float]:
            if intent is None:
                return None, -1.0
            t_str = f"{intent.time_limit // 60:02d}:{intent.time_limit % 60:02d}" if intent.time_limit is not None else "None"
            deps = [list(pair) for pair in intent.dependencies]
            graph = build_llmap_graph(
                scenario=sc,
                requested_pois=list(intent.pois),
                time_limit_str=t_str,
                dependencies=deps,
                quality_weight=intent.quality_weight,
                distance_weight=1.0 - intent.quality_weight,
            )
            p, grps, _ = msgs_adapted(graph)
            eval_res = evaluate_llmap_path(graph, p, grps)
            util = compute_composite_utility(eval_res, quality_weight=intent.quality_weight, distance_weight=1.0 - intent.quality_weight)
            return eval_res, util

        eval_a, util_a = solve_and_eval(intent_a)
        eval_b, util_b = solve_and_eval(intent_b)
        eval_rev, util_rev = solve_and_eval(intent_rev)
        eval_llmap, util_llmap = solve_and_eval(intent_llmap) if intent_llmap else (None, -1.0)

        delta_u = abs(util_a - util_b) if (eval_a and eval_b) else 1.0
        # Protection item h: either candidate invalid
        h_flag = 1 if (eval_a is None or not eval_a.get("is_valid", False) or eval_b is None or not eval_b.get("is_valid", False)) else 0

        # Param diff flag
        param_diff = 1 if (intent_a != intent_b) else 0

        rec = {
            "utterance_id": uid,
            "group_id": gid,
            "variant_type": vtype,
            "source_index": utt["source_index"],
            "gold_hard": utt["gold_hard"],
            "w_synthetic": utt["w_synthetic"],
            "intent_a": intent_a.solver_args() if intent_a else None,
            "intent_b": intent_b.solver_args() if intent_b else None,
            "intent_rev": intent_rev.solver_args() if intent_rev else None,
            "intent_llmap": intent_llmap.solver_args() if intent_llmap else None,
            "eval_a": eval_a,
            "eval_b": eval_b,
            "eval_rev": eval_rev,
            "eval_llmap": eval_llmap,
            "util_a": util_a,
            "util_b": util_b,
            "util_rev": util_rev,
            "util_llmap": util_llmap,
            "delta_u": delta_u,
            "h_flag": h_flag,
            "param_diff": param_diff,
        }
        save_json(record_file, rec)
        return rec

    if concurrency <= 1:
        for idx, utt in enumerate(utterances, start=1):
            uid = utt["utterance_id"]
            rec = process_single_utterance(utt)
            results_by_id[uid] = rec
            print(f"[{idx}/{len(utterances)}] Processed {uid} ({utt['variant_type']})...", flush=True)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_utt = {executor.submit(process_single_utterance, u): u for u in utterances}
            completed = 0
            for fut in concurrent.futures.as_completed(future_to_utt):
                u = future_to_utt[fut]
                uid = u["utterance_id"]
                rec = fut.result()
                results_by_id[uid] = rec
                completed += 1
                print(f"[{completed}/{len(utterances)}] Completed {uid} ({u['variant_type']})...", flush=True)

    return results_by_id


def compute_metrics(records: dict[str, Any], budget_fraction: float = 0.10) -> dict[str, Any]:
    """Compute system-level and mechanism-level metrics."""
    utt_ids = sorted(list(records.keys()))
    groups = sorted(list(set(r["group_id"] for r in records.values())))
    N = len(records)
    K = int(round(N * budget_fraction))

    # Identify review selections for policies
    # DARC: prioritize h_flag == 1, then delta_u descending
    sorted_darc = sorted(utt_ids, key=lambda x: (records[x]["h_flag"], records[x]["delta_u"]), reverse=True)
    darc_review_set = set(sorted_darc[:K])

    # B4: prioritize h_flag == 1, then param_diff == 1, then tie-breaking by ID
    sorted_b4 = sorted(utt_ids, key=lambda x: (records[x]["h_flag"], records[x]["param_diff"], x), reverse=True)
    b4_review_set = set(sorted_b4[:K])

    # B3: random selection with fixed seed
    rng = random.Random(20260912)
    # Always include h_flag == 1 first, then random
    h_items = [x for x in utt_ids if records[x]["h_flag"] == 1]
    non_h_items = [x for x in utt_ids if records[x]["h_flag"] == 0]
    rng.shuffle(non_h_items)
    b3_ordered = h_items + non_h_items
    b3_review_set = set(b3_ordered[:K])

    # B6: All review
    b6_review_set = set(utt_ids)

    # B0: No review
    b0_review_set: set[str] = set()

    policies = {
        "B0_no_review": b0_review_set,
        "B3_random": b3_review_set,
        "B4_param_diff": b4_review_set,
        "DARC_delta_u": darc_review_set,
        "B6_all_review": b6_review_set,
    }

    metrics: dict[str, Any] = {
        "N_utterances": N,
        "N_groups": len(groups),
        "budget_K": K,
        "policies": {},
        "system_level_v0": {},
    }

    # 1. Mechanism-level evaluation for each policy
    for pname, r_set in policies.items():
        success_count = 0
        total_utility = 0.0
        group_success: dict[str, list[bool]] = {g: [] for g in groups}
        corrected_count = 0
        degraded_count = 0

        for uid, rec in records.items():
            gid = rec["group_id"]
            # Decision: if uid in r_set, use review; else use A
            if uid in r_set:
                eval_chosen = rec["eval_rev"]
                util_chosen = rec["util_rev"]
                # Fallback to A if rev is invalid and A was valid
                if (eval_chosen is None or not eval_chosen.get("is_valid", False)) and (rec["eval_a"] and rec["eval_a"].get("is_valid", False)):
                    eval_chosen = rec["eval_a"]
                    util_chosen = rec["util_a"]
                # Count corrections and degradations relative to A
                a_valid = rec["eval_a"] is not None and rec["eval_a"].get("is_valid", False)
                rev_valid = eval_chosen is not None and eval_chosen.get("is_valid", False)
                if not a_valid and rev_valid:
                    corrected_count += 1
                elif a_valid and not rev_valid:
                    degraded_count += 1
            else:
                eval_chosen = rec["eval_a"]
                util_chosen = rec["util_a"]

            is_succ = eval_chosen is not None and eval_chosen.get("is_valid", False)
            if is_succ:
                success_count += 1
                total_utility += util_chosen
            else:
                total_utility += -1.0  # standard invalid penalty
            group_success[gid].append(is_succ)

        tsr = (success_count / N * 100.0) if N > 0 else 0.0
        gtsr = sum(1 for g, res in group_success.items() if all(res)) / len(groups) * 100.0 if groups else 0.0
        avg_util = total_utility / N if N > 0 else 0.0

        # Flip calculation: among groups where V0 succeeded, did any variant fail?
        v0_succ_groups = [g for g in groups if records.get(f"{g}_v0", {}).get("eval_a", {}).get("is_valid", False)]
        flip_count = 0
        for g in v0_succ_groups:
            if not all(group_success[g]):
                flip_count += 1
        cond_flip_rate = (flip_count / len(v0_succ_groups) * 100.0) if v0_succ_groups else 0.0
        full_flip_fail = sum(1 for g in groups if not all(group_success[g])) / len(groups) * 100.0 if groups else 0.0

        metrics["policies"][pname] = {
            "TSR_pct": round(tsr, 2),
            "GTSR_pct": round(gtsr, 2),
            "cond_flip_rate_pct": round(cond_flip_rate, 2),
            "full_flip_or_failure_pct": round(full_flip_fail, 2),
            "mean_composite_utility": round(avg_util, 4),
            "reviews_conducted": len(r_set),
            "corrected_count": corrected_count,
            "degraded_count": degraded_count,
        }

    # 2. System-level comparison on V0
    v0_records = [r for r in records.values() if r["variant_type"] == "V0"]
    if v0_records and v0_records[0].get("eval_llmap") is not None:
        def calc_v0_stats(eval_key: str) -> dict[str, Any]:
            covs, lengths, ratings, t_viols, d_viols, a_viols, valids = [], [], [], [], [], [], []
            for r in v0_records:
                ev = r.get(eval_key)
                if ev:
                    covs.append(ev.get("group_coverage", 0.0))
                    lengths.append(ev.get("path_length_km", 0.0))
                    ratings.append(ev.get("avg_rating", 0.0))
                    t_viols.append(ev.get("time_violations_hours", 0.0))
                    d_viols.append(ev.get("dependency_violations", 0))
                    a_viols.append(ev.get("availability_violations", 0))
                    valids.append(1 if ev.get("is_valid", False) else 0)
            n_v0 = len(covs) or 1
            return {
                "count": len(covs),
                "valid_pct": round(sum(valids) / n_v0 * 100.0, 2),
                "mean_group_coverage_pct": round(sum(covs) / n_v0, 2),
                "mean_path_length_km": round(sum(lengths) / n_v0, 2),
                "mean_rating": round(sum(ratings) / n_v0, 2),
                "time_violations_count": sum(1 for t in t_viols if t > 0),
                "dependency_violations_count": sum(d_viols),
                "availability_violations_count": sum(a_viols),
            }

        metrics["system_level_v0"]["LLMAP_adapted_baseline"] = calc_v0_stats("eval_llmap")
        metrics["system_level_v0"]["DARC_pipeline_A"] = calc_v0_stats("eval_a")

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="LLMAP Transfer Experiment Runner")
    parser.add_argument("command", choices=["preflight", "health_check", "collect", "evaluate", "replay", "status"])
    parser.add_argument("--split", choices=["dev", "eval"], default="dev")
    parser.add_argument("--run-dir", type=str, default=None)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--budget", type=float, default=0.10)
    args = parser.parse_args()

    if args.command == "preflight":
        sys.exit(run_preflight())

    # Load prompts
    prompt_a = (PROMPTS_DIR / "parse_a.txt").read_text(encoding="utf-8")
    prompt_b = (PROMPTS_DIR / "parse_b.txt").read_text(encoding="utf-8")
    prompt_rev = (PROMPTS_DIR / "review_plain.txt").read_text(encoding="utf-8")
    prompt_llmap_sys = (PROMPTS_DIR / "llmap_direct_original.txt").read_text(encoding="utf-8")
    prompt_llmap_user = (PROMPTS_DIR / "llmap_user_original.txt").read_text(encoding="utf-8")

    cfg_file = CONFIGS_DIR / "deepseek_official_v4_flash.json"

    if args.command == "health_check":
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = Path(args.run_dir) if args.run_dir else (RESULTS_BASE / f"health_check_dev_{timestamp}")
        caller = LLMCaller(config_path=cfg_file, run_dir=run_dir)

        print(f"Executing Health Check on Dev set (5 samples) in {run_dir}...")
        records = execute_pipeline(
            split="dev",
            run_dir=run_dir,
            caller=caller,
            prompt_a=prompt_a,
            prompt_b=prompt_b,
            prompt_rev=prompt_rev,
            prompt_llmap_sys=prompt_llmap_sys,
            prompt_llmap_user=prompt_llmap_user,
            concurrency=args.concurrency,
        )
        metrics = compute_metrics(records, budget_fraction=0.20)
        save_json(run_dir / "joint_metrics.json", metrics)
        print("Dev Health Check completed successfully!")
        print(json.dumps(metrics, indent=2))
        return

    if args.command == "collect":
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = Path(args.run_dir) if args.run_dir else (RESULTS_BASE / f"transfer_branch_b_{timestamp}")
        caller = LLMCaller(config_path=cfg_file, run_dir=run_dir)

        print(f"Executing Collection on {args.split} in {run_dir} (concurrency={args.concurrency})...")
        records = execute_pipeline(
            split=args.split,
            run_dir=run_dir,
            caller=caller,
            prompt_a=prompt_a,
            prompt_b=prompt_b,
            prompt_rev=prompt_rev,
            prompt_llmap_sys=prompt_llmap_sys,
            prompt_llmap_user=prompt_llmap_user,
            concurrency=args.concurrency,
        )
        metrics = compute_metrics(records, budget_fraction=args.budget)
        save_json(run_dir / "joint_metrics.json", metrics)
        print("Collection completed successfully!")
        print(json.dumps(metrics, indent=2))
        return

    if args.command == "evaluate":
        if not args.run_dir:
            print("ERROR: --run-dir is required for evaluate")
            sys.exit(1)
        run_dir = Path(args.run_dir)
        records_dir = run_dir / "records"
        records = {p.stem: load_json(p) for p in records_dir.glob("*.json")}
        metrics = compute_metrics(records, budget_fraction=args.budget)
        save_json(run_dir / "joint_metrics.json", metrics)
        print(json.dumps(metrics, indent=2))
        return

    if args.command == "replay":
        if not args.run_dir:
            print("ERROR: --run-dir is required for replay")
            sys.exit(1)
        run_dir = Path(args.run_dir)
        print(f"Replaying offline evaluation from records in {run_dir}...")
        records_dir = run_dir / "records"
        records = {p.stem: load_json(p) for p in records_dir.glob("*.json")}
        metrics = compute_metrics(records, budget_fraction=args.budget)
        save_json(run_dir / "replay_joint_metrics.json", metrics)

        # Hash check
        orig_metrics = load_json(run_dir / "joint_metrics.json")
        orig_bytes = json.dumps(orig_metrics, sort_keys=True).encode("utf-8")
        replay_bytes = json.dumps(metrics, sort_keys=True).encode("utf-8")
        orig_hash = hashlib.sha256(orig_bytes).hexdigest()
        replay_hash = hashlib.sha256(replay_bytes).hexdigest()

        print(f"Original hash: {orig_hash}")
        print(f"Replay hash:   {replay_hash}")
        assert orig_hash == replay_hash, "Replay hash mismatch!"
        print("REPLAY VERIFICATION SUCCESS: Output bit-for-bit identical!")
        return

    if args.command == "status":
        if not args.run_dir:
            print("ERROR: --run-dir is required for status")
            sys.exit(1)
        run_dir = Path(args.run_dir)
        attempts = list((run_dir / "attempts").glob("*.json"))
        records = list((run_dir / "records").glob("*.json"))
        expected_ids = load_json(run_dir / "expected_ids.json") if (run_dir / "expected_ids.json").exists() else []
        print(f"Run directory: {run_dir}")
        print(f"Expected IDs: {len(expected_ids)}")
        print(f"Completed records: {len(records)}")
        print(f"Total HTTP attempts logged: {len(attempts)}")


if __name__ == "__main__":
    main()
