# DARC-Route: Metric v1 vs Metric v2 Comprehensive Comparison

> Generated in remediation phase R2. Metric v2 enforces exact coordinate-level route distances and unified gold-weight regret calculation.

## 1. Regret & Flip Comparison (v1 vs v2)

### Key Findings:
- **Regret Change Rationale (P0-3)**: In v1, regret was computed via cross-scale subtraction `(oracle_u - actual_u) / 2` where `oracle_u` and `actual_u` used different weight objectives ($w_{\text{gold}}$ vs $w_{\text{pred}}$) and 3-decimal rounded distances. Under Metric v2, both routes are evaluated under the exact same gold quality weight using exact unrounded distances. Consequently, regret drops from ~0.022 to ~0.002–0.003, removing spurious penalty on optimal routes.
- **Property C01 Verification**: Across all models, Baseline B0 and Baseline B2 yield identically matching routes, identical task success, and identical regret.
- **Route Flip Stability**: Route flip values are identical between v1 and v2 because the route solver produces the exact same optimal sequence of POIs for each candidate.

### Model: gpt-5.4-mini (`20260906T051339Z_main_test`)

| Method | TSR v2 | GTSR v2 | Route Flip (v1 / v2) | Regret v1 | Regret v2 | Mean Calls | Review Rate |
|---|---|---|---|---|---|---|---|
| B0 | 1.0000 | 1.0000 | 0.2385 / 0.2385 | 0.022737 | 0.002924 | 1.0000 | 0.0000 |
| B1 | 1.0000 | 1.0000 | 0.2188 / 0.2188 | 0.022327 | 0.002701 | 3.0000 | 0.0000 |
| B2 | 1.0000 | 1.0000 | 0.2385 / 0.2385 | 0.022737 | 0.002924 | 2.0000 | 0.0000 |
| B3 | 1.0000 | 1.0000 | 0.1896 / 0.1896 | 0.022835 | 0.002478 | 2.5094 | 0.5094 |
| B4 | 1.0000 | 1.0000 | 0.2271 / 0.2271 | 0.021288 | 0.002461 | 2.0766 | 0.0766 |
| B5 | 1.0000 | 1.0000 | 0.2385 / 0.2385 | 0.022737 | 0.002924 | 2.0016 | 0.0016 |
| B6 | 1.0000 | 1.0000 | 0.1635 / 0.1635 | 0.021875 | 0.002018 | 3.0000 | 1.0000 |
| Ours | 1.0000 | 1.0000 | 0.2031 / 0.2031 | 0.02177 | 0.002361 | 2.0422 | 0.0422 |

### Model: deepseek-v4-flash (`20260906T081920Z_main_test_deepseek_v4`)

| Method | TSR v2 | GTSR v2 | Route Flip (v1 / v2) | Regret v1 | Regret v2 | Mean Calls | Review Rate |
|---|---|---|---|---|---|---|---|
| B0 | 0.6469 | 0.6062 | 0.095 / 0.095 | 0.033437 | 0.001672 | 1.0000 | 0.0000 |
| B2 | 0.6469 | 0.6062 | 0.095 / 0.095 | 0.033437 | 0.001672 | 2.0000 | 0.0000 |
| B3 | 0.6484 | 0.6062 | 0.1106 / 0.1106 | 0.033872 | 0.001661 | 2.7000 | 0.7000 |
| B4 | 0.6484 | 0.6062 | 0.1075 / 0.1075 | 0.034459 | 0.001538 | 2.4813 | 0.4813 |
| B5 | 0.6484 | 0.6062 | 0.095 / 0.095 | 0.033433 | 0.001668 | 2.3609 | 0.3609 |
| B6 | 0.6484 | 0.6062 | 0.109 / 0.109 | 0.034067 | 0.001448 | 3.0000 | 1.0000 |
| Ours | 0.6484 | 0.6062 | 0.1012 / 0.1012 | 0.033722 | 0.001484 | 2.3797 | 0.3797 |

### Model: qwen38-max (`20260906T123744Z_main_test_qwen38_max`)

| Method | TSR v2 | GTSR v2 | Route Flip (v1 / v2) | Regret v1 | Regret v2 | Mean Calls | Review Rate |
|---|---|---|---|---|---|---|---|
| B0 | 0.9375 | 0.8125 | 0.0865 / 0.0865 | 0.023188 | 0.001466 | 1.0000 | 0.0000 |
| B2 | 0.9375 | 0.8125 | 0.0865 / 0.0865 | 0.023188 | 0.001466 | 2.0000 | 0.0000 |
| B3 | 0.9375 | 0.8125 | 0.0928 / 0.0928 | 0.023199 | 0.001544 | 2.5625 | 0.5625 |
| B4 | 0.9375 | 0.8125 | 0.0865 / 0.0865 | 0.023188 | 0.001466 | 2.1047 | 0.1047 |
| B5 | 0.9375 | 0.8125 | 0.0865 / 0.0865 | 0.023188 | 0.001466 | 2.0969 | 0.0969 |
| B6 | 0.9375 | 0.8125 | 0.0897 / 0.0897 | 0.022914 | 0.001461 | 3.0000 | 1.0000 |
| Ours | 0.9375 | 0.8125 | 0.0897 / 0.0897 | 0.023101 | 0.001436 | 2.1125 | 0.1125 |

### Model: gpt-5.6-luna (`20260906T133009Z_main_test_gpt56_luna`)

| Method | TSR v2 | GTSR v2 | Route Flip (v1 / v2) | Regret v1 | Regret v2 | Mean Calls | Review Rate |
|---|---|---|---|---|---|---|---|
| B0 | 1.0000 | 1.0000 | 0.2292 / 0.2292 | 0.042909 | 0.003723 | 1.0000 | 0.0000 |
| B2 | 1.0000 | 1.0000 | 0.2292 / 0.2292 | 0.042909 | 0.003723 | 2.0000 | 0.0000 |
| B3 | 1.0000 | 1.0000 | 0.2198 / 0.2198 | 0.0463 | 0.003774 | 2.5203 | 0.5203 |
| B4 | 1.0000 | 1.0000 | 0.2156 / 0.2156 | 0.047222 | 0.003507 | 2.3859 | 0.3859 |
| B5 | 1.0000 | 1.0000 | 0.2292 / 0.2292 | 0.043035 | 0.003723 | 2.0266 | 0.0266 |
| B6 | 1.0000 | 1.0000 | 0.2229 / 0.2229 | 0.050937 | 0.003848 | 3.0000 | 1.0000 |
| Ours | 1.0000 | 1.0000 | 0.2198 / 0.2198 | 0.04453 | 0.003610 | 2.1641 | 0.1641 |

### Model: gpt-5.6-sol (`20260907T014117Z_main_test_gpt56_sol`)

| Method | TSR v2 | GTSR v2 | Route Flip (v1 / v2) | Regret v1 | Regret v2 | Mean Calls | Review Rate |
|---|---|---|---|---|---|---|---|
| B0 | 1.0000 | 1.0000 | 0.2604 / 0.2604 | 0.041306 | 0.003340 | 1.0000 | 0.0000 |
| B2 | 1.0000 | 1.0000 | 0.2604 / 0.2604 | 0.041306 | 0.003340 | 2.0000 | 0.0000 |
| B3 | 1.0000 | 1.0000 | 0.2448 / 0.2448 | 0.043427 | 0.003195 | 2.5172 | 0.5172 |
| B4 | 1.0000 | 1.0000 | 0.225 / 0.225 | 0.043933 | 0.003106 | 2.3891 | 0.3891 |
| B5 | 1.0000 | 1.0000 | 0.2604 / 0.2604 | 0.041431 | 0.003340 | 2.0141 | 0.0141 |
| B6 | 1.0000 | 1.0000 | 0.2271 / 0.2271 | 0.045593 | 0.002969 | 3.0000 | 1.0000 |
| Ours | 1.0000 | 1.0000 | 0.2375 / 0.2375 | 0.041633 | 0.003144 | 2.1406 | 0.1406 |

## 2. Rigorous Cost Accounting Breakdown (P0-5 Remediation)

The review parameter $q$ specifically denotes the proportion of requests triggering the 3rd review call.
To prevent inflated or misleading claims of 'cost savings', we distinguish three distinct cost metrics:

1. **Review Call Reduction** relative to B6 (Always Review, 3 calls): $1 - q / 1.0$
2. **Total Logic Call Reduction** relative to B6: $(3 - (2 + q)) / 3 = (1 - q) / 3$
3. **Total Logic Call Overhead** relative to B0 (Single A, 1 call): $1 + q$
4. **Provider Token & Latency Accounting** (Physical API resources consumed during collection):

| Model | Total Calls | Schema Valid | Failures | Input Tokens | Output Tokens | Total Tokens | Latency (s) | Review Call Reduction vs B6 | Total Call Reduction vs B6 | Call Overhead vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.4-mini | 3200 | 3200 | 0 | 1,528,566 | 218,183 | 1,746,749 | 12006.6 | 95.78% | 31.93% | +104.22% |
| deepseek-v4-flash | 1467 | 1233 | 233 | 679,018 | 2,379,402 | 3,058,420 | 23189.1 | 62.03% | 20.68% | +137.97% |
| qwen38-max | 1818 | 1708 | 78 | 563,414 | 92,694 | 656,108 | 22401.6 | 88.75% | 29.58% | +111.25% |
| gpt-5.6-luna | 1918 | 1910 | 3 | 1,914,212 | 140,385 | 2,054,597 | 84732.2 | 83.59% | 27.86% | +116.41% |
| gpt-5.6-sol | 1920 | 1920 | 0 | 2,898,704 | 150,668 | 3,049,372 | 72998.1 | 85.94% | 28.65% | +114.06% |

### Interpretation & Submission Boundary:
- Claiming a '95.8% compute saving' on GPT-5.4-mini is **inaccurate** because it only refers to the review call stage ($q = 4.22\%$).
- The true reduction in total logical inference calls compared to B6 (full verification) is **31.93%**.
- Compared to B0 (unverified single-turn baseline), Ours requires **104.22% more calls** (2.0422 vs 1.0000).
- In formal submissions, all three metrics must be reported together alongside actual token consumption and latency.

### Limitations in Historical Telemetry Records (Sol Runner & Attempts Accounting):
- In `scripts/run_frontier_5model_suite.py` and `scripts/run_gpt56_sol_experiment.py`, the outer retry loop on transient HTTP 429/5xx exceptions saved only the final attempt's telemetry (`llm.telemetry[-1]`), omitting logs from earlier aborted retry attempts.
- Recomputed metrics (`results/reports/recomputed_v2_metrics.json`) carry forward this historical summary telemetry and cannot retroactively reconstruct dropped attempt tokens or latency.
- Status: Formally recorded as `historical_attempts_unrecoverable`. In future confirmatory runs, all attempt records must be appended into an immutable attempt ledger.
