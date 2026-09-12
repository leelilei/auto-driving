# v5.1 单组端到端诊断

日期：2026-09-10（Asia/Shanghai）。范围：`pilot_01`，4条等义表达，3种配对图，72个逻辑调用。该结果用于开发与工程准入，不是论文结果。

## 模型与接口

- 模型：`deepseek-v4.1-flash-expires-on-0910`。
- 接口：DeepSeek官方API。
- 状态：限时预览ID；不在官方`/models`三项公开目录中，但2026-09-10单次探针与实际调用均成功。
- 该模型不替代已经选择的Terra主模型；其用途是验证完整采集链并评估候选模型行为。

## 采集完整性

修正版run：`9-AutoDriving-core/results/v5/diagnostic/20260910_deepseek_v41_pilot01_72_contrast_v2`。

| 项目 | 结果 |
|---|---:|
| 计划逻辑调用 | 72 |
| 完成逻辑调用 | 72 |
| 物理尝试 | 72 |
| 传输失败 | 0 |
| Schema失败 | 0 |
| Provider input tokens | 32,483 |
| Provider output tokens | 136,958 |
| Provider total tokens | 169,441 |

第一次72调用run使用`contrast-1`，暴露出报告遗漏原始平均质量的问题。该run只证明采集链可运行，不进入方法比较。修复后报告升级为`darc-v5.1-contrast-2`，增加`average_quality`与`coverage_count`，重新采集全部72调用，没有复用旧复核输出。

## 解析与复核诊断

| 角色 | n | 硬约束正确 | 偏好方向正确 | total tokens |
|---|---:|---:|---:|---:|
| A | 4 | 4 | 4 | 3,351 |
| B | 4 | 4 | 4 | 3,018 |
| A2 | 4 | 4 | 4 | 3,330 |
| A3 | 4 | 4 | 4 | 4,512 |
| LLMAP direct | 4 | 4 | 4 | 3,399 |
| LLMAP CoT | 4 | 4 | 4 | 2,698 |
| Review Plain | 12 | 12 | 11 | 60,177 |
| Review Fields | 12 | 12 | 12 | 27,325 |
| Review Constraints | 12 | 12 | 12 | 24,695 |
| DARC | 12 | 12 | 12 | 36,936 |

唯一错误为`pilot_01_v3::tradeoff::review_plain`：硬约束保持正确，但把明确的距离优先解释为`quality_weight=0.5`。这说明无附加证据复核会产生随机改坏；样本仅1组，不能估计总体退化率。

A/B在四句话上完全一致且均正确，因而本组不存在可供任何复核方法纠正的基础错误。DARC的12/12只能说明没有改坏，不能声称比Fields或Constraints提升。需要继续选择包含A/B真实分歧或错误的已审核开发组，才可能检验研究假设。

## 信息边界检查

- Plain和Fields每句跨三图请求保持相同，各有4个唯一请求哈希。
- Constraints本组因A/B完全一致，交叉约束相同，各有4个唯一请求哈希。
- 修正版DARC共8个唯一请求哈希：tradeoff质量值进入报告；本组time-sensitive收紧没有改变候选路线后果，因此与父条件部分相同。
- 报告不含gold、人工方向标签、split或哈希决策字段。

## 准入结论

工程采集链与DeepSeek官方通道通过单组完整性检查。方法收益门禁未通过也未失败，因为本组没有基础错误，缺乏纠错机会。下一步应先完成离线replay与篡改拒绝，再在其余已审核组中做有界诊断；不得从本组宣称提升、SOTA或统计显著性。
