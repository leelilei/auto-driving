# ChinaTravel 下一步工程交接任务单

日期：2026-09-11。执行者：Claude Code / agy CLI；复核者：Codex；研究负责人：本对话用户。

项目根目录：`/Users/mac/Documents/6-Research/9-AutoDriving`。

## 1. 本轮目标与完成定义

修复工具协议和预算分配，使 **完整用户原句 → 真实 sandbox 查询 → 最终行程 → 官方评分 → 断网回放** 可以完整执行。先完成离线验收，再执行最多三个开发案例。

本轮属于工程开发验证，不是 DARC 有效性实验，也不是公开 benchmark 主表。允许最终任务失败；成功交付的条件是失败可定位、原始证据完整、分母不变。只有实际产出有效行程并通过官方评价，才能把对应案例标为任务成功。

研究原则继续执行：实验真实落地 → Codex 独立验收 → 负责人认可 → 最后写论文。论文 CLOSED。本任务不包括论文撰写、60 例扩量、模型横向比较、修改 benchmark 或为获得提升重设评价标准。

## 2. 先读这些材料

1. [Codex 整改执行记录](CODEX_REMEDIATION_20260911.md)。这是当前工程事实入口。
2. [机器可读单例总结](codex_validation/smoke_summary.json)。
3. [此前进度复核](CODEX_PROGRESS_REVIEW_20260911.md)。了解为何旧 B0/B1/B2 和“评分器 5/5”不能使用。
4. [Proposal 重新定位](../../plans/PROPOSAL_REASSESSMENT_20260911.md)。新方向仍是候选，不能当已有方法贡献。

旧 STAGE3_BASELINE_PLAN、COMPLETION_REPORT 和阶段百分比仅作历史材料，不覆盖本任务单。

## 3. 已有资产与已验证状态

| 资产 | 路径或状态 |
|---|---|
| 官方源码 | `external/ChinaTravel`，commit `0936f2727dd102ad811ed015b7bf6f7d6533f28e` |
| 独立 Python | `external/ChinaTravel/.venv-chinatravel/bin/python` |
| Sandbox | 发布版本 2026.08.2；发布清单 23 文件、评分工具实际读取的中英文 264 源文件均已重算匹配 |
| 开发数据 | `9-AutoDriving-core/data/chinatravel_dev_60.json`；60 dev 与 544 hold 的 UID 不重叠，尚不等于语义家族完全隔离 |
| 当前适配器 | `9-AutoDriving-core/scripts/chinatravel_pipeline.py` |
| 官方评分测试 | `9-AutoDriving-core/scripts/stage2_evaluator_test.py`，目前 13 项通过 |
| 测试实现 | `9-AutoDriving-core/tests/test_chinatravel_pipeline.py` |
| 已有真实单例 | `9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_haiku_smoke` |
| 模型配置来源 | `9-AutoDriving-core/configs/scene_xcode_haiku.json`；xcode，`claude-haiku-4-5-20251001` |

已有单例是开发 ID `e20241028160248698752`，原句为上海出发、一个人去杭州一天、预算 1500 元。实际 8 次请求，约 59.5 秒，记录 input 15,152、output 4,285 token。三次查询得到实际数据，两次无数据，三次命令错误；在第九次发送前达到累计字符预算。没有最终 itinerary，官方 all-pass 为 0/1，两次断网回放一致。

不能把这个结果写成“模型能力不足”“ChinaTravel 不适合”或“DARC 无效”。它目前说明采集过程消耗了最终规划所需预算，同时工具协议仍有错误。

## 4. 修改前必须保护历史证据

当前 v1 replay 会校验自身 `pipeline_sha256`。**直接修改 `chinatravel_pipeline.py` 会让旧 run 无法按原命令重放。** 推荐保留 v1 文件及旧兼容入口，新建 `chinatravel_pipeline_v2.py` 和独立测试，不静默覆盖旧实现。

- 不改旧 run、数据、gold DSL、评分器源码或 fixture 来让新测试通过。
- 保持现有 13 项测试仍能执行，新增 v2 测试使用不同文件名。
- 新采集使用全新且不可覆盖的运行目录，manifest 记录适配版本。
- `codex_validation/fixture_candidate.json` 是给定 gold 后离线构造、人工修正的评分器正例。它仅用于测试评分器，不是模型成绩，不进入 few-shot、模型上下文或候选选择。
- 新运行需要额外固定官方评价相关源码哈希，不能只保存 schema 哈希。至少覆盖调用的 schema/commonsense/hard v2 模块、symbol verification 及相关数据清单。

## 5. 工作包 A：结构化工具协议

### 问题

当前 Act 让模型输出 Python 风格命令。单例两次输出了不必要的反斜杠，导致命令无法解析；`goto` 对“西湖”的查询返回解包错误，既没有明确说明实体匹配失败，也没有给调用方稳定错误结构。

### 实现要求

用 JSON 描述动作，由宿主做类型校验并调度官方工具。例如：

```json
{
  "kind": "tool",
  "name": "intercity_transport_select",
  "arguments": {
    "start_city": "上海",
    "end_city": "杭州",
    "intercity_type": "train",
    "earliest_leave_time": "08:00"
  }
}
```

这只是接口示例，不要求把该具体班次条件硬编码到所有案例。

1. 只允许白名单工具和显式参数。未知工具、缺少参数、错误类型分别返回可判读错误。不要用 `eval` 执行模型内容。
2. 对需要筛选谓词的官方工具，用有限的结构化操作符（如 eq、contains、比较）生成宿主侧函数。不要接受模型传来的任意 Python/lambda 字符串；支持范围与不支持的条件写清楚。
3. 保留 `raw_response → parsed_action → dispatched_call → observation` 四层记录。原始输出必须保留，不用全局去反斜杠等方式偷偷修复。若允许去除外层 Markdown 围栏，规则必须固定、测试并记录该转换。
4. 区分“没有匹配数据”“实体名称无法解析”“工具参数错误”“工具内部异常”。不要把任何异常都记为合理空结果。对未知实体可提示查询 POI 名称工具，但不能用 gold 替它选答案。
5. 每个模型响应最多执行一个动作；多个动作或未知 kind 应明确拒绝。格式纠错也计入调用预算。
6. 使用真实本地环境工具。可以缩减每次返回条数并提供显式分页，但排序、截断和分页规则要记录；不依据 gold 或最终成绩挑选返回数据。

这是对官方 Act 的本地协议适配，报告中使用明确的适配名称，不声称未修改的官方 Act 复现，也暂不冠名“新强基线”。

## 6. 工作包 B：给最终规划预留预算

### 问题

v1 每次发送完整增长的会话，累计字符预算在调用上限前耗尽，没有留出最终输出机会。只增加并发或上限不能修复这一结构问题。

### 本轮采用的固定预算

| 项目 | 上限或规则 |
|---|---|
| 模型、节点 | 继续使用现有 Haiku/xcode，不自动换模型或供应商 |
| 并发 | 1 |
| 每案例物理请求 | 最多 12；所有重试、格式纠错、摘要调用均计入 |
| 信息查询阶段 | 最多 8 次请求，错误动作也占用名额 |
| 最终规划 | 预留至少 1 次；原句、已查询事实与官方输出 schema 同时输入 |
| 累计请求字符 | 上限 160,000，以实际发送的 system/user 内容统一计数；其中为最终规划保留 50,000，查询阶段最多使用 110,000 |
| 单请求输出 | 上限 4,096 token |
| 单请求超时 | 60 秒；自动传输重试 0 |
| 每案例时间 | 900 秒；说明正在进行的请求如何受剩余时限约束 |
| 连续协议失败 | 2 次则停止该案例，记录明确状态 |
| 全轮采集 | 最多 3 案例、36 次物理请求；未使用额度不转成反复调参重跑 |

字符上限是工程资源约束，不是算法门控参数，也不代表精确 token 或费用上限。新计数口径包含 system，与旧 run 的仅 user 累计值不能直接当同口径效率提升。

查询阶段结束时明确进入最终规划；即使信息不充分，也保存模型最终输出或诚实的失败原因，不能造数据补齐。两次连续协议失败等硬停止例外不强行追加规划调用。

可以把观察结果保存到结构化事实记录，避免每轮重复全量历史。若压缩历史，采用可追溯的确定性保留/截断规则，保留原始完整轨迹，标明哪些内容不再进入后续上下文。不要偷偷添加未计费的 LLM 摘要，也不要让执行器根据 gold 修正事实。

## 7. 工作包 C：原句、gold 与官方评分隔离

- 原始 `nature_language` 完整进入任务上下文；不得只保留城市、天数和人数。
- 尽量由独立的数据准备入口生成仅含 uid/原句的模型输入文件；gold 与结构化标签交给单独评分进程。模型运行入口不需要整份带 gold 的数据对象。
- 请求边界做哨兵测试，检查最终实际序列化的 system、messages、工具参数、修复反馈，而不只是检查清理函数返回值。
- `hard_logic_py`、正确答案及其逐约束评价反馈不能用于生成或修复。官方评分在采集结束后进行；如未来测试 oracle 条件，应另行命名和隔离。
- 官方评分使用与 `eval_exp.py` 相同的三层函数和最终通过 ID 交集。空、缺失、无效输出均保留在全部预期 ID 分母；运行失败不能从主表删除。
- JSON 格式不合格是原始输出失败。即使以后增加回退，raw 与 final 也必须分开，不把回退算作模型纠正。
- 无效实体、时间冲突或次优路线不自动等于“语义误读”。本轮只做工程错误分类，不给 DARC 机制贴正负结论。

## 8. 工作包 D：先离线验收，再按固定顺序试跑

### 离线验收

至少覆盖以下行为，按实际断言数量报告，不为凑数量新增镜像测试。

| 检查 | 必须观察到的行为 |
|---|---|
| 合法 JSON 动作 | 类型检查通过，并真实调用官方工具 |
| 转义/无效 JSON/多动作 | 不误执行，原响应和错误原因可追踪 |
| 未知工具/危险表达式 | 拒绝执行，不产生任意代码能力 |
| 未知实体与空结果 | 区分可恢复查询失败和内部异常；没有编造实体替换 |
| 完整原句、gold 哨兵 | 检查实际请求；模型端不出现注入的独立 gold 哨兵 |
| 预算边界 | 计入失败请求；查询阶段不能吞掉预留规划额度；超限请求不发送 |
| 最终输出 | 使用官方 object/itinerary/activities schema，而不是旧双层数组 |
| 官方评分 | 有效正例通过；错误实体、时间、硬约束、空输出分别失败 |
| 分母 | 例如 1 个有效预测加 1 个缺失预测，all-pass 应为 1/2 |
| 重放 | 禁止网络后复算一致；删除预测、修改响应或替换相关评价源码均被检测 |

重放至少校验预期文件角色、调用计数及 ID 完整性，不能仅遍历可被删空的哈希字典。哈希用于完整性，不声称可抵御同时重写全部清单的对手。

### 真实采集顺序

1. 离线通过后，在模型调用前冻结三例 ID、顺序、提示、协议、代码哈希、模型配置及预算到 `plan.json`。
2. 第一例使用已暴露的 `e20241028160248698752`，明确标为回归开发例。其余两例从冻结的 dev 分区中，分别选择 medium、human 的字典序最小 UID；不根据成绩更换案例。不得从 hold 或 human1000 取样调试。
3. 先执行第一例。若工具调用、最终输出与官方评分流程均能完成，再用相同代码配置执行其余两例。第一例可以是官方约束失败，但必须有可评分的最终 schema 合格计划；否则停止扩展，交付根因。
4. 若第一例停在传输、协议或预算错误，不现场放宽预算继续冲成绩。本轮交付失败轨迹与修复建议；下一次修改另立版本和计划。
5. 三例全部属于开发，不能称确认性实验、泛化验证或“取得 SOTA”。到这一步交给 Codex 复核，不自行扩量到 60 例。

## 9. 应交付的文件

建议沿用以下命名；如调整名称，必须在总入口给出准确路径和可运行命令。

```text
9-AutoDriving-core/scripts/chinatravel_pipeline_v2.py
9-AutoDriving-core/tests/test_chinatravel_pipeline_v2.py
9-AutoDriving-core/configs/chinatravel_act_v2.json
9-AutoDriving-core/results/chinatravel_baselines/<新运行目录>/
    plan.json
    manifest.json
    public_inputs.json
    requests/                 # 原始请求、响应、错误与usage
    tool_trace.jsonl           # 原动作、解析动作、执行及观察结果
    predictions.json           # 全部预期ID，失败也保留
    collection.json
    official_score.json
    replay_report.json
    manifest_hashes.json
docs/experiments/chinatravel_setup/
    NEXT_IMPLEMENTATION_REPORT.md
    NEXT_ACCEPTANCE_CHECKLIST.md
```

已有密钥继续从环境或已配置的安全入口读取。配置、日志、文档、终端输出不写入密钥，不使用打印完整环境变量的排查命令。

`NEXT_IMPLEMENTATION_REPORT.md` 必须回答：改了什么；与官方 Act 有哪些差异；调用数、失败数、未知 usage、token 与耗时；每案例 schema/commonsense/hard/all-pass；为何停止或允许下一步；尚未解决什么。清楚区分模型未产出、产出格式错误、环境不可执行、硬约束失败，不用单个“失败”掩盖原因。

给出的执行命令必须实际验证，不能写尚不存在的 CLI 参数。现有可验证的回归命令如下；v2 的运行和 replay 命令由执行者实现后补入交付报告。

```bash
cd /Users/mac/Documents/6-Research/9-AutoDriving

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/stage2_evaluator_test.py

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_pipeline.py replay \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_haiku_smoke
```

## 10. Codex 收到交付后的独立检查

1. 对照源代码确认调用的是官方评分器，检查 v1 未被破坏、新旧输出未混写。
2. 独立执行旧回归与 v2 测试；核验正例来源，没有改 gold、削弱断言或替换评价目标。
3. 抽查实际请求的完整原句、环境事实、模型配置和 gold 隔离，核对原响应到执行动作的每次转换。
4. 用原始逐请求记录重算物理调用、失败、usage 未知和预算消耗，检查有无未计入的重试、摘要或后处理调用。
5. 比对计划预期 ID 与预测/评分 ID；检查停止后的未执行案例被标为未执行，而不是悄悄删除。若报告三例汇总，未执行项不得被包装成已完成实验。
6. 独立断网重放官方分数；在副本上删预测、改响应、改评价文件，检查失败检测。
7. 查看每个错误的具体证据，拒绝把次优或检索错误直接解释为语义误读。小样本仅判断工程可用性。
8. 输出 PASS / PARTIAL / FAIL，并给出逐项理由。工程 PASS 不等于 DARC 有效、不等于 60 例扩量获批，也不解除论文 CLOSED。

## 可直接复制给 Claude 的执行指令

> 请按 `docs/experiments/chinatravel_setup/NEXT_HANDOFF_20260911.md` 执行。保留 v1 及其重放能力，新建 v2，优先修复结构化工具调用和最终规划预算预留。先完成离线验收，再按冻结计划、同一 Haiku/xcode 配置执行最多 1—3 个 dev 案例；第一例未产出可评分计划则停止扩展。所有失败原样保存，不修改 gold 或官方评分器，不提高预算追求成功，不写论文。完成后提交实现报告、验收清单、准确运行命令及原始证据，交由 Codex 独立检查。
