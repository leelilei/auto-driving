# 证据表
| 主张 | 来源 | 强度/状态 | 使用位置 | 风险 |
|---|---|---|---|---|
| LLMAP使用LLM解析与MSGS，提供HIPP | https://arxiv.org/html/2509.12273v1 §B.1 | evidence-backed | 背景/benchmark | 不声称复现其真实地图结果 |
| RouteLLM已有全局约束验证和替代路线解释 | https://arxiv.org/html/2510.06078v1 §3.2 | evidence-backed | 相关工作 | 不将路线比较泛称首创 |
| 预测误差与决策损失区别已有SPO | https://arxiv.org/abs/1710.08005 | evidence-backed | 理论动机 | 不声称新决策理论 |
| 外部工具反馈可支持修正 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/fef126561bbf9d4467dbb8d27334b8fe-Abstract-Conference.html | evidence-backed | 方法边界 | 不保证本任务有效 |
| 无外部反馈自修正可能失效 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html | evidence-backed | 动机 | 不泛化所有模型 |
| 条件验证与符号反馈已有工作 | https://aclanthology.org/2024.emnlp-main.714/ ; https://arxiv.org/abs/2606.27757 | evidence-backed | 竞争方法 | 不能宣称新增核验范式 |
| 显式候选决策对比能改善原句意图复核 | 尚无v5实验 | hypothesis | 核心方法 | 决策信息可能诱导改写偏好 |
| 同意图跨图配对可以隔离环境影响 | 本项目实验设计 | plausible-inference | 机制实验 | 控制样本不可当自然频率 |
| v5优于v4或更省token | 无证据 | unsupported/禁用 | 无 | 固定3调用不承诺节省 |
| 候选意图交叉规划＋字段替换后果＋一次语义复核具有区别于近邻方法的原创增量 | 尚待针对性近邻检索 | unverified | 新颖性边界 | 当前定向检索不足以证明原创 |

| HIPP已有四项解析指标与公开成绩，非本项目TSR/regret榜单 | LLMAP Table 2、Appendix A.3 https://arxiv.org/html/2509.12273v1 | evidence-backed | §9.1–9.2 | 新图/新标签/新模型不可直接计算文献提升 |
| RouteLLM表1为另一数据设置，Preference F1不等于HIPP相似度 | https://arxiv.org/html/2510.06078v1 | evidence-backed | §9.2 | 不混表排名 |
| LLMAP发表于Findings EMNLP 2025 | https://aclanthology.org/2025.findings-emnlp.416/ | evidence-backed | 文献元数据 | 本次历史数值来源仍固定arXiv v1 |
| 本地HIPP包含原指令和24份历史模型解析字段 | data/raw/HIPP.json 顶层键只读核验 | local evidence | §9.3 | 历史缓存不当新鲜调用或等义改写预测 |
| 已达到SOTA或已优于现有方法 | 尚无v5有效实验 | unsupported | 禁止成果表述 | 扩展基准第一名不等于公认SOTA |
