# ChinaTravel Repair v1 结果

日期：2026-09-12。性质：固定六条开发集上的工程修复与离线官方评分复核。不是完整 benchmark、SOTA、DARC 有效性或独立语义裁决结果。

## 结论

在不修改搜索策略、搜索宽度和单例 30 秒时限的前提下，使用 DeepSeek 官方接口重新解析固定六条，并仅对规划器输出做官方 schema 类型适配：全六条官方 all-pass 为 **5/6（83.33%）**。五条搜索成功的计划经适配后全部通过官方 schema、commonsense 和 hard-constraint 评价；剩余一条是在限定时间内未搜索到计划，不是 API 或 schema 失败。

当前没有建立可独立判定的自然语言语义错误候选，因此不能启动或宣称阶段 5 的语言反馈与计算后果反馈比较。下一步按执行书转入预先冻结的 12 条基线错误分布诊断，不继续针对固定六条调参追求 6/6。

## 固定条件与结果

| 项目 | 结果 |
|---|---|
| 开发样本 | 预先固定 6 条，顺序与 `public_inputs.json` 一致 |
| 模型调用 | DeepSeek 官方 API，6 个逻辑请求，6 份成功响应 |
| 请求暴露 | 仅 `uid` 与 `nature_language`；不含 gold DSL / `hard_logic_py` |
| 人数约定 | 提示中显式披露数据集约定：单人表述为 1，同行关系为 2，“N 个人”为 N |
| 搜索 | 原策略，宽度 10，30 秒/例；规划阶段无模型调用 |
| 官方 all-pass | 5/6，83.33%，按固定六条全分母计算 |
| 搜索成功条件子集 | 5/5 官方 all-pass；不替代主分母 |
| schema 适配 | 仅住宿 `room_type` 的字符串 `"1"` / `"2"` 转整数 |
| 适配次数 | 9 |
| 补造值 | 0 |
| 唯一失败 | `e20241028160848776495`，30 秒边界内搜索失败 |

六条解析意图均包含本版接口所需信息。适配器采用深拷贝，记录每个修改路径；缺失结构、其他字符串数字或非法值不会被补齐。首次规划目录中未生效的内联适配结果原样保留为历史证据，最终成绩来自独立确定性后处理及全分母离线复算。

## 可复核证据

- 原始 API 请求与响应：`9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1/collection.json`
- 规划原始结果：`9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1/planning/summary.json`
- 确定性后处理：`9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1/postprocessed/summary.json`
- 最终全分母审计：`9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1/final_audit.json`
- 证据哈希：`9-AutoDriving-core/data/chinatravel_repair_v1_deepseek6_retry1/final_hashes.json`

最终审计检查了固定 ID、请求隔离、真实响应、原始计划到适配计划的确定性重算、官方六条全分母评分和适配修改计数，结果为 PASS。适配器测试 2 项、现有 v4 解析/编译测试 4 项均通过。

## 研究边界

Repair v1 说明 ChinaTravel 的 parse → compile → RuleNeSy → official evaluation 工程链路已经可用，并将先前的 API、schema 与模型语义问题分开。它没有证明计算后果反馈优于语言反馈，也没有发现适合进入配对反馈实验的语义错误。只有冻结 12 条诊断经人工独立审查确认真实语义误读后，才进入阶段 5；否则应报告错误主要来自接口或搜索，或重新评估研究问题。
