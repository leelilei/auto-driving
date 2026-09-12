# ChinaTravel 当前入口

> **2026-09-12 方向更新：Travel 本周期停止新增投入。** 工程/诊断成果保留，转向 [v4.1 主线](../../plans/proposal.md)。不是宣布 Travel 全任务已解决或机制被否证。以下历史待办不自动执行。

> **2026-09-12 冻结 12 条基线诊断已完成。** fixed6 之外按审计 manifest 顺序冻结 12 条；DeepSeek 官方解析 12/12，规划搜索 12/12，原始/适配 schema 12/12，官方全分母 all-pass 12/12（100%），schema 转换 0、补造值 0。该切片均为基础单人一天预算模板，未发现语义错误候选，不启动阶段 5。见 [冻结 12 条结果](CHINATRAVEL_BASELINE12_20260912.md)。后续只有在负责人认可更难覆盖切片并重新预注册后才继续 ChinaTravel；不再对当前批次调参。

> **2026-09-12 Repair v1 已通过最终审计。** DeepSeek 官方接口重跑固定六条，在搜索策略、宽度 10 和 30 秒时限不变的条件下，仅适配住宿 `room_type` 的字符串到整数。全分母官方 all-pass 为 5/6（83.33%）；五条搜索成功结果为 5/5，另一条为 bounded search failure。共 9 次类型转换、补造值 0。尚未发现可独立判定的语义错误，不构成 DARC / 阶段 5 证据。见 [Repair v1 结果](CHINATRAVEL_REPAIR_V1_20260912.md)。下一步冻结并执行 12 条基线错误分布诊断，不再针对固定六条调参。

> **当前执行入口**：[Travel 工程收尾与下一阶段执行书](TRAVEL_READINESS_CLOSEOUT_20260911.md)。受限实验底座已打通：固定六例官方 3/6，另外三例明确澄清；66 项测试及断网评分回放通过。进入基线错误分布诊断；以下旧状态仅作历史记录。

> **最新：DS 官方六例已完成端到端复核。** 六份真实解析响应已确认；复用同批响应，修复数值序列化并完成官方全分母评分，all-pass 从原保存结果的 1/6 变为新版离线重算的 2/6。三例人数未确定，一例限定预算内搜索失败。新增 API 0 次，断网回放通过。见[本轮结果与下一步](DS6_PROGRESS_20260911.md)。这是工程修复，不是 DARC 有效性证据，论文 CLOSED。

以下为此前阶段状态。


更新：2026-09-11。

**最新：60 条 dev 语义覆盖审计完成，离线核验通过，新增模型调用 0 次。** 当前五字段完整表达 30 条 easy 模板需求，其余 30 条有接口缺口，10 条未提供预算。预算遗漏、酒店费用单位、交通量词及天数冲突等评价边界已标注，不能直接算作模型误读。

- [审计结论、固定 10 条清单与接口待办](semantic_audit_20260911/REPORT.md)
- [60 条逐条证据](semantic_audit_20260911/results/AUDIT_60.md)
- [离线验证](semantic_audit_20260911/verification.json)

下一步：新增独立版本支持未指定预算与明确住宿/餐饮/城际方式/景点类别，先离线验收，再固定 6 条小批验证；另 4 条保留为评价诊断。10 条本轮均未执行。未扩量、未验证 DARC。

DeepSeek 官方接口阶段 3/4 已完成：固定 6 条解析调用全部返回 JSON；3 条因人数缺失阻断，3 条进入离线规划，其中 1 条 schema 有效、1 条搜索超时、1 条 schema 无效。未发现可独立判定的 semantic error，阶段 5 不启动。详见 [DeepSeek 阶段 4 归因](../../../9-AutoDriving-core/data/chinatravel_stage3_fixed6/stage4_deepseek_final.json)。

**单例工程链路已通过：真实 Haiku 解析 → 显式宿主请求处理 → RuleNeSy 本地适配 → 官方三层评价 → 断网回放。** 开发回归例 all-pass 1/1；这不是未经适配的模型成绩，也不是完整 benchmark 或 DARC 有效性验证。

- [本轮结果、限制和准确命令](CHINATRAVEL_CLOSEOUT_20260911.md)
- [与 proposal 的对应关系和继续投入判断](CHINATRAVEL_RESEARCH_MAPPING_20260911.md)
- [机器可读完成审计](v3_validation/completion_audit.json)
- [成功行程与原始证据](../../../9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_parse_rulenesy_routed_dev1/)

旧 [v2 实现报告](NEXT_IMPLEMENTATION_REPORT.md) 与 [验收清单](NEXT_ACCEPTANCE_CHECKLIST.md) 保留为当时状态。最新发现：旧合并数据遗漏官方 `start_city` 字段，不能直接用于合法行程的完整 commonsense 评价；新入口使用经一致性核验的原始 dev 记录，未修改旧数据、旧评分或官方评价代码。

此前工程轮实际 10 次模型请求：Act v3 9 次失败轨迹，加结构化解析 1 次。成功行程复用同一条真实解析，宿主处理和规划不追加模型调用，不算第二个模型样本。本次审计追加 0 次。论文 CLOSED，未扩量到 60 例模型实验。
