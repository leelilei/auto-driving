# 交给 agy CLI 的执行指令

> **2026-09-09 执行入口已更新**：本文件主体为旧协议/历史交接。当前请使用 [v5.1实验指导书](v5_1/EXPERIMENT_GUIDE.md)、[agy第一批任务](v5_1/AGY_HANDOFF.md) 与 [Codex验收清单](v5_1/CODEX_ACCEPTANCE_CHECKLIST.md)。不要按下方旧门控任务启动v5实验。

以下整段可直接发送给 agy CLI：

---

请在 `/Users/mac/Documents/6-Research/9-AutoDriving` 实现并推进 DARC-Route 实验。

先完整阅读：

1. `docs/experiments/EXPERIMENT_GUIDE.md`：实施与实验协议。
2. `docs/experiments/ACCEPTANCE_CHECKLIST.md`：逐项证据要求。
3. `docs/experiments/readiness_20260906.md`：实际已完成内容与风险。
4. `docs/plans/proposal.md`、`docs/guides/todolist.md`：研究目标与状态。

任务目标是可靠地实现、运行和交付可复查实验，不是必须得到正向提升。复用已有核心代码，使用 `9-AutoDriving-core/.venv/bin/python`。不要重跑已有 20 条原句来冒充正式 80 句 Pilot，不要未经检查跑全量 Test。

第一批交付先完成指导书 P0 和 P1 的可独立实施部分：

- 检查和补齐精确求解、独立评价、严格 schema、门控、基线、缓存、预算和日志。
- 实现统一实验入口及 dry-run/resume/离线 replay；新增接口必须确实可运行。
- 构建开发暴露清单、候选划分、20组×4句等义候选与可填写的人工审核表。
- 完成离线测试、数据结构与泄漏检查，保存证据。
- 有真实人工确认后，才将数据标为 human_verified 并运行正式 E1。没有人工确认时，把正式 Pilot 标为 blocked_on_annotation，交付待审核清单；继续完成不依赖人工答案的工程工作，不伪造审核状态。

如果前提成立、Pilot 支持继续，则按指导书推进校准与冻结测试；否则完整交付 no-go/inconclusive 的证据，不擅自改变研究任务来制造收益。后续正式阶段仍需遵守协议前提和明确运行预算。

保留所有失败、原始响应、模型参数、图、数据/代码哈希、成本和命令。API key 仅从环境变量读取，不写入文件；不删除历史运行，不修改其他项目。所有新结果必须标清 exploratory、pilot、calibration 或 test。

请维护 `docs/guides/todolist.md`，并将关键变更写入 `docs/project/decisions.md`。完成后交付：

- `docs/experiments/HANDOFF_RESULTS.md`：完成/未完成项、真实运行命令、结果、成本、问题和下一步。
- 已填写状态与证据路径的验收清单；只有真正运行的检查才填 PASS。
- `submission_manifest.json`：代码、数据、标注、图、配置、运行、报告的路径与 SHA256。
- 一条不联网即可重算主表的命令，以及完整测试命令。

最后明确报告：工程是否通过、正式数据是否审核、Gate A/B/C 是否实际检验、是否存在研究增量。不要代替 Codex 签署最终验收；后续由 Codex 独立检查。

---

## 交付报告建议结构

```markdown
# HANDOFF_RESULTS
日期 / 协议版本 / 源码版本

## 本批范围
实现了哪些阶段，哪些阶段未运行。

## 变更与测试
修改文件、原因、命令、退出码、证据路径。

## 数据与运行
数据审核与划分状态、图版本、模型配置、运行 ID、失败与补测。

## 结果
真实计数与分母、成本、纠正/改坏、区间、明确的结论边界。

## 验收证据索引
清单 ID → 状态 → 文件路径。

## 阻塞与下一步
需要人工审核的具体条目；尚未完成的实现；是否建议继续扩量。
```
