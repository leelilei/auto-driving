# 核心文献索引与扩展论证 (Reference Sources & Extension Framework)

> 更新时间：2026-09-06  
> 本地 PDF 资产：44 篇已完整归档至 `assets/papers/pdf/`，元数据见 [`assets/papers/metadata/reference-report.md`](../../assets/papers/metadata/reference-report.md)。

---

## 1. 核心文献三维分类与本地已归档资产

本项目将文献资产按照 DARC-Route 的方法论支柱划分为三大主题库：

### 维度一：路线规划、偏好建模与旅行规划 (`01_route_preference`)
聚焦于“自然语言指令 → 结构化偏好/意图 → 求解器决策”的直接前序研究：
- **[001] LLMAP** (EMNLP Findings 2025): 自然语言多目标路线规划基石，HIPP 数据集来源。`assets/papers/pdf/01_route_preference/001_LLMAP.pdf`
- **[002] RouteLLM (Constraint-Aware)** (arXiv 2025): 层次化 Agent 路线推荐与最终验证。`assets/papers/pdf/01_route_preference/002_RouteLLM.pdf`
- **[003] PathGPT** (arXiv 2025): 基于大模型的个性化路线生成。`assets/papers/pdf/01_route_preference/003_PathGPT.pdf`
- **[004] MAPLE** (AAAI 2025): LLM 引导的主动偏好学习。`assets/papers/pdf/01_route_preference/004_MAPLE.pdf`
- **[005] Personal Travel Solver (PTS)** (ACL 2025): 偏好驱动的 LLM-求解器旅行规划。`assets/papers/pdf/01_route_preference/005_PTS.pdf`
- **[006] TravelPlanner** (ICML 2024): 语言 Agent 真实世界旅行规划 Benchmark。`assets/papers/pdf/01_route_preference/006_TravelPlanner.pdf`
- **[007] Personal LLM Agents** (EMNLP Industry 2024): 定制化旅行规划工业级实证。`assets/papers/pdf/01_route_preference/007_TravelPlanner.pdf`
- **[008] TravelAgent** (arXiv 2024): 个性化旅行规划 Agent 框架。`assets/papers/pdf/01_route_preference/008_TravelAgent.pdf`
- **[009] Formal Planning** (NAACL 2025): 结合形式化验证工具严谨求解规划。`assets/papers/pdf/01_route_preference/009_Formal_Travel_Planner.pdf`
- **[010] LLMFP** (ICLR 2025): 基于形式化编程的通用零样本规划。`assets/papers/pdf/01_route_preference/010_LLMFP.pdf`
- **[011] COMPASS** (Apple / arXiv 2025): 多轮工具规划与偏好优化 Benchmark。`assets/papers/pdf/01_route_preference/011_COMPASS.pdf`
- **[012] LAPPI** (IEEE Access 2026): 交互式偏好问题实例化与优化。`assets/papers/pdf/01_route_preference/012_LAPPI.pdf`
- **[013] APRICOT** (CoRL 2024 / PMLR 2025): 约束感知的主动偏好任务规划。`assets/papers/pdf/01_route_preference/013_APRICOT.pdf`
- **[019] Autoformulation** (ICML 2025): 使用 LLM 自动建立数学优化模型。`assets/papers/pdf/01_route_preference/019_Autoformulation.pdf`
- **[020] QuestBench** (NeurIPS 2025): LLM 主动提问获取偏好信息评测。`assets/papers/pdf/01_route_preference/020_QuestBench.pdf`
- **[025] Agentic Day-to-Day Route Choices** (TR-Part C 2025): 交通路线决策中 Agent 的动态演化。`assets/papers/pdf/01_route_preference/025_R3_Paper_25.pdf`
- **[027] Reward Surface Approximation** (IEEE CASE 2016): 偏好驱动的正交勒让德路线规划。`assets/papers/pdf/01_route_preference/027_R3_Paper_27.pdf`
- **[107] TransitLM** (arXiv 2025): 公共交通路线规划语言基准。`assets/papers/pdf/01_route_preference/107_TransitLM.pdf`
- **[114] CityBench** (NeurIPS 2024): 城市级 LLM 规划与移动评测基准，确立 POI 规划在空间计算中的核心学术地位。`assets/papers/pdf/01_route_preference/114_CityBench_Jin.pdf`

### 维度二：语言等义扰动、鲁棒性与下游决策一致性 (`02_linguistic_robustness`)
评测语言表述微调是否引发解析崩溃或决策漂移：
- **[014] Intent2Drive** (arXiv 2026): 自动驾驶中的人类意图理解。`assets/papers/pdf/02_linguistic_robustness/014_Intent2Drive.pdf`
- **[015] WASSA Paraphrase** (WASSA 2026): 测量 LLM 对改写观点提示词的敏感性。`assets/papers/pdf/02_linguistic_robustness/015_WASSA_Paraphrase.pdf`
- **[016] LAP Robustness** (EMNLP 2025): 同质提问不同措辞下的潜在对抗扰动分析。`assets/papers/pdf/02_linguistic_robustness/016_LAP_Robustness.pdf`
- **[017] Judge Robustness** (ACL Findings 2026): 非对抗性提示变化对 LLM 评估器的鲁棒性影响。`assets/papers/pdf/02_linguistic_robustness/017_ACL_Judge_Robustness.pdf`
- **[018] LIBERO-Para** (arXiv 2026): VLA 具身模型在改写指令下的动作鲁棒性。`assets/papers/pdf/02_linguistic_robustness/018_LIBERO-Para.pdf`
- **[021] ICR-Drive** (CVPRW 2026): 语言驱动端到端自动驾驶的反事实鲁棒性（核心对照）。`assets/papers/pdf/02_linguistic_robustness/021_R3_Paper_21.pdf`
- **[022] Moral Beliefs Encoded in LLMs** (NeurIPS 2023): 等义问题表述引发的模型信念漂移。`assets/papers/pdf/02_linguistic_robustness/022_R3_Paper_22.pdf`
- **[023] Same Question, Different Answers** (arXiv 2026): 超越准确率的 LLM 可靠性评测。`assets/papers/pdf/02_linguistic_robustness/023_R3_Paper_23.pdf`
- **[024] Position Bias in Reranking** (arXiv 2026): 列表重排中的偏好一致性缺陷。`assets/papers/pdf/02_linguistic_robustness/024_R3_Paper_24.pdf`
- **[028] NL Path Planning Constraints** (arXiv 2026): 自然语言指令下的约束感知路径规划。`assets/papers/pdf/02_linguistic_robustness/028_R3_Paper_28.pdf`
- **[029] LEADE** (arXiv 2024): 视频多模态极限安全场景生成。`assets/papers/pdf/02_linguistic_robustness/029_R3_Paper_29.pdf`
- **[030] Calibration Under Variation** (arXiv 2026): 语言变体下的置信度校准失效分析。`assets/papers/pdf/02_linguistic_robustness/030_R3_Paper_30.pdf`
- **[115] PromptBench** (IEEE T-AI 2023): 提示词自然变体（Natural Perturbation）鲁棒性基准，为 HIPP-Robust 构建协议提供权威分类依据。`assets/papers/pdf/02_linguistic_robustness/115_PromptBench_Zhu.pdf`

### 维度三：选择性复核、决策优化 (SPO) 与成本调度 (`03_verification_and_spo`)
**【本次重点扩展的理论与方法支柱】**，直接支撑 DARC-Route 的核心创新：
- **[101] Smart “Predict, then Optimize” (SPO)** (*Management Science* 2022):
  - **定位**：理论基石。证明了参数预测误差（Prediction Loss）不等于最终决策后悔（Regret / Decision Loss）。为本项目主张“仅看参数分歧会造成资源浪费，必须结合下游规划效用”提供严密的运筹学与 ML 理论依据。`assets/papers/pdf/03_verification_and_spo/101_SPO_Elmachtoub.pdf`
- **[102] LLMs Cannot Self-Correct Reasoning Yet** (ICLR 2024):
  - **定位**：机理依据。揭示了无外部反馈或缺乏决策引导的盲目自纠错（Blind Self-Correction）往往改坏原有正确答案。为本方案设计“严格保护结构、严控复核触发、不盲目多轮自循环”提供强有力支撑。`assets/papers/pdf/03_verification_and_spo/102_SelfCorrection_Huang.pdf`
- **[103] Self-Consistency in CoT** (ICLR 2023):
  - **定位**：对比基线 B1。通过多次采样（3 次）与 Medoid 投票提升鲁棒性。本项目用其实证证明：决策门控复核在相同或更低 Token 预算下，能够比盲目 3 次采样的自一致性更高效。`assets/papers/pdf/03_verification_and_spo/103_SelfConsistency_Wang.pdf`
- **[104] FrugalGPT** (NeurIPS 2023):
  - **定位**：成本调度架构。首创 LLM 级联（Cascading）与有限预算下性能-成本 Pareto 边界分析。支撑本方案在 Table 1 和图表中分析 Token 节省量与 TSR 质量权衡。`assets/papers/pdf/03_verification_and_spo/104_FrugalGPT_Chen.pdf`
- **[105] RouteLLM (Model Routing)** (LMSYS / arXiv 2024):
  - **定位**：概念澄清与路由对照。澄清与路线推荐 RouteLLM 的概念重名，并引入其在强弱模型调度中的阈值判定机制。`assets/papers/pdf/03_verification_and_spo/105_RouteLLM_Ong.pdf`
- **[106] Decision-Focused Learning Survey** (IJCAI 2023 Survey):
  - **定位**：领域全景。系统梳理端到端将求解器嵌入学习环路的决策导向学习前沿，巩固本文在“优化环路反馈”层面的学术深度。`assets/papers/pdf/03_verification_and_spo/106_DFL_Survey_Mandi.pdf`
- **[108] CRITIC: Tool-Interactive Critiquing** (ICLR 2024):
  - **定位**：工具反馈复核。论证必须结合外部环境/求解器的客观结果作为反馈才能真正纠错，支撑路线求解器作为判定证据的立论。`assets/papers/pdf/03_verification_and_spo/108_CRITIC_Gou.pdf`
- **[109] Self-Refine** (NeurIPS 2023):
  - **定位**：对比参照。多轮无外部指导自迭代的代表作，正文中用于对比本方案严格最多复核 1 次的成本控制优势。`assets/papers/pdf/03_verification_and_spo/109_SelfRefine_Madaan.pdf`
- **[110] CriticBench** (Findings of ACL 2024):
  - **定位**：评判模型基准。LLM 作为 Critic 评判者的权威基准，支撑对复核器纠错/改坏能力边界的分析。`assets/papers/pdf/03_verification_and_spo/110_CriticBench_Lan.pdf`
- **[111] Language Model Cascades** (arXiv 2022):
  - **定位**：级联理论。建立语言模型级联与条件调度的理论框架，为双路 A/B 低成本生成到高成本复核提供理论基石。`assets/papers/pdf/03_verification_and_spo/111_LMCascades_Dohan.pdf`
- **[112] Let’s Verify Step by Step** (ICLR 2024):
  - **定位**：分层验证。过程监督与步骤验证代表作，支撑硬约束先验检查与路线效用后验评估的分层门控设计。`assets/papers/pdf/03_verification_and_spo/112_VerifyStepByStep_OpenAI.pdf`
- **[113] Combinatorial Decision-Focused Learning** (AAAI 2019):
  - **定位**：离散图决策优化。将预测与离散图组合优化融为一体的经典之作，直接证明下游路线解变动对误差评估的决定性作用。`assets/papers/pdf/03_verification_and_spo/113_CombinatorialDFL_Wilder.pdf`

---

## 2. 论文写作与审稿防御中的文献引用策略

在撰写 CCEAI 2027 手稿时，应采用如下策略引用本批文献，消除潜在审稿质疑：

1. **防御“为什么不做端到端自动驾驶/真实大图导航？”**
   * **策略**：引用 **LLMAP [001]**、**TravelPlanner [006]** 与 **CityBench [114]**，确立离线 POI 多目标规划（POI Itinerary Planning）是一类成熟、独立且有重要商业价值的 NLP-Planning 交叉任务；
   * 引用 **ICR-Drive [021]**，指出端到端 VLA 驾驶模型黑盒且不可解耦，而解耦框架（LLM 解析 + 确定性求解器）能明确隔离语言意图误差与空间图搜索。
2. **防御“为什么不始终调用复核器（Always Review）或进行多轮反思？”**
   * **策略**：引用 **FrugalGPT [104]** 与 **LM Cascades [111]** 强调现实部署中 API Token 与延迟预算约束；
   * 引用 **Self-Correction [102]**、**CRITIC [108]** 与 **Self-Refine [109]**，指出缺乏客观环境决策反馈的多轮盲目自反思不仅增加成本，还会频繁出现负向纠错（改坏正确答案）。
3. **防御“决策感知门控（$\Delta_U > \tau$）相比单纯文本差异（$|w_A - w_B| > \tau_{sem}$）好在哪里？”**
   * **策略**：正面引用 **SPO [101]**、**Wilder et al. [113]** 与 **DFL Survey [106]**。证明在组合优化图中，大量数值权重扰动并不会翻转可行域和最优路线；只有当权重差异足以引发下游规划效用剧烈震荡时，复核才有真实收益。
