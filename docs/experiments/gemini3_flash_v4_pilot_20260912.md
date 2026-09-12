# Gemini 3 Flash × v4 主实验协议 pilot

## 运行信息

- 模型：`gemini-3-flash`，Xcode API (`https://xcode.best`)
- 协议：v4 E3 主实验，同一 `test_640_utterances.json`、同一冻结参数、B0/B2/B3/B4/B5/B6/Ours
- 规模：10 groups × 4 variants = 40 utterances；120 次计划调用
- 运行目录：`9-AutoDriving-core/results/runs/20260911T181131Z_main_test_gemini-3-flash_pilot10_net`

## 结果

- 120/120 调用完成；113/120 schema-valid；0 transport failure；7 次 schema-invalid
- B0、B2、B3、B4、B5、B6、Ours：TSR/GTSR 均为 1.0000
- 各方法 Route Flip 均为 0.0667，bootstrap 差异均为 0
- Ours 平均 2.00 calls/request，review rate 0%；平均 utility loss 0.056739

## 解释

该 pilot 证明 Gemini 可按 v4 协议接通，但在这 10 组上没有观察到选择性复核的增益；不能据此宣称机制有效。7 次 schema-invalid 需要在扩大实验前分类记录。下一步应直接使用同一 Gemini 入口跑完整 160 groups，并与 DeepSeek、GPT 结果按相同失败处理和指标口径汇总；若完整结果仍无增益，应把结论写成“模型条件下的边界效应”，而不是换 proposal。
