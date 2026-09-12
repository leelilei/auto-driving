# Claude 160 组断点恢复记录

## 接管时状态

2026-09-12，用户明确要求续跑 Haiku/Sonnet，仅恢复缺失/失败部分，保留已有结果。

- Haiku: PID 20702 原进程仍运行；首次检查已有 125 组，旧 summary 仅 56 组。保留原进程，不另起全量副本。
- Sonnet: 未找到本轮历史160组进程或运行目录；已存在的 E2 40组使用另一批数据，不能作为本轮前40组直接复用。使用已有 xcode Sonnet 配置启动相同历史160采集协议。
- 在接管后生成 existing_assets_sha256.json，作为当时已存在文件的保留校验；不追溯声称在更早采集时已冻结。

## 恢复实施

Sonnet 入口 scripts/resume_claude_full160.py：先完成首组连通性/断点检查，再以8个工作线程继续，首组直接复用。使用原 run_full160_claude_experiment.py 的提示、解析、图seed和有界重试。每个 LLM.complete 返回/最终异常单独存入 completion_checkpoints，再保存逐输入结果。再次启动会复用已保存调用；同一目录采用文件锁避免两个恢复进程同时写入。

每次 LLM.complete 内部仍可能有多次传输尝试；completion条数不是精确HTTP尝试数。旧脚本会覆盖部分重试记录，因此不能声称历史真实费用或全部尝试数已完整恢复。

失败恢复入口 scripts/repair_claude_failed.py：只针对 schema失败、调用失败或候选缺失导致跳过的记录做一次有界恢复。预先缓存已有成功调用，原样复用，不重新请求成功字段。不重试语义上错误但schema有效的结果。恢复写入 recovery_repairs/utterances，原 test_*.json 不覆盖。原始结果和恢复组合结果分别报告，不能把补采后成功率当作原实验的一次成功率。

旧采集器的评估函数中，随机种子字典键与 range索引不一致，可能在采集后生成摘要时报错。本轮完成判定使用全部预期160组/640个唯一ID、文本匹配与独立collection_status.json，而非旧summary。汇总器 scripts/summarize_claude_recovery.py 不调用API。

## 当前证据入口

- collection_status.json：原始采集、补采、恢复组合的独立计数；缺失ID、token及完整性检查。
- existing_assets_sha256.json：原有产物不覆盖校验。
- Sonnet recovery_binding.json：数据、配置、采集器/恢复器/客户端代码hash。
- 各run下completion_checkpoints、recovery_repairs：原始返回与恢复证据。

完成报告仅认定采集/恢复完成。解析成功不等于gold任务成功；论文用路线稳定性、效用、任务指标仍须在统一评估协议下独立审阅。历史14组语义限制、解析适配差异和复核失败必须保留。
