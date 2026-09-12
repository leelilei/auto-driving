# Scene-Pilot12 工程交接与下一步

> 后续进展：Haiku / xcode已完成真实开发采集，115项测试通过，最新结果及新合同回放命令见 [Haiku实测报告](HAIKU_SCENE12_RESULTS_20260910.md)。本文下方API调用0和DS准备目录描述保留为此前交付记录。

更新：2026-09-10。工程链路已实现并完成本轮自检；新数据语义人审仍为 PENDING；真实 API 调用 0。论文写作未启动。本文件不替代后续独立实验验收。

## 已落地

- `9-AutoDriving-core/src/scene_policy.py`：三字段规则 DSL、严格响应解析、全候选场景事实、按模型预测规则执行、独立参考评分。最近距离、最小额外距离、最高评分明确分开，没有哈希参数或隐含权重。
- `9-AutoDriving-core/scripts/scene_pilot12.py`：prepare / collect / mock / replay。Direct 与两个复核共享候选，复核系统提示相同，差异只有计算事实表；第二次重复交换两种复核调用顺序。
- `9-AutoDriving-core/tests/test_scene_pilot12.py`：35 项新增检查。全项目 **112 passed**。覆盖 12 例独立参考对齐、速度、禁止等待、关门/返家等号、资格参考时刻、并列最优、错误规则实际影响输出、输入隔离、失败回退及账本破坏。
- `9-AutoDriving-core/results/scene_pilot12/20260910_mock_validation/`：在阻断 socket 连接的上下文中完成 72 个模拟单元；完整汇总经 JSON 规范化后重放相等。使用固定虚拟规则，不读取 gold 生成响应；其中所有准确率均无研究意义，不能进入模型主表。
- `9-AutoDriving-core/results/scene_pilot12/20260910_prepared/`：数据、提示所在源码、配置与 72 单元计划的快照；没有 attempts 目录。`readiness_check.json` 记录未审核时在读取密钥和调用 API 前被拒绝。

## 已固定的开发试跑安排

12 例 × 2 次重复，每次共享一个 Direct，再分别做 Language 和 Evidence，共 72 次基础调用。最多补 8 次传输失败，每个单元最多 2 次物理尝试，并发 4，超时 120 秒，输出上限 1600 tokens，temperature 0，客户端内重试 0。先串行完成首例的一次三方法链路，再推进其他单元。

候选配置沿用 DS 官方 `deepseek-v4.1-flash-expires-on-0910`。该名称带日期，**本轮没有验证它当前仍可用**；正式采集前应确认实际模型身份。若需要换模型，另建配置和快照，不能改已运行快照后继续合并结果。首例请求可作为采集内的连通性检查，但不能据其正确率改后续提示。

Schema 失败不重试：Direct 失败导致两个复核登记上游失败，仍保留分母；复核失败回退 Direct。网络失败记录原始尝试，预算耗尽或鉴权错误使运行不完整，不产生完整排名。遗留 STARTED 状态需要核对实际响应/计费，不能盲目重发。

哈希只用于检查文件版本完整性，不参与算法决策、目标函数或 POI 选择。它不构成防篡改签名或人审真实性证明。

## 下一步所需材料

请以 [CASE_REVIEW.md](CASE_REVIEW.md) 为准审核这轮 **12 个新案例**的原句、资格条件及预期答案。历史测试集获批不能替代这批新数据人审；本轮“推进”用于落实工程，不被代填为逐例语义裁决。

收到真实裁决后，按 `20260910_prepared/admission_template.json` 另存 `admission.json`，如实记录审核者、时间、原始裁决文本、覆盖案例及版本，绑定最终选定模型。存在争议则修订并另存数据版本。不要为了通过程序校验编造审核记录。此处审批记录是实验来源证据，并非研究方法中的门控模块。

## 运行与复核命令

在项目根目录运行。当前可直接执行测试和模拟回放：

```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/pytest -q 9-AutoDriving-core/tests

PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python \
  9-AutoDriving-core/scripts/scene_pilot12.py replay \
  --run-dir 9-AutoDriving-core/results/scene_pilot12/20260910_mock_validation
```

真实人审记录齐备且模型配置确认后使用以下命令；当前运行会拒绝，不能把 PENDING 改成 APPROVED 来绕过：

```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python \
  9-AutoDriving-core/scripts/scene_pilot12.py collect \
  --run-dir 9-AutoDriving-core/results/scene_pilot12/20260910_prepared \
  --admission 9-AutoDriving-core/results/scene_pilot12/20260910_prepared/admission.json
```

DS 密钥由现有系统 Keychain 的 `DEEPSEEK_API_KEY` 条目读取，不写入结果目录。完成后将 collect 改为 replay 并移除 admission 参数，可断网重算真实结果。

## Codex 后续验收与去留

1. 验证真实审核证据、模型实际身份、请求来源和快照；模型接通不能等同效果成立。
2. 查全 72 单元及每次失败记录；检查复核确实复用同一 Direct，输入没有 gold、配对关系或人审标签；网络失败不得从分母静默删除。
3. 离线重建原始解析、回退、预测规则执行与参考评分。汇总须包含两次重复、可行/不可行分层、6 对的双侧正确、净纠正/改坏、schema 状态、provider tokens 和延迟；未知 usage 不能记成免费。请求时长之和不是并发墙钟耗时。
4. 逐例解释 Evidence 相对 Language 的差异，判断收益是否跨至少两个案例族、是否代价或退化抵消。12 例仅是 6 对开发案例，不能用重复增加独立样本量。
5. Direct 再次全对则如实认定当前任务饱和；Evidence 不优于 Language 则不扩量。这一轮用于判断是否值得继续研究，不给出 SOTA 或论文级有效性结论。

研究原则持续有效：实验落地 → 独立验收 → 负责人明确认可 → 论文写作。
