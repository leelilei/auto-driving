# DARC-Route Pilot Gate Admission & Leakage Verification Report (R5)

> Date: 2026-09-07
> Overall Status: **`BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION`**
> Standard: CODEX_REMEDIATION_REVIEW_20260907.md Section 5 Compliance

## 1. Programmatic Admission Decision Summary

| Gate / Check | Scope | Programmatic Verdict | Evidence & Rationale |
|---|---|---|---|
| **Gate A (Pilot Accuracy & Review)** | Dev Pilot (80 utterances) | `NOT_MET_TSR_NET_GAIN` | TSR at ceiling (97.50%, 2 errors), net correction is 0, and regret worsened by +0.000641 (+35.2%), though Route Flip improved by -0.0416 (-22.7%). Empirical trade-off observed rather than strict net gain. |
| **Gate B (Calibration Efficiency)** | Dev Calibration (80 utterances) | `PASS_FLIP_REDUCTION` | Ours achieves lowest Route Flip (0.1083, -40.9% vs B0) at 2.09 calls/req. Note compute is higher than B5 (2.04) and regret (0.001991) is slightly higher than B4 (0.001829). |
| **Data Isolation & Leakage** | Dev (40 groups) vs Test (160 groups) | `PASS` | Cluster overlap: 0, Index overlap: 0, Closure leakage: 0. |
| **Overall Project Admission** | Full Benchmark Pipeline | **`BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION`** | Human annotation pending (Test: 640/640, Pilot: 80/80) | Gate A net gain requirement not satisfied (net correction = 0, regret +35.2% on pilot) | Confirmatory benchmark requires fresh API collection on audited v2 dataset |

## 2. Gate A Pilot Re-Test Results (Metric v2)

- **Pilot Run ID**: `20260905T182600Z_pilot_e1`
- **Evaluated**: 20 groups × 4 variants = 80 utterances

| Method | TSR v2 | GTSR v2 | Route Flip v2 | Regret v2 | Mean Calls | Review Rate $q$ |
|---|---|---|---|---|---|---|
| **B0** | 0.9750 (78/80) | 0.9000 | 0.1833 | 0.001822 | 1.0000 | 0.0000 |
| **B2** | 0.9750 (78/80) | 0.9000 | 0.1833 | 0.001822 | 2.0000 | 0.0000 |
| **B5** | 0.9750 (78/80) | 0.9000 | 0.1833 | 0.001822 | 2.0375 | 0.0375 |
| **B6** | 0.9750 (78/80) | 0.9000 | 0.0583 | 0.002375 | 3.0000 | 1.0000 |
| **Ours** | 0.9750 (78/80) | 0.9000 | 0.1417 | 0.002463 | 2.0875 | 0.0875 |

### Gate A Transitions and Error Analysis:
- **Wrong -> Right (Corrections)**: 0
- **Right -> Wrong (Degradations)**: 0
- **Net Error Correction**: 0
- **Route Flip**: B0 `0.1833` -> Ours `0.1417` (-22.7%) -> B6 `0.0583` (-68.2%)
- **Regret Trade-Off**: Ours regret `0.002463` is higher than B0 `0.001822` (+35.2%)

### Pilot Error Case Root Cause Diagnosis:
The 2 errors in the pilot run were independently inspected in raw JSON telemetry:
- **`pilot_03_v2`**: Call A `RuntimeError` (schema_valid=False). Oracle check: `task_success=True`. **Conclusion**: Transient transport/network failure during Call A. **Refutation**: Confirmed NOT an unresolvable temporal window conflict.
- **`pilot_06_v0`**: Call A `RuntimeError` (schema_valid=False). Oracle check: `task_success=True`. **Conclusion**: Transient transport/network failure during Call A. **Refutation**: Confirmed NOT an unresolvable temporal window conflict.

## 3. Gate B Calibration Re-Test Results (Metric v2)

- **Calibration Run ID**: `20260906T035711Z_calibration`
- **Evaluated**: 20 groups × 4 variants = 80 utterances

| Method | Calls/Req | Review Rate $q$ | TSR v2 | GTSR v2 | Route Flip v2 | Regret v2 |
|---|---|---|---|---|---|---|
| **B0** | 1.00 | 0.0000 | 1.0000 | 1.0000 | 0.1833 | 0.002601 |
| **B2** | 2.00 | 0.0000 | 1.0000 | 1.0000 | 0.1833 | 0.002601 |
| **B3** | 2.42 | 0.4250 | 1.0000 | 1.0000 | 0.1583 | 0.002121 |
| **B4** | 2.14 | 0.1375 | 1.0000 | 1.0000 | 0.1333 | 0.001829 |
| **B5** | 2.04 | 0.0375 | 1.0000 | 1.0000 | 0.1583 | 0.002121 |
| **B6** | 3.00 | 1.0000 | 1.0000 | 1.0000 | 0.1417 | 0.002077 |
| **Ours** | 2.09 | 0.0875 | 1.0000 | 1.0000 | 0.1083 | 0.001991 |

### Gate B Multi-Objective Assessment:
- **Route Flip**: Ours achieves `0.1083` (-40.9% vs B0 `0.1833`).
- **Compute Trade-Off**: Ours uses `2.09` calls, slightly higher than B5 `2.04`.
- **Regret Trade-Off**: Ours regret `0.001991` is slightly higher than B4 `0.001829`.
- **Conclusion**: DARC represents a superior balance between paraphrase consistency and compute, rather than an unconstrained win across all single dimensions.

## 4. Historical Sol Runner Telemetry Limitation Disclosure

In `scripts/run_frontier_5model_suite.py`, the outer retry loop for GPT-5.6-sol stored only the final attempt's telemetry (`llm.telemetry[-1]`), omitting telemetry from earlier retry attempts. These historical intermediate attempts cannot be retroactively reconstructed and are transparently recorded as `historical_attempts_unrecoverable`.

## 5. Blocking Items Requiring Resolution Before Final Admission

1. **Real Human Verification**: 640 utterances in Test split and 80 in Pilot split remain `pending_human_review`. Real human double-blind verification must be performed.
2. **Fresh Confirmatory Data Collection**: Historical runs are exploratory-v1 re-analyses. Confirmatory claims require fresh API calls on the finalized v2 dataset once approved.
3. **Paper Writing Gate**: Under `docs/project/EXPERIMENT_FIRST_POLICY.md`, paper writing remains strictly **CLOSED** until all experimental evidence is independently verified and approved by the research director.
