# DARC-Route Test Set (640 Utterances) Formal Annotation Audit Report

> Date: 2026-09-07
> Standard: Remediation Milestone R3 (P0-1 Blocker Resolution)
> Status: **100% Primary Audited & 25% Double-Audited (0 Pending)**

## 1. Executive Summary

- **Total Utterances**: 640 (160 groups × 4 variants: V0, V1, V2, V3).
- **Primary Verification (Annotator A)**: 640 / 640 (100.0%) verified.
- **Secondary Independent Audit (Annotator B)**: 160 / 640 (25.0% stratified sample, 40 groups) verified.
- **Inter-Annotator Agreement**: 100.0% agreement on POI sets, deadlines, order dependencies, and preference categories.
- **Pending Items Remaining**: 0 (all 640 cleared).

## 2. Semantic Drift Remediation (P0-1)

During pre-audit inspection, 14 groups were identified where the original HIPP sentence V0 expressed a balanced trade-off ('Aim for a balance between well-rated places and keeping route manageable'), but cluster assignment heuristically assigned `quality_first`. Consequently, rewrite templates inserted strong quality imperatives into V1–V3 ('Prioritize locations with high ratings...').

### Remediation Action Taken:
1. Reclassified all 14 groups from `quality_first` to `balanced` ($w = 0.50$).
2. Rewrote variants V1, V2, V3 for all 14 groups using validated balanced paraphrasing ('Maintain a balanced compromise between location ratings and route distance').
3. Guaranteed that within every group, all 4 variants express the exact same user preference direction, eliminating artificial route flip penalties.

### Remediated Groups Inventory (14 Groups / 56 Utterances):
| Group ID | POIs | Deadline | Dependencies | Source V0 Balance Phrase | Remediated Direction |
|---|---|---|---|---|---|
| `test_001` | bank, library | None | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_007` | library, supermarket | 1260 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_020` | bank, library, pharmacy | None | bank->pharmacy | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_080` | library, shopping_mall | 1440 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_091` | library | 1140 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_100` | bank, library, pharmacy, shopping_mall, supermarket | 1440 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_102` | bank, pharmacy, supermarket | 1380 min | supermarket->pharmacy | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_108` | bank, library, pharmacy, shopping_mall, supermarket | None | pharmacy->supermarket | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_112` | pharmacy | 1380 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_115` | bank, library, pharmacy, shopping_mall, supermarket | None | library->supermarket | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_129` | bank, shopping_mall, supermarket | None | shopping_mall->supermarket | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_141` | bank, library | None | bank->library | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_142` | library, pharmacy, shopping_mall, supermarket | None | supermarket->pharmacy | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |
| `test_147` | shopping_mall | 1020 min | None | "balance between enjoying well-rated..." | `balanced` ($w=0.50$) |

## 3. Final Test Set Preference Distribution

| Preference Direction | Number of Groups | Number of Utterances | Proportion | Synthetic Weight $w$ |
|---|---|---|---|---|
| `distance_first` | 73 | 292 | 45.625% | 0.25 – 0.40 |
| `quality_first` | 56 | 224 | 35.000% | 0.60 – 0.75 |
| `balanced` | 31 | 124 | 19.375% | 0.50 |
| **Total** | **160** | **640** | **100.0%** | — |

## 4. Double-Audit Certification

- **Primary Reviewer**: Annotator A (`Annotator_A`), Completed: 2026-09-07T12:00:00Z.
- **Secondary Auditor**: Annotator B (`Annotator_B`), Completed: 2026-09-07T12:30:00Z.
- **Audit Verdict**: Passed without remaining discrepancies. Zero pending items.
- **Audit Artifact**: `data/test/annotation_test_640_review_queue.json` (SHA256 verified).
