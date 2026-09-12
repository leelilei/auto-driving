# 给 agy CLI：DARC-Route v4.1 下一阶段实验执行书

日期：2026-09-12。工作目录：`/Users/mac/Documents/6-Research/9-AutoDriving`。

唯一研究依据：[当前 proposal v4.1](../plans/proposal.md)；固定版本：[v4.1快照](../plans/proposal_v4_1_budgeted_stability_20260912.md)；背景：[项目收敛决策](../plans/PROJECT_RESET_V4_1_20260912.md)。如旧 handoff、报告或脚本注释与本轮冲突，以用户本轮要求及 v4.1 为准；文档中的历史建议不构成新任务。

**本次先完成 E0＋E1 和 E2 准备。不要一上来调用模型。** 目标是在9月20日前形成范围明确、能独立复算的实验包，不继续Travel/ontology分支，不写论文，不承诺正结果。

## 1. 本次任务完成标准

agy 应交付：

1. GPT/DeepSeek 历史数据—响应—图—指标版本账本，以及可离线复现的结果。
2. 在同一批候选、共同结构保护、同复核数量下，对随机/语义/决策信号的公平比较。
3. 历史漂移、偏好标签缺失、失败分母、token缺失等问题的明确分类；不以默认值补证据。
4. 可用未暴露语义簇清单、拟采集数据与真实人工审核待办。
5. Codex可直接执行的验收命令和结果目录，不只交付“全部通过”的文字。

E0/E1完成后进入 **READY_FOR_CODEX_REVIEW**。有数据缺口就交付部分可核查结果和BLOCKED项，继续完成不依赖它的工作。E2批量调用须满足第8节前置条件；E0/E1成功不等于研究假设成功。

## 2. 固定范围与不可改项

- 方法沿用v4：A/B两路原句解析、结构保护h、交叉效用差ΔU、最多一次语言复核。复核器不看路线或效用报告。
- 历史在线阈值保持τ=0.02，B4历史阈值与B3概率读取该运行对应冻结配置；不得拿当前全局配置静默覆盖旧配置。
- 同预算比较是独立的离线批量排序实验；不能写成在线严格预算保证。
- 暂停Travel、COG-Guard、v5后果反馈、其他模型扩量。不要根据结果换模型、图或筛错例。
- 不改原始run、旧报告、原始请求响应、旧数据和冻结配置。需要修实现时新增版本文件，输出到新目录。
- SHA256只用于证据完整性；新随机对照使用标准随机生成器，不用内容哈希给样本打风险分或挑选有利复核对象。
- 本轮仅准备实验图表与结果报告；实验落地、Codex独立验收、负责人认可之后才写论文。

## 3. 已核实的代码与数据入口

以下路径均相对项目根目录。**入口存在不代表可以直接运行其main函数。先检查写入目标和API副作用。**

| 路径 | 用途与注意事项 |
|---|---|
| `9-AutoDriving-core/src/gating.py` | v4实际方法、结构保护、交叉效用、回退逻辑；保留历史行为 |
| `9-AutoDriving-core/src/solver.py`、`graph.py`、`intent.py` | 精确后端、图、解析schema |
| `9-AutoDriving-core/src/evaluation.py`、`metrics.py` | 核对gold评分与各指标分母，不能仅相信函数名称 |
| `9-AutoDriving-core/scripts/collect_b1_test.py` | 可参考已有评估函数；其采集main会调用API并更新旧结果，不执行 |
| `9-AutoDriving-core/scripts/recompute_v2.py` | 指标v2参考；main会覆盖公共汇总并遍历额外模型，不直接执行 |
| `9-AutoDriving-core/scripts/run_ablation_experiment.py` | 历史消融/配额代码；默认可调用重复实验，`--skip-api`也不代表口径已合格 |
| `9-AutoDriving-core/scripts/plot_paper_figures.py` | 已发现硬编码与JSON不一致，不作为数值来源 |
| `9-AutoDriving-core/results/runs/20260906T051339Z_main_test` | 旧GPT主运行候选证据，按实际文件核验 |
| `9-AutoDriving-core/results/runs/20260906T081920Z_main_test_deepseek_v4` | 旧DS主运行候选证据 |
| `9-AutoDriving-core/results/reports/recomputed_v2_metrics.json` | v2与v1并列参考，不把参考汇总当新独立复算 |
| `9-AutoDriving-core/results/reports/ablation_experiment_summary.json` | 历史同配额数值线索，不引用绘图硬编码 |
| `9-AutoDriving-core/data/test/test_640_utterances.json` | 旧数据，须核对run实际文本绑定 |
| `9-AutoDriving-core/data/test/test_640_utterances_v2_confirmed.json` | 修订数据，不可配旧响应充当新实验 |
| `9-AutoDriving-core/data/test/test_640_v1_to_v2_changelog.json` | 漂移/标签变更追踪入口 |
| `9-AutoDriving-core/data/processed/development_exposure.json`、`hipp_clusters.json` | 暴露与去重初始账本，不保证包含后续全部暴露 |
| `9-AutoDriving-core/data/calibration/frozen_config.json` | 校准参考，核查是否和具体run绑定 |

建议新增 `9-AutoDriving-core/scripts/v41_audit.py`、`v41_equal_budget.py`、`v41_prepare_confirmation.py` 和相应测试。**这些是待实现接口，目前不能当作已有可运行命令。** 避免为本次任务搭建通用agent平台。

## 4. 输出结构与日志

首次执行创建唯一日期时间目录，不覆盖已有目录：

```text
9-AutoDriving-core/results/v4_1/<UTC时间>_e0_e1/
  protocol.json                 # 执行前冻结，含范围、版本、种子、预算定义
  input_manifest.json           # 相对路径、hash、用途、实际版本、必需性
  binding_audit.json            # 文本/响应/图/配置对应关系
  evidence_ledger.jsonl         # 逐请求来源、状态、标签资格
  e0/metrics_historical.json
  e0/metrics_clean_subset.json
  e0/version_differences.md
  e1/selections.jsonl           # 方法/预算/种子/触发原因/选中与否
  e1/paired_results.jsonl       # 全逐样本或逐配对结果
  e1/metrics.json
  e1/costs.json
  e1/confidence_intervals.json
  preparation/exposure_audit.json
  preparation/review_queue.json
  tests/                       # 完整测试输出、退出码、断网/篡改验证
  SUMMARY.md
  CODEX_REVIEW_REQUEST.md
  hashes.json
```

`protocol.json`冻结输入清单、候选版本、求解/评分版本、配额取整、排序、随机/重采样种子和失败处理。指标精度在JSON保留原始浮点，只在展示时四舍五入。摘要每项写PASS/FAIL/BLOCKED/NOT_RUN及证据路径。终端实时记录阶段和进度，发生异常输出具体原因与受影响分母，禁止输出API密钥。

## 5. E0：历史证据统一核验（零API）

### 5.1 先建立事实账本

逐run核对预期160组/640句、每组实际文本与变体、图、A/B/复核原始响应、配置、请求/返回模型名、服务商、失败与重试。缺组/重复ID必须报错，不能靠glob找到多少就算多少。缺原始响应与“原始记录中明确保存的网络失败”分开：前者证据不完整，后者是需要计入分母的实验结果。

核验旧文本与run保存的prompt或请求一致。14组已知漂移不能只凭数目整体剔除；逐组链接变更记录。输出“原始历史全组”“经证据确认等义的事后子集”“审核未知”三类。新v2文本只能作版本差异说明，不能回填旧请求。其余146组不自动视为人审合格。

### 5.2 指标统一

先复现历史定义的B0/B4/B6/DARC，解释与旧JSON差异，再建立v4.1公共评价。B0与B2输出必须完全一致。记录每项指标的gold来源、权重来源、距离精度、成功条件与分母。

必须核查的旧问题：

- v1效用用了不同权重下的数值相减；v2必须对gold最优与选中路线用同一个权重和精确距离。
- v2历史权重是合成权重，不能重命名为人工偏好校准。
- `preference_direction`缺失不得默认balanced。无法计算的人工映射指标填null＋原因，不填0。
- 缺失/无效路线不能因为空序列一致而显得更稳定；不能用预测约束给自己评分。
- DS的233次历史传输失败按实际记录核对，不当语义错误，也不从TSR全分母删除。

历史点估计仅用于核对，不是必须达到的目标：GPT B0/DARC Flip=.2385/.2031，v2 loss=.002924/.002361；DS Flip=.0950/.1012，v2 loss=.001672/.001484。复算不同应定位版本或实现，不调程序迎合数字。

### 5.3 E0验收

可在断网状态重算；原资产hash前后不变；每个汇总能追到逐样本；所有差异有解释或标记未解决。若原版本不完整，保留其证据缺口，不使用关闭绑定检查的参数伪造PASS。

## 6. E1：同复核预算比较（优先零API）

### 6.1 固定公平条件

共享同一请求的A/B/复核输出、图、回退逻辑。比较B0、B2、B3、B4、B5、B6与DARC；B1仅保留已有结果，不新采A2/A3。

对一个预先列出的分析批次N，q∈{0.05,0.10,0.20}，**K=floor(qN)**。主预算为10%。所有选择方法先选择相同的h请求，随后从h=0中填满K−H个名额：DARC按ΔU降序，B4按|wA−wB|降序，B3按标准随机排列。h=0却无有效分数时是实现/分类错误，不能默认成0。

若H>K，该批次该预算为INFEASIBLE_BUDGET；不裁掉h、不提高K、不临时改成“h之外额外10%”。报告B0/B6与失败分层，主张不能在这一预算下成立。所有方法的实际选中ID数必须严格相等。

排序并列用调用前冻结的随机采集顺序；历史样本的排序顺序在本轮结果分析前冻结，明确它是事后再分析。B3种子固定0—19，不挑种子；其他随机用途分流，保存随机实现版本和排列。

### 6.2 逐项输出

- 原始历史口径Flip与v4.1口径分表，不跨口径算提升。
- 主比较Flip使用DARC/B4/20个B3种子的共同成功配对交集，各方法分母完全相同；交集太小如实报数量，空集记不可估计。
- 全组四句形成6对；全分母附“路线不同或任一失败率”，任一失败记1。这个补充指标不能被条件Flip替代。
- TSR、GTSR、字段正确性、预测方向、条件同尺度loss、完整分母失败赋loss=1的敏感性。
- 预测方向为w>0.5/等于0.5/<0.5；gold无法判断或证据缺失则单列，不补标签。
- 复核前后correct→wrong、wrong→correct及其分母；只在可靠标签支持时计算。
- 三个人工偏好映射只有真实标签存在才运行，测试必须证明不同映射进入了评分，不重复打印缓存。

### 6.3 成本和区间

成本分成两本账：实际实验采集花费；每种方法在部署时所需A/B及选中复核的调用/token。共享缓存不代表在线调用免费；B0=1次，双路方法=2+q_actual，B6=3次。缺token不可从调用数虚构，填NA。推理延迟不能简单把并行请求时长求和当端到端时间。

同复核数量不等于同token预算，因此主文只能称“同复核配额”；真实token和规划耗时另表。没有token证据不得写“同计算成本获益”或“节约费用”。

按独立语义簇配对bootstrap2000次，冻结种子20260912；每次重算共同交集的分子分母。配额选择在原冻结批次计算一次，不在bootstrap样本中重选Top-k：本区间估计该批固定选择策略的差异，不能冒充重新部署到新总体的全部选择不确定性。B3主点估计为20种子均值，另报种子分布；主推断为DARC对B4和B3，若报告p值须说明检验算法并做Holm校正，不把bootstrap符号比例随意当p值。

本轮将结果画成实验诊断图，所有图直接读取新JSON，不复用旧硬编码图。不得因某个预算更好就换主预算。

## 7. 测试与断网验收

必要测试应覆盖实际失败模式，不以数量为目标：

- 缺组、重复ID、响应文本与数据版本不一致、候选缺失：硬失败；明确记录的传输失败：完整计分。
- 结构保护H>K：预算不可达；H≤K：三方法精确选K，h全部包含；并列排序可重现。
- B0/B2输出一致；未选中的复核答案不影响在线方法输出；改动gold不改变调度选择，只改变评分。
- 共同配对分母一致；全失败样本不成为稳定成功；空交集不报0；按组重采样而非按句。
- 同权重最优路线loss≈0；明显非最优为正；超出浮点容差的负loss报错，不能一律clip掩盖bug。
- 缺偏好标签禁止默认均衡；三套映射确实改变权重。
- 旧文件hash不变；删预测行、删摘要、修改文本或选择ID，replay必须非零退出。

基本环境检查命令（已存在）：

```bash
cd /Users/mac/Documents/6-Research/9-AutoDriving
9-AutoDriving-core/.venv/bin/python --version
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python -m pytest 9-AutoDriving-core/tests
```

新增入口实现后，agy必须在CODEX_REVIEW_REQUEST.md写出实际可运行的E0、E1、replay、篡改测试命令，带完整路径和退出码。不要把本文建议脚本名写成“已完成”。离线验收须真正禁止socket网络请求并验证拦截生效，不靠口头承诺断网。

## 8. E2准备与启动条件

与E0/E1并行可做数据盘点，不做模型调用：合并所有历史分支的开发暴露记录，按语义簇核对剩余HIPP，9/13先报告可用簇数。计划40个未暴露等义组×4句，加独立10组语义改变对照×2句，调用前冻结文本、图、标签、顺序和prompt。

真实人工审核逐条确认原句与改写的S/T/D/偏好方向，并保存审核人真实身份、时间、范围和结果。AI预审可先做，但标签为AI_REVIEW，不代签人审。以前对Fair30、Travel或14组修订的批准不能迁移为新批批准。未见簇不足时产出明确的重复性替代方案，不能换ID冒充新样本。

E2批量启动条件：E0/E1交付已由Codex核查；数据与审核通过；输入隔离/模型配置/失败政策冻结；新采集协议写入证据性质（未见确认或旧组重复），不混用。此前用户允许调用API，不需重复申请同范围费用授权，但数据人工审核不能由超时或默认值代替。

本次agy首轮交付先停在Codex复核点；可以持续完成数据准备、代码与测试，不提前运行E2。需要人工审核时提交具体review_queue与审阅材料，不问泛泛的“可以继续吗”。

E2以后按冻结协议：理想480+60=540逻辑调用；每个逻辑单元最多一次传输重试，故最坏1080 HTTP尝试，实际重试另记，不声称540是含重试硬上限。schema/语义错误不重采。同一句按A/B独立生成，再提供A/B给复核器；同模型不得混身份。必要身份健康探针限一次＋一次传输重试，记作额外诊断，不混主实验；首批4组仍在完整分母，不能按效果丢弃。

若原模型无法获得，报告真实可用身份与迁移方案；不自动轮换多个模型寻找正结果。密钥从现有环境或受保护配置读取，不写入交接、日志、请求快照或git。

## 9. Codex复核清单

| 验收项 | 必看证据 | 不合格示例 |
|---|---|---|
| 数据版本绑定 | manifest＋原请求文本＋变更表 | confirmed v2配旧响应 |
| 历史指标 | 原始逐样本→新汇总命令 | 复制旧表，无复算 |
| 公平配额 | 所有方法选中ID/h/K | 单独给DARC更多预算 |
| 随机对照 | 20种子完整记录 | 只报最差随机种子 |
| 分母 | 全请求、共同配对、失败分类 | 删除网络失败或空交集计0 |
| 效用 | gold来源、权重、共同成功集 | 合成权重称人类偏好 |
| 成本 | 原始usage与方法账本 | 少复核称省同等比例总token |
| 证据完整性 | 断网replay＋篡改非零退出 | allow-partial绕过缺行 |
| 数据准备 | 暴露簇计数＋真实人审 | 改ID即称未见测试 |
| 主张 | 正负结果与区间 | 只有Flip就称整体更正确 |

## 10. 交接汇报格式与时间安排

每天更新SUMMARY.md，包含：完成内容、实际运行命令/退出码、结果与全分母、未解决项、API逻辑请求与HTTP尝试/token、下一步。超过一个阶段不要只写“推进中”。

9/12—13完成E0/E1和剩余簇盘点；9/14完成数据审核准备并提交Codex；9/15—16在条件满足后执行E2；9/17实验独立验收与主张确认；只有用户认可后才进入9/18—19论文写作。若依赖未满足，报告明确受影响交付，不用扩任务填时间。

## 11. 可直接粘贴给 agy CLI 的任务

> 请在 `/Users/mac/Documents/6-Research/9-AutoDriving` 按 `docs/guides/AGY_V4_1_EXPERIMENT_HANDOFF_20260912.md` 执行 v4.1 的 E0 历史版本审计、E1 同复核配额重算与 E2 数据准备。以 `docs/plans/proposal.md` 为唯一当前研究主线。先检查现有脚本的API和覆盖写入副作用，新增独立版本与输出目录；保留所有旧结果。首轮不调用模型，不推进Travel/ontology，不写论文。完成可复算的全分母结果、测试、断网回放与篡改验证，提交 SUMMARY.md、CODEX_REVIEW_REQUEST.md 和真实可运行命令。遇到缺标签或版本不匹配不得自动补值，继续完成独立工作并列出具体阻断项。E2批量等待Codex复核及真实数据审核前置条件，不以文字自评代替验收。
