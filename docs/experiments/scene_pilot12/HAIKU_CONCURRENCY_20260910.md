# Haiku 4.5 / FHL 并发准入实测

2026-09-10。用户授权先测试节点并发，再推进场景实验。

请求模型：`claude-haiku-4-5-20251001`；接口：FHL `/v1/messages`，Anthropic Messages 协议。凭据仅从私有环境变量读取。

计划按并发1、2、4、6、8逐档，每档两批短JSON探针；任一批失败停止升档。若通过，再以最多4并发验证实际场景提示，最后串行执行两例三方法共6次。请求零重试，60秒超时，短探针64输出tokens，场景1600。最高请求预算56次，实际只发出1次。

| 并发 | 批次 | 成功/尝试 | 延迟 | HTTP | 节点返回 |
|---:|---:|---:|---:|---:|---|
| 1 | 1 | 0/1 | 9.973秒 | 429 | Upstream rate limit exceeded, please retry later |

已停止后续批次及升档，未发送场景实验请求；无模型正文、无provider usage，未测得模型效果。

**结论：当前单请求被上游限流；没有测得可用并发或并发上限。** 不能把此结果解释为“最大并发1”，也不能凭错误消息区分账号额度、共享上游负载或具体限流策略。应待节点恢复后从并发1重新检查，当前不启动批量实验。

证据目录：`9-AutoDriving-core/results/scene_pilot12/20260910T064756Z_haiku_fhl_probe/`，包含manifest、原始请求、429响应及summary。脚本：`9-AutoDriving-core/scripts/scene_claude_probe.py`。该脚本不修改正式采集快照或人审状态；新数据仍PENDING。
