# 可支持的主张（实验定稿范围）

证据包：`9-AutoDriving-core/results/v4_1/closeout_v2c_20260912/`。这是主张审定材料，不是论文正文；所有统计结果为本轮事后统一重算。

1. **有限复核预算下，决策效用差异可以提供比语义权重差异及随机选择更有效的稳定性排序信号。** GPT 历史 160 组和 Luna 40 组的 10% 配额支持此结论：`joint_metrics.json` → `gpt54/luna.comparisons.10`。分别相对 B4 降低 6.04/5.91 pp，相对 B3 降低 7.09/4.85 pp，组 bootstrap CI 不跨零。这是受控合成 POI 图上的模型条件性结果，不是五模型通用规律或公开 benchmark SOTA；GPT 旧语义问题和数据资格限制须披露。

2. **稳定性改善与任务成功不是同一目标，复核预算必须与改坏风险联合评价。** `joint_metrics.json` → `luna.methods` 和逐例 `e2_clean_028_v0`：DARC 10% 条件 Flip 下降，但 TSR 从 160/160 降到 159/160。`failure_penalty_sensitivity.csv` 显示全分母效用结论随失败代价变化。不能声称 DARC 无损、必然改善整体质量，也不能从 Haiku 单个避开失败的例子推导普遍保护能力。

3. **额外复核收益依赖基础解析和接口协议；部分运行没有显示决策信号相对简单基线的增量。** `joint_metrics.json` → `gemini/haiku/sonnet.comparisons.10`：相对 B4 点差均为 0；结合 `parser_change_ledger.json` 与 `fallback_selected` 披露解析适配与回退。成本表支持选择性复核比 B6 少消耗 token，但不支持其成本低于 B0、各模型性能单调演进或 B6 是理论上界。
