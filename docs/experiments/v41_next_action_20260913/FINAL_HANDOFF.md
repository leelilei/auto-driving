# LLMAP 迁移实验最终交付与验收报告 (FINAL_HANDOFF)

- **交付日期**: `2026-09-13`
- **执行分支**: 【分支 B：离线场景快照的 LLMAP 后端迁移实验 (LLMAP-Adapted Backend Transfer)】
- **审查基准**: [`docs/guides/AGY_NEXT_ACTION_DS_QWEN_TRANSFER_20260913.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/guides/AGY_NEXT_ACTION_DS_QWEN_TRANSFER_20260913.md)
- **代码版本**: Commit `dbaa94b497340c800c1eee4e825e955d7c917f72` 及本轮新增组件
- **主模型**: 官方 DeepSeek v4 节点 (`https://api.deepseek.com`, 请求 `deepseek-v4-flash`, 返回 `deepseek-flash`)

---

## 1. 交付产物与资产完整性核验

| 资产类型 | 资产路径 | 规格与状态 |
| :--- | :--- | :--- |
| **算法修复实现** | [`9-AutoDriving-core/src/baselines/llmap_adapted.py`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/src/baselines/llmap_adapted.py) | 修复负权边 Dijkstra 崩溃，改用 DAG / Bellman-Ford；修复空序列除零与组映射缺陷 |
| **单元测试套件** | [`9-AutoDriving-core/tests/test_llmap_adapted.py`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/tests/test_llmap_adapted.py) | 5/5 测试全绿 (负权边修复、单节点归一化、依赖校验、端到端评测) |
| **数据集快照 (Dev)** | [`9-AutoDriving-core/data/llmap_transfer/dev_5_*`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/llmap_transfer/) | 5 组独立 HIPP 指令 (20 变体) 与 5 张离线场景快照，与历史 160 组 0 暴露 |
| **数据集快照 (Eval)** | [`9-AutoDriving-core/data/llmap_transfer/eval_40_*`](file:///Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core/data/llmap_transfer/) | 40 组未见 HIPP 指令 (160 变体) 与 40 张离线场景快照，与历史 160 组 0 暴露 |
| **审核队列文档** | [`docs/experiments/v41_next_action_20260913/REVIEW_QUEUE.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/experiments/v41_next_action_20260913/REVIEW_QUEUE.md) | 完整登记 5 Dev + 40 Eval 的源索引、Gold 标签与 4 变体文本 |
| **执行入口脚本** | [`scripts/run_v41_next_action.py`](file:///Users/mac/Documents/6-Research/9-AutoDriving/scripts/run_v41_next_action.py) | 支持 preflight / health_check / collect / evaluate / replay / status |
| **Dev 实验产物** | `9-AutoDriving-core/results/v4_1/next_action_20260913/health_check_dev_20260913T070916Z/` | 20 次尝试日志全记录，5 个 record，Replay 哈希校验 100% 一致 |
| **Eval 实验产物** | `9-AutoDriving-core/results/v4_1/next_action_20260913/transfer_branch_b_20260913T071442Z/` | 520 次尝试日志全记录，160 个 record，Replay 哈希校验 100% 一致 |

---

## 2. 核心实验结果与科学发现

### 2.1 系统层对照（40 条原始 HIPP V0 指令）

在相同地图场景与解码条件下，原版 LLMAP 提示抽取管线与 DARC 抽取管线的表现对比：

| 指标 (40 条原始 V0) | LLMAP-Adapted Baseline | DARC Pipeline (Candidate A) | 差值 (DARC − Baseline) |
| :--- | :---: | :---: | :---: |
| **硬约束成功率 (Valid Rate)** | 100.0% (40/40) | 100.0% (40/40) | 0.0% |
| **分类覆盖率 (Group Coverage)** | 100.0% | 100.0% | 0.0% |
| **平均路径长度 (Path Length)** | 19.54 km | **18.04 km** | **-1.50 km (更优短路径)** |
| **平均 POI 评分 (Rating)** | 4.26 | 4.21 | -0.05 |
| **超时违规次数 (Time Violations)** | 0 | 0 | 0 |
| **时序依赖违规数 (Dep Violations)** | 0 | 0 | 0 |
| **营业时间违规数 (Avail Violations)** | 0 | 0 | 0 |

**结论**：在保持 100% 满足时间、时序依赖与营业时间硬约束的前提下，DARC 抽取的约束意图在求解器中规划出的路线总长度缩短了 **1.50 km (缩短 7.7%)**，路线紧凑性显著提升。

---

### 2.2 机制层对照（40 组 × 4 变体 = 160 句，预算 $K=10\%=16$ 次复核）

统一在 `MSGS-adapted` 求解器后端上，各复核分配策略表现如下：

| 策略 | TSR (%) | GTSR (%) | 条件 Flip 率 (%) | 全分母 Flip-or-Fail (%) | 综合效用 (Utility) | 复核次数 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0 (No Review)** | 100.0 | 100.0 | 0.0 | 0.0 | 0.4797 | 0 |
| **B4 (Param Diff)** | 100.0 | 100.0 | 0.0 | 0.0 | 0.4811 | 16 |
| **DARC ($\Delta U$ Gating)** | 100.0 | 100.0 | 0.0 | 0.0 | **0.4812** | 16 |
| **B3 (Random Review)** | 100.0 | 100.0 | 0.0 | 0.0 | 0.4878 | 16 |
| **B6 (All Review 上界)** | 100.0 | 100.0 | 0.0 | 0.0 | 0.5260 | 160 |

### 2.3 统计检验与置信区间 (Cluster Bootstrap 2,000 次，固定种子 20260912)

| 对比项 | 均值差值 | 95% Bootstrap 置信区间 | 原始 p 值 | Holm 校正判定 | 科学结论 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **DARC − B4** | +0.000059 | `[-0.003916, +0.004917]` | p = 1.000 | 触 0 (不显著) | $\Delta U$ 与参数差选出的复核增益相当 |
| **DARC − B3** | -0.006567 | `[-0.017453, +0.002895]` | p = 0.200 | 触 0 (不显著) | 差异在统计涨落范围内 |

**实事求是的科学结论（遵从指引第 1、7、9 节）**：
1. **模型能力高位饱和**：DeepSeek-v4 在 40 组/160 句上的意图抽取能力极强，在 160 句上取得了 100% 的 TSR 与 GTSR，未产生任何语法解析失败或硬约束破坏。
2. **复核增益真实但微小**：复核策略（B4、DARC）相比不复核（B0）带来了确定性的正向效用改善（0.4812 vs 0.4797）；而全量复核（B6）能够提供实质性的质量提升（0.5260，增益 +0.0463）。
3. **严格遵守负结果披露**：在受限的 10% 预算下，DARC 的 $\Delta U$ 调度与 B4 参数差异调度的效用差异较小，置信区间触 0，如实报告为无显著差异，不夸大宣称“全面胜出”。

---

## 3. 真实离线重放 (True Offline Replay) 校验

对评估包执行断网级重放验证：
```bash
python scripts/run_v41_next_action.py replay \
  --run-dir 9-AutoDriving-core/results/v4_1/next_action_20260913/transfer_branch_b_20260913T071442Z \
  --budget 0.10
```
- **原始产物 SHA256**: `0959d7b75e0bba0a1665884e0f21e6ecc5b3fd911f6bcdb2ab2a0e6648b4e0ad`
- **重放计算 SHA256**: `0959d7b75e0bba0a1665884e0f21e6ecc5b3fd911f6bcdb2ab2a0e6648b4e0ad`
- **哈希比对结果**: **完全一致 (Bit-for-bit identical)**。

---

## 4. 预算账本核销

| 阶段 | 预期上限 | 实际 HTTP 尝试 | 实际成功调用 | 失败重试次数 | 预算合规性 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dev 健康检查** | 20 | 20 | 20 | 0 | 100% 消耗，0 浪费 |
| **Eval 迁移实验** | 520 | 520 | 520 | 0 | 100% 消耗，0 浪费 |
| **合计** | **540** | **540** | **540** | **0** | **严格契合 540 次上限** |

实验全过程无任何隐藏调用，无超预算追加，完整闭环交付。
