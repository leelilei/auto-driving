# 阶段二至阶段三执行计划与实测进度

> **2026-09-08 版本提示**：当前研究主线以 [Proposal v5](../../plans/proposal.md) 为准。本文件以下内容保留为旧方案记录，不能直接用作 v5 执行协议或完成证明。旧阶段三暂停扩量；需落实新数据资格、对比报告、配对图与对照协议。论文写作仍 CLOSED。

日期：2026-09-08（Asia/Shanghai；run_id 为 UTC，故显示 20260907T16…）。用户授权：核查当前进度并推进至阶段三。论文写作 CLOSED；本轮不推进阶段四跨模型扩量。

## 当前实际状态

- 原有 59 项测试通过（3.27s）；新运行器 5 项针对性测试通过（0.06s）。不能把测试通过等同于数据与实验验收。
- confirmed 数据文件存在，160 组/640 句；本轮对人工审核范围发出了澄清，尚未收到答复。用户提交的进度汇报说明 14 组已终审，但“14 组修订通过”不能自动证明 A 全审/B 独立复核、其余 146 组或 Pilot 的人审完成。本轮未否定已报告的 14 组认可，也未代填任何人工审核状态。
- 原主脚本仍默认读取旧数据，只采集 A/B/review，缺 B1 所需 A2/A3；resume 可能重跑覆盖失败组。因此没有直接启动该旧入口。
- 已新增 `scripts/run_fresh_stage.py`：可绑定指定数据、冻结快照/代码/参数/哈希，stage main 每句收集 A/B/review/A2/A3 五份独立响应并评价八方法；Pilot 每句三份响应。原始请求开始/结束各自留档、不覆盖、不静默重试；任何传输错误停止后续批次。阶段三必须提供独立准入 JSON，且目标数据 SHA256 必须一致。
- 新入口仅有 dry-run 和本地生产路径测试通过，尚未通过完整成功的真实端到端采集验收。它是阶段三的准备成果，不是已完成主实验。

## 实际网络尝试

| UTC run_id | 实际完成调用记录 | 有效响应 | 结果 |
|---|---:|---:|---|
| 20260907T160417Z_fresh_pilot | 1 | 0 | 沙箱内 curl 连接失败；失败汇总暴露未尝试 B 调用的 KeyError，随后修复并加入回归测试；保留原目录，不当作完成 run |
| 20260907T160619Z_fresh_pilot | 1 | 0 | 经联网授权后，供应商 HTTP 502；自动中止，退出码 2 |
| 20260907T160716Z_fresh_pilot | 1 | 0 | 独立重试遇 LibreSSL SSL_ERROR_SYSCALL；自动中止，退出码 2 |

三条调用记录均保留。未获得 provider usage，因此“已知 provider tokens=0”不等于已证实费用为零。未启动 640 句主实验，也没有以旧输出代替新响应。不同错误均属于采集失败；不能据此判断算法、模型准确率或门控研究假设。

## 冻结本轮运行口径

- 主模型：沿用 FHL 配置中的 gpt-5.4-mini；本轮未擅自切换模型。
- 提示：复用现有 A/B/review；A2/A3 使用与 A 相同提示和配置，独立调用。
- Pilot 上限 80×3=240 次；阶段三上限 640×5=3,200 次。无自动重试；独立重试使用新 run_id，失败不覆盖。不要承诺固定“两分钟”完成。
- τ=0.02、τ_sem=0.10、p=现有 frozen_config 的精确值，不用本轮测试选择阈值。
- 评价权重按方向映射 0.75/0.50/0.25，明确是校准评价假设，不是用户精确数值真值；原始 w_synthetic/w_proposed 保留。指标版本为 fresh-v3-valid-task-pairs。
- Flip 使用双侧 task_success 的有效对；同时报有效对分母、TSR/GTSR、成功样本 regret 分母及缺失调用。中断 run 的已尝试样本指标不能冒充全计划样本结果。
- 收集成本与各策略反事实逻辑调用/已知 provider tokens 分开；缺失 usage 显式报告。
- 此次数据沿用已暴露意图组；即使重新采集新鲜 API 响应，也只能称为固定协议的新鲜复现实验，不能称“完全未见的独立确认集”。若要求独立确认性结论，必须另行准备未暴露语义簇及审核。

## 阶段三准入条件

1. API 可完成 Pilot，所有预定记录完整且版本一致，失败有可追溯记录。
2. 明确实际人审范围；补足 Pilot/全量数据的真实审核或如实修订研究范围，不能把状态字段直接清零。
3. 对新鲜 Pilot 计算逐例纠正/改坏、TSR、Flip、同尺度 regret 和成本；按实验协议独立审查 Gate A/B。没有正向结果也要如实保存，不能自动写 PASS。旧 calibration 可参考但不是新鲜 Gate B 已通过的证据。
4. 确认数据暴露边界、完整基线与计划，并形成 `admission.json`：只有独立审查允许时才置 `stage3_allowed: true`，记录 `test_dataset_sha256`、所依据 Pilot run、审阅范围及剩余限制。
5. 然后执行下面的 main 命令。当前 `admission.json` 为 false，运行器必须拒绝。

```bash
# 无网络计划检查（已执行）
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/run_fresh_stage.py \
  --stage main --dataset 9-AutoDriving-core/data/test/test_640_utterances_v2_confirmed.json --dry-run

# API 恢复后重新采集 Pilot（新目录，不覆盖当前失败）
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/run_fresh_stage.py \
  --stage pilot --dataset 9-AutoDriving-core/data/pilot/pilot_80_utterances.json --workers 1

# 仅独立准入后执行；当前 admission=false，会拒绝
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/run_fresh_stage.py \
  --stage main --dataset 9-AutoDriving-core/data/test/test_640_utterances_v2_confirmed.json \
  --admission docs/experiments/stage3_20260908/admission.json --workers 4
```

## 后续验收仍要做的事

成功采集后，基于独立 manifest 验证完整 160×4×5 资产并断网重算八方法，检查结果一致；完成组级配对区间、同预算对照与预设假设判定，不把本次新入口的点估计输出当作全部统计已完成。需要增加 resume 时按不可变 attempt 和 manifest 实现，不能恢复旧脚本的覆盖失败行为。本轮代码不支持 resume，以避免未经验证的缓存复用。

日志：`pytest_before.txt`、`fresh_stage_tests.txt`、`main_dry_run.json`、`pilot_console.txt`、`pilot_network_attempt1.txt`、`pilot_network_console.txt`、`pilot_attempt_inventory.json`。
