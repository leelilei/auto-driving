# ChinaTravel 单例链路完成记录

2026-09-11。执行与复核：Codex，同一执行者；隔离进程评分与独立账本重算不冒充独立人员签字。

## 结果

**工程单例 PASS，研究准备 PARTIAL。** 使用真实 Haiku/xcode 对原句提取城市、天数、人数和预算，再由固定规划器生成实际行程，成功通过官方 schema、commonsense、hard 三层评价及断网重放。涉及公开任务适配，不是未经修改的官方 Act / RuleNeSy 复现。

案例 `e20241028160248698752` 是已暴露的回归开发例：上海出发，独自去杭州一天，预算 1500 元。最终行程 6 个活动，包含往返火车、3 个景点和午餐；数据库口径总费用 368.12 元。该费用是 sandbox 计算结果，不是现实旅游报价。评价均为 100%，all-pass 1/1。

| 路径 | 实际模型请求 | 结果 | 证据边界 |
|---|---:|---|---|
| Act 原生工具 v3 | 9 | 2 次协议错误、5 次有效查询、1 次 finish、1 次最终行程；行程缺少火车 start/end，schema 失败 | 三例计划只尝试首例，其余两例未执行；固定计划分母仍为 3 |
| 原生解析＋规划入口 v1 | 1 | 五个字段和原句依据正确；将“请给我一个旅行规划”标为 unsupported，宿主停止，all-pass 0/1 | 原始模型响应、停止原因、空预测均原样保存 |
| 同一解析的显式宿主请求处理＋规划 | **0 新增** | 通用“输出旅行规划”请求交由规划器兑现；真实搜索成功，all-pass 1/1 | 复用上一行同一个模型样本；不是模型自行纠错，也不是第二次成功采样 |

本轮累计 10 次物理请求，无自动重试、传输失败或未知 usage。提供方报告 input 14,121、output 1,696，共 15,817 token。Act 9 次为 13,942 / 1,583 token；单次解析为 179 / 113 token，约 3.059 秒。最终本地搜索约 1.817 秒，3,396 次官方环境查询、1,630 个搜索节点、工具异常 0。该 token 数只代表提供方返回的 usage，不等于账单核验。

## 修复的实际阻断

1. **模型动作格式**：v3 使用 Anthropic 原生 tool_use，固定只允许一个结构化动作，文本块另外保留、不执行。原始 API envelope 与序列化输入均可追溯；工具定义及 tool_choice 也计入字符预算。未从说明文字中抽取代码块。Act 仍出现未查询的接驳数据和缺字段，停止该分支扩展。
2. **RuleNeSy 用餐状态**：官方 `rule_driven_rec.py` 的选择函数每次将用餐状态设为 False，实际搜索反复生成两顿午餐，被官方 `Repeated Meal Types in One Day` 拒绝。新增本地子类读取当天已安排活动，过滤已吃过的 lunch/dinner；不修改官方源码、不删除生成后活动、不改评分器。修复前的 30 秒失败轨迹保留。
3. **评分查询字段**：旧 `prepare_chinatravel_dev.py` 将 `start_city` 改名为 `org`；官方 commonsense 需要 `start_city`，合法计划因此触发 `Commonsense Evaluator Exception`。新评分入口使用原始 `dev_split/<uid>.json`，逐条核对原句、gold DSL、目标城市、天数、人数及 start_city/org。60 条全部一致；原数据和 gold 未改。
4. **通用请求的宿主分工**：原生解析把“请给我一个旅行规划（具体行程规划）”放进 unsupported。新处理规则只接受完整匹配的通用规划输出请求，且基础短语必须逐字出现在原句中，将其记录为由规划器处理。任何交通、餐饮、预算、节奏等具体限制仍保留并停止，不静默丢弃。规则和处理记录先于本次重新规划冻结；没有追加模型请求。

旧 v1/v2/v3 运行目录与评分保持原样。Act v3 使用原始完整评分记录的独立复算另存为 [评分输入诊断](v3_validation/act_original_query_score_diagnostic.json)，all-pass 仍为 0；没有改写历史成绩。此前评分器 fixture 测试使用完整官方记录，因而未暴露合并数据的字段缺失，现已补实际数据路径的回归测试。

## 实现入口

- [原生 Act v3](../../../9-AutoDriving-core/scripts/chinatravel_pipeline_v3.py)：封存失败的 Act 分支及原生协议实现。
- [原生解析入口](../../../9-AutoDriving-core/scripts/chinatravel_parse_plan.py)：只接收 uid/完整原句，一次模型调用，保存原始结构化预测和逐字段依据。
- [宿主请求处理与离线续接](../../../9-AutoDriving-core/scripts/chinatravel_parse_plan_v2.py)：保留原生响应，单独保存 capability_resolution，复用同一解析，不增加 LLM 请求。
- [RuleNeSy 本地适配](../../../9-AutoDriving-core/scripts/chinatravel_symbolic_backend.py)：用餐状态修复、30 秒搜索上限、search_width=10、完整官方工具轨迹；只用成功的原始搜索返回值，best-so-far 仅作诊断。
- [有限 JSON→DSL 编译接口](../../../9-AutoDriving-core/scripts/chinatravel_symbolic_probe.py)：仅支持城市、天数、人数、预算，不接受任意模型 Python。原始 RuleNeSy 探针与修复前错误另行保留。

所有实际模型调用仅使用 public_inputs。gold 和结构化评价记录只进入独立评分进程。规划器内部检查的是**模型预测经宿主编译的约束**，不是 gold；这与禁止生成期间获取 gold 反馈不冲突。

## 验证

48 项 ChinaTravel 联合测试通过，后续新增的 2 项宿主请求处理测试通过，共 50 项；包括真实官方工具、原始评分数据兼容性、重复用餐修复、原句依据、具体限制不可丢弃、原生动作、预算、gold 隔离和历史 replay。日志见 [联合测试](v3_validation/final_offline_tests.log) 与 [请求处理测试](v3_validation/routing_tests.log)。

成功归档两次独立进程断网回放完全一致。副本删除预测、修改 provider_response、删除工具轨迹、清空哈希、替换评价源码字节均被检测；没有改正式评价源码。完整工具轨迹 3,396 行，连续编号和调用数一致。回放同时验证父归档，确保复用的模型响应没有被替换；不声称能抵御同时重写全部清单的对手。

原生解析、宿主请求处理、编译约束、原始搜索返回、最终预测和官方评分分文件保留。最终预测逐对象等于搜索原始成功返回；没有依据 gold 挑选、删除或修补活动。

机器可读证据：[completion_audit.json](v3_validation/completion_audit.json)。

## 可运行命令

项目根目录下，下列 replay 已实际执行，不调用模型：

```bash
external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_parse_plan_v2.py replay \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_parse_rulenesy_routed_dev1
```

本轮实际使用的两阶段命令如下。它们记录创建过程；已有目录不可覆盖，不应再次采集来追求更好结果。

```bash
external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_parse_plan.py run \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_parse_rulenesy_dev1

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_parse_plan_v2.py run \
  --source-run 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_parse_rulenesy_dev1 \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_parse_rulenesy_routed_dev1
```

## 当前限制

这是一个含显式宿主适配的开发单例通过，不是原始模型零处理成功，也不是方法有效性证明。宿主处理规则是在本轮观察到接口错误后制定的，属于开发修订，不能作为预注册方法收益。原始与处理后结果必须并列，不能只展示 1/1。

语义接口目前只覆盖起终点、天数、人数和总预算；房型、交通方式、餐饮类型、行程强度等尚未纳入。RuleNeSy 是规则排序和有界搜索，未证明全局最优，超时不能解释为任务不可行。此例没有观察到五个字段的语义误读，不能据此宣称已找到 DARC 可修正的错误。

下一阶段应围绕“固定解析＋规划器”的接口做小规模语义审计，再决定是否存在值得比较的复核信息增量；不再把反复修 Act 当作方法验证。具体对应见 [研究映射](CHINATRAVEL_RESEARCH_MAPPING_20260911.md)。本轮未扩到 60 例，没有自动解锁论文写作。
