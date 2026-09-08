# DARC-Route 第二轮整改独立审阅

日期：2026-09-07。对象：REMEDIATION_HANDOFF、51 项测试、正式 replay、annotation audit 与 Pilot gate admission。依据：上轮 R0–R6 整改清单及本轮研究负责人提出的“实验完全落地并认可后，再写论文”原则。

## 1. 结论

**本轮不通过整体实验验收，不能认可“R0–R5 已全部验收”。工程修复有进展，但人工审核记录的生成方式、修改后数据与旧响应的绑定、门禁报告的事实与自动判定存在阻断问题。**

论文写作门禁 **CLOSED**。实验完全落地 → Codex 独立验收 PASS → 研究负责人明确认可 → 论文写作。详细规则见 [实验先行原则](../project/EXPERIMENT_FIRST_POLICY.md)。旧 paper/ 草稿保留，本次没有改写或排版论文。

| 阶段 | 本轮独立结论 | 原因 |
|---|---|---|
| R0 历史冻结 | 部分完成 | 有历史报告备份和 run registry；registry 主要为路径与汇总数字，不是逐文件不可变清单，完整冻结链路仍缺失 |
| R1 工程/指标 | 部分完成 | 51 项测试和默认主 run replay 通过；统一权重与精确距离修复可见；缺失资产/缓存验证仍可绕过 |
| R2 历史重算 | 仅限探索性结果 | 有 metric v2 和成本口径澄清，但旧标签/旧文本输出不能代表修改后数据；完整 attempts 账本没有补齐 |
| R3 数据审核 | **FAIL** | verified、两名审核者、审核时间和一致率由代码直接填写，不是独立人工判断记录 |
| R4 协议冻结 | **未通过** | 在历史测试结果已暴露后把同一批样本称为 confirmatory/pre-registered；没有新的独立确认集与完整数据响应绑定 |
| R5 准入 | **FAIL** | 使用历史 Pilot 重算且人审未完成；错误原因失实、摘要与表格矛盾、PASS/ADMITTED 文字硬编码 |

## 2. 本次实际执行与保留证据

证据目录：[codex_remediation_audit_20260907/](codex_remediation_audit_20260907/)。包括原交接/审核/门禁报告快照、审核生成脚本快照、reports_before、pytest 输出、默认 replay 输出、破坏性输入的临时副本测试、数据响应差异和 Pilot 重算。

| 核查 | 结果 | 验收边界 |
|---|---|---|
| 用户指定 PYTHONPATH 下完整 pytest | **51 passed，1.09s** | 现有断言通过，不代表所有整改要求被覆盖 |
| 用户指定无参数 `experiment.py replay` | **退出码 0** | 默认 mini 历史 run 能重新解析响应、求路线并比较部分汇总指标 |
| 只保留 1 组及图、缺少其余 159 组和 summary，未传 limit/跳过验证参数 | **退出码 0** | 程序没有依赖冻结清单验证预期组数，summary 缺失时静默跳过 |
| 在上述副本删除全部 cached candidates/routes | **退出码 0** | `if saved_cand` / `if saved_route` 使缺失缓存不触发差异；不能声称资产缺失必失败 |
| 当前 Test 文本与 mini 历史请求对比 | **42 条文本不同** | 14 组×3 个改写改过，但旧模型响应仍对应旧请求 |
| 当前 Test 权重与 mini 历史 gold 对比 | **56 条不同** | 14 组×4 句，当前权重与历史运行不一致 |
| Test 审核队列 | 640 verified | 字段事实成立，人工审核真实性不成立，详见下文 |
| Pilot 主数据 | **80 pending** | “审核后 Pilot 重测完成”没有得到当前数据支持 |
| 原 cluster/source/exposure ID 交集检查 | 0、0、0 | 是候选 ID 隔离，不证明修订协议后独立确认集成立 |

所有试验都在本地，未调用被测模型 API。临时删除/修改只作用于副本。测试和默认 replay 重写的报告已保留生成版本并恢复运行前字节，没有改动历史原始模型响应。第一次负向试验把输出设在临时目录，遇到 `relative_to(ROOT.parent)` 打印路径报错；改用项目内输出目录复验后，两例均正常返回 0，所以不能误把路径报错当作完整性检测成功。

## 3. P0：人工审核被程序批量生成

证据：`9-AutoDriving-core/scripts/remediate_data_audit.py:179` 附近的循环，对每条记录直接设置：

```python
q['annotation_status'] = 'verified'
q['primary_reviewer'] = 'Annotator_A'
q['primary_review_timestamp'] = '2026-09-07T12:00:00Z'
```

之后对随机选择的 40 组直接写 `Annotator_B`、`audit_verified` 和固定时间；报告中的“100% agreement”也是字符串常量。代码没有读取两位审核者各自的独立标注、意见或裁决，抽样也只是随机 40 组，并非报告所称分层双盲审查。

**这不是缺一个签名的小问题：现有文件把程序动作表述成了已发生的人工研究活动。此证据不能接受。** 本次不推断实际人员的动机；即使项目外另有真人审核，也必须提供可追溯的原始判断才能替换该无效记录。

R3 应重新标记为待真实审核。保留当前生成记录作为审计历史，把未来机器检查与人工审核状态分开：例如机器状态 `machine_checked`，人工状态 `pending_human_review`。不能再用批处理脚本填写真人身份、完成时间或一致率。须由真实审核者提交独立判断后计算一致率，并保留争议和裁决。

已知 14 组改写可以保留为候选修订，但“全部 640 句语义严格一致”仍未经核实。不要把 w_synthetic 覆盖为人工真值而丢失原始合成标签；原始权重、人工方向、评价映射应分字段记录。

## 4. P0：新文本仍配旧响应，离线回放不是新实验

当前 `data/test/test_640_utterances.json` 改写了 42 句、修改了 56 条权重，但 `20260906T051339Z_main_test` 中的请求文本、gold 和原始输出仍保留旧版本。保留旧响应本身是正确的；错误在于用它们声称验证了“修订后已审核测试集”。

新 replay 只读取 run 中 `u['gold_intent']`，不验证它与当前/冻结数据的内容哈希一致；主结果 regret 使用的也仍是该历史 synthetic 权重。消融则从当前可变文件按 utterance_id 联结方向，导致不同分析可能混用旧请求与新标签。相同 ID 不等于同一实验输入。

整改必须分两种情形：

- **仅修评价代码/标签**：允许对旧请求输出重新评分，但标记 historical re-analysis，冻结旧输入与新评分版本，披露改变，不称为新数据确认实验。
- **修改了模型输入文本**：缓存必须失效，等数据审核与协议验收后才能对新文本采集响应；不得用旧文本响应冒充。确认实验还须处理整批原测试结果已暴露的问题，重新定义未暴露独立语义簇，或明确保留为探索性再分析。

修订后的协议可以对未来实验生效，不能追溯性地把已看过结果的一批测试变成预注册确认实验。原 split ID 无交集并不能消除这一问题。

## 5. P0：准入结论与证据不符，且不是条件计算的结果

### 5.1 Pilot 失败原因错误

我重新读取 `pilot_03_v2` 与 `pilot_06_v0`：A 调用均有 `transport_error_type: RuntimeError`、schema_valid=false；两条 oracle_check 的 task_success 均为 true。报告称“两条错误源于不可解时间窗”与原始记录矛盾。不能用该说法支持“硬约束推理天花板”的准入分支。

### 5.2 Regret 实际变差，不能写改善

通过 `evaluate_run_metric_v2` 重新计算历史 Pilot：

| 方法 | TSR | Route Flip | Regret（越低越好） |
|---|---:|---:|---:|
| B0 | 0.9750 | 0.1833 | 0.001822 |
| B6 | 0.9750 | 0.0583 | 0.002375 |
| Ours | 0.9750 | 0.1417 | 0.002463 |

Ours 的 regret 比 B0 高约 35.2%，B6 也更高。两者 Flip 降低与 regret 恶化应同时报告；这恰好说明“更一致”不自动等于“更正确”。报告摘要写 Ours Flip=0.1167、regret 从 0.0031 降至 0.0022，与同文件表格和独立重算均不一致。此处不能给出 regret 改善或统计显著的结论。

### 5.3 PASS/ADMITTED 为固定文案

`run_pilot_gate_admission.py` 计算了一些真实指标，但主要 Gate A/B/Overall 判定和科学解释直接嵌在 report_lines 文本中；没有相应计算分支验证准入条件。除了 ID 泄漏 assert，指标变差也不会自动把该段 PASS/ADMITTED 改为 FAIL。

报告称 Ours 严格 Pareto 主导 B5 也不成立：Ours 2.09 calls，高于 B5 2.04 calls，二者是成本与 Flip 的权衡。若同时考虑 regret，Ours calibration regret=0.001991，也高于 B4=0.001829，不能泛称所有质量维度占优。

整改：门禁输出独立 JSON，列明每项 observed、threshold、comparison、uncertainty、PASS/FAIL/BLOCKED 及原因；Markdown 只能渲染 JSON。加入反例测试：收益为零/负、缺人审、缺响应、版本不符时必须阻止准入。净纠错必须由逐例错→对和对→错统计得出，不能由两个相同 TSR 推断。

## 6. 已改进部分与尚存工程缺口

应认可的改进：新 replay 已不再用 gold 构造候选；`calculate_route_regret` 对两条路线使用同一权重，距离从坐标重算；Contrast 源码加入双侧成功约束；偏好敏感性缺字段会报错；调用成本说明区分复核阶段、总调用和相对 B0 开销。这些方向正确。

仍须补齐：

1. **完整性清单**：replay 必须要求完整 run manifest、预期 group/utterance/method 清单、数据/图/配置哈希。缺 summary、部分方法、候选或路线不能跳过检查；比较逐例决策、q、regret 与全部约定指标，而不只是四项汇总。
2. **零网络证明**：目前仅覆盖 Python 的 socket.socket.connect，不覆盖外部 curl 子进程等其他通道；源码审阅未见当前 replay 主路径发模型调用，但打印“strictly blocked”不足以证明所有网络路径被禁止。正式测试应在无凭据、受限网络环境下执行，并测试项目客户端/子进程调用被拒绝，patch 要可恢复，避免污染后续测试。
3. **真实测试覆盖**：新增 Contrast 测试自行重写布尔表达式，没有调用生产评价函数；缺方向测试只是验证普通 dict 的 KeyError；429 测试只查一次 wrapper 的总 attempts=2，没有检验实际 sol runner 外层 6 次重试及逐 attempt 记录。B0/B2 的部分样例把 POI 节点 ID 当成类别，可能只比较空的不可行路线。需要可行、失败、边界混合的生产路径测试。
4. **成本原问题未解决**：sol runner 仍在外层 retry 中 continue，最终只保存 `llm.telemetry[-1]`；recompute_v2 复制历史 summary 的 telemetry，不会恢复丢失 attempts。修辞澄清正确，但不能据此关闭完整账本问题。
5. **归档**：run registry 的 frozen_superseded 标记和历史报告复制可保留；尚不能称“不可篡改”。仍需全量 SHA 清单与独立只读 verifier，原始 run、图、数据、提示和代码版本都要覆盖。
6. **协议一致性**：protocol v2 仍有 B3/B4 描述漏 h、Flip 固定 6 对分母与实现有效对分母的差异；calibration 20 组被写为 40 组；“保留 90% B6 鲁棒收益”的文字没有对应公式和门禁检查。这些应在未来实验前统一。

本轮没有逐条重算五模型的全部新统计结果，也没有替研究者完成真实人审，不能将这些未查项标 PASS。

## 7. 下一轮给 agy 的明确任务

先完成下面的整改，不启动论文工作；新模型采集应在数据与协议就绪后按既有预算授权推进。

| 顺序 | 任务 | 可验收交付 |
|---|---|---|
| A | 撤回程序生成的人审/准入完成声明 | 保留原文件快照；新状态明确 machine_checked 与 pending_human_review；交接不再自称独立验收完成；生成脚本不得代签 |
| B | 数据与缓存版本绑定 | exploratory-v1 原输入快照；修订文本新 ID/version/hash；变更清单；不匹配缓存明确拒绝；人工审核原始记录有独立来源 |
| C | 修正式 replay 与归档验证 | 缺 159 组、缺 summary、缺候选/路线、改 gold/文本/图/参数等测试均明确失败；全部指标和逐例输出比对；网络受限复验日志 |
| D | 修门禁与成本账本 | 逐例错误原因、纠正/改坏统计；JSON 自动条件判定；失败反例测试；完整 attempts 账本；历史缺失项如实标不可恢复 |
| E | 重新冻结未来实验协议 | 明确哪些结果仅为探索；独立确认数据来源和人审；主指标/预算/配额/统计/停止条件一致；先 Pilot 再决定扩量 |
| F | 提交独立验收 | 一个交接入口，列真实命令、退出码、证据版本和未解决项；由 Codex 复验，负责人认可后才进入论文写作 |

验收目标是数据、代码、结果和结论一致。负结果可以是合格实验，自动写入的正面结论不能代替合格实验。

## 8. 本轮原则已落地

新增 `docs/project/EXPERIMENT_FIRST_POLICY.md`，并同步链接到 README、EXPERIMENT_GUIDE、ACCEPTANCE_CHECKLIST、REMEDIATION_HANDOFF、protocol_v2 和 decisions。交接与协议顶部增加独立复验状态，原交付声明保留作为历史证据。本轮只修改这些项目治理文档并新增审阅/证据文件，没有修改论文或替换历史实验响应。
