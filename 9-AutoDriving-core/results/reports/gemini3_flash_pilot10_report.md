# DARC-Route Gemini 3 Flash Main Experiment Report (Test Split)

- **Run ID**: `20260911T181131Z_main_test_gemini-3-flash_pilot10_net`
- **Model**: `gemini-3-flash` via `https://xcode.best`
- **Timestamp**: `2026-09-11T18:15:04.787896+00:00`
- **Dataset**: 10 test groups × 4 variants = 40 utterances
- **Provider Tokens**: Total 122,269 (Input: 0, Output: 0)
- **API Attempts**: 120 calls (Valid: 113, Transport Failures: 0)
- **Frozen Parameters**: $\tau^*=0.02$, $\tau_{sem}^*=0.1$, $p^*=0.48$

## 1. Gemini 3 Flash Main Results Comparison Table

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| B2 | A+B, always A (2 calls) | 2.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| B5 | Protection $h$ only | 2.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| B6 | Always Review (3 calls) | 3.00 | 100.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| B3 | Random Review ($p^*=0.48$) | 2.55 | 55.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| B4 | Semantic Weight Gate ($\tau_{sem}^*=0.1$) | 2.05 | 5.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |
| **Ours** | DARC Utility Gate ($\tau^*=0.02$) | 2.00 | 0.0% | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0667 | +0.0% |

## 2. Paired Bootstrap 95% Confidence Intervals (2,000 Resamples)

| Comparison | Delta TSR | 95% CI (TSR) | Delta Route Flip | 95% CI (Flip) | Significant Flip Reduction? |
|---|---|---|---|---|---|
| `Ours_vs_B0` | +0.0000 | [+0.0000, +0.0000] | +0.0000 | [+0.0000, +0.0000] | No |
| `Ours_vs_B3` | +0.0000 | [+0.0000, +0.0000] | +0.0000 | [+0.0000, +0.0000] | No |
| `Ours_vs_B4` | +0.0000 | [+0.0000, +0.0000] | +0.0000 | [+0.0000, +0.0000] | No |
| `Ours_vs_B6` | +0.0000 | [+0.0000, +0.0000] | +0.0000 | [+0.0000, +0.0000] | No |

## 3. Cross-Model Findings (Gemini 3 Flash vs GPT-5.4-mini vs DeepSeek-v4)

1. **Route Flip Stability on Gemini 3 Flash**: DARC achieves Route Flip of `0.0667` (vs B0 `0.0667`, `0.0%` reduction).
2. **TSR Preservation**: DARC achieves TSR `1.0000` on Gemini 3 Flash.
3. **Compute Efficiency**: DARC requires `2.00` calls/req (review rate `0.0%`).
