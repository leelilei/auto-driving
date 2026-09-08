# DARC-Route Qwen3.8-max Main Experiment Report (Test Split)

- **Run ID**: `20260906T123744Z_main_test_qwen38_max`
- **Model**: `qwen3.8-max` via `https://xcode.best`
- **Timestamp**: `2026-09-06T13:02:30.061022+00:00`
- **Dataset**: 160 test groups × 4 variants = 640 utterances
- **Provider Tokens**: Total 656,108 (Input: 563,414, Output: 92,694)
- **API Attempts**: 1818 calls (Valid: 1708, Transport Failures: 78)
- **Frozen Parameters**: $\tau^*=0.02$, $\tau_{sem}^*=0.1$, $p^*=0.48$

## 1. Qwen3.8-max Main Results Comparison Table

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.00 | 0.0% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0865 | +0.0% |
| B2 | A+B, always A (2 calls) | 2.00 | 0.0% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0865 | +0.0% |
| B5 | Protection $h$ only | 2.10 | 9.7% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0865 | +0.0% |
| B6 | Always Review (3 calls) | 3.00 | 100.0% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0897 | -3.7% |
| B3 | Random Review ($p^*=0.48$) | 2.56 | 56.2% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0928 | -7.3% |
| B4 | Semantic Weight Gate ($\tau_{sem}^*=0.1$) | 2.10 | 10.5% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0865 | +0.0% |
| **Ours** | DARC Utility Gate ($\tau^*=0.02$) | 2.11 | 11.2% | 0.9375 | 0.8125 | 0.94 | 0.96 | 0.97 | 0.89 | 0.0897 | -3.7% |

## 2. Paired Bootstrap 95% Confidence Intervals (2,000 Resamples)

| Comparison | Delta TSR | 95% CI (TSR) | Delta Route Flip | 95% CI (Flip) | Significant Flip Reduction? |
|---|---|---|---|---|---|
| `Ours_vs_B0` | +0.0000 | [+0.0000, +0.0000] | +0.0031 | [+0.0000, +0.0094] | No |
| `Ours_vs_B3` | +0.0000 | [+0.0000, +0.0000] | -0.0031 | [-0.0094, +0.0000] | No |
| `Ours_vs_B4` | +0.0000 | [+0.0000, +0.0000] | +0.0031 | [+0.0000, +0.0094] | No |
| `Ours_vs_B6` | +0.0000 | [+0.0000, +0.0000] | +0.0000 | [-0.0094, +0.0115] | No |

## 3. Cross-Model Findings (Qwen3.8-max vs GPT-5.4-mini vs DeepSeek-v4)

1. **Route Flip Stability on Qwen3.8-max**: DARC achieves Route Flip of `0.0897` (vs B0 `0.0865`, `-3.7%` reduction).
2. **TSR Preservation**: DARC achieves TSR `0.9375` on Qwen3.8-max.
3. **Compute Efficiency**: DARC requires `2.11` calls/req (review rate `11.2%`).
