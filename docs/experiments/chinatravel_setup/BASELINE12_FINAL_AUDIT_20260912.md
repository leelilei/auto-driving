# ChinaTravel baseline12 最终输入隔离与分母审计

日期：2026-09-12。范围：冻结的 12 条开发诊断样本；不是 benchmark、SOTA 或 DARC 证据。

## 结果

- 公开模型输入：12/12，仅包含 `uid` 与 `nature_language`；未发现 `hard_logic_py`、官方评分结果、oracle/gold 约束等私有字段标记。
- 采集：12/12 完整，逻辑模型调用 12 次。
- 规划：12/12 搜索成功，12/12 原始 schema 有效，12/12 适配后 schema 有效，schema 适配改动 0。
- 官方评分：12/12 all-pass；完整分母为 12，排除项为 0。
- 规划 trace：12/12 未发现官方评分或 oracle 标记；官方评分文件只在搜索输出产生后读取。

因此，`100%` 的准确表述是本诊断切片上的 `12/12`。它只说明该批简单需求未观察到可见的接口/规划语义错误，不能外推到完整 dev/hold，也不能启动阶段 5。

## 停止决策

停止扩量；不做反馈对照，不把本批结果包装成方法收益。后续若继续 travel，只能先冻结更难且独立审计的样本/强基线方案，并重新定义进入阶段 5 的证据门槛。

## 可复核产物

- 审计脚本：[`audit_chinatravel_baseline12_isolation.py`](../../../9-AutoDriving-core/scripts/audit_chinatravel_baseline12_isolation.py)
- 机器可读结果：[`input_isolation_audit.json`](../../../9-AutoDriving-core/data/chinatravel_baseline12_20260912/input_isolation_audit.json)
- 汇总审计：[`final_audit.json`](../../../9-AutoDriving-core/data/chinatravel_baseline12_20260912/final_audit.json)

审计为离线检查，无新增模型/API 调用，也未改写原始采集或规划结果。
