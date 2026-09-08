# DARC-Route DeepSeek-v4-Flash Main Experiment Report (Test Split)

- **Run ID**: `20260906T081920Z_main_test_deepseek_v4`
- **Model**: `deepseek-v4-flash` via `api.apilio.ai`
- **Timestamp**: `2026-09-06T08:43:54.098360+00:00`
- **Dataset**: 160 test groups × 4 variants = 640 utterances
- **Provider Tokens**: Total 3,058,420 (Input: 679,018, Output: 2,379,402)
- **API Attempts**: 1467 calls (Valid: 1233, Transport Failures: 233)
- **Frozen Parameters**: $\tau^*=0.02$, $\tau_{sem}^*=0.1$, $p^*=0.48$

## 1. DeepSeek-v4 Main Results Comparison Table

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.00 | 0.0% | 0.6469 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.0950 | +0.0% |
| B2 | A+B, always A (2 calls) | 2.00 | 0.0% | 0.6469 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.0950 | +0.0% |
| B5 | Protection $h$ only | 2.36 | 36.1% | 0.6484 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.0950 | +0.0% |
| B6 | Always Review (3 calls) | 3.00 | 100.0% | 0.6484 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.1090 | -14.7% |
| B3 | Random Review ($p^*=0.48$) | 2.70 | 70.0% | 0.6484 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.1106 | -16.4% |
| B4 | Semantic Weight Gate ($\tau_{sem}^*=0.1$) | 2.48 | 48.1% | 0.6484 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.1075 | -13.2% |
| **Ours** | DARC Utility Gate ($\tau^*=0.02$) | 2.38 | 38.0% | 0.6484 | 0.6062 | 0.68 | 0.67 | 0.64 | 0.61 | 0.1012 | -6.5% |

## 2. Paired Bootstrap 95% Confidence Intervals (2,000 Resamples)

| Comparison | Delta TSR | 95% CI (TSR) | Delta Route Flip | 95% CI (Flip) | Significant Flip Reduction? |
|---|---|---|---|---|---|
| `Ours_vs_B0` | +0.0016 | [+0.0000, +0.0047] | +0.0042 | [-0.0073, +0.0187] | No |
| `Ours_vs_B3` | +0.0000 | [+0.0000, +0.0000] | -0.0063 | [-0.0250, +0.0125] | No |
| `Ours_vs_B4` | +0.0000 | [+0.0000, +0.0000] | -0.0042 | [-0.0177, +0.0083] | No |
| `Ours_vs_B6` | +0.0000 | [+0.0000, +0.0000] | -0.0052 | [-0.0219, +0.0104] | No |

## 3. Cross-Model Findings (DeepSeek-v4 vs GPT-5.4-mini)

1. **Route Flip Stability on DeepSeek**: DARC achieves Route Flip of `0.1012` (vs B0 `0.0950`, `-6.5%` reduction).
2. **TSR Preservation**: DARC achieves TSR `0.6484` on DeepSeek-v4.
3. **Compute Efficiency**: DARC requires `2.38` calls/req (review rate `38.0%`).
