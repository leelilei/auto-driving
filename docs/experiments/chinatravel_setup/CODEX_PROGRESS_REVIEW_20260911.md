# Claude 的 ChinaTravel 进度复核

2026-09-11，Codex 本地源码、文件及离线接口审查。没有调用模型 API，没有改写 Claude 的代码、实验结果或原报告。本报告不是论文评审，不判定新研究假设已成立。

## 当前结论

已经完成有价值的环境与数据准备，但尚未通过官方评分器验收，也没有成功的基线实验结果。当前应定位为“环境资产已落地，端到端单例待修通”，不能按文档中的 65% 或阶段完成勾选视为研究进度。

| 项目 | 独立查验结果 |
|---|---|
| 上游代码 | HEAD 为计划固定的 `0936f2727dd102ad811ed015b7bf6f7d6533f28e`；有新增本地脚本 |
| 独立环境 | `.venv-chinatravel/bin/python` 可运行，jsonschema 和项目模块可导入；这不等于所有任务依赖已运行验收 |
| Sandbox | 2026.08.2 发布清单，14 个中英文 parquet 表已落地；逐项重算发布清单 23 个文件 SHA256，全部匹配，无缺失 |
| 数据分区 | 分区清单含 60 dev、544 hold，UID 交集为 0；实际 60 个 dev JSON 与合并文件均匹配 dev 清单，DSL 已为 list |
| Oracle 隔离 | 有过滤函数和哨兵检查，但还未验证最终模型调用边界；不能标完整链路 PASS |
| 官方 Act 尝试 | 三个模型目录各有同一个案例的错误文件，均为 `Exceed maximum steps`，没有成功计划 |
| 新 B0/B1/B2 实验 | 三个结果目录均为空；脚本有确定性接口与评分错误，尚不能运行完整实验 |
| 评分器验证 | “5/5”只覆盖自定义结构与部分函数，不构成官方三层评分验收 |

详见机器可读 [核验记录](CODEX_AUDIT_EVIDENCE_20260911.json)。604 总量与 hold 内容主要核对清单，未逐条重新审核全体语义；UID 不重叠不等于语义家族无泄漏。

## 阻断问题

### P0-1 评分器测试验证了错误的输出格式

`9-AutoDriving-core/scripts/stage2_evaluator_test.py:21` 自定义 `PLAN_SCHEMA` 是双层数组，含 current_city、breakfast 等字段。官方 `external/ChinaTravel/chinatravel/evaluation/output_schema.json` 的顶层是 object，包含 itinerary/activities 等字段。离线用同一“正常计划”验证，自定义 schema 通过，官方 schema 失败；空数组也是自定义通过、官方失败。

该脚本只导入 hard evaluator，没有实际调用。测试 2 无论正常返回或异常均可通过，测试 5 只要不抛异常就返回 True；没有真正的部分预测缺失分母测试。两个 commonsense 低分也可能来自错误结构，不能据此定位为预期的城市或时间冲突。因此 `STAGE2_EVALUATOR_VALIDATION.md` 的“三层验证完成”“完整分母正常”和“离线权限隔离确认”超出证据。

验收修复要求为使用官方 schema 和 `eval_exp.py` 同一路径的 v2 hard evaluator，先准备真实有效正例，再逐项制造实体、时间、硬约束、空输出和缺失预测错误。断言具体错误原因及全体预期 ID 分母；禁止把任意异常算通过。

### P0-2 基线没有接收到完整研究任务

`9-AutoDriving-core/src/baselines/direct.py:27` 及 fewshot/cot 只拼接城市、天数、人数，忽略 `nature_language/query` 中的用户要求。用实际 dev 原句做离线提示检查，完整原句不在提示中。它们要求生成的又是上述双层数组，并要求模型凭常识选择知名场所，没有接通 sandbox 检索或同条件规划后端。

这类结果即使低分，也不能解释为模型误读用户约束，更不能作为 DARC 的强基线。先保留完整原句和公开环境访问，再谈对比方法；不要删掉任务要求后统计“语义理解错误”。

### P0-3 基线运行链路有多处接口断裂

`stage3_baseline_experiment.py:22` 先把项目 src 插到路径首位，随后又把 external/ChinaTravel 插到首位。新 Python 进程实际导入的是 `external/ChinaTravel/baselines.py`，这份类只有 generate_response，没有 runner 所需的 method_name/generate_plan。离线新进程已确认；若会话曾导入另一模块，表现还可能因模块缓存不同而变化。

即便修复导入，项目 `src/baselines/base.py` 调用 `llm_client.call(...)`，实际项目 `LLM` 提供 `complete(system, user)`，没有 call。两份同名模块不应继续混用，先统一一种明确接口。

### P0-4 实际评分不是 ChinaTravel 官方指标

`stage3_baseline_experiment.py:30` 的 `simple_evaluate` 是目的地字符串匹配，含固定 `clarity=0.8` 占位值。60 条 dev 均无 expected_destinations，因此即使传入预期 dict 也不能得到有效官方成绩；按基线声明传入 list 会直接触发 AttributeError。

脚本仅对非 None 计划评分，排除生成失败后计算正确率，导致分母缩小。随后输出不存在的 schema_pass_rate、commonsense_macro_avg、hard_pass_rate 等键，还会报错。没有可用的官方评分主表或完整离线 replay 链路。

验收时保留全部预期 ID，失败计失败；使用官方三层评分与 all-pass，不将“字符串匹配”或固定占位评分写成实验结果。

## 需补齐但不等于已发生泄漏的问题

Oracle 过滤的 `verify_oracle_isolation` 主要检查顶层字段名；清理后的显式验证仅抽查每个分区前 10 条。它没有捕获最后实际送入模型的请求。合并 dev 文件仍带 hard_logic_py，这对独立评分数据可以合理，但不能由“曾经执行过滤”推断所有后续路径都隔离成功。也没有证据证明已经向模型泄漏，应标为未完成端到端验证。

数据 manifest 缺少查询仓库 revision 及完整文件哈希，只有样本截短 hash；prepare 脚本的 glob 未排序，`--subset` 取前 N 条的含义不稳定。补齐源版本、固定 ID 序列、查询/评分数据分离和请求哨兵测试。分区按 UID 前段抽取，还需检查生成模板/城市聚集性，不能把无 UID 交集称为无语义泄漏。

## 已有 Act 错误记录怎样解释

三个目录分别命名为 Claude-3.5-Sonnet、GPT-4o、GPT-5.6-Terra，均只有同一 UID 的错误记录。前两份记录 token 为 0，Terra 记录 input 305,839、output 5,098。它们支持“尝试未产出最终计划”，不支持三模型性能比较，也不能仅凭步数超限判定节点故障或模型能力不足。需要查看完整工具轨迹、停止条件及原始响应，才能定位 Terra 在哪里消耗步数。

## 研究设计需要纠正的方向

`STAGE3_BASELINE_PLAN.md` 把 E6 次优路线当作语义错误，把“所有基线弱”视为任务有挑战性的证据，并提出基线强就重新设计标准。这会偏离本项目的研究原则。

次优不等于误读；没有明确用户目标或最优性参考就不应标 suboptimal。基线全弱首先检查输入、工具、格式和评分。强基线正确时允许停止，不以制造差距为目的改标准。“每类至少三个案例”只能是展示愿望，不能要求产生不存在的错误。新 ChinaTravel 候选也不是历史 v5.1 的直接续验。

## 建议 Claude 下一轮只完成的任务

1. 修正阶段状态，把 Stage 2 改为未验收，Stage 3 改为未跑通；保留历史报告并链接本审查。
2. 使用官方结构和评分入口，完成一个有效正例及独立的失败/缺失预测测试。固定源版本和 sandbox 路径，阻断网络后复算。
3. 统一基线导入和 LLM 接口，原句完整输入，真实连接公开环境工具；用记录请求的假客户端验证输入权限和输出格式。
4. 复查已有 Terra 轨迹，在明确调用/步数预算下只跑 1 个 dev 案例，取得官方完整评分和原始证据。再考虑 3 例，最后才是 60 例。
5. 将“正确行程但错误语义”独立定义并审核，不能从格式、常识或次优标签直接推断；根据自然错误决定研究去留。

本轮未擅自继续模型采集或重写实验实现。论文写作仍为 CLOSED。当前优先级是修正实验有效性，而非增加模型与并发。
