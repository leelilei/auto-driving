# DARC-Route Offline Analysis Summary

> Date: 2026-09-06
> Note: Offline verification run on Pilot 80-utterance set.

## Method Comparison Table

| Method | Description | TSR | GTSR | V0 | V1 | V2 | V3 | Route Flip |
|---|---|---|---|---|---|---|---|---|
| B0 | Single A (1 call) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B1 | Medoid A/A2/A3 (3 calls) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B2 | A+B, always A (2 calls) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B3 | Random review p=0.5 (2+q) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B4 | Semantic weight gate (2+q) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B5 | Protection h only (2+q) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| B6 | Always review (3 calls) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
| Ours | DARC Utility Gate (2+q) | 1.0000 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 |
