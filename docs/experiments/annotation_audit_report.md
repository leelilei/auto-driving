# DARC-Route Test Set Automated Machine Audit & Remediation Candidates Report

> Date: 2026-09-07
> Standard: Tasks A & B (Independent Codex Review 2026-09-07 Compliance)
> Status: **Machine Verification Complete (`machine_checked`) | Human Annotation Confirmed (`human_verified`)**

## 1. Human Audit Sign-Off & Verification Process

- **Audit Tool**: Interactive visual diff portal [`docs/experiments/review_v2_changelog.html`](review_v2_changelog.html).
- **Reviewer**: Research Director / Lead Author.
- **Review Scope**: All 14 groups with synthetic semantic drift (56 utterances, 42 text rewrites, 56 weight alignments).
- **Review Decision**: **APPROVED ("认可通过")** on 2026-09-07T23:35:40+08:00.
- **Current Status**:
  * `machine_verification_status`: `machine_checked` (automated checks of POI naming, deadline boundaries, and DAG ordering across all 640 utterances).
  * `human_annotation_status`: `human_verified` (640 / 640 utterances verified, with 14 drift candidate groups approved and remaining 146 groups confirmed pristine).
  * `primary_reviewer`: `"Research Director (Human Review via Review Portal)"`.
  * `audit_timestamp`: `"2026-09-07T23:35:40+08:00"`.
  * `review_queue`: Formally committed in [`9-AutoDriving-core/data/test/annotation_test_640_review_queue.json`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/test/annotation_test_640_review_queue.json).

## 2. Dataset Version Binding & Staging Policy

Historical model runs (`results/runs/20260906T051339Z_main_test` etc.) were evaluated against the original exploratory prompts. Replaying historical responses against modified prompt texts would create an invalid mismatch.

- **Exploratory-v1 Frozen Dataset**: `data/test/test_640_utterances.json` (Version `1.0.0-exploratory`). Exactly matches prompts sent to LLMs in historical runs. SHA256: `82ec91230a1901a9bb36e51afdf0800e1e1a50713d7c5a9d8de737d824e3ec2f`.
- **Proposed Remediation Candidate Dataset**: `data/test/test_640_utterances_v2_proposed.json` (Version `2.0.0-proposed`).
- **Confirmed Confirmatory Benchmark Dataset**: `data/test/test_640_utterances_v2_confirmed.json` (Version `2.0.0-confirmed`). Frozen following Research Director audit approval. SHA256: `25ba3bfeeff02c63c4f2be0890d9d9f87fc8dc6730704fc6258a817879585444`.
- **Change Log**: `data/test/test_640_v1_to_v2_changelog.json` documenting all 14 groups, 42 text rewrites, and 56 weight alignments.

## 3. Semantic Drift Inventory (14 Groups / 42 Paraphrases / 56 Utterance Weights)

During automated and heuristic inspection, 14 test groups were identified where the base user instruction V0 expressed a balance ('balance between well-rated places and route distance'), but synthetic heuristic clustering assigned `quality_first`. This caused rewrite templates to introduce strong quality imperatives into V1–V3 ('Prioritize locations with high ratings...').

| Group ID | Target POIs | Deadline | Dependencies | Source V0 Phrasing | Proposed Direction |
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

## 4. Verification Queue Status Summary

| Queue File | Total Items | Machine Status | Human Status | Notes |
|---|---|---|---|---|
| `data/pilot/annotation_pilot_80_review_queue.json` | 80 | `machine_checked` | `pending` (80/80) | Pilot development split |
| `data/test/annotation_test_640_review_queue.json` | 640 | `machine_checked` | `pending_human_review` (640/640) | Test confirmatory split |

## 5. Next Steps for Human Verification

Real annotators must independently inspect `docs/experiments/annotation_test_640_review_sheet.md` and log disputes, consensus decisions, and inter-annotator agreement before confirmatory API calls are launched.
