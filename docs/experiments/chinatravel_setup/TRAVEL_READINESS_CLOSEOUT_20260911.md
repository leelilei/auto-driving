# ChinaTravel 工程收尾与下一阶段执行书

## 2026-09-12 Repair v1 增补

后续 Repair v1 使用 DeepSeek 官方接口重新解析同一固定六条，并按照已选范围只修规划输出 schema 适配，不修改搜索策略、宽度 10 或 30 秒时限。最终全分母官方 all-pass 为 **5/6（83.33%）**；五条成功搜索均在只转换住宿 `room_type` 类型后官方全通过，一条为 bounded search failure。适配共 9 处、补造值 0，最终离线审计 PASS。详见 [Repair v1 结果](CHINATRAVEL_REPAIR_V1_20260912.md)。

下文 3/6 是 2026-09-11 v3 的历史工程结果，不被覆盖。Repair v1 仍未建立独立语义错误候选，不构成 DARC 或阶段 5 证据。执行方向不变：进入预先冻结的 12 条基线错误分布诊断，不继续在固定六条上追求 6/6。

日期：2026-09-11。结论：受限范围的离线实验底座可用，可结束本轮环境/后端打通工作，进入基线错误分布实验。不是完整 ChinaTravel 能力验收，不是 DARC 有效性结论，论文 CLOSED。

## 本轮实际交付

复用固定六例的真实 DS 解析，不新增 API。模型请求名 deepseek-v4-flash，返回名 deepseek-flash；不据此认证底层模型版本。

| 项目 | 结果 |
|---|---|
| 全六例官方 all-pass | 3/6，50% |
| 信息完整的三例 | 3/3；这是条件子集，不替换全分母 |
| 其余三例 | NEEDS_CLARIFICATION：预测人数为空，无行程，官方分数计失败 |
| 多约束广州→杭州 | 4 人、火车、2 间双床房、5600 元，官方通过，搜索约 5.75 秒 |
| 北京→重庆五日 | 官方通过，搜索约 5.88 秒 |
| 上海→杭州一日 | 官方通过，搜索约 0.89 秒 |
| 验证 | ChinaTravel 相关 unittest 66 项通过；六例断网评分回放通过 |
| 通用 CLI | 已实跑成功行程和缺字段澄清两个分支 |

成绩来自同一开发六例上适配后端的回归，不能作为独立泛化成绩。旧保存结果 1/6，数值修复版 2/6，本版 3/6；差异是工程诊断，不做显著性或方法增益宣称。

## 改了什么

新增独立 v3 适配器，不改官方评价器：将预测预算/房间字段接入已有搜索钩子；交通按明确出行方式过滤并按价格排序；酒店按床型过滤，返回行位置而非酒店 ID；景点和餐馆按价格与地理距离的正确秩排序，缓存坐标距离。地理距离仅为搜索启发式，实际交通可行性仍由官方工具/评价检查。不保证全局最优或完整求解。

保留 NumPy 标量转原生数值的严格序列化，不把字符串数字或非法行程修成答案。人数缺失明确澄清。未完成搜索只表示有限预算内未找到，不能解释为问题不可满足。

v1 搜索仍有一例失败；v2 因使用错误环境属性导致两例 AttributeError；这些运行目录原样保留。修复后的 v3 增加公开 env 接口排序测试。各版本均为工程开发版本，最终版本才是后续统一后端。

## 运行入口

在项目根目录执行，使用 external/ChinaTravel/.venv-chinatravel/bin/python。

```bash
external/ChinaTravel/.venv-chinatravel/bin/python 9-AutoDriving-core/scripts/chinatravel_plan_local.py --request 9-AutoDriving-core/data/chinatravel_local_examples/resolved.json --out /tmp/chinatravel_my_resolved
external/ChinaTravel/.venv-chinatravel/bin/python 9-AutoDriving-core/scripts/chinatravel_plan_local.py --request 9-AutoDriving-core/data/chinatravel_local_examples/clarification.json --out /tmp/chinatravel_my_clarification
external/ChinaTravel/.venv-chinatravel/bin/python 9-AutoDriving-core/scripts/run_chinatravel_readiness_v3.py replay --out 9-AutoDriving-core/results/chinatravel_baselines/20260911_ds6_constraint_aware_v3
external/ChinaTravel/.venv-chinatravel/bin/python -m unittest discover -s 9-AutoDriving-core/tests -p 'test_chinatravel*.py'
```

输出目录必须不存在。请求 JSON 为 nature_language 和 parsed_intent；示例使用已保存真实模型输出，不调用旧正则默认人数解析器。CLI 处理保存的解析结果，不内置在线聊天服务。PLAN_FOUND 只表示预测约束下找到结构合法候选，officially_evaluated=false；官方实验另外用隔离评分器评价。NEEDS_CLARIFICATION 是交互返回，不能计作 benchmark 成功。INVALID_INTENT / SEARCH_FAILED / SEARCH_ERROR 不隐藏，后两类不代表 UNSAT。原句与字段语义一致性还需独立审查，类型校验不能替代语义审核。

支持字段：出发城市、目标城市、天数、人数、预算、房间数量、床型、菜系、城际交通方式、景点类别。这个接口不能完整覆盖所有自由文本需求；不在此轮扩成通用旅游产品。单案例默认 30 秒搜索、宽度 10；缓存距离使部分工具调用减少，不能将工具数变化解释为模型效率提升。

## 下一阶段：固定开发集的基线错误分布

目标是判断公开任务上是否存在值得研究的语义误读及任务后果，先不实现新的 DARC 干预，也不为达到 100% 调后端。

1. 基于已审计 60 条 dev，在任何新响应前固化批次：以原 dev 清单顺序选未在 fixed6 出现的前 12 条。只输出自然语言和 UID 给解析模型；保留所有类型，不按难度、可解性或结果筛选。其余分区不动。保存预注册清单、输入哈希、字段覆盖人工审核表；模型不能读取 gold DSL/人数。
2. 使用同一 DS 接口与冻结的十字段提示，一次初始解析/条，共 12 个逻辑请求。网络异常至多一次重试并另记实际请求/费用；结构或语义错误不自动重采。先以并发 2 运行，不在本批混入节点测速或多模型切换。预算控制是研究运行规则，不是方法门控。
3. 固定本版后端、30 秒/例、宽度 10，保存每一条解析、编译约束、搜索日志、状态和候选；所有方法后续共用这个后端。遗漏字段和不支持需求单独标记；没有真实澄清答复的请求不能生成假回复。
4. 在生成结束后独立读取 gold 评分，报告完整 12 例的官方 all-pass、澄清/接口缺口/解析失败/搜索失败数；另报输入完备子集，但不得替代主分母。逐条人工审查原句与预测字段，区分 gold 表达缺口、解析错误和搜索错误。审核未完成时标注 provisional。
5. 只有确认存在语义错误才设计等调用预算的“无复核 / 字段复核 / 计算后果复核”配对实验。若主要错误仍是接口或搜索，先报告这一事实；若几乎没有语义误读，停止该批扩量，重新评估研究问题。12 例仅开发诊断，不能做 SOTA 或确认性主表。

## Codex 下次必须核查

- 12 条清单在调用前固化；没有测试暴露、按成绩换样或丢行。
- 在线请求体不含 gold；所有原始响应/重试/模型返回名/费用可追踪。
- 全分母评分、缺人数政策一致；人工语义审核与模型自评区分。
- 官方评价代码和本版后端未变；若改动，创建新版本并将该轮重新标为开发。
- 断网复算一致；官方任务成功不能替代预测约束忠实度。
- 研究是否继续由真实错误分布决定。实验落地 → 独立验收 → 负责人明确认可 → 最后写论文。

## 证据路径

- 最终六例：9-AutoDriving-core/results/chinatravel_baselines/20260911_ds6_constraint_aware_v3/
- 失败开发版本：同目录的 20260911_ds6_constraint_aware 和 20260911_ds6_constraint_aware_v2/
- CLI 验证：同目录的 20260911_local_cli_resolved / 20260911_local_cli_clarification/
- 实现：9-AutoDriving-core/scripts/chinatravel_ready_backend_v3.py、chinatravel_plan_local.py、run_chinatravel_readiness_v3.py。
