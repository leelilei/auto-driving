# DARC-Route

**Decision-Contrastive Verification for Language-Based POI Route Planning**<br>
**面向自然语言 POI 路线规划的决策对比证据复核**

项目目录：`9-AutoDriving` ｜ 研究类型：离线受控 POI 路线规划实证研究

> **2026-09-09 实操入口**：[v5.1实验指导书](docs/experiments/v5_1/EXPERIMENT_GUIDE.md) · [交给agy的第一批任务](docs/experiments/v5_1/AGY_HANDOFF.md) · [Codex独立验收清单](docs/experiments/v5_1/CODEX_ACCEPTANCE_CHECKLIST.md)。先实施S0/S1，当前未启动v5采集。

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

当前阶段：**v5 方案评审与实现准备**。旧代码、运行记录保留，但不能视为 v5 实验已完成。下一步按 proposal 审计未暴露数据、实现对比报告与配对图，再从 8 组开发诊断开始。旧任务清单与实验指导书的主体仍描述 v4，须完成协议迁移后执行。

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
