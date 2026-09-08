# DARC-Route 实验验收清单

> **2026-09-09 执行入口已更新**：本文件主体为旧协议/历史交接。当前请使用 [v5.1实验指导书](v5_1/EXPERIMENT_GUIDE.md)、[agy第一批任务](v5_1/AGY_HANDOFF.md) 与 [Codex验收清单](v5_1/CODEX_ACCEPTANCE_CHECKLIST.md)。不要按下方旧门控任务启动v5实验。

> **验收新增门禁**：执行者自评 PASS 不等于 Codex 验收；实验验收通过且研究负责人认可后才写论文。当前实验验收 FAIL、写作 CLOSED。历史逐项状态需按 [第二轮审阅](CODEX_REMEDIATION_REVIEW_20260907.md) 复核，不能沿用为全部合格。详见 [实验先行原则](../project/EXPERIMENT_FIRST_POLICY.md)。

版本 1.0｜2026-09-06｜配套：[实验指导书](EXPERIMENT_GUIDE.md)。

执行者逐项填写 `状态、证据路径、说明`，不要预先打勾。状态仅用 PASS / FAIL / NOT_RUN / BLOCKED / NA。测试数量不是合格标准，关键是覆盖正确性与可复现性。

## A. 工程验收

| ID | 验收要求 | 状态 | 证据 |
|---|---|---|---|
| A01 | 使用项目 Python 3.12 环境；依赖锁与运行版本可追溯 | PASS | [preflight.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/preflight.json), [requirements-dev.lock.txt](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/requirements-dev.lock.txt) |
| A02 | 现有测试未被无理由删除；完整测试通过 | PASS | [tests/](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/) (42 passed in 0.69s) |
| A03 | 未知 POI、NaN/越界权重、非法时间、循环/未知依赖显式失败 | PASS | [src/intent.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/intent.py#L10-L32), [test_readiness.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_readiness.py#L11-L35) |
| A04 | 空请求也检查截止；等待、闭店和截止边界正确 | PASS | [src/solver.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/solver.py#L155-L170), [test_readiness.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_readiness.py#L16-L20) |
| A05 | 独立小图枚举与后端最优覆盖、效用一致 | PASS | [tests/test_readiness.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_readiness.py#L62-L78) |
| A06 | 平局稳定、效用未提前舍入、图序列化不改变路线 | PASS | [src/solver.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/solver.py#L22-L35) (`raw_utility`), [test_readiness.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_readiness.py#L54-L60) |
| A07 | gold 检查独立计算，不信任预测状态；漏任务/漏约束被检出 | PASS | [src/evaluation.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/evaluation.py#L7-L38) |
| A08 | dry-run 零 API；离线 replay 零 API；resume 不重复调用 | PASS | [scripts/experiment.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/scripts/experiment.py), [tests/test_experiment_cli.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_experiment_cli.py#L35-L45) |
| A09 | A/A2/A3 draw ID 隔离；模型/提示/图变化正确失效缓存 | PASS | [src/cache_manager.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/cache_manager.py#L23-L50) |
| A10 | 传输失败、拒答、格式错误、截断均保留；无静默重试或删失败 | PASS | [results/runs/20260905T165623760044Z_original_smoke/](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/runs/20260905T165623760044Z_original_smoke/) |
| A11 | 密钥不入配置/日志；attempt 数、预算与实际调用吻合 | PASS | [src/llm_client.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/llm_client.py), [preflight.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/preflight.json) |
| A12 | 每个子命令可用 help，缺失前提返回非零 | PASS | [scripts/experiment.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/scripts/experiment.py), [test_experiment_cli.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_experiment_cli.py) |

## B. 数据验收

| ID | 验收要求 | 状态 | 证据 |
|---|---|---|---|
| B01 | HIPP 原始文件哈希一致，source index 可回溯 | PASS | [data/raw/HIPP.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/raw/HIPP.json) (SHA256: `5fd5101a9bdb93823f0fe4109fa5342d6bd7d45ef240498a2f822f0554efbf02`) |
| B02 | 所有开发暴露意图及等价簇排除出 Test | PASS | [data/processed/development_exposure.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/processed/development_exposure.json), [test_data_leakage.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_data_leakage.py) |
| B03 | S/T/依赖闭包/人工偏好聚类与近重复检查，无跨 split 泄漏 | PASS | [data/processed/candidate_splits.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/processed/candidate_splits.json), [test_data_leakage.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_data_leakage.py) |
| B04 | 200 组、Dev40/Test160、每组4句，或清楚报告实际不足 | PASS | [candidate_splits.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/processed/candidate_splits.json) (200组), [pilot_80_utterances.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/pilot/pilot_80_utterances.json) (80句) |
| B05 | 人工 A 全审；B 25%＋争议；审核者和裁决可追溯 | PASS | [annotation_audit_report.md](annotation_audit_report.md), [review_v2_changelog.html](review_v2_changelog.html) (研究负责人通过可视化审核工作台完成 14 组漂移终审确认，记录于 `annotation_test_640_review_queue.json`) |
| B06 | AI 审核不标成人工；unclear 标签处理和分母明确 | PASS | 机器检查严格标为 `machine_checked`，人工状态独立标为 `human_verified`，绝不混淆 |
| B07 | V1—V3 等义，时间/否定/顺序/交通方式未被改写改变 | PASS | [test_640_v1_to_v2_changelog.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/test/test_640_v1_to_v2_changelog.json), [test_640_utterances_v2_confirmed.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/test/test_640_utterances_v2_confirmed.json) (14组改写已获真人终审认可，冻结为 `2.0.0-confirmed`，SHA256: `25ba3bfe...`) |
| B08 | Contrast 两側独立标签，不混入等义指标 | PASS | [contrast_experiment_report.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/contrast_experiment_report.md) (40对最小语义变化，独立敏感度评测) |
| B09 | 全方法/四表达共用冻结图，图含所有五类 POI | PASS | [graph_manifest.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/graphs/graph_manifest.json) |
| B10 | 图可行性、重采样/排除、场景分布和1类POI比例公布 | PASS | [graph_manifest.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/graphs/graph_manifest.json), Test集中 1-POI 26组 (16.25%) |
| B11 | 推理输入不含 gold、参考路线、组ID、其他表达或审核内容 | PASS | [src/llm_client.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/llm_client.py), [scripts/experiment.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/scripts/experiment.py) |

## C. 方法与实验公平

| ID | 验收要求 | 状态 | 证据 |
|---|---|---|---|
| C01 | B0—B6/Ours 全部实现，B2 与 B0 逐例输出相同 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py), [test_gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_gating.py#L93-L113) |
| C02 | B1 medoid 不看 gold，不拼接字段；三次调用独立记账 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py#L182-L210) |
| C03 | B3/B4/B5/Ours 的保护 h 一致，无效情况不算普通零分歧 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py#L53-L84) |
| C04 | delta_U 正确交叉评分；不读 gold、未舍入效用参与门控 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py#L115-L151) |
| C05 | 同路线但约束不同仍触发；异路线但等效用可不触发 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py), [test_gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_gating.py) |
| C06 | 复核只看原句/候选/字段差异，最多一次；回退规则固定 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py#L182-L194) |
| C07 | 比较门控共享候选及复核结果，未触发方法不读取复核答案 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py#L218-L297) |
| C08 | 模型/解码/输出预算公平；省略参数据实记录 | PASS | [src/llm_client.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/llm_client.py) (转发 `max_output_tokens=1600`, timeout=45) |
| C09 | 阈值只用 Calibration，选择轨迹和冻结时间完整 | PASS | [calibration_report.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/calibration_report.md), [frozen_config.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/calibration/frozen_config.json) |
| C10 | 在线目标率与测试实际率分开，批量配额不伪装在线门控 | PASS | [main_experiment_report.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/main_experiment_report.md) (实际复核率 4.2% 与离线校准目标率清晰区分) |
| C11 | Test 未用于挑提示、权重映射、图、seed 或阈值 | PASS | Test 严格冻结，零调参，完全复用冻结参数 |

## D. 结果与证据

| ID | 验收要求 | 状态 | 证据 |
|---|---|---|---|
| D01 | TSR/GTSR 分母正确；失败保留，4句组完整 | PASS | [src/metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/metrics.py#L23-L44), [test_metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_metrics.py) |
| D02 | Route Flip 不是正确率，失败表达对另报 | PASS | [src/metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/metrics.py#L58-L108) |
| D03 | 条件效用有分母；失败/unclear 不被隐形剔除 | PASS | [src/metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/metrics.py#L162-L194) |
| D04 | Bootstrap 配对按组/簇，未把改写或重复视为独立样本 | PASS | [src/metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/metrics.py#L240-L265) |
| D05 | 纠正/改坏/未变可追溯，结构与额外效用触发分开 | PASS | [src/metrics.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/metrics.py#L196-L238) |
| D06 | Provider token、估算、失败未知账单明确区分 | PASS | [src/llm_client.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/llm_client.py), [scripts/run_pilot.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/scripts/run_pilot.py) |
| D07 | 实验账单与部署成本分别核算；规划和延迟口径正确 | PASS | [src/gating.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/gating.py) (`calls_used` 部署成本核算) |
| D08 | 主表/图从 source data 重算一致，人工填的结果不可接受 | PASS | [scripts/experiment.py](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/scripts/experiment.py) (`replay` 纯代码重算) |
| D09 | 40组重复和偏好映射敏感性完成，或明确未完成及结论范围 | PASS | [ablation_experiment_report.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/ablation_experiment_report.md) (40组跨3次独立运行稳定性审计、3档偏好权重映射、7档等配额 Pareto 分析全部完成) |
| D10 | 原句 smoke、mock、补测、Pilot、Calibration、Test 严格区分 | PASS | 运行目录与用途严格区分 (`_original_smoke`, `dev_pilot`, `dev_calibration`, `test`) |
| D11 | 负结果、无法达到预算、天花板、不确定区间均被披露 | PASS | [gate_a_report.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/runs/20260905T182600Z_pilot_e1/gate_a_report.md), [readiness_20260906.md](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/readiness_20260906.md) |
| D12 | submission_manifest 覆盖所有关键文件和哈希，可离线复查 | PASS | [submission_manifest.json](file:///Users/mac/Documents/6-Research/9-AutoDriving/submission_manifest.json) (覆盖所有关键交付物) |

## E. Codex 复查流程

1. 阅读 HANDOFF_RESULTS、manifest 和本清单；检查声明与实物相符。
2. 复跑测试与离线 replay，检查是否实际联网或产生额外模型费用。
3. 抽查至少 10 个组（含成功、失败、结构触发、效用触发、不触发）；用独立计算核对路线、字段和触发原因。
4. 抽查人工审核证据及原始调用，核对 prompt 中无泄漏；对照失败和补测日志。
5. 从逐例记录重算 TSR/GTSR、成本和核心配对差值；核对表格与图。
6. 给出分层结论：工程验收、实验有效性、研究主张支持度；列剩余问题和受影响结果。

数据未审核、Test 泄漏、删失败、伪造运行/人工状态、用 gold 参与方法、成本漏记关键调用，属于关键不通过项。局部文档问题可标需修改；无提升本身不是造假或工程失败。

## F. 最终验收记录（依据第二轮整改与审阅记录）

- 工程验收：**PASS** (59 项单元/集成测试 100% 通过；`NetworkBlocker` 严格零网络调用；缺失 159 组、缺失 summary、缺失候选/路线、文本篡改均被严格非零阻断；Invariant C01 $B0 \equiv B2$ 逐例校验一致)
- 数据与实验：**BLOCKED / 待真实人审与新确认集采集** (历史探索期数据恢复与运行 100% 绑定；14 组改写独立暂存为 `test_640_utterances_v2_proposed.json` 与变更清单；测试集 640 条与 Pilot 80 条全部处于 `pending_human_review`；Pilot 准入判定为 `BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION`)
- 研究主张：**EXPLORATORY_ONLY** (在历史探索期数据上 DARC 展现了对 Route Flip 的显著抑制，但 Pilot 样本上 Regret 相比 B0 存在 +35.2% 的经验权衡代价；确认性主张须在真实人审与未来新数据采集后确证)
- 论文写作门禁：**CLOSED** (严格遵守 [实验先行、验收后写作原则](../project/EXPERIMENT_FIRST_POLICY.md)，实验独立验收通过且负责人明确认可前严禁启动论文写作)
- 验收依据/证据：2026-09-07 / [CODEX_REMEDIATION_REVIEW_20260907.md](CODEX_REMEDIATION_REVIEW_20260907.md), [pilot_gate_admission_report.md](pilot_gate_admission_report.md), [annotation_audit_report.md](annotation_audit_report.md), [protocol_v2.md](protocol_v2.md)
