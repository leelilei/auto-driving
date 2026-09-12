# DARC-Route

> **2026-09-12 实验收尾完成（当前入口）**：[Codex 收尾结果与下一步](docs/experiments/v41_codex_audit_20260912/closeout/RESULTS_AND_NEXT.md)。负责人当前人工审核已通过；v2c 冻结包完成联合评分、固定策略分层和断网重放，12 项新增验收测试通过。停止新增 API，进入证据/主张定稿；论文写作 CLOSED。下方较早状态按历史保留。

> **2026-09-12 当前唯一主线：回到 v4.1 决策感知选择性复核。** [最新 proposal](docs/plans/proposal.md) · [项目整体梳理与收敛决策](docs/plans/PROJECT_RESET_V4_1_20260912.md)。20号前只推进历史证据审计、同预算比较、小型冻结验证；Travel/ontology 不再扩量。论文 CLOSED。以下较早“最新/下一步”为历史状态。

> **2026-09-11 ChinaTravel 最新工程状态**：官方评分适配与 13 项离线测试通过；单例 Haiku/xcode 8 请求后按预算停止，未生成行程，官方全通过率 0/1，两次断网回放一致。下一步修正工具协议与查询/规划预算分配，暂不扩到 60 例。见[执行记录](docs/experiments/chinatravel_setup/CODEX_REMEDIATION_20260911.md)。下方此前状态按时间追溯，论文 CLOSED。

**Decision-Aware Selective Verification for Language-Based POI Route Planning**<br>
**面向自然语言 POI 路线规划的决策感知选择性复核**

项目目录：`9-AutoDriving` ｜ 研究类型：离线受控 POI 路线规划实证研究

> **2026-09-11 当前入口**：[公开任务审计](docs/experiments/task_audit_20260911/TASK_AUDIT.md) · [三份独立评审与综合判断](docs/experiments/task_audit_20260911/REVIEW_SYNTHESIS.md) · [proposal 重新定位](docs/plans/PROPOSAL_REASSESSMENT_20260911.md)。当前事实表方法停止扩量，外部环境尚未验收；优先核验 ChinaTravel 原始自然语言任务及评分器。新的语义忠实性诊断方向仍为候选，论文 CLOSED。
> **2026-09-12 ChinaTravel 收尾**：冻结的 12 例基础模板完成规划与官方评分（搜索 12/12、schema 12/12、all-pass 12/12）；输入隔离与完整分母审计通过。该结果仅是简单切片诊断，停止扩量、不启动阶段 5、不做反馈对照。见[最终审计](docs/experiments/chinatravel_setup/BASELINE12_FINAL_AUDIT_20260912.md)。

**以下为历史执行记录，按时间倒序保留。其中“最新”“尚未采集”等措辞仅指对应交付当时。**

> **睡前长任务已完成：接口2×2诊断120/120，实际124请求**。职责澄清使证据合同失败由3/30降为0/30；澄清后的语言/证据任务成功均29/30，证据token分项多约53%。171测试、120决策离线核验通过。按预定标准停止当前事实复核实现扩量，论文CLOSED。见[醒来后的完整汇总与研究去留](docs/experiments/scene_pilot12/INTERFACE_DIAGNOSTIC_RESULTS_20260911.md)。

> **Fair30真实公平对照已完成**：负责人批准已记录，180逻辑单元、186请求、6次传输恢复，163测试及180决策离线核验通过。Direct / 语言 / 证据最终成功 **56/60、59/60、57/60**；证据原始48/60，12次合同失败回退。当前没有计算事实额外收益，暂停该实现扩量，先复核规则抽取与直接规划指令冲突。见[完整结果](docs/experiments/scene_pilot12/FAIR30_RESULTS_20260911.md)。论文CLOSED。

> **最新：术语定义对照已补齐并独立核验**。Direct / 原语言复核 / 计算证据 / 术语定义的最终任务成功为 **42/60、42/60、48/60、60/60**；术语组原始成功57/60，3次格式失败回退。此次补39请求、0传输失败，累计111请求含51次历史失败。简单术语说明已超过证据组，当前不支持计算证据的独特收益。158项测试通过，人审PENDING，论文CLOSED。见[完整结果与下一步建议](docs/experiments/scene_pilot12/GLOSSARY60_RESULTS_20260911.md)。

> **Scene-Rule30的180单元实验已完成**：Direct/语言复核/证据复核任务成功42/60、42/60、48/60；证据组净纠正6次、改坏0次，含3次格式失败回退。并发16持续负载出现TLS断连，降为8后完成补采；实际200次实验请求，另56次探针。149项测试及180决策独立离线核验通过。见[完整结果、并发记录与复核命令](docs/experiments/scene_pilot12/SCENE_RULE30_RESULTS_20260910.md)。开发证据，人审仍PENDING，论文未启动。下方“尚未采集”为此前交付状态。

> **最新补充：Scene-Rule30候选集已落盘**。18个目标区分案例＋12个边界/保持关系对照；主集36/36错误目标替换会改变决策，全项目138项测试通过。人审PENDING，本轮补充未调用API，后续计划180个开发单元，尚未采集。见[补充设计与逐例审阅入口](docs/experiments/scene_pilot12/SCENE_RULE30_SUPPLEMENT.md)。

> **最新实测：Haiku / xcode 已完成72次新合同开发采集**。Direct/语言复核/证据复核的任务成功为24/24、22/24、24/24，规则正确为12/24、14/24、22/24（证据组含1次失败回退）。独立离线核验通过，尚未证明相对Direct的任务收益，人审仍PENDING。见[完整结果与去留判断](docs/experiments/scene_pilot12/HAIKU_SCENE12_RESULTS_20260910.md)。下方“API调用0”为此前工程交付时的历史状态。

> **2026-09-10 当前入口**：[研究问题调整说明](docs/plans/SCENE_GROUNDING_REASSESSMENT_20260910.md) · [Scene-Pilot12实验设计与交接](docs/experiments/scene_pilot12/EXPERIMENT_DESIGN.md) · [12例待审表](docs/experiments/scene_pilot12/CASE_REVIEW.md)。旧反馈机制的独特收益尚未确证；新候选方向已完成DSL/三方法采集链路、112项测试及72单元断网模拟；真实人工审核PENDING，真实API调用0。见[工程交接与运行命令](docs/experiments/scene_pilot12/IMPLEMENTATION_STATUS.md)。

> **2026-09-09 历史实操入口**：[v5.1实验指导书](docs/experiments/v5_1/EXPERIMENT_GUIDE.md) · [agy任务单](docs/experiments/v5_1/AGY_HANDOFF.md) · [Codex验收清单](docs/experiments/v5_1/CODEX_ACCEPTANCE_CHECKLIST.md)。该阶段后续已进行开发采集与机制消融，最新状态见上方入口。

> **2026-09-08 研究方案更新**：[Proposal v5.1](docs/plans/proposal.md) 已落盘，主线调整为固定一次复核下的决策对比证据。新增方法与 HIPP-DC 尚待实现；旧阶段三暂停扩量。历史网络实测见 [执行记录](docs/experiments/stage3_20260908/STAGE3_EXECUTION_PLAN.md)，不代表当前连通性。

> **项目原则：实验完整落地并经独立验收、研究负责人认可后，才开始论文写作。当前写作门禁 CLOSED。** 见 [实验先行原则](docs/project/EXPERIMENT_FIRST_POLICY.md)。

> 一句话研究问题：**在相同的一次复核机会下，呈现不同语言解释的规划后果，能否比仅指出字段差异更好地纠正误读，并避免改坏合理偏好？**

- **英文题目**：DARC-Route: Decision-Contrastive Verification for Language-Based POI Route Planning
- **中文题目**：DARC-Route：面向自然语言 POI 路线规划的决策对比证据复核
- **目标**：一篇 EI 会议论文；CCEAI 2027 为候选，投稿与检索信息另行核验
- **基准**：公开 HIPP 语言数据＋待建设的 HIPP-DC 配对图与反馈干预评测
- **项目定位**：离线受控 POI 规划的实证研究；哈希仅用于文件完整性，主方法不使用选择性门控

---

## 当前状态

当前阶段：**接口诊断完成，当前计算事实复核实现停止扩量**。四条件新采120单元，职责澄清后合同失败减少，但语言与证据均29/30任务成功，未建立额外收益。下一步先重新审计研究问题、外部任务与强基线，再决定新proposal；不是继续改这批提示。论文CLOSED。

---

## 工作准则 (Working Principles)

1. **检验反馈信息的增量**：固定复核机会，比较字段差异、约束反馈与决策对比；最终修改必须依据原句。
2. **严格受控与先小后大**：复用精确小图后端，先验证报告正确性与开发集净纠正，不直接扩量历史测试。
3. **保留失败与真实成本**：记录所有调用、token、耗时、错误及版本；不把调用次数相同写成成本相同。

---

## 目录结构导航

本项目遵循 [`0-Tools/research-standard/RESEARCH-PROJECT-STANDARD.md`](../0-Tools/research-standard/RESEARCH-PROJECT-STANDARD.md) 规范：

```text
9-AutoDriving/
├── README.md                      # [L0] 项目主页与当前状态入口
├── docs/
│   ├── guides/
│   │   ├── todolist.md            # [L0] 任务清单（唯一真相源）
│   │   └── project.yaml           # [L1/L2] 阶段流图、里程碑与论文结构统一视图
│   ├── plans/
│   │   ├── proposal.md            # [L1] 当前研究方案（DARC-Route v5）
│   │   └── archive/               # 方案历史版本（v1, v3, v4快照）
│   ├── project/
│   │   ├── reference_sources.md   # [L2] 核心文献索引与定位
│   │   ├── decisions.md           # [L3] 关键架构与方法决策日志
│   │   └── reference_screening_matrix_v3.xlsx # 文献筛选矩阵
│   ├── background/                # 理论背景与前期主题文档
│   ├── experiments/               # 实验设计、记录与阶段报告
│   └── reviews/                   # 评审意见与批判性审查（Review v3 等）
├── 9-AutoDriving-core/            # [L3] 实证研究核心代码包
│   ├── src/                       # 解析器、求解器、门控及评估核心模块
│   ├── scripts/                   # 批处理运行脚本与 Pilot 测试脚本
│   ├── configs/                   # 场景生成、模型调用与网格阈值配置
│   ├── data/                      # 离线缓存、HIPP-Robust 标注数据（大文件走 .gitignore）
│   ├── results/                   # 实验输出、指标汇总与配对检验结果
│   └── tests/                     # 单元测试与求解正确性校验
├── paper/                         # [L3] 论文手稿与正文图表（面向 CCEAI 2027）
└── assets/papers/                 # 文献资产（PDF、提取全文、元数据报告与精读笔记）
```

## 实验实施与验收入口

- [完整实验指导书](docs/experiments/EXPERIMENT_GUIDE.md)：数据、图、方法、指标、预算、执行阶段与交付要求。
- [agy CLI 执行指令](docs/experiments/AGY_HANDOFF.md)：可直接复制的交接任务。
- [验收清单](docs/experiments/ACCEPTANCE_CHECKLIST.md)：实现与实验完成后，由 Codex 独立复查。
