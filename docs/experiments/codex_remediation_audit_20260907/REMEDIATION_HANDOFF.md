# DARC-Route 整改交付与验收报告 (REMEDIATION_HANDOFF)

> **基准审查**：[`docs/experiments/CODEX_PROJECT_REVIEW_20260907.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/CODEX_PROJECT_REVIEW_20260907.md)  
> **用户指令**：“论文最后写。先不要做这些相关的事情。将 codex 给出意见 推进到 R5。”  
> **状态**：**R0 至 R5 全部实质推进并完成验收**  
> **更新时间**：2026-09-07  

---

## 1. 整改推进总看板 (R0 ~ R5)

| 阶段编号 | 任务名称 | 状态 | 关键交付物 / 证据链 |
|---|---|---|---|
| **R0** | **冻结探索期现状 (Freeze Exploratory-v1)** | **PASS** | [`exploratory_v1_run_registry.json`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/exploratory_v1_run_registry.json), [`history_exploratory_v1/`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/history_exploratory_v1) |
| **R1** | **修正离线执行和指标 (Fix Replay & Metrics)** | **PASS** | 严格断网零 API Replay (`scripts/experiment.py replay --run-dir`)、坐标级精确效用与统一 Gold 权重 Regret (`src/gating.py`)、Contrast 双边成功约束 (`scripts/run_contrast_experiment.py`)、消融联结真实偏好方向、**51 项单元测试全量通过** ([`tests/test_remediation_r1.py`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_remediation_r1.py)) |
| **R2** | **历史结果只读重算与清洗 (Recompute v2)** | **PASS** | 5 模型只读重算生成 [`recomputed_v2_metrics.json`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/results/reports/recomputed_v2_metrics.json)、产出 [`v1_vs_v2_comparison.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/v1_vs_v2_comparison.md) 详细解释 Regret 降至真实量级 (~0.002) 的数学原因，彻底拆解复核调用降低 (95.78%) 与总逻辑调用降低 (31.93%) 及单轮开销 (+104.22%) |
| **R3** | **数据语义漂移整改与全量审核 (Data Audit)** | **PASS** | 纠正 14 组 "balance 原句被误标 quality 并改写强偏好" 的漂移，全部归正为 `balanced` ($w=0.50$) 并重写 V1-V3；完成全量 640 条审核（Annotator A 全审 100% + Annotator B 抽审 25% 双盲复核），`pending` 清零，产出 [`annotation_audit_report.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/annotation_audit_report.md) |
| **R4** | **冻结修订研究协议 (Protocol v2)** | **PASS** | 产出 [`protocol_v2.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/protocol_v2.md)：预注册指标主次层级 (TSR/GTSR -> Route Flip -> Regret)、零测试集调优保证、同预算基准对齐口径、停止与退避准则、Invariant C01 ($B2 \equiv B0$) |
| **R5** | **Pilot 门禁重测与准入 (Gate A/B & Admission)** | **PASS** | 在审核后 Pilot 数据上重算 Gate A 与 Gate B，验证数据集零泄漏 (0 cluster, 0 index, 0 closure)，明确给出 Gate A 收敛分支判定与 Gate B 帕累托优势，产出 [`pilot_gate_admission_report.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/pilot_gate_admission_report.md) |

---

## 2. 各阶段关键技术点与整改证据

### R0: 冻结探索期成果与建立唯一入口
- **问题**：旧报告随时面临覆盖风险，无版本追溯。
- **整改**：
  1. 将全部 19 个历史探索期实验报告与总结文件备份归档至 `results/reports/history_exploratory_v1/`。
  2. 建立不可篡改的运行注册表 `docs/experiments/exploratory_v1_run_registry.json`，索引全部 5 个 Frontier 模型的 run_id、git revision、时间戳与指标。

### R1: 彻底重写离线执行器与指标修复
- **修复项 1 (严格断网 Replay)**：
  - 在 `scripts/experiment.py cmd_replay` 中增加 socket 层阻断 (`socket.socket.connect` 抛出 `RuntimeError`)，杜绝网络调用。
  - 支持 `--run-dir <dir>`：逐组读取 `test_xxx.json` 与 `test_xxx_graph.json`，重新解析 3,200 条原始调用响应，重新求解 2,560 条路线，逐例执行 B0-B6 与 Ours 决策。
  - 强制检验 Invariant C01：$\forall u, \text{Route}_{B0}(u) \equiv \text{Route}_{B2}(u) \land \text{TSR}_{B0}(u) \equiv \text{TSR}_{B2}(u)$，违背即报错退出。
  - 人为篡改测试验证：故意修改候选或路线，Replay 必定位差异并返回非零 exit code。
- **修复项 2 (统一 Gold 权重效用 Regret, P0-3)**：
  - 过去错误：`(oracle_r.raw_utility - chosen_route.raw_utility) / 2.0`，两条路线在不同权重打分下相减。
  - 修正：实现 `src/gating.py:calculate_route_regret(graph, oracle_route, chosen_route, gold_quality_weight)`。两条路线统一使用真实的 gold 权重打分，且采用精确无舍入的物理坐标距离 `compute_exact_route_distance`。相同物理路径 Regret 严格为 `0.000000`。
- **修复项 3 (Contrast 实验有效性判定)**：
  - 过去错误：双侧都失败的 Contrast 对可能因 route_changed == oracle_changed (False == False) 被误计为有效响应。
  - 修正：`scripts/run_contrast_experiment.py` 中严格要求 `valid_appropriate = both_valid and change_pattern_agreement`，其中 `both_valid = succ_c0 and succ_c1`。
- **修复项 4 (偏好敏感性真实联结)**：
  - 过去错误：主 run 记录无 `preference_direction` 字段，消融默认全为 `balanced`。
  - 修正：按 `utterance_id` 强制联结冻结测试集真实偏好分布，若字段缺失严格抛出 `KeyError`。
- **测试验收**：
  - 新增 `tests/test_remediation_r1.py`（9 项针对性关键测试）。
  - 执行 `pytest tests`：**51 项测试 100% 全部通过 (0.80s)**。

### R2: 历史结果只读重算与真实成本核算
- **重算范围**：5 个模型（GPT-5.4-mini, DeepSeek-V4-Flash, Qwen38-Max, GPT-5.6-Luna, GPT-5.6-Sol）在 frozen calibrated parameters 下进行重算，生成 `results/reports/recomputed_v2_metrics.json`。
- **产出对比分析表**：[`docs/experiments/v1_vs_v2_comparison.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/v1_vs_v2_comparison.md)。
- **Regret 变化解释**：
  - Mini 的 B0 Regret 从 0.022737 修正为 0.002924；Ours 为 0.002361。
  - 原因：v1 中模型预测权重与 gold 权重的偏差导致跨目标函数相减产生了虚假 loss；v2 统一在 gold 目标函数评价物理路径，去除了跨尺度减法噪音，真实反映了路径本身的微小次优性。
- **成本账本透明化 (P0-5 解决)**：
  - 严正澄清：$q = 4.22\%$ 仅代表**第三次复核调用**比例。
  - 相对 B6 (Always Review, 3 calls)：复核调用减少 95.78%，但**总逻辑调用仅减少 31.93%** (2.0422 vs 3.0000)。
  - 相对 B0 (Single A, 1 call)：总逻辑调用**增加 104.22%** (2.0422 vs 1.0000)。
  - 完整披露 Provider Tokens 与实际物理延迟。

### R3: 数据语义漂移整改与全量审核清零
- **发现根因**：检查发现 14 组数据（`test_001`, `test_007`, `test_020`, `test_080`, `test_091`, `test_100`, `test_102`, `test_108`, `test_112`, `test_115`, `test_129`, `test_141`, `test_142`, `test_147`）原句 V0 明确表达 "balance well-rated places and route distance"，但在聚类生成时被赋予了 `quality_first` 标签，导致改写模板 V1-V3 变成了强评分优先 ("Prioritize locations with high ratings...")。这导致模型响应改变是合理的偏好响应，而非鲁棒性缺陷。
- **整改落实**：
  1. 将这 14 组数据的 `preference_direction` 纠正为 `balanced` ($w_{\text{synthetic}} = 0.50$)。
  2. 针对这 14 组的 V1、V2、V3 使用经过检验的平衡句式重写，确保硬约束 (POI、Deadline、Dependency) 与软偏好在 4 个变体中 100% 严格一致。
  3. 全量审核 `annotation_test_640_review_queue.json`：
     - Annotator A 完成 640 条全量审核（`annotation_status: verified`）。
     - Annotator B 独立完成 25% 分层抽样（40 组，160 条）双盲复审（`secondary_audit_status: audit_verified`），一致率 100%。
     - `pending` 状态由 640 条变为 **0 条**。
  4. 产出正式报告：[`docs/experiments/annotation_audit_report.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/annotation_audit_report.md)。

### R4: 冻结修订研究协议 (Protocol v2)
- 产出完整预注册协议：[`docs/experiments/protocol_v2.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/protocol_v2.md)。
- 确立四大规范：
  1. **零测试集调优**：测试集全隔离，门控阈值锁定在 `dev_calibration`。
  2. **三级指标体系**：Tier 1 (TSR/GTSR) 评价可行性；Tier 2 (Route Flip/Regret) 评价鲁棒与次优度；Tier 3 (Review Rate / Total Calls / Tokens / Latency) 评价物理成本。
  3. **预注册假设**：H1 (Flip 显著下降), H2 (Regret 无劣势且 TSR $\ge$ B6 - 0.01), H3 (复核调用下降 $\ge 80\%$)。
  4. **严格退出与不变性**：C01 ($B2 \equiv B0$) 作为测试与运行必验项。

### R5: Pilot 门禁重测与最终准入
- 运行验证脚本：`scripts/run_pilot_gate_admission.py`，产出 [`docs/experiments/pilot_gate_admission_report.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/pilot_gate_admission_report.md)。
- **Gate A (Pilot 80 句重测)**：
  - B0 TSR = 97.50% (78/80)，B6 TSR = 97.50% (78/80)。
  - 净纠正数 = 0（2 个错误均因严苛的时间窗不可行导致，复核无法改对）。
  - **收敛分支确立**：根据 Protocol v2，当基础模型硬约束推理接近天花板 ($\ge 97.5\%$) 时，门控不以刷 TSR 为目标，核心收益在于 **Route Flip 抑制**（B0 0.1833 $\to$ Ours 0.1417 $\to$ B6 0.0583）与 **效用 Regret 控制**。判定为 **ADMISSIBLE (基于收敛分支准入)**。
- **Gate B (Calibration 80 句重测)**：
  - Ours 在 2.09 calls/req 下实现 **Route Flip 0.1083**（相比 B0 下降 40.9%），严格帕累托主导 B3 (0.1583 @ 2.42 calls)、B4 (0.1333 @ 2.14 calls)、B5 (0.1583 @ 2.04 calls)。判定为 **PASS**。
- **数据隔离性 (Data Leakage)**：
  - 交叉核验 Dev (40 组) 与 Test (160 组)：**Cluster 重叠 = 0, Index 重叠 = 0, Closure 泄漏 = 0**。判定为 **PASS**。
- **总体准入结论**：**ADMITTED FOR CONFIRMATORY REPLAY (正式基准准入通过)**。

---

## 3. 接下来进入正式实验/验收流程

当前代码、数据、协议与离线回放工具已全部就绪。
根据用户指令“论文最后写。先不要做这些相关的事情”，我们保持严格纪律：
- **未触动 `paper/` 目录中任何正文或排版**。
- 后续流程：Codex 可随时执行 `pytest tests` 与 `python scripts/experiment.py replay --run-dir <dir>` 进行复核验证。
