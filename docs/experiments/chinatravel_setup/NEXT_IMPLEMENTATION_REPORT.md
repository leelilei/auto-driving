# ChinaTravel v2 实现与开发试跑报告

日期：2026-09-11。执行者：Codex。依据：[NEXT_HANDOFF_20260911.md](NEXT_HANDOFF_20260911.md)。

**结论：PARTIAL。离线工程验收通过；真实首例在工具执行前连续两次协议失败，按冻结规则停止，其余两例未执行。** 本轮没有形成可评分的最终行程，没有完成真实端到端成功验证。失败证据和完整分母均已保留，没有提高预算、改变解析规则或再次采集。论文仍为 CLOSED。

## 实现和证据入口

- [v2 执行器](../../../9-AutoDriving-core/scripts/chinatravel_pipeline_v2.py)：独立新文件，继续调用 v1 的官方三层评分封装；v1 源码、旧测试、gold、官方评分器和正例 fixture 未修改。
- [v2 测试](../../../9-AutoDriving-core/tests/test_chinatravel_pipeline_v2.py)：新增 20 项离线测试。
- [冻结配置](../../../9-AutoDriving-core/configs/chinatravel_act_v2.json)：xcode / claude-haiku-4-5-20251001，temperature=0，4096 输出 token，60 秒超时，重试 0，并发 1。
- [本轮运行目录](../../../9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_json_v2_dev3/)：plan、manifest、public_inputs、逐请求与完整提供方响应、tool_trace、predictions、collection、official_score、replay_report、manifest_hashes 均已落盘。
- [离线测试账本](v2_validation/offline_test_summary.json)、[测试日志](v2_validation/offline_tests.log)、[实际采集日志](v2_validation/live_run.log)、[复核证据](v2_validation/acceptance_audit.json)。

## 改了什么

工具协议改为单个 JSON 动作，只允许 `tool` 或 `finish`。宿主检查工具白名单、必填和未知参数、值类型、城市、时间与枚举。筛选只支持 scalar 的 eq/ne/contains/lt/le/gt/ge，多个条件取 AND；contains 是字面子串，不支持 regex、OR、Python 或 lambda。由宿主闭包调用官方 select，不执行模型文本。

轨迹保留 raw_response → parsed_action → dispatched_call → observation。只允许剥离**独占整个响应的一层** Markdown JSON 围栏；前后有说明文字则拒绝，不全局修正转义。最终输出直接严格解析 JSON，围栏、说明文字或非对象均不回退修复。重复 JSON key、多动作、非有限字面常量会被拒绝。

`goto`、nearby、POI 精确查询先使用官方 POI 做实体预检；未知实体、无匹配数据、协议/参数错误和工具内部异常各自记录。新增 `poi_names` 是对公开官方 `Poi.data` 名称索引的只读适配，按原顺序提供名称，不根据 gold 选实体。keys 一次返回所有字段，官方 Python 类型对象明确转成类型名称。表格/列表查询每页 5 条，零基页号、总数和 next_page 显式记录，保持官方返回顺序，不重排。

查询最多 8 次，错误动作也计入；查询累计 system+user 最多 110,000 字符，最终规划保留 50,000，总上限 160,000。通常最多 8 次查询加 1 次最终规划，12 次物理请求是硬上限，不把剩余额度用于重试。每次请求在发送前记账落盘；失败也保留。请求的实际序列化 payload 被捕获，核对 system/messages 与记录一致；不保存认证头或密钥。保存提供方完整 JSON 响应和 usage。

事实上下文按确定规则保留：从最新开始选取能放入 30,000 字符的完整动作/观察记录，再恢复时间顺序；在实际上下文标明省略的 trace index。完整原始轨迹始终留盘，无额外 LLM 摘要。原句不截断；最终阶段另附官方 schema。单个在途请求使用 `min(60 秒, 案例剩余时间)` 的进程计时器，阻止该请求越过剩余时限；900 秒预算在请求前检查，工具调用和本地落盘未另设可中断计时器。

prepare 是单独数据准备入口，生成只含 uid/完整原句的 public_inputs；collect 进程不解析 gold 文件。评分在 collect 退出后由独立 score 进程执行，不向模型回传约束结果。评分仍调用官方 schema、commonsense、hard v2，all-pass 取三层通过 ID 交集。不同长度 DSL 在官方 DataFrame 中形成的 NaN 空位仅序列化为 null，不改变任何得分或评价条件。

冻结计划固定了三例顺序、提示、协议、预算、模型配置及 75 个相关代码/数据清单/配置/测试文件哈希，覆盖官方 evaluation、symbol_verification、environment 与 v1/v2/client。中英文评分工具读取的 264 个源文件重新匹配发布 SHA256 清单。dev 60 与 hold 544 的成员和 UID 无交集重新核验；不宣称语义家族隔离。

## 与官方 Act 的差异

名称为 **ChinaTravel Act JSON 本地协议适配 v2**，不是未经修改的官方 Act 复现。v2 自行管理查询/最终规划阶段、JSON 动作、公开名称索引、分页、确定性上下文保留和资源限制；直接调用官方工具的 bound methods，未使用官方 Python 文本动作循环，也未加入官方示例或本地 gold 正例作为 few-shot。官方工具数据和评价目标保持原样。

## 真实采集结果

| 固定顺序 / UID | 执行状态 | 请求数 | schema | commonsense macro | hard macro | all-pass |
|---|---|---:|---:|---:|---:|---:|
| 1 / e20241028160248698752 | 已暴露回归开发例；连续两次协议失败；无最终输出 | 2 | 0% | 0% | 0% | 0% |
| 2 / e20241028160842228543 | medium 字典序最小 UID；未执行 | 0 | 0%* | 0%* | 0%* | 0%* |
| 3 / h20241029143447759844 | human 字典序最小 UID；未执行 | 0 | 0%* | 0%* | 0%* | 0%* |

*未执行项以空预测留在固定计划分母，零分不代表这些案例完成了模型实验。已执行案例的 all-pass 为 0/1；固定计划账本为 0/3，明确只有 1 例尝试。*

实际物理请求 2，传输失败 0，协议失败 2，真实工具调度 0，最终规划请求 0，usage 未知 0。提供方报告 input 1,468、output 163，共 1,631 token；逐条 provider_response usage 与遥测一致。案例耗时 7.854 秒，system+user 累计 6,142 字符。该统计不是供应商账单核对，也不能与 v1 的仅 user 字符口径直接比较效率。

两次提供方响应 model 字段均为 `claude-haiku-4-5-20251001`；这是可观察到的返回标识，不是对代理后端架构的独立证明。

## 停止原因和定位

第一次原始响应以 `I'll help you plan ... Let me start by querying transportation options.` 开头，之后才给 JSON 围栏。第二次同样先说明再输出围栏。两次均不是单个 JSON 响应，触发 `invalid_json`，解析器未提取内嵌代码块，也没有误执行工具。第二次 JSON 中还出现 Shanghai/Hangzhou 英文城市名，但该动作未进入调度，不能把它统计为已发生的城市参数错误。

实际第二次请求包含第一次的 `invalid_json / Expecting value` 反馈，但没有保留失败原文，也没有专门解释“移除 JSON 外所有说明文字”。这提示当前压缩反馈对格式纠正的信息不足；尚不能从两次响应判断模型是否利用了反馈，更不能解释为规划能力不足、sandbox 不可用、DARC 无效或语义误读。

两次连续协议错误属于交接单明确的硬停止例外，因此没有追加最终规划请求；预算没有耗尽，预留预算机制在真实成功路径上仍未被验证。首例未通过扩展门槛，medium/human 未发送任何请求。

## 验证和复核边界

旧版 13 项与 v2 20 项共 33 项测试通过；运行时计数为 130 次最外层 unittest 断言调用，含循环和 assertRaises 上下文，另有 mock 的“不被调用”检查未混入该数字。旧 stage2 原命令的 13 项也单独通过，旧 v1 单例仍可按原命令断网重放。

v2 本轮真实归档完成两次一致的断网重放。独立于执行器汇总，重新从实际 wire_payload 计算原句完整性、字符数、逐请求 attempts 和 provider usage；没有发现完整 gold DSL 片段进入请求。加上离线独立哨兵测试，构成当前 gold 隔离证据，不宣称对任意编码的完备防泄漏证明。

在真实归档的临时副本上，删除预测、修改响应、清空哈希字典、删除请求并同时删除其哈希项均被检测；将评价源码的字节读取替换为实际改写的临时源码副本也被检测，正式评分器文件未修改。校验要求固定文件角色、预测/计划/评分 ID 和逐请求计数，不能通过单纯删空哈希表绕过；不声称抵御同时重写全部清单与所有证据的攻击者。

本轮实现与复核均由同一 Codex 执行，包含独立进程和独立账本重算，**不是另一位执行者的独立验收签字**。完整验收状态见 [NEXT_ACCEPTANCE_CHECKLIST.md](NEXT_ACCEPTANCE_CHECKLIST.md)。

## 已验证命令

从项目根目录运行。下列回归与 replay 不访问模型。

```bash
external/ChinaTravel/.venv-chinatravel/bin/python -m unittest discover \
  -s 9-AutoDriving-core/tests -p 'test_chinatravel_pipeline*.py' -v

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/stage2_evaluator_test.py

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_pipeline.py replay \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_haiku_smoke

external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_pipeline_v2.py replay \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_json_v2_dev3
```

本轮实际执行的采集命令如下，作为审计记录；目录现已存在并封存，同一命令再次运行会拒绝覆盖。不要更换目录再次采集 v2 来追求成功。

```bash
external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/chinatravel_pipeline_v2.py run \
  --run-dir 9-AutoDriving-core/results/chinatravel_baselines/20260911_codex_act_json_v2_dev3
```

## 下一步建议，不在本轮继续采集

保留已冻结 v2。下一版另建代码和 plan，优先补充明确的协议纠错反馈：携带可追溯的失败响应片段，准确指出 JSON 外说明文字被拒绝，在实际 user 内容中重申唯一动作格式；把中文城市值范围明示到工具文档。仍只允许既定外层围栏转换，不从说明文字中静默抽取任意代码块。

先用本轮两条真实失败响应作为离线回归输入，验证错误可定位、纠错请求可审计、原句/gold 边界不变，再决定下一轮有限单例验证。不得把剩余 34 次请求额度转成当前轮反复调参。真实工具→最终行程的成功路径尚未验证，暂不扩到 60 例，也不启动模型横向比较或论文写作。
