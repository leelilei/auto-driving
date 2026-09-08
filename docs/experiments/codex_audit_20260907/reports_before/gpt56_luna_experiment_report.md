# DARC-Route GPT-5.6-luna Main Experiment Report (Test Split)

- **Run ID**: `20260906T133009Z_main_test_gpt56_luna`
- **Model**: `gpt-5.6-luna` via `https://www.fhl.mom`
- **Timestamp**: `2026-09-06T15:06:31.308477+00:00`
- **Dataset**: 160 test groups × 4 variants = 640 utterances
- **Provider Tokens**: Total 2,054,597 (Input: 1,914,212, Output: 140,385)
- **API Attempts**: 1918 calls (Valid: 1910, Transport Failures: 3)
- **Frozen Parameters**: $\tau^*=0.02$, $\tau_{sem}^*=0.1$, $p^*=0.48$

## 1. GPT-5.6-luna Main Results Comparison Table

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2292 | +0.0% |
| B2 | A+B, always A (2 calls) | 2.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2292 | +0.0% |
| B5 | Protection $h$ only | 2.03 | 2.7% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2292 | +0.0% |
| B6 | Always Review (3 calls) | 3.00 | 100.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2229 | +2.7% |
| B3 | Random Review ($p^*=0.48$) | 2.52 | 52.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2198 | +4.1% |
| B4 | Semantic Weight Gate ($\tau_{sem}^*=0.1$) | 2.39 | 38.6% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2156 | +5.9% |
| **Ours** | DARC Utility Gate ($\tau^*=0.02$) | 2.16 | 16.4% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.2198 | +4.1% |

## 2. Paired Bootstrap 95% Confidence Intervals (2,000 Resamples)

| Comparison | Delta TSR (95% CI) | Delta Route Flip (95% CI) | Significant Flip Reduction? |
|---|---|---|---|
| `Ours_vs_B0` | +0.0000 [+0.0000, +0.0000] | -0.0094 [-0.0354, +0.0177] | No |
| `Ours_vs_B3` | +0.0000 [+0.0000, +0.0000] | -0.0000 [-0.0292, +0.0281] | No |
| `Ours_vs_B4` | +0.0000 [+0.0000, +0.0000] | +0.0042 [-0.0135, +0.0229] | No |
| `Ours_vs_B6` | +0.0000 [+0.0000, +0.0000] | -0.0031 [-0.0281, +0.0208] | No |

## 3. Cross-Model Findings (GPT-5.6-luna vs Others)

1. **Route Flip Stability**: DARC achieves Route Flip of `0.2198` vs B0 `0.2292`.
2. **TSR Preservation**: DARC achieves TSR `1.0000` on GPT-5.6-luna.
3. **Compute Efficiency**: DARC requires `2.16` calls/req (review rate `16.4%`).
