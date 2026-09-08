"""Evaluation metrics, statistics, and paired bootstrap estimation for DARC-Route.

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 9:
- TSR: Task Success Rate (mean of binary task success over all utterances, all failures retained)
- GTSR: Group Task Success Rate (all 4 variants in group must succeed)
- Variant TSR: breakdown by V0, V1, V2, V3
- Route Flip: proportion of differing valid POI sequences across 6 variant pairs per group
- POI F1 & Dependency F1 (on transitive closure)
- Calibrated Utility Loss L_U: (U_weval(r*) - U_weval(r)) / 2 for successful runs with evaluable preference
- Gating diagnostics: corrected, harmed, unchanged, protection triggers, utility triggers
- Paired bootstrap confidence intervals (resampling by group, 2,000 iterations, seed 20260906)
- Cost accounting: provider tokens vs estimated tokens, deployment calls vs experiment attempts
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from src.intent import Intent, closure


def compute_tsr(records: list[dict[str, Any]]) -> float:
    """Task Success Rate across all records. All failures stay in denominator."""
    if not records:
        return 0.0
    successes = sum(1 for r in records if r.get("task_success", False))
    return successes / float(len(records))


def compute_gtsr(records: list[dict[str, Any]]) -> float:
    """Group Task Success Rate. A group succeeds iff all 4 variants succeed."""
    groups = defaultdict(list)
    for r in records:
        gid = r.get("group_id", "unknown")
        groups[gid].append(r.get("task_success", False))

    if not groups:
        return 0.0

    group_successes = sum(1 for gid, res in groups.items() if len(res) == 4 and all(res))
    return group_successes / float(len(groups))


def compute_variant_tsr(records: list[dict[str, Any]]) -> dict[str, float]:
    """Breakdown of TSR by variant type (V0, V1, V2, V3)."""
    by_variant = defaultdict(list)
    for r in records:
        v = r.get("variant_type", r.get("variant", "V0"))
        by_variant[v].append(r.get("task_success", False))

    res = {}
    for v in ["V0", "V1", "V2", "V3"]:
        vals = by_variant.get(v, [])
        res[v] = sum(1 for x in vals if x) / float(len(vals)) if vals else 0.0
    return res


def compute_route_flip(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute Route Flip metric per EXPERIMENT_GUIDE.md Section 9.1.

    For each group of 4 variants, examine all 6 pairs (Va, Vb).
    Only evaluate flip on pairs where BOTH routes are valid.
    A group flip rate is the mean over valid pairs. Groups with 0 valid pairs are NA.
    """
    groups = defaultdict(dict)
    for r in records:
        gid = r.get("group_id", "unknown")
        v = r.get("variant_type", r.get("variant", "V0"))
        # Save route details: valid boolean and poi_ids tuple
        route = r.get("route") or {}
        is_valid = route.get("is_valid", False) if isinstance(route, dict) else getattr(route, "is_valid", False)
        poi_ids = tuple(route.get("poi_ids", ())) if isinstance(route, dict) else tuple(getattr(route, "poi_ids", ()))
        groups[gid][v] = {"is_valid": is_valid, "poi_ids": poi_ids}

    variants = ["V0", "V1", "V2", "V3"]
    group_flips = []
    total_pairs = 0
    valid_pairs = 0
    differing_pairs = 0
    invalid_pairs = 0

    for gid, var_dict in groups.items():
        curr_valid_pairs = 0
        curr_diff_pairs = 0

        for i in range(len(variants)):
            for j in range(i + 1, len(variants)):
                v_i, v_j = variants[i], variants[j]
                if v_i not in var_dict or v_j not in var_dict:
                    continue
                total_pairs += 1
                r_i = var_dict[v_i]
                r_j = var_dict[v_j]

                if r_i["is_valid"] and r_j["is_valid"]:
                    valid_pairs += 1
                    curr_valid_pairs += 1
                    if tuple(r_i["poi_ids"]) != tuple(r_j["poi_ids"]):
                        differing_pairs += 1
                        curr_diff_pairs += 1
                else:
                    invalid_pairs += 1

        if curr_valid_pairs > 0:
            group_flips.append(curr_diff_pairs / float(curr_valid_pairs))

    mean_flip = sum(group_flips) / float(len(group_flips)) if group_flips else None
    return {
        "mean_route_flip": round(mean_flip, 4) if mean_flip is not None else None,
        "valid_groups_count": len(group_flips),
        "total_groups_count": len(groups),
        "valid_pairs_count": valid_pairs,
        "total_pairs_count": total_pairs,
        "invalid_pairs_ratio": round(invalid_pairs / float(total_pairs), 4) if total_pairs > 0 else 0.0,
    }


def compute_intent_f1(records: list[dict[str, Any]]) -> dict[str, float]:
    """Compute POI F1, Dependency F1, and Deadline exact match."""
    poi_f1_list = []
    dep_f1_list = []
    time_matches = []

    for r in records:
        pred_intent = r.get("predicted_intent") or {}
        gold_intent = r.get("gold_intent") or {}

        # 1. POI F1
        pred_pois = set(pred_intent.get("pois", []))
        gold_pois = set(gold_intent.get("pois", []))

        if not pred_pois and not gold_pois:
            poi_f1 = 1.0
        elif not pred_pois or not gold_pois:
            poi_f1 = 0.0
        else:
            tp = len(pred_pois & gold_pois)
            p = tp / float(len(pred_pois))
            rec = tp / float(len(gold_pois))
            poi_f1 = (2 * p * rec) / (p + rec) if (p + rec) > 0 else 0.0
        poi_f1_list.append(poi_f1)

        # 2. Dependency F1 on transitive closures
        pred_raw_deps = pred_intent.get("dependencies", [])
        gold_raw_deps = gold_intent.get("dependencies", [])

        try:
            pred_closure = set(closure([tuple(d) for d in pred_raw_deps if len(d) == 2]))
        except Exception:
            pred_closure = set()

        try:
            gold_closure = set(closure([tuple(d) for d in gold_raw_deps if len(d) == 2]))
        except Exception:
            gold_closure = set()

        if not pred_closure and not gold_closure:
            dep_f1 = 1.0
        elif not pred_closure or not gold_closure:
            dep_f1 = 0.0
        else:
            tp_d = len(pred_closure & gold_closure)
            p_d = tp_d / float(len(pred_closure))
            rec_d = tp_d / float(len(gold_closure))
            dep_f1 = (2 * p_d * rec_d) / (p_d + rec_d) if (p_d + rec_d) > 0 else 0.0
        dep_f1_list.append(dep_f1)

        # 3. Deadline exact match
        p_t = pred_intent.get("time_limit")
        g_t = gold_intent.get("time_limit")
        time_matches.append(1.0 if p_t == g_t else 0.0)

    return {
        "poi_f1": round(sum(poi_f1_list) / float(len(poi_f1_list)), 4) if poi_f1_list else 0.0,
        "dependency_f1": round(sum(dep_f1_list) / float(len(dep_f1_list)), 4) if dep_f1_list else 0.0,
        "time_exact_match": round(sum(time_matches) / float(len(time_matches)), 4) if time_matches else 0.0,
    }


def compute_calibrated_utility_loss(
    records: list[dict[str, Any]],
    weight_mapping: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Compute calibrated utility loss L_U = (U_weval(r*) - U_weval(r)) / 2.

    Only computed for samples where:
    - Gold task was completely satisfied (task_success == True)
    - Preference direction is evaluable (direction in quality_first, balanced, distance_first, not unclear)
    """
    if weight_mapping is None:
        weight_mapping = {
            "quality_first": 0.75,
            "balanced": 0.50,
            "distance_first": 0.25,
        }

    losses = []
    evaluable_count = 0

    for r in records:
        if not r.get("task_success", False):
            continue
        pref_dir = r.get("preference_direction")
        if pref_dir not in weight_mapping:
            continue

        evaluable_count += 1
        w_eval = weight_mapping[pref_dir]

        oracle_u = r.get("oracle_utility")
        actual_u = r.get("actual_utility")
        if oracle_u is not None and actual_u is not None:
            loss = max(0.0, (float(oracle_u) - float(actual_u)) / 2.0)
            losses.append(loss)

    mean_loss = sum(losses) / float(len(losses)) if losses else None
    return {
        "mean_calibrated_loss": round(mean_loss, 4) if mean_loss is not None else None,
        "evaluable_samples_count": evaluable_count,
        "evaluated_losses_count": len(losses),
    }


def compute_gating_diagnostics(
    records_b0: list[dict[str, Any]],
    records_eval: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute gating diagnostic breakdown: corrected, harmed, unchanged, trigger counts."""
    assert len(records_b0) == len(records_eval), "Mismatched record lists for gating diagnostics"

    corrected = 0
    harmed = 0
    unchanged = 0
    h_triggers = 0
    utility_triggers = 0
    no_triggers = 0
    unneeded_triggers = 0
    omitted_errors = 0

    for r_b0, r_ev in zip(records_b0, records_eval):
        succ_b0 = bool(r_b0.get("task_success", False))
        succ_ev = bool(r_ev.get("task_success", False))

        if not succ_b0 and succ_ev:
            corrected += 1
        elif succ_b0 and not succ_ev:
            harmed += 1
        else:
            unchanged += 1

        meta = r_ev.get("gating_meta") or {}
        trig = meta.get("review_triggered", False)
        reason = meta.get("trigger_reason", "none")

        if "protection_h" in reason or meta.get("h", 0) == 1:
            h_triggers += 1
        elif "utility_discrepancy" in reason:
            utility_triggers += 1
        else:
            no_triggers += 1

        if trig and succ_b0 and succ_ev:
            unneeded_triggers += 1
        if not trig and not succ_b0:
            omitted_errors += 1

    return {
        "corrected_count": corrected,
        "harmed_count": harmed,
        "net_gain": corrected - harmed,
        "unchanged_count": unchanged,
        "protection_h_triggers": h_triggers,
        "utility_triggers": utility_triggers,
        "no_triggers": no_triggers,
        "unneeded_triggers": unneeded_triggers,
        "omitted_errors": omitted_errors,
    }


def compute_paired_bootstrap(
    group_diffs: list[float],
    num_samples: int = 2000,
    seed: int = 20260906,
) -> tuple[float, float, float]:
    """Compute mean paired difference and 95% bootstrap confidence interval [ci_lower, ci_upper].

    Resamples whole groups (not individual utterances).
    """
    if not group_diffs:
        return 0.0, 0.0, 0.0

    rng = random.Random(seed)
    n = len(group_diffs)
    observed_mean = sum(group_diffs) / float(n)

    boot_means = []
    for _ in range(num_samples):
        sample = [rng.choice(group_diffs) for _ in range(n)]
        boot_means.append(sum(sample) / float(n))

    boot_means.sort()
    ci_lower = boot_means[int(0.025 * num_samples)]
    ci_upper = boot_means[int(0.975 * num_samples)]

    return round(observed_mean, 4), round(ci_lower, 4), round(ci_upper, 4)
