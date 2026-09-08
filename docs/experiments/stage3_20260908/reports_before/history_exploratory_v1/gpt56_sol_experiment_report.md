# DARC-Route GPT-5.6-sol Main Experiment Report (Test Split)

- **Run ID**: `20260907T014117Z_main_test_gpt56_sol`
- **Model**: `gpt-5.6-sol` via `https://www.fhl.mom`
- **Timestamp**: `2026-09-07T02:40:55.779697+00:00`
- **Dataset**: 160 test groups × 4 variants = 640 utterances
- **Provider Tokens**: Total 3,049,372 (Input: 2,898,704, Output: 150,668)
- **API Attempts**: 1920 calls (Valid: 1920, Transport Failures: 0)
- **Frozen Parameters**: $\tau^*=0.02$, $\tau_{sem}^*=0.1$, $p^*=0.48$

## 1. GPT-5.6-sol Main Results Comparison Table

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2604 | +0.0% |
| B2 | A+B, always A (2 calls) | 2.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2604 | +0.0% |
| B5 | Protection $h$ only | 2.01 | 1.4% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2604 | +0.0% |
| B6 | Always Review (3 calls) | 3.00 | 100.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2271 | +12.8% |
| B3 | Random Review ($p^*=0.48$) | 2.52 | 51.7% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2448 | +6.0% |
| B4 | Semantic Weight Gate ($\tau_{sem}^*=0.1$) | 2.39 | 38.9% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2250 | +13.6% |
| **Ours** | DARC Utility Gate ($\tau^*=0.02$) | 2.14 | 14.1% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2375 | +8.8% |

## 2. Paired Bootstrap 95% Confidence Intervals (2,000 Resamples)

| Comparison | Delta TSR (95% CI) | Delta Route Flip (95% CI) | Significant Flip Reduction? |
|---|---|---|---|
| `Ours_vs_B0` | +0.0000 [+0.0000, +0.0000] | -0.0229 [-0.0458, -0.0010] | Yes |
| `Ours_vs_B3` | +0.0000 [+0.0000, +0.0000] | -0.0073 [-0.0281, +0.0146] | No |
| `Ours_vs_B4` | +0.0000 [+0.0000, +0.0000] | +0.0125 [-0.0042, +0.0323] | No |
| `Ours_vs_B6` | +0.0000 [+0.0000, +0.0000] | +0.0104 [-0.0135, +0.0344] | No |

## 3. Cross-Model Findings (GPT-5.6-sol vs Others)

1. **Route Flip Stability**: DARC achieves Route Flip of `0.2375` vs B0 `0.2604`.
2. **TSR Preservation**: DARC achieves TSR `1.0000` on GPT-5.6-sol.
3. **Compute Efficiency**: DARC requires `2.14` calls/req (review rate `14.1%`).
