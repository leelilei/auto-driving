# 9-AutoDriving (DARC-Route)

> **2026-09-08 最新实测**：阶段三入口已准备；新鲜 Pilot 遭遇 HTTP 502/TLS 连接错误，尚未完成，主实验未启动。见 [阶段二至三执行计划](docs/experiments/stage3_20260908/STAGE3_EXECUTION_PLAN.md)。论文写作 CLOSED。

> **项目原则：实验完整落地并经独立验收、研究负责人认可后，才开始论文写作。当前写作门禁 CLOSED。** 见 [实验先行原则](docs/project/EXPERIMENT_FIRST_POLICY.md) 与 [第二轮审阅](docs/experiments/CODEX_REMEDIATION_REVIEW_20260907.md)。

> 一句话研究问题：**在自然语言解析结果存在分歧时，利用其对路线规划的影响，能否比仅看语义分歧或随机抽样，更有效地分配有限的 LLM 复核预算？**

- **论文工作题目**：DARC-Route: Decision-Aware Selective Verification for Language-Based POI Route Planning
- **中文题目**：DARC-Route：面向自然语言 POI 路线规划的决策感知选择性复核
- **目标会议**：CCEAI 2027（EI Compendex 检索会议）
- **项目定位**：实证研究（Empirical Research），离线受控 POI 行程规划与 LLM 选择性复核调度

---

## 当前状态

当前阶段：**Phase 1 — 基础环境与 20 条原句试跑已完成；正式等义 Pilot 待审核** ｜ 更新：**2026-09-06**

本次 25 项测试通过；20 条原句首轮 19 条跑通，1 条 API 失败单独补测后成功。B0/B6 均未观察到任务净纠错，不能判定 Gate A 通过。详见 [环境与首轮报告](docs/experiments/readiness_20260906.md)。

详见 [docs/guides/todolist.md](docs/guides/todolist.md) 与 [docs/guides/project.yaml](docs/guides/project.yaml)。

---

## 工作准则 (Working Principles)

1. **坚持决策感知驱动**：规划结果用于复核门控调度（决定是否花钱），复核器仅读原句与分歧（语言判定用户意图），绝不凭无代价的语言一致性假定任务正确。
2. **严格受控与先小后大**：采用小规模固定合成 POI 图（10 个 POI，枚举 6,331 条路线）与纯 Python 精确后端，不盲目依赖重型黑盒求解器；优先通过 20 组 Pilot（Gate A）检验复核器净纠错能力。
3. **真实成本与防止幸存者偏差**：所有 LLM 调用均记录真实 Token、端到端延迟及规划耗时，失败/不可行案例严格计入统计分母，绝不暗中剔除错误样本。

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
│   │   ├── proposal.md            # [L1] 当前研究方案（DARC-Route v4）
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
