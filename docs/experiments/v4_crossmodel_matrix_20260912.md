# v4 模型矩阵阶段性汇总（Qwen 移除版）

## 主矩阵

| 模型/协议 | 规模 | B0 TSR / Flip | Ours TSR / Flip | Ours calls | Ours review | 结论 |
|---|---:|---:|---:|---:|---:|---|
| GPT 主实验 | 160 groups / 640 utterances | 1.0000 / 0.2385 | 1.0000 / 0.2031 | 2.04 | 4.2% | Route Flip 相对下降 14.8%，但只相对 B0/B4 显著；不优于 B6 |
| DeepSeek-v4-flash | 160 groups / 640 utterances | 0.6469 / 0.0950 | 0.6484 / 0.1012 | 2.38 | 38.0% | TSR 略升，但 Flip 未下降，utility loss 略差；存在 233 次 transport failure |
| Gemini 3 Flash pilot | 10 groups / 40 utterances | 1.0000 / 0.0667 | 1.0000 / 0.0667 | 2.00 | 0% | 可接通；pilot 中无机制增益，7/120 schema-invalid |

## 决策

1. Qwen 从新主矩阵移除；历史结果仅保留在补充材料。
2. Gemini 暂停扩量，不作为主结论依据。当前主要价值是记录 schema/服务稳定性边界。
3. 不再继续调门限或扩模型。现有跨模型结果已经表明：DARC 的 Route Flip 改善依赖模型条件，不能作为普适机制结论。
4. 下一步转向 v4 的受控机制核验：以 GPT 完整结果为开发证据，以 DeepSeek 作为负/边界复现，重新计算统一的 utility/regret、纠正/改坏和失败分母；优先比较 Ours 与 B4、B6，而不是只比较 B0。
5. 若统一核验后 Ours 只在 GPT 上有效，则论文主张应收窄为“模型条件下的决策稳定性信号”，不能声称跨模型稳健提升；若 utility/regret 也不改善，则停止修旧 gate，转入 v5 的固定三次调用、决策对比反馈方案。

## 当前不能写入论文的结论

- Route Flip 下降不等于任务成功提升；GPT 主集 TSR 已达天花板。
- DeepSeek 的较低 TSR 和传输失败不能直接与 GPT 数值横比，必须把失败处理和协议差异单独报告。
- Gemini pilot 的无差异结果不能证明机制无效，只能说明当前样本和服务条件下未观察到增益。
