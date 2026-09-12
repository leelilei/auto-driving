# ChinaTravel 冻结 12 条基线诊断

日期：2026-09-12。性质：开发诊断，不是 benchmark、SOTA 或 DARC 有效性证据。

## 结果

按 2026-09-11 审计 manifest 的原始 `expected_ids` 顺序，排除先前 fixed6 后冻结前 12 条；冻结发生在任何新模型调用前。模型只收到 `uid` 与原始 `nature_language`。沙箱首次运行发生 DNS provider failure，原始失败批次保留；按既定规则对 provider failure 做一次独立 retry，retry1 全部成功。

| 指标 | 结果 |
|---|---:|
| 固定样本 | 12 |
| DeepSeek 官方解析 | 12/12 |
| 本地规划搜索 | 12/12 成功 |
| 原始 schema 有效 | 12/12 |
| schema 适配转换 | 0 |
| 补造值 | 0 |
| 官方 all-pass（全分母） | 12/12，100% |
| 工具错误 | 0 |
| 独立语义错误候选 | 0 |

## 解释边界

这 12 条是审计清单中 fixed6 之后的顺序切片，均为基础单人、一天、预算模板。没有按结果筛选，但切片本身不覆盖此前审计标出的房型、菜系、交通方式、多人和人类复杂需求。因此 100% 只说明这批简单基线在当前后端上稳定通过，不能外推 ChinaTravel 全集，也不能证明 proposal 的反馈机制主张。

逐条请求隔离检查确认请求体不含 `hard_logic_py` 或其他 gold；规划阶段无模型调用。逐条官方评分均为 all-pass，未发现可供人工独立确认的自然语言语义误读。故不启动阶段 5 的无复核/字段复核/计算后果复核对照，也不继续调固定六条或这 12 条以追求更高分。

## 下一步决策

ChinaTravel 的工程链路已完成当前范围的收尾：Repair v1 固定六条为 5/6，冻结基线 12 条为 12/12。研究上下一步不是继续修 API 或规划器，而是由负责人决定是否值得抽取一个更难、需求覆盖更广且仍可独立判定的审计切片（例如明确多人/房型/菜系/城际方式的 12 条）重新预注册；只有该切片出现真实语义错误，才有理由进入 proposal 的阶段 5。否则应把 ChinaTravel 作为已完成的工程验证，不制造反馈实验。

## 证据

- 冻结规则和公开输入：`9-AutoDriving-core/data/chinatravel_baseline12_20260912/preregistration.json`、`public_inputs.json`
- 首次 provider 环境失败：`collection.json`
- 一次重试及 12 份官方响应：`collection_retry1.json`
- 规划、工具轨迹和官方分数：`planning/`
- 最终审计：`final_audit.json`
