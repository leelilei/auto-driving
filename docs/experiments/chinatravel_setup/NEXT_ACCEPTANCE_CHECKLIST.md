# ChinaTravel v2 验收清单

2026-09-11。总体 **PARTIAL**：离线验收 PASS，真实端到端流程 FAIL（协议停止，尚未执行工具），证据交付完整。工程失败不等于研究假设被否证。

入口：[实现报告](NEXT_IMPLEMENTATION_REPORT.md)；[机器可读复核](v2_validation/acceptance_audit.json)；[测试计数](v2_validation/offline_test_summary.json)。本轮由同一 Codex 实现与复核，分进程核验不冒充独立人员验收。

| 检查项 | 状态 | 实际证据与边界 |
|---|---|---|
| 保留 v1 和旧证据 | PASS | v1 源码未改，原 13 项通过，旧 run 按原 replay 命令复算一致 |
| 官方评分入口与分母 | PASS | 沿用三层官方函数和通过 ID 交集；正例、错误实体/时间/硬约束/空输出以及 1/2 缺失预测测试通过 |
| v2 离线测试 | PASS | 20 项新增测试；合计 33 项、130 次实际 unittest 断言调用，0 failure/error |
| JSON 白名单调度 | PASS（离线） | 合法动作调用真实官方 select；参数类型/缺失/未知工具/危险表达式、多动作和无效 JSON 均拒绝 |
| 实体与错误分类 | PASS（离线） | 未知 POI 返回 unknown_entity，零行 no_match；注入的内部异常为 tool_internal_error；不替换实体 |
| 原始轨迹与转换 | PASS | 两次真实 raw 完整保留；parsed/dispatched 为 null，转换 none，拒绝原因在 tool_trace 中；仅完整外层围栏允许转换 |
| 原句与 gold 隔离 | PASS（已测试边界） | collect 只接收 public_inputs；真实 wire_payload 包含完整原句；独立哨兵检查 system/messages/修复反馈；实际未发现完整 gold DSL 片段 |
| 模型和预算冻结 | PASS | 既有 Haiku/xcode；三例顺序、代码/配置哈希和预算在第一次请求前落盘；75 项固定文件、264 个 sandbox 源文件校验 |
| 请求账本 | PASS | 实际 2 次、每次 attempts=1；system+user 6142 字符；提供方 input/output 1468/163，未知 usage=0；不记录认证头 |
| 预算预留 | PASS（离线）；真实路径待验证 | 110000 查询/50000 最终额度及超限不发送测试通过；八次查询后进入最终阶段测试通过；真实因连续协议失败例外停止 |
| 在途超时 | PASS（请求层） | 请求定时器受案例剩余时限约束；离线计时器测试通过；本地工具执行及落盘无独立可中断计时器 |
| 官方 object/itinerary schema | PASS（离线）；真实未产出 | 评分器正例仍通过；最终围栏不静默修复；真实没有最终响应，不能称模型输出 schema 错误已修好 |
| 固定三例与扩展门槛 | PASS | 仅第一例尝试；两次协议错误触发硬停止；medium/human 均 not_executed，预测 ID 未删 |
| 真实工具→行程→评分 | FAIL | 两次响应含 JSON 外说明，0 个工具动作执行，0 次最终规划；已尝试案例 all-pass 0/1 |
| 评分归档完整性 | PASS | 三例固定计划账本为 0/3，明确两例未执行；每例三层评分已保留，未将未执行包装为完成实验 |
| 断网回放 | PASS | 本轮真实归档两次分进程回放一致；禁用 socket connect/create_connection/connect_ex |
| 篡改检测 | PASS | 副本删预测、改响应、清空 hash、删请求及其 hash 均拒绝；改写后的临时评价源码替身被源码哈希拒绝 |
| 不改评价目标、不现场重跑 | PASS | 无 gold/官方评分器/fixture 修改；未追加格式修复调用、换模型、提高预算或采集其余案例 |
| 独立人员验收 | 未完成 | 本轮是同一执行者自检与独立账本复算，后续可据归档进行独立复核 |
| 扩量 / DARC 结论 / 论文 | 未开放 | 本轮只支持工程故障定位，论文 CLOSED，未授权扩到 60 例 |

剩余事项：新版本应改进协议错误的具体反馈和中文工具值说明，冻结新的开发计划后再验证真实工具调用及最终规划。不要修改本轮已冻结 v2 文件，以免破坏源码哈希回放；不要在本轮继续使用未消耗的请求额度。
