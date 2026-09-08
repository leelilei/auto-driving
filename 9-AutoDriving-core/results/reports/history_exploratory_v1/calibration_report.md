# DARC-Route Calibration Report (dev_calibration)

- **Run ID**: `20260906T035711Z_calibration`
- **Timestamp**: `2026-09-06T04:05:17.062486+00:00`
- **Dataset**: 20 groups × 4 variants = 80 utterances
- **Provider Tokens**: Total 139346 (Input: 118892, Output: 20454)
- **API Attempts**: 238 calls (Valid: 234, Transport Errors: 4)

## 1. Baseline Operating Points

| Method | Description | Calls/Req | Review Rate $q$ | TSR | GTSR | Route Flip | Utility Loss $L_U$ |
|---|---|---|---|---|---|---|---|
| **B0** | Single A | 1.00 | 0.0000 | 1.0000 | 1.0000 | 0.1833 | 0.017269 |
| **B2** | A+B (always A) | 2.00 | 0.0000 | 1.0000 | 1.0000 | 0.1833 | 0.017269 |
| **B5** | Only Protection $h$ | 2.04 | 0.0375 | 1.0000 | 1.0000 | 0.1583 | 0.016790 |
| **B6** | Always Review | 3.00 | 1.0000 | 1.0000 | 1.0000 | 0.1417 | 0.018873 |

## 2. DARC Utility Threshold ($	au$) Grid Sweep

| $\tau$ | Review Rate $q$ | Calls/Req | $P(h)$ | $P(\Delta_U > \tau)$ | TSR | GTSR | Route Flip | Selection Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.0000 | 0.1125 | 2.11 | 0.0375 | 0.0750 | 1.0000 | 1.0000 | 0.1417 | Admissible |
| 0.0050 | 0.1125 | 2.11 | 0.0375 | 0.0750 | 1.0000 | 1.0000 | 0.1417 | Admissible |
| 0.0100 | 0.0875 | 2.09 | 0.0375 | 0.0500 | 1.0000 | 1.0000 | 0.1083 | Admissible |
| 0.0200 | 0.0875 | 2.09 | 0.0375 | 0.0500 | 1.0000 | 1.0000 | 0.1083 | **SELECTED $\tau^*$** |
| 0.0300 | 0.0625 | 2.06 | 0.0375 | 0.0250 | 1.0000 | 1.0000 | 0.1333 | Admissible |
| 0.0500 | 0.0500 | 2.05 | 0.0375 | 0.0125 | 1.0000 | 1.0000 | 0.1583 | Admissible |
| 0.0750 | 0.0375 | 2.04 | 0.0375 | 0.0000 | 1.0000 | 1.0000 | 0.1583 | Admissible |
| 0.1000 | 0.0375 | 2.04 | 0.0375 | 0.0000 | 1.0000 | 1.0000 | 0.1583 | Admissible |
| 0.1500 | 0.0375 | 2.04 | 0.0375 | 0.0000 | 1.0000 | 1.0000 | 0.1583 | Admissible |
| 0.2000 | 0.0375 | 2.04 | 0.0375 | 0.0000 | 1.0000 | 1.0000 | 0.1583 | Admissible |
| inf (off) | 0.0375 | 2.04 | 0.0375 | 0.0000 | 1.0000 | 1.0000 | 0.1583 | Admissible |

## 3. Comparison of Calibrated Operating Points ($q \approx 0.50$ Target)

| Method | Setting | Calls/Req | Review Rate $q$ | TSR | GTSR | Route Flip | Flip Reduction vs B0 |
|---|---|---|---|---|---|---|---|
| **B0** | Single A | 1.00 | 0.0000 | 1.0000 | 1.0000 | 0.1833 | 0.0% (Ref) |
| **B3** (Random) | $p=0.48$ | 2.42 | 0.4250 | 1.0000 | 1.0000 | 0.1583 | 13.6% |
| **B4** (Semantic) | $\tau_{sem}=0.1$ | 2.14 | 0.1375 | 1.0000 | 1.0000 | 0.1333 | 27.3% |
| **B5** (Protection) | $h$ only | 2.04 | 0.0375 | 1.0000 | 1.0000 | 0.1583 | 13.6% |
| **B6** (Always) | Full Review | 3.00 | 1.0000 | 1.0000 | 1.0000 | 0.1417 | 22.7% |
| **Ours** (DARC) | $\tau^*=0.02$ | 2.09 | 0.0875 | 1.0000 | 1.0000 | 0.1083 | 40.9% |

## 4. Frozen Protocol Confirmation

- **Frozen $\tau^*$**: `0.02`
- **Frozen $\tau_{sem}^*$**: `0.1`
- **Frozen $p^*$**: `0.4805194805194805`
- **Status**: Parameters successfully frozen on Dev Calibration split. Test split remains 100% untouched.
