# Fair30：统一 DSL 定义后的公平对照实验指导书

> 后续更新：负责人已明确批准，真实180单元及离线核验完成，结果56/60、59/60、57/60。见[完整报告](FAIR30_RESULTS_20260911.md)。下方保留采集前协议。


日期：2026-09-11。当前已完成数据与代码准备、180 单元断网模拟、163 项测试；真实 API 调用 **0**，语义人审 **PENDING**。论文写作仍 CLOSED。

## 研究问题与本轮边界

上一轮术语组最终任务成功 60/60、原始成功 57/60，超过计算证据组 48/60。下一步检验：**所有方法都获得明确且相同的 DSL 定义之后，额外计算事实是否仍能提高最终任务成功，并且值得增加的调用与 token？**

这是对当前机制主张的开发检验，不是确认性主实验。新几何由固定规则一次生成，语言模板仍沿用开发模板，不能称作未见语言泛化或外部 benchmark。几何复杂度不必然增加规则抽取难度，若再次饱和，应如实停止当前扩量。

## 三个方法及唯一差异

| 方法 | 输入 | 输出 / 后续 |
|---|---|---|
| Direct＋定义 | 原句、完整 scene、固定 DSL 定义 | 抽取规则后交给共享执行器 |
| Language＋定义 | 同一原句和 scene、同一套定义、该轮 Direct 候选 | 一次复核，再交共享执行器 |
| Evidence＋定义 | 与 Language 相同，再添加 scene-only 计算事实表 | 一次复核，再交共享执行器 |

三个 system 都追加完全相同的固定定义。两个 review 的 system 完全一致，user 只有 `computed_scene_facts` 一处差异（null / 事实表）。事实函数只接收公开 scene，不接收原句、gold、案例分组或预期正确对象。不使用方法选择门控，不用哈希决定方法或答案；文件摘要只校验完整性。

重新采集 60 个 Direct 候选，两个复核共享对应的新候选。旧候选与旧模型回答不混入。每个案例两次重复；复核顺序在重复间交换，以减少固定先后顺序影响，但不能声称完全消除了缓存或时间效应。

## 新数据固定规则

入口：`9-AutoDriving-core/scripts/prepare_scene_fair30.py`；目录：`9-AutoDriving-core/data/scene_fair30_candidate/`。

- 5 类场景各 6 例：宽松营业、出发时已开门、返家期限、关门约束、组合约束。
- 每类有 3 种目标 × 2 个独立几何抽样，共 30 个几何；每例 5 个药房。每种目标共 10 例。
- 伪随机种子固定为 20260911，仅用于可重复生成合成数据。银行 x∈[8,20]、y∈[-4,4]；药房 x∈[-5,25]、y∈[-10,10]，整数均匀抽样。
- 评分从 2.0–4.9 的 0.1 网格无放回抽 5 个；涉及开门条件时从 500/535/555/575 分钟抽样，涉及关门条件时从 585/595/610/660 抽样；涉及返家期限时从 595/605/620 抽样。
- 09:00 出发、银行服务 20 分钟、药房服务 10 分钟、速度 1；不等待，服务结束不得晚于关门，返家期限包含最后一段行程。
- 一次生成全部保留，无模型调用、无按输赢挑选、无重抽直到“有区分度”、无事后平衡赢家。

离线参考结果：26 例可行，其中 25 例唯一最优；4 例不可行（F14、F27、F28、F29）；F22 并列最优 P_B/P_C。并列按原评分器接受任一非空最优子集，不要求列出所有并列答案。180 项单字段规则替换中 75 项改变决策；这是数据属性，不是方法提升。全部案例属于新生成主集，旧引擎的 `control` 汇总为 n=0；场景类别以 `block_kind` 分层，不能解释成复用了旧18＋12控制结构。

参考答案来自 `prepare_scene_pilot12.solve`，与生产执行器逐例核对。**没有人工手算独立标注，不能把程序一致性写成人审通过。**

## 实际语义审核

逐例入口：[CASE_REVIEW.md](../../../9-AutoDriving-core/data/scene_fair30_candidate/CASE_REVIEW.md)。若相对链接因阅读器失效，可在项目根目录直接打开上述数据目录中的文件。

核对原句与三个规则字段、时间语义、候选表和不可行理由；有歧义或计算错误逐例指出。若需改动数据，另存新版本并重新生成 gold、摘要、运行目录；不能修改已冻结版本后继续沿用旧结果。

只有负责人对本版具体案例作出实际认可后，才记录审核者、时间、原始批准依据和数据 manifest 摘要，生成独立 `human_review_receipt.json`。Codex 可以在收到真实批准后代为记录，但不得伪造批准或用测试通过替代批准。

## 采集预算与执行

- xcode / `claude-haiku-4-5-20251001`，Anthropic Messages，经 curl HTTP/1.1；密钥仅从环境或 Keychain 读取。
- 固定 temperature=0、max output=1600、timeout=120 秒；并发 2，客户端内部不重试。
- 30 × 2 × 3 = **180 逻辑单元**，最多额外 18 次传输重试，单元最多 2 次物理尝试，总物理请求上限 **198**。首个完整三阶段单元包含在计划内。
- 401/403/429 或恢复预算耗尽停止启动新请求；已在途请求完成并记账。语义错误、格式错误均不重试。
- Direct 格式失败时两个 review 标为上游失败，不发送伪造候选；分母仍各60，但实际调用少于180。Review 格式失败回退原 Direct；原始失败与回退后结果分别统计。
- 中断后用相同目录继续 collect，保留所有终态。未核对的 STARTED 必须先处理，不可直接重复发送；追加预算或改变传输条件另行记录。

```bash
# 工程复核，无 API
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/pytest -q 9-AutoDriving-core/tests
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python \
  9-AutoDriving-core/scripts/scene_fair30.py replay \
  --run-dir 9-AutoDriving-core/results/scene_fair30/engineering_mock_v1

# 收到实际人审批准、记录 receipt 后，用新的真实运行目录执行
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python \
  9-AutoDriving-core/scripts/scene_fair30.py prepare \
  --run-dir 9-AutoDriving-core/results/scene_fair30/reviewed_development_v1 \
  --review-receipt /实际路径/human_review_receipt.json
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python \
  9-AutoDriving-core/scripts/scene_fair30.py collect \
  --run-dir 9-AutoDriving-core/results/scene_fair30/reviewed_development_v1
```

审核凭证字段：`status=APPROVED`、`reviewer`、`reviewed_at`、`approval_evidence`、`dataset_manifest_sha256`、`approved_case_ids`（F01–F30）。模板不是批准；代码会在读取密钥和启动采集前检查该记录。

## Codex 验收与去留标准

1. 断网重建180逻辑单元、每组60分母；重新解析原文，检查非法重试、缺失记录、额外记录、共享 Direct 及三组同定义。任何缺失不能算完整实验。
2. 每个可执行预测与独立参考求解器一致；原始 provider 正文与保存文本一致、请求与返回模型名一致；保留数据、提示、代码版本及所有失败。第三方返回模型名不等同后端身份认证。
3. 主表报告最终任务成功、原始任务成功、规则正确、纠正/改坏、不可行误报、格式回退；两次重复与五种场景分层；成本包括所有阶段、失败次数及缓存分项。
4. 主比较为 Evidence＋定义 对 Language＋定义 的配对净任务收益，同时检查 Direct＋定义 是否已饱和。60个重复单元不是60个独立案例；如计算区间，至少以案例为簇，不拆开同一案例的两次重复。本轮不以未预定的显著性筛选结果。
5. 若语言组仍60/60，或证据组净收益≤0，则当前样本不支持计算事实的额外价值，停止该数据上的扩量，不通过换弱模型制造结论。若净收益>0，也只视为候选信号，必须核对改坏与格式依赖，再经新数据和跨模型复现。小幅正差不能直接解锁论文。

## 已完成交付

`prepare_scene_fair30.py`、`scene_fair30.py`、5项新增测试、30例数据/参考轨迹/变异审计/审核表/180计划；完整断网模拟保存在 `results/scene_fair30/engineering_mock_v1/`。全项目163项测试通过，模拟180个预测决策独立核验通过，模拟成绩不报告为模型准确率。

复用引擎的摘要中 `human_review` 保守保留 PENDING；真实审核以独立凭证为准，验收报告另记凭证是否存在，避免把程序成功改写成负责人批准。
