# ChinaTravel 整改执行记录

2026-09-11。当前已完成官方评分与调用适配离线验证，以及一次真实单例采集和两次一致的断网评分回放。论文 CLOSED。本文替代旧进度文档的阶段百分比；原报告保留为历史。

## 已完成的改动

- 新执行入口 `9-AutoDriving-core/scripts/chinatravel_pipeline.py` 使用官方 Act、真实 WorldEnv 和项目 `LLM.complete`，避免两个同名 baselines 模块的导入冲突。
- `stage3_baseline_experiment.py` 改为新入口代理。旧 B0/B1/B2 与目的地字符串评分不再通过该入口执行，原脚本保存在 `retired_20260911/`。它们不构成已复现的强基线。
- `stage2_evaluator_test.py` 改为运行官方评分集成测试，不再接受旧双层数组 schema。执行与 `eval_exp.py` 相同的 schema、commonsense、hard v2 三个函数，all-pass 取通过 ID 的交集。
- 每批按全部预期 ID 评价，缺失或非对象预测进入空对象失败路径；额外 ID 直接报错。字段分别保留官方 micro/macro/all-pass，不替换评分标准。
- 模型输入只从原记录提取 uid 和完整 nature_language；实际 Act 只接受原句文本。gold 不进入提示或纠错反馈，官方评分在单独 replay 命令中运行。
- 本地工具采用官方受限命令解释器。适配提示明确宿主实际执行文本命令，不要求 API 原生 tools 声明。该提示和调用接口是本地适配，不能称与原论文完全相同配置。
- 每个请求在发送前落盘，返回后保存响应和遥测；限制逻辑调用数、累计请求字符数和时间，关闭自动重试。连续两条非命令响应停止，保留失败原样。
- 官方工具实际读取的中英文 264 个 CSV/JSON 等源文件 SHA256 全部匹配发布清单；此前还已验证 sandbox 发布清单中的 23 个文件。

## 评分器验收及证据边界

`codex_validation/tests.log` 记录 13 项检查通过。包括官方 schema 拒绝旧数组、真实本地工具查询、原句白名单、非命令停止与调用上限，以及有效行程、错误实体、时间冲突、硬约束、空预测和部分预测缺失。

有效正例保存在 `codex_validation/fixture_candidate.json`。它来自 **给定 gold 的离线 RuleNeSy 测试构造**，初始候选含重复午餐；为构造评分器正例，删除重复午餐并通过公开 goto 重新计算衔接出租车，补全 cars=1。修改过程记录在 fixture 中。此正例经过官方三层评分全部通过；不计入模型表现，不作为 few-shot 示例，不用它证明 RuleNeSy 或 DARC 有效。查询与 gold 未更改。

这次测试证明特定正常/错误输入的官方评分路径可运行，不证明整个公开基准的标注无误或所有边界已穷尽。有效正例是本地验收 fixture，不冒称官方发布的标准答案。

## 旧 Terra 故障解释

`external/ChinaTravel/cache/Act_gpt-5.6-terra/e20241028160248698752.json` 显示 50 次响应持续声称未提供工具；WorldEnv 反复返回命令解析错误。该轨迹没有形成有效工具规划。它支持接口协议失配诊断，不支持模型规划能力比较，也不能仅用 token 计数断言供应商计费金额。

## 当前真实采集

运行目录 `9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_haiku_smoke`。模型配置为既有 xcode Haiku，开发 ID 为排序后第一条 `e20241028160248698752`。仅一个案例，最多 12 次模型调用，单请求 timeout 60 秒，累计请求字符预算 160,000，关闭自动重试；总体时间预算在每次调用前检查，因此进行中的单次调用可能越过该时点最多一个请求时限。

不在失败后自动换模型、扩大预算或修改原句。原始请求、工具轨迹、最终预测与评分分别存档。数据文件和采集文件有校验值，重放阻断 socket 网络连接。此机制是当前开发验收工具，尚不是面向任意恶意清单篡改的完整归档安全证明。

## 复核命令

在项目根目录执行。

```bash
external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/stage2_evaluator_test.py

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_pipeline.py replay \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_haiku_smoke
```

真实采集完成后运行第二条。它读取当前冻结数据进行 gold 评分，不再访问模型。后续新采集必须换新 run-dir；已有运行目录不能覆盖。

## 单例完成结果与下一步

本次 8 次真实请求，约 59.5 秒，记录 input 15,152、output 4,285 token，遥测均标为 provider；该统计按现有客户端归一化字段汇总，不等于核对供应商账单。3 次工具查询取得实际数据，2 次无数据，3 次工具命令错误。两次错误来自额外转义，另一次 goto 针对“西湖”调用返回参数解包错误，需进一步区分实体匹配与工具错误信息质量。

在第 9 次请求发送前，累计字符预算阻止继续调用。已发送请求字符累计为 142,292，下一个完整历史请求会超过 160,000。没有 plan/最终 itinerary，官方 schema、commonsense macro、hard macro、all-pass 全部为 0；该失败保留在唯一案例分母中。两次断网回放结果一致。

全部 8 条实际请求均包含完整原句；对本例 gold DSL 完整片段的请求扫描未发现泄漏。该扫描与白名单测试构成当前已查证边界，不宣称对任意编码/间接泄漏的完备证明。

当前能支持的结论是工具交互不再停留于“没有工具”的连续拒绝，且失败可被官方评分链路如实记录；尚不能称强基线已跑通或研究问题已证明。没有把预算提高后重跑同例，也没有扩到 60 例。

下一步先离线修正接口效率。把动作输出定义为可解析的结构化工具调用，保留原始响应并记录转换，不用字符串替换偷偷修复；测试未知实体的清楚错误返回；显式分配查询与最终规划的预算，避免把全部额度花在信息采集。修复后冻结新配置和新运行目录，再跑 1—3 个 dev 案例。该工程验证通过后，才选择真正适合机制对照的解析＋规划强基线。
