# 公开任务与实验可行性审计

审计日期 2026-09-11。目标是一篇可信的 EI 会议研究论文。此次检查公开论文、固定版本仓库、数据字段和评分代码，没有新调用实验模型，没有运行外部完整评分器，也没有向数据作者发送申请。

## 结论

当前问题不只是数据太容易。三字段抽取、事实计算和完整旅行规划是不同任务；换成更复杂的数据不能自动证明计算复核必要。建议停止当前 Scene 事实表方法扩量，保留已经完成的开发证据。下一项工程优先核验 **ChinaTravel 的原始自然语言模式**，同时用 TravelPlanner 的公开训练集核对评分接口。两者都尚未在本项目达到可运行验收状态。

ChinaTravel 是候选主任务，不是已经锁定的新 benchmark；选择理由是它有可组合约束及显式区分自然语言输入与 oracle 标注的接口。仍须实际核对数据版本、依赖、标签和评分器，不能仅凭其知名度决定新方法。见[官方代码](https://github.com/LAMDA-NeSy/ChinaTravel)。

## 已实际核查的任务

| 任务 | 输入、输出与评价 | 当前可获取性及边界 | 对本项目的判断 |
|---|---|---|---|
| TravelPlanner | 原始旅行要求与环境资料 → 多日行程；常识、硬约束及全通过率 | 已下载并解析 train 45、validation 180 的 CSV；代码与数据库分离，完整评分尚未运行。代码 MIT，数据卡 CC-BY-4.0 | 适合官方评价接口的首个工程核验；不是三字段 POI 任务的直接替代。[仓库](https://github.com/OSU-NLP-Group/TravelPlanner)、[数据卡](https://huggingface.co/datasets/osunlp/TravelPlanner) |
| ChinaTravel | 中英文自然语言要求 → 结构化多日行程；环境与可执行组合约束校验 | 代码有普通模式和 oracle_translation；查询、sandbox 为独立发布资产。已静态审查加载器和 hard evaluator，尚未安装完整环境；本次仓库 metadata 未识别许可证，不把这等同于禁止使用 | 最值得优先做任务映射的候选。必须隔离 gold DSL，并固定发布版本。[仓库](https://github.com/LAMDA-NeSy/ChinaTravel)、[官方论文](https://openreview.net/forum?id=0YRVlxY9BH) |
| FlexTravelBench | 约束逐步加入或优先级要求 → 行程；约束保持与偏好评价 | 有数据文件与代码，但依赖 TravelPlanner；其数据基于原 validation，不能算独立于 TravelPlanner 的另一测试集。所查快照未发现 LICENSE | 如转向约束更新，可作派生协议来源；不宜现在同时扩展到多轮任务。[仓库](https://github.com/juhyunohh/FlexTravelBench) |
| TripCraft | 含时间、空间和 persona 的多日行程；连续质量与离散可行性 | README 要求邮件申请数据和辅助数据库，限制再分发；部分输出后处理使用模型。本轮未申请、未拿到数据 | 暂不作第一实操任务，不能称已可复现。[仓库](https://github.com/Soumyabrata2003/TripCraft)、[ACL 论文](https://aclanthology.org/2025.acl-long.834/) |
| PTS / RealTravel | 隐含偏好与显式约束，结合用户资料和旅行数据 | 所查 PTS 仓库主要提供 RealTravel 数据与处理材料；没有据此确认完整 PTS 规划、求解、评分管线。metadata 无明确代码许可证 | 可用于相关工作，暂不承诺直接复现为完整强基线。[仓库](https://github.com/cliftclift/PTS)、[论文](https://aclanthology.org/2025.acl-long.1339/) |
| LLMAP / HIPP | 语言 → 结构化偏好、任务及依赖；图搜索规划 | 仓库列有 HIPP.json，代码 MIT；运行还涉及 Google Maps，所查树未提供足以复原原论文全部地图的冻结图资产 | HIPP 可作为解析来源，但 HIPP-DC 是本项目扩展，不能当现成榜单。不能仅继承数据名便对比路线 SOTA。[仓库](https://github.com/liangqiyuan/LLMAP)、[论文](https://arxiv.org/abs/2509.12273) |
| TravelBench | 单轮、多轮偏好与不可解任务；带工具交互及模型评估 | 有数据和缓存工具资产；评估还配置用户、工具或评价模型，不能称纯代码 oracle。代码 MIT，数据另有 CC-BY-NC-4.0 | 更贴近交互代理，但目前成本与研究范围过大，暂缓。[仓库](https://github.com/small-xiangcheng/TravelBench)、[论文](https://arxiv.org/abs/2512.22673) |

许可证列仅记录本次查到的发布声明，不是完整法律审核。代码许可和数据许可分开确认，来源不明的部分不打包再分发。

## TravelPlanner 数据与评分器审查

数据 revision 为 `8736504ecfc31b7f8b7e40122873c337e83fff7c`。实际 CSV 行数为 train 45、validation 180；两者均有 org、dest、days、visiting_city_number、date、people_number、local_constraint、budget、query、level、reference_information；train 另有 annotated_plan。三个难度乘 3/5/7 天的九个格子，train 每格 5，validation 每格 20。原始文件与校验值保存在 `data_probe/`。

本轮没有下载 test 内容。train/validation 已用于本次结构审计，后续必须记录这种开发访问；不得声称本地从未接触 validation。今后的提示和方法调试先限于 train，不依据 validation 成绩选方案。

静态代码检查发现以下实施约束。

1. `evaluation/eval.py` 的本地评分流程直接支持 train/validation，并按数据索引匹配预测。必须保存完整预期 ID，缺失预测记失败，不能只平均有输出的部分。
2. 硬约束评价的前置检查是输出不缺失且信息存在于 sandbox，不是“所有常识约束先通过”。微观约束满足、宏观全约束满足和最终全通过不是同一分母。
3. 评分器依赖数据库，并有工作目录和较旧依赖假设。距离工具代码还包含网络方法，必须跟踪实际评价调用路径之后才能宣称评分完全离线。本次只审查代码，没有完成这一运行验证。
4. `local_constraint`、`budget` 等结构标签不能整体直接送给原始自然语言模式的模型。评价器可以读 gold，候选生成与修复接口不可以读 gold。官方 sole-planning 所允许的环境信息也应按原协议提供。
5. 原基准的任务被设计为可行，不能仅运行它便宣称不可行检测有效。没有统一最优行程标签，也不能凭约束通过率计算“相对最优路线 regret”。见[官方任务说明](https://osu-nlp-group.github.io/TravelPlanner/)。

数据库清单显示航班 CSV 约 305 MB，还需住宿、餐饮、景点和距离等文件；本次没有安装完整数据库。代码快照见 `sources/TravelPlanner/`，数据库清单见 `data_probe/hf_leaderboard_tree.json`。

## ChinaTravel 的关键公平性边界

补充数据卡核查记录在 `data_probe/chinatravel_card.md` 和 `chinatravel_metadata.json`。查询仓库 revision 为 `44d5dbf3bba26bdf9a212c3e76d3242b67f0d349`，数据卡声明 CC-BY-NC-SA-4.0。卡片列出 easy 300、medium 150、human 154，以及单独 test 配置的 human1000；这些数量来自官方卡片，本轮未下载对应查询逐行重数。Phase 2 的 2,000 条 full 与 100 条 competition_test 存在包含关系，不能作为独立训练/测试两份使用。见[官方数据卡](https://huggingface.co/datasets/LAMDA-NeSy/ChinaTravel)。

数据卡记载 2026-08-20 修订 28 条 Phase 1 记录，并要求匹配 2026.08.1 或更新 sandbox；其声称修订后的 604 条 Phase 1 均有通过当前评分器的计划。这是官方发布声明，本轮未复验。不要把旧版不可行案例直接沿用到新版，更不能引用其他仓库基于旧版的剔除分母作为当前上限。后续先用 Phase 1 开发资源核验版本，保留 human1000 不参与调试。

固定代码版本为 `0936f2727dd102ad811ed015b7bf6f7d6533f28e`。`chinatravel/data/load_datasets.py` 明确列出 `hard_logic`、`hard_logic_py`、`hard_logic_nl` 为 oracle 字段。默认 Hugging Face 加载路径会去除它们；本地加载路径的条件还依赖 args 是否含相应属性。自己的适配器应显式设置 `oracle_translation=False`，并在模型入口再次以白名单检查，而不是依赖默认对象形态。

`chinatravel/evaluation/hard_constraint.py` 的 v2 评价执行 gold `hard_logic_py` 检查预测行程，并分别累计约束 micro、任务 macro、结合环境通过条件的结果。后续应以官方完整入口核对最终 all-pass，不得拿其中一个有利分项替代总成功率。官方仓库还持续修订实体、时间与无效计划评价；不能把新评分器结果直接与旧论文表格相减。

官方 README 的 `--oracle_translation` 会向算法开放标注 DSL，LLM-modulo 的该种用法属于 oracle 条件。正式比较必须区分以下两层。

| 信息层 | 算法可见内容 | 如何报告 |
|---|---|---|
| 自然语言主实验 | query、公开环境、自己产生的中间表示和从自身约束计算的反馈 | 与相同信息条件的基线同场比较 |
| Oracle 诊断 | 上述内容加官方 gold DSL，或来自它的逐约束纠错提示 | 单独作为求解上限诊断，不混入自然语言主表 |

来源为[官方使用说明与代码](https://github.com/LAMDA-NeSy/ChinaTravel/tree/0936f2727dd102ad811ed015b7bf6f7d6533f28e)。本次没有确认完整 sandbox 在本机可运行，没有逐条审完自然语言与 DSL 的语义一致性，不能标为 READY。

## 相关工作改变了什么判断

“LLM 解析加求解器”已不是新贡献。Hao 等的 NAACL 2025 工作使用约束满足求解，还处理不可满足核心与修改建议，论文报告 TravelPlanner 93.9% 成功率。该数字是作者在其协议下的报告，不是我们的复现，也不是跨版本、跨模型的当前排名。因此不能以早期纯语言模型低分作主要对手。[论文](https://aclanthology.org/2025.naacl-long.176/)、[实现](https://github.com/yih301/LLM_Formal_Travel_Planner)。

此外，公开 CORAL 仓库已经主张原始查询解析与局部行程修复，在 TravelPlanner、ChinaTravel 上提供结果。此次只核查公开页面，仓库快照下载失败，未独立验证论文状态或成绩。它足以提示下一版必须查清近邻差异，但不足以证明其结果可靠，更不能据此断言它已实现我们全部候选设计。[公开仓库](https://github.com/ChouYuanjue/coral-travel-planner)。

所以“改名为约束引导修复”仍不能解决原创性问题。潜在研究空间是 **正确执行错误解释时，怎样测出语义错误及其跨场景后果**。这只是值得验证的方向，不是已经认证的新颖性。

## 下一项可验收工程任务

范围限于一个外部任务的可执行证据链，先做 ChinaTravel；若数据/环境无法取得，则明确记录阻碍，使用 TravelPlanner train 完成接口核验，不把两者成绩合并。

1. 固定查询、sandbox、代码和评价器版本，记录实际下载与许可；用独立环境，不升级现有实验虚拟环境。
2. 从允许开发的分区按事先规则选一个小批次用于运行核验，完整列出排除理由。公开数据没有明确开发分区时先制定隔离方案，不能拿全部 human split 反复调试再称未见确认集。
3. 实现 raw-query 输入白名单和独立 gold 评分进程。保存两份实际送入模型/评价器的字段清单，以哨兵标签验证 gold 不进入提示或修复反馈。
4. 先对官方示例输出、空输出、无效实体、时间冲突、部分缺失预测执行原评分器，核对分母和非零失败处理。任意自写 checker 只作诊断，不冒充官方分数。
5. 再运行原文输入下的充分定义解析＋既有规划基线，记录语义、求解、信息检索、格式四类错误。正式模型采集要使用后续冻结的小批次计划，本审计未启动它。
6. 若剩余失败主要来自搜索/检索，停止将其包装为“语言误读复核”；若解析几乎全对，不再为了压低分数制造陷阱。只有发现自然出现、可审核且与候选干预对应的错误，才设计新方法确认实验。

验收交付应包括版本清单、字段映射、离线评分日志、缺失/无效预测测试、逐例错误表及是否值得立题的判断。此阶段不以模型次数和并发作为进展主指标。

## 证据存档与限制

`sources/*/metadata.json` 保存八个仓库的固定 commit 和树；`sources/` 保存选择性源码，不是完整可运行克隆。初始抓取缺失 TravelPlanner 的 `tools/planner/env.py`、`utils/query_element_selection.py`，CORAL 后续抓取失败。不能以文件数量宣称已完成完整复现。

三份独立评审只看到冻结的六仓库包。ChinaTravel、正式求解器近邻工作和 CORAL 是主审随后补查，未反馈给评审，也不冒称这些新增判断属于评审共识。此次是定向任务审计，并非穷尽文献的新颖性认证。
