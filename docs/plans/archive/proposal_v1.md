# Research Proposal v1
## Robustness and Error Propagation in Implicit Route-Preference Grounding

**中文暂定题目：** 隐式路线偏好理解中的语言鲁棒性与误差传播研究  
**英文暂定题目：** *Robustness and Error Propagation in Implicit Route-Preference Grounding*  
**项目代号：** Implicit2Route-Robust  
**版本：** v1  
**状态：** 基于三轮 Reference Screening 后的可执行研究方案

---

## 0. Executive Summary

本项目研究一个比“LLM 能否理解路线偏好”更窄、但更可验证的问题：

> **当用户用不同但语义等价的自然语言表达同一个隐式路线偏好时，LLM 是否能够稳定地得到相同或近似的结构化偏好表示？如果 grounding 发生变化，这种变化又会在什么情况下进一步传播为路线选择变化、硬约束违反或实际效用损失？**

项目不再把以下内容作为核心创新：

- LLM 将自然语言转成结构化路线偏好；
- 将偏好分为 soft preference 与 hard constraint；
- LLM 负责语言理解、确定性 solver 负责路线选择；
- 构建普通的 synthetic route-preference benchmark；
- 泛化地研究“paraphrase 会不会影响 LLM / driving decision”。

这些方向已经分别被 LLMAP、RouteLLM、Personal Travel Solver、LAPPI、Formal Travel Planner、ICR-Drive 等工作明显覆盖。

本项目当前真正值得推进的切口是：

\[
\text{Language Variation}
\rightarrow
\text{Preference Representation Drift}
\rightarrow
\text{Constraint Flip}
\rightarrow
\text{Route Flip}
\rightarrow
\text{Downstream Regret}
\]

换言之，本研究不只问：

> “换个说法，模型答案会不会变？”

而是进一步问：

> **语言变化产生的 grounding error 是否会沿着一个可解释的 route-planning pipeline 传播，并最终造成有实际意义的决策错误？**

这构成本文最核心的 scientific question。

---

# 1. Motivation

现有导航系统通常要求用户显式指定：

- fastest route；
- shortest route；
- avoid toll；
- avoid highway；
- avoid congestion。

但真实用户常常不会直接使用这种机器友好的表达，而更可能说：

> “我已经迟到了。”

> “高速让我有点紧张，慢一点没关系。”

> “今天不想再多花路费了。”

> “爸妈在车里，我想开得稳一点。”

这些表达包含明确的路线决策信息，但偏好是**隐式的、语用性的、上下文相关的**。

近年来，LLM 已被用于自然语言路线规划、路线偏好解析和约束规划。LLMAP 将 LLM 作为 parser 提取用户偏好并交给图搜索算法；RouteLLM 将自然语言解析为结构化路线约束和 preference-conditioned costs；PTS 和 LAPPI 进一步证明了“自然语言偏好 → 结构化 optimization instance → numerical solver”的可行性。

因此，“LLM 能否理解自然语言路线偏好”本身已经不是足够新的研究问题。

真正仍然值得研究的是其**可靠性**：

> 如果用户表达的是同一个意思，只是 wording 不同，系统是否仍然做出同样的路线决策？

这一问题对 route planning 尤其重要，因为结构化 preference 的微小变化并不总是 harmless。

例如：

\[
w_{\text{highway}}: 0.15 \rightarrow 0.25
\]

可能不会影响最终路线。

但是：

\[
\text{soft avoid highway}
\rightarrow
\text{hard avoid highway}
\]

可能直接改变可行解集合：

\[
R'=\{r_i\in R\mid r_i\models C\}
\]

最终造成完全不同的路线。

因此，**representation instability 与 decision instability 不应被视为同一件事**。

---

# 2. Reference Audit and Novelty Boundary

## 2.1 已经不能安全 claim 的内容

### 2.1.1 Structured Preference Grounding

LLMAP 已明确采用：

\[
\text{Natural Language}
\rightarrow
\text{LLM-as-Parser}
\rightarrow
\text{User Preferences / Constraints}
\rightarrow
\text{Graph Search}
\]

并在 1,000 个 routing prompts 上进行实验。

RouteLLM 同样将自然语言解析成 POI、路线约束和 preference-conditioned routing objectives。

因此：

> **“将自然语言路线需求转换为结构化 preference representation”不能作为本文的主要创新。**

### 2.1.2 Soft Preference / Hard Constraint

RouteLLM 已显式区分不同强度的 preference，并使用离散 preference levels 表达 moderate preference 与 strong requirement。

旅行规划、optimization 与 conversational planning 文献中也已经大量使用 hard constraints / soft preferences。

因此：

> **soft-hard distinction 应作为 benchmark schema 和 stress-test 维度，而不是 contribution。**

### 2.1.3 LLM + Deterministic Solver

LLMAP、Formal Travel Planner、PTS、LAPPI 等工作已经充分证明：

\[
\text{Language}
\rightarrow
\text{Formal / Structured Representation}
\rightarrow
\text{Solver}
\]

这一范式。

本文仍然使用该架构，但用途不同：

> **它是一个 diagnostic instrument，用来隔离 language grounding error 与 route optimization error。**

### 2.1.4 普通 Synthetic Implicit Preference Benchmark

LLMAP 的 HIPP 已经采用 synthetic labels 生成自然语言 routing instructions，并评估 preference estimation。

因此，仅仅构造：

> template-controlled gold preference + LLM-generated implicit utterance

并不足以形成新的 benchmark contribution。

本文 benchmark 必须具有一个更明确的结构：

> **每个 gold intent 对应一组经过控制的 semantic-equivalent utterances，并能够追踪这些 utterances 在 representation 与 decision 两层造成的变化。**

### 2.1.5 泛化的 Paraphrase Robustness

ICR-Drive 已经在自动驾驶中固定相同 CARLA route 与 simulator seed，只改变 instruction language，并构造：

- Paraphrase；
- Ambiguity；
- Noise；
- Misleading。

随后直接评估 closed-loop driving performance。

更早的 LLM robustness 研究也已经系统研究 semantically equivalent question forms 对模型 choice consistency 的影响。

因此：

> **本文不能声称“首次研究语言改写对自动驾驶/导航决策的影响”。**

---

# 3. Remaining Research Gap

根据当前三轮文献筛查，尚未发现与以下完整链路完全同构的工作：

\[
\boxed{
\text{Implicit Route Preference}
\rightarrow
\text{Semantic-Equivalent Utterance Group}
\rightarrow
\text{Structured Preference / Constraint}
\rightarrow
\text{Representation Drift}
\rightarrow
\text{Route Decision Change}
\rightarrow
\text{Downstream Regret}
}
\]

现有工作的缺口主要在于：

1. **LLMAP / RouteLLM**  
   已研究 language → preference → route，但没有系统研究同一语义在 wording 变化下的稳定性和误差传播。

2. **ICR-Drive**  
   已研究 instruction variation → driving behavior，但中间过程基本是 end-to-end black box，无法解释错误究竟来自 preference understanding、constraint interpretation 还是 downstream control。

3. **General paraphrase robustness**  
   已研究 semantic-equivalent input → answer/action consistency，但没有 route-specific preference representation 和 deterministic route optimization。

因此，本项目的 novelty 不应该建立在任何一个单独组件上，而应该建立在：

> **route-preference-specific multi-level robustness diagnosis and error propagation analysis**

之上。

---

# 4. Core Research Questions

## RQ1 — Grounding Robustness

> **For semantically equivalent utterances expressing the same implicit route preference, how stable are the grounded preference vectors and hard/soft constraints?**

对于同一个潜在真实意图 \(z\)，存在：

\[
E(z)=\{x_1,x_2,\dots,x_k\}
\]

其中所有 \(x_i\) 在语义上等价。

定义 grounding function：

\[
G(x_i)=(P_i,C_i)
\]

其中：

- \(P_i\)：soft preference representation；
- \(C_i\)：hard constraints。

研究：

\[
G(x_1)\approx G(x_2)\approx \cdots \approx G(x_k)?
\]

## RQ2 — Error Propagation

> **When grounding varies across equivalent utterances, how often does this variation propagate into route flips, constraint violations, or downstream regret?**

即比较：

\[
r_i=f(G(x_i),R)
\]

其中 \(R\) 为相同的候选路线集合。

核心关注：

\[
G(x_i)\neq G(x_j)
\]

是否一定导致：

\[
r_i\neq r_j
\]

本文预期证明：

\[
\boxed{
\text{Representation Instability}
\neq
\text{Decision Instability}
}
\]

真正重要的是：

\[
\text{Harmful Propagation}
\]

## RQ3 — Boundary Sensitivity

> **Which linguistic phenomena are most likely to produce harmful decision changes?**

重点研究：

- explicit vs implicit；
- semantic paraphrase；
- pragmatic/contextual expression；
- colloquial/noisy expression；
- ambiguity；
- soft wording；
- hard wording；
- conflicting preferences。

其中最值得重点分析的是：

\[
\text{Soft Preference}
\leftrightarrow
\text{Hard Constraint}
\]

的错误切换。

---

# 5. Hypotheses

### H1 — Implicitness Hypothesis

隐式表达比显式表达产生更大的 preference drift：

\[
D_{\text{implicit}}
>
D_{\text{explicit}}
\]

### H2 — Boundary Amplification Hypothesis

soft/hard boundary 附近的 grounding error 会产生不成比例的 downstream effect：

\[
\Delta G_{\text{small}}
\not\Rightarrow
\Delta U_{\text{small}}
\]

特别是 constraint flip 可能改变可行路线集合。

### H3 — Error Propagation Is Nonlinear

Preference Drift 与 Route Flip 不呈简单线性关系。

大量 grounding variation 可能是 harmless 的，而少量 boundary-crossing error 可能造成显著 regret。

### H4 — Structured Grounding Improves Diagnosability

与 Direct LLM Route Selection 相比，结构化 grounding 不一定保证更高 accuracy，但能够显著提高：

- error localization；
- constraint verification；
- decision reproducibility。

### H5 — Simple Consistency-Aware Mitigation Can Reduce Harmful Flips

如果 pilot 结果显示 harmful propagation 足够明显，则加入轻量 consistency-aware verification，预计能够降低：

- Constraint Flip Rate；
- Route Flip Rate；
- Regret。

这一部分作为**可选方法贡献**，而不是 proposal 当前成立的前提。

---

# 6. Problem Formulation

## 6.1 User Intent

设用户真实 latent route preference 为：

\[
z
\]

同一 \(z\) 可以产生多个语义等价表达：

\[
E(z)=\{x_1,\dots,x_k\}
\]

## 6.2 Preference Grounding

LLM parser：

\[
G:x\rightarrow(P,C)
\]

其中：

\[
P=[w_t,w_d,w_c,w_h,w_g]
\]

初版保留五个可控路线维度：

- \(w_t\)：travel time；
- \(w_d\)：distance；
- \(w_c\)：toll/cost；
- \(w_h\)：highway preference；
- \(w_g\)：congestion avoidance。

其中 soft preference 与 hard constraint 分离：

\[
G(x)=(P,C)
\]

## 6.3 Route Candidates

候选路线：

\[
R=\{r_1,r_2,\dots,r_n\}
\]

每条路线包含可计算属性：

\[
F(r)=[t,d,c,h,g]
\]

例如：

```json
{
  "time": 31,
  "distance": 24.5,
  "toll": 0,
  "highway_ratio": 0.10,
  "traffic_level": 0.25
}
```

## 6.4 Constraint Filtering

首先执行硬约束：

\[
R_C=\{r_i\in R\mid r_i\models C\}
\]

## 6.5 Preference-Based Selection

在可行集合中：

\[
r^*
=
\arg\max_{r_i\in R_C}
U(r_i|P)
\]

初版使用透明、确定性的线性 utility：

\[
U(r_i|P)
=
\sum_j w_j f_j(r_i)
\]

所有 route attributes 在计算前统一归一化。

重要的是：

> **LLM 不直接决定最终路线。**

这不是为了 claim 新算法，而是为了确保：

> 当 route selection 发生变化时，我们能够知道变化来自 grounding，而不是来自另一个黑盒 LLM decision。

---

# 7. Benchmark Design

## 7.1 Benchmark Unit：Semantic Intent Group

本文不把单条 utterance 当成最基本样本。

最基本单位应当是：

\[
\mathcal{G}_m=
(z_m,\{x_{m1},...,x_{mk}\},P_m^*,C_m^*)
\]

即：

> 一个 gold latent intent + 一组语义等价表达 + gold structured preference。

这是与 HIPP / RouteLLM 普通 query benchmark 最大的结构性区别。

## 7.2 Core Preference Dimensions

第一版保持五个维度，不建议继续扩大：

1. **Time**
2. **Distance**
3. **Toll / Cost**
4. **Highway**
5. **Traffic / Congestion**

理由：

- 与真实 route decision 有直接关系；
- 可以构造清晰 trade-off；
- 能形成 deterministic gold route；
- 不需要视觉、天气、地图语义等额外系统。

“Scenic / Safety / Comfort”等更抽象属性先不放进主 benchmark，以避免 gold semantics 过于主观。

## 7.3 Intent Composition

建议覆盖三类 latent intents：

### A. Single-Preference

例如：

- minimize time；
- avoid highway；
- avoid toll；
- avoid congestion。

### B. Multi-Preference Trade-off

例如：

> “慢十分钟没事，但不要高速。”

对应：

\[
time=medium,\quad highway=low
\]

### C. Preference + Hard Constraint

例如：

> “其他都无所谓，但绝对不要走收费路。”

对应：

\[
C=\{\text{avoid toll}\}
\]

---

# 8. Language Variation Taxonomy

必须区分两种实验。

## 8.1 Core Invariance Set

这一组中的 utterances **必须保持相同 gold semantics**。

### V1 — Explicit

> Avoid highways.

### V2 — Direct Paraphrase

> Please stay off highways.

### V3 — Implicit

> High-speed roads make me uncomfortable.

### V4 — Pragmatic / Contextual

> My parents are in the car, so I’d prefer a calmer route.

### V5 — Colloquial

> No rush today. Let’s keep it easy.

### V6 — Mild Surface Noise

轻微 typo、口语、省略，但不能改变真实 preference。

这六类构成真正的 **semantic-equivalence robustness benchmark**。

## 8.2 Contrastive Stress Set

以下变化**不是语义等价 paraphrase**，不能混入 consistency denominator。

它们用于研究 decision boundary。

### S1 — Soft vs Hard

> “尽量别走高速。”

vs.

> “绝对不要走高速。”

### S2 — Ambiguity

> “走舒服一点的路。”

gold 可能无法唯一确定。

### S3 — Conflict

> “我已经迟到了，但绝对不要走高速。”

### S4 — Preference Strength

> “最好别收费。”

vs.

> “能省钱就省一点。”

vs.

> “绝对不能有收费。”

这一拆分非常重要。

否则 reviewer 很容易质疑：

> “你把本来语义就不一样的输入也算成 paraphrase inconsistency。”

---

# 9. Dataset Scale — Recommended Initial Version

目标不是盲目追求数据量，而是保证每个 group 具有受控结构。

建议第一版：

- **40 latent intent groups**
- 每组 **6 semantic-equivalent utterances**
- 共：

\[
40\times6=240
\]

条核心自然语言表达。

每组再匹配 **3 个不同 candidate-route scenarios**：

\[
240\times3=720
\]

个 route-decision evaluation instances。

另外增加约：

- 10–20 个 soft/hard contrast groups；
- 10 ambiguity/conflict groups；

作为 stress-test subset。

如果 pilot 结果足够明显，再扩展到 500–1000 utterances，而不是一开始就批量生成大量低质量 paraphrase。

---

# 10. Data Generation and Validation

## 10.1 Gold First

必须先定义：

\[
(P^*,C^*)
\]

再生成语言。

不能：

> 先生成一句自然语言，再让另一个 LLM 猜 gold label。

否则 benchmark ground truth 本身不可验证。

## 10.2 Paraphrase Generation

语言生成模型只负责：

> 将一个固定 latent intent 转写成多种自然表达。

生成模型与主要被测模型尽量不同，降低 same-model artifact。

## 10.3 Semantic Validation

自动生成后需要过滤。

### Automatic Validation

使用第二个独立 LLM 判断：

> 两个 utterances 是否保持相同 route-preference semantics。

### Human Validation Subset

建议对至少一个代表性子集进行人工 semantic-equivalence 标注。

推荐至少双人独立判断部分样本，并记录一致性。

如果现实人力有限：

> 人工验证优先覆盖 implicit / pragmatic / colloquial 类，而不是最简单的 explicit paraphrases。

---

# 11. Metrics

这是本文最值得做深的地方。

## 11.1 Grounding Accuracy

对于离散 preference category：

- Accuracy；
- Macro-F1。

用于回答：

> 模型有没有理解对？

但它不是主要 robustness metric。

## 11.2 Preference Drift

对于同一个 semantic group：

\[
D_P(x_i,x_j)
=
\|P_i-P_j\|_1
\]

或者归一化：

\[
ND_P
=
\frac{1}{d}
\|P_i-P_j\|_1
\]

也可报告 group-level dispersion：

\[
PD(\mathcal G)
=
\frac{1}{k}
\sum_i
\|P_i-\bar P\|
\]

## 11.3 Constraint Flip Rate

最重要指标之一。

对于语义等价表达：

\[
CFR
=
\frac{
\#\text{constraint state changes}
}{
\#\text{equivalent comparisons}
}
\]

重点观察：

- none → soft；
- soft → hard；
- hard → soft；
- hard constraint missing。

其中：

\[
soft\leftrightarrow hard
\]

应单独报告。

## 11.4 Route Flip Rate

\[
RFR
=
\frac{
\#\{(i,j):r_i\neq r_j\}
}{
\#\text{equivalent pairs}
}
\]

它直接回答：

> 换一种说法，路线会不会真的变？

## 11.5 Constraint Violation Rate

即模型 grounding error 是否导致 gold hard constraint 被最终路线违反。

\[
CVR
=
\frac{\#\text{violations}}{\#\text{cases}}
\]

## 11.6 Downstream Regret

这是本文建议的核心指标。

设真实 gold preference 为 \(P^*\)，gold optimal route：

\[
r^*
=
\arg\max_r U(r|P^*)
\]

模型 grounding 后选出的路线：

\[
\hat r
\]

则：

\[
Regret
=
U(r^*|P^*)
-
U(\hat r|P^*)
\]

可进一步归一化为：

\[
NRegret
=
\frac{Regret}
{|U(r^*|P^*)|+\epsilon}
\]

## 11.7 Harmful Propagation Rate

定义：

> grounding representation 发生变化，并最终造成 route flip / constraint violation / significant regret 的比例。

\[
HPR
=
P(
\text{Downstream Harm}
\mid
\text{Grounding Drift}
)
\]

这是串起整篇论文的指标。

---

# 12. Error Propagation Analysis

本文最重要的图不应该只是 Accuracy bar chart。

建议画：

```text
Language Variation
       │
       ▼
Grounding Error?
   │        │
  No       Yes
            │
            ▼
      Constraint Flip?
       │          │
      No         Yes
       │          │
       ▼          ▼
   Route Same   Route Flip
                  │
                  ▼
           Regret / Violation
```

从而得到四类 error：

### Type I — Harmless Representation Drift

\[
P_i\neq P_j
\]

但：

\[
r_i=r_j
\]

### Type II — Benign Route Flip

路线不同，但 gold utility 基本等价：

\[
Regret\approx0
\]

### Type III — Harmful Route Flip

\[
r_i\neq r_j,\quad Regret>0
\]

### Type IV — Constraint-Critical Failure

因为 hard/soft grounding error 导致硬约束被违反。

这类最值得在论文 qualitative examples 中展示。

---

# 13. Baselines

所有 LLM baseline 尽量使用同一个 backbone，避免 reviewer 认为 improvement 来自更强模型。

## B1 — Direct LLM Route Selection

```text
User utterance
+ Route candidates
→ LLM directly chooses route
```

用途：

> 测 end-to-end decision robustness。

## B2 — CoT Direct Selection

```text
Understand user need
→ reason over routes
→ choose route
```

## B3 — Structured Grounding

```text
User
→ Preference JSON
→ deterministic scorer
```

这是最重要的 controlled baseline。

## B4 — Constraint-Aware Structured Grounding

```text
User
→ (Soft Preference, Hard Constraint)
→ Filter
→ Score
```

注意：

> 这不是“ours novelty”，而是 reference-supported baseline architecture。

---

# 14. Optional Mitigation Module

第一阶段不要急着把它包装成方法贡献。

只有 pilot 证明 instability 确实明显后，再加入。

暂定：

## Consistency-Aware Preference Grounding

核心逻辑：

```text
Utterance
   ↓
Structured Grounding
   ↓
Independent Verification / Re-grounding
   ↓
Are P/C consistent?
  ├─ Yes → Route Solver
  └─ No  → Resolve / Abstain / Clarify
```

可以比较三种最简单策略：

### M1 — Canonicalization

先将隐式表达重写成标准路线偏好语言，再解析。

### M2 — Multi-Sample Aggregation

同一 utterance 独立 grounding 多次：

\[
P^{final}=median(P_1,...,P_m)
\]

hard constraint 用多数表决。

### M3 — Consistency-Triggered Clarification

仅当：

- parser disagreement 大；
- soft/hard state 不一致；
- confidence 低；

时才触发澄清。

该模块只能作为轻量 mitigation，不能声称“首次 conversational clarification”。

---

# 15. Experimental Protocol

## 15.1 Models

至少测试：

- 一个强闭源模型；
- 一个高性价比闭源模型；
- 一个主流 open-weight model。

正式实验时冻结具体模型版本。

## 15.2 Prompt Control

主要 robustness 实验：

> **固定 system prompt，只变化 user utterance。**

这一点用于明确区别于 Formal Travel Planner 等 system-prompt paraphrase experiments。

## 15.3 Temperature

主实验使用尽可能 deterministic 的 decoding 设置。

另外抽取一个 subset 做 repeated runs，用于区分：

\[
\text{wording sensitivity}
\]

与：

\[
\text{sampling variance}
\]

## 15.4 Route Candidates

同一个 semantic group 必须使用完全相同的 route candidate set。

因此：

\[
R(x_1)=R(x_2)=...=R(x_k)
\]

否则 route change 无法归因于语言变化。

---

# 16. Synthetic Route Scenario Design

第一版建议不用真实地图 API 作为主实验。

例如：

| Route | Time | Distance | Toll | Highway Ratio | Traffic |
|---|---:|---:|---:|---:|---:|
| A | 24 | 31 | 10 | 0.85 | 0.30 |
| B | 33 | 25 | 0 | 0.10 | 0.20 |
| C | 28 | 27 | 5 | 0.45 | 0.50 |

通过控制 route attributes，可以人为创建：

### Scenario 1 — Stable Region

Preference 有一定 drift，但最优 route 不变。

### Scenario 2 — Decision Boundary

轻微 weight drift 即可能 route flip。

### Scenario 3 — Constraint Boundary

soft / hard 状态变化会直接改变 feasible routes。

这三类 route scenarios 是 error-propagation experiment 的关键。

---

# 17. Real-World Validation

为了降低 reviewer 对 purely synthetic benchmark 的质疑，建议主实验完成后增加一个**小规模 real-world case study**。

优先考虑：

- OpenStreetMap；
- 可复现的固定 OD pairs；
- 多条 candidate routes；
- 可稳定计算的 distance / travel-time estimate / highway ratio。

Real-world case 不需要成为主 benchmark。

其作用仅是验证：

> synthetic benchmark 中观察到的 instability 是否也能在真实道路结构中出现。

不建议第一版直接接复杂的实时 traffic API，以免工程量反客为主。

---

# 18. Main Experiment Matrix

## E1 — Grounding Accuracy

回答：

> 各模型能否正确理解 explicit / implicit preferences？

输出：

| Model | Explicit | Implicit | Pragmatic | Noisy | Overall |
|---|---:|---:|---:|---:|---:|

## E2 — Semantic-Equivalent Robustness

输出：

| Model | Pref. Drift ↓ | Constraint Flip ↓ | Route Flip ↓ |
|---|---:|---:|---:|

## E3 — Error Propagation

输出：

| Model | Grounding Drift Cases | Route Flip | Harmful Flip | Violation | Regret |
|---|---:|---:|---:|---:|---:|

## E4 — Linguistic Factor Analysis

| Variation | Pref Drift | Constraint Flip | Route Flip | Regret |
|---|---:|---:|---:|---:|
| Explicit paraphrase |  |  |  |  |
| Implicit |  |  |  |  |
| Pragmatic |  |  |  |  |
| Noisy |  |  |  |  |
| Soft/Hard boundary |  |  |  |  |

## E5 — Decision Boundary Analysis

控制 route scenario 与 preference margin，研究：

\[
Margin
=
U(r_1)-U(r_2)
\]

是否决定 grounding drift 被放大的概率。

预期：

\[
Margin\downarrow
\Rightarrow
RouteFlip\uparrow
\]

这是非常值得做的一组分析。

## E6 — Mitigation（可选）

| Method | Grounding Acc | Constraint Flip ↓ | Route Flip ↓ | Regret ↓ |
|---|---:|---:|---:|---:|
| Direct |  |  |  |  |
| Structured |  |  |  |  |
| + Canonicalization |  |  |  |  |
| + Consistency Check |  |  |  |  |

---

# 19. Statistical Analysis

建议使用：

- bootstrap 95% confidence intervals；
- paired bootstrap 比较不同方法；
- Spearman correlation：

\[
Preference\ Drift
\leftrightarrow
Regret
\]

- 对不同 language variation 比较 harmful propagation probability。

如果数据规模允许，可以增加简单 logistic regression：

\[
P(RouteFlip)
=
\sigma(
\beta_0
+
\beta_1 Drift
+
\beta_2 Margin
+
\beta_3 ConstraintFlip
)
\]

这样能够回答：

> **什么因素真正决定语言错误会不会传播成路线错误？**

---

# 20. Expected Contributions

当前建议把 contribution 写成以下三点。

## Contribution 1 — Controlled Benchmark

> We construct a controlled benchmark organized around semantic-equivalent groups of implicit route-preference utterances, enabling instance-level robustness evaluation while keeping latent preference semantics and route candidates fixed.

重点不在 synthetic，而在：

> **semantic-equivalent group structure**。

## Contribution 2 — Multi-Level Robustness Evaluation

> We introduce a multi-level evaluation protocol that distinguishes preference representation drift, hard/soft constraint flips, route decision flips, and downstream regret.

这里不建议使用：

> “first metric for semantic consistency”

这种容易被已有 robustness 文献击穿的说法。

## Contribution 3 — Error Propagation Analysis

> We empirically characterize when linguistic instability remains harmless and when it propagates into harmful route decisions, revealing the role of constraint boundaries and route utility margins.

这应当是全文最核心的 contribution。

## Optional Contribution 4 — Lightweight Mitigation

如果实验结果支持：

> We further evaluate a lightweight consistency-aware grounding strategy that reduces harmful propagation without replacing the deterministic route optimizer.

---

# 21. Recommended Novelty Claim

目前推荐的安全表述：

> **We study the robustness of implicit route-preference grounding under semantically equivalent user expressions, with particular focus on how representation-level instability propagates into downstream route decisions.**

以及：

> **Rather than treating robustness as answer consistency alone, we separate preference drift, constraint-state changes, route flips, and downstream regret in a transparent language-to-routing pipeline.**

暂时不建议写：

- first-ever；
- first implicit route preference framework；
- first LLM route preference grounding；
- first paraphrase robustness study for navigation；
- first hard/soft constraint reasoning system。

在最终投稿前再做一次 latest-work sweep，如果仍无直接 precedent，可谨慎使用：

> *To the best of our knowledge...*

---

# 22. Scope Control

## 本文做

- 单轮自然语言；
- utterance-level implicit route preference；
- semantic-equivalent robustness；
- structured preference / hard constraint；
- deterministic route selection；
- synthetic controlled benchmark；
- small real-world validation；
- error propagation。

## 本文暂时不做

- 地图视觉理解；
- VLA control；
- trajectory generation；
- long-horizon autonomous-driving agent；
- multi-modal passenger state；
- 用户长期 memory/profile；
- reinforcement learning；
- 模型训练 / fine-tuning；
- 大规模真实地图 API 系统；
- fully conversational travel planning。

保持这个边界，对 EI 小论文非常重要。

---

# 23. Decision Gates

项目推进时设置三个 gate。

## Gate A — 问题是否真实存在

先跑一个 pilot subset。

如果所有主流模型：

\[
RouteFlip < 2\%
\]

且：

\[
Regret \approx 0
\]

说明 semantic-equivalent paraphrase 可能不足以形成论文问题。

此时应把研究重心转到：

- implicit pragmatic expressions；
- soft/hard boundaries；
- conflicting preferences。

## Gate B — 是否存在 Harmful Propagation

如果：

\[
PreferenceDrift>0
\]

但：

\[
RouteFlip\approx0
\]

则说明 representation instability 本身不够有意义。

论文必须寻找：

- 更接近 decision boundary 的 route scenarios；
- constraint-critical cases。

不能只因为 JSON 数值不一致就写 robustness paper。

## Gate C — 是否需要 Method Contribution

只有当 benchmark 明确暴露 instability 后，再决定是否做 consistency-aware mitigation。

如果一个非常简单的 canonicalization 就能解决问题：

> 可以把它作为 baseline/mitigation，而不要强行包装成复杂新 framework。

---

# 24. Implementation Plan

## Phase 0 — Freeze Problem

完成：

- preference schema；
- gold semantics；
- language variation taxonomy；
- route scorer；
- metrics definition。

这是当前下一步。

## Phase 1 — Pilot Benchmark

实现：

```text
40 latent intents
→ semantic-equivalent variants
→ route scenarios
→ 2–3 LLM baselines
```

首先验证 Route Flip / Regret 是否真实存在。

## Phase 2 — Full Benchmark

扩展：

- 更多 intent composition；
- language variations；
- route boundaries；
- multiple LLMs。

## Phase 3 — Error Analysis

重点产生：

- error propagation graph；
- constraint-flip cases；
- decision-boundary analysis；
- qualitative examples。

## Phase 4 — Optional Mitigation

只有 Phase 3 证明问题足够明显后再做。

## Phase 5 — Real-World Case Study

使用小规模 OSM route candidates 验证 external validity。

---

# 25. Suggested Repository Structure

```text
ImplicitRouteRobust/
│
├── data/
│   ├── intents/
│   │   ├── latent_intents.json
│   │   └── contrastive_intents.json
│   ├── utterances/
│   │   ├── equivalent_groups.json
│   │   └── stress_groups.json
│   ├── routes/
│   │   ├── synthetic_routes.json
│   │   └── osm_routes.json
│   └── benchmark.json
│
├── prompts/
│   ├── direct.md
│   ├── cot.md
│   ├── structured.md
│   └── verify.md
│
├── src/
│   ├── schemas.py
│   ├── llm_client.py
│   ├── grounding.py
│   ├── scorer.py
│   ├── route_generator.py
│   ├── validators.py
│   └── metrics.py
│
├── experiments/
│   ├── run_grounding.py
│   ├── run_route_selection.py
│   ├── run_robustness.py
│   ├── run_boundary_analysis.py
│   └── run_mitigation.py
│
├── analysis/
│   ├── error_propagation.py
│   ├── statistics.py
│   └── figures.py
│
├── results/
└── README.md
```

---

# 26. Suggested Paper Structure

## 1. Introduction

核心叙事：

1. Natural-language route planning 正在快速发展；
2. existing work 已能把语言 grounding 成 route objectives；
3. 但 deployment 中用户表达高度多样；
4. 现有 robustness 工作大多只看 end-to-end performance；
5. 缺少对 **language grounding error 如何传播为 route decision error** 的系统研究；
6. 本文提出 controlled benchmark + multi-level diagnostic framework。

## 2. Related Work

### 2.1 LLM-Based Route and Travel Planning

- LLMAP
- RouteLLM
- PathGPT
- TravelPlanner
- PTS
- Formal Travel Planner
- LAPPI

### 2.2 Implicit Preference and Human Intent

- PTS
- Intent2Drive
- preference-learning / route-choice literature

### 2.3 Linguistic and Instruction Robustness

- ICR-Drive
- question-form consistency
- paraphrase robustness literature

## 3. Problem Formulation

定义：

\[
x\rightarrow(P,C)\rightarrow r
\]

以及 semantic-equivalent group。

## 4. ImplicitRoute-Robust Benchmark

- preference taxonomy；
- equivalent utterance generation；
- contrastive stress set；
- route scenario construction；
- gold labels；
- validation。

## 5. Evaluation Metrics

- grounding accuracy；
- preference drift；
- constraint flip；
- route flip；
- regret；
- harmful propagation。

## 6. Experiments

### 6.1 Setup
### 6.2 Grounding Robustness
### 6.3 Route Decision Robustness
### 6.4 Error Propagation
### 6.5 Boundary Sensitivity
### 6.6 Mitigation / Ablation
### 6.7 Real-World Case Study

## 7. Discussion

重点讨论：

- representation stability 是否真的重要；
- route margin 的作用；
- hard constraints 为什么危险；
- benchmark synthetic bias；
- human-language ambiguity。

## 8. Conclusion

---

# 27. Current Overall Assessment

基于三轮 reference screening，目前项目判断为：

| 维度 | 判断 |
|---|---|
| 原版 Structured Grounding novelty | 低 |
| Soft/Hard novelty | 低 |
| LLM + Solver novelty | 低 |
| 普通 Synthetic Benchmark novelty | 低 |
| 泛化 Paraphrase Robustness novelty | 中低 |
| Implicit Route Preference 专项 robustness | 中 |
| Preference → Route Error Propagation | **中高，当前最值得推进** |
| 实验可控性 | **高** |
| 工程难度 | **低–中** |
| 算力要求 | **低** |
| EI 小论文可行性 | **较高，前提是 pilot 能观察到 meaningful harmful propagation** |

当前不建议再扩大题目。

最重要的是把论文从：

> **“我们设计了一个更好的 route preference parser。”**

转成：

> **“我们研究 route preference parser 的语言不稳定性什么时候真正造成决策伤害。”**

这是经过当前 reference audit 后更安全、也更有研究价值的 framing。

---

# 28. Key References

1. **Yuan, L., Han, D.-J., Brinton, C. G., & Brunswicker, S. (2025).**  
   *LLMAP: LLM-Assisted Multi-Objective Route Planning with User Preferences.*  
   Findings of EMNLP 2025.  
   https://aclanthology.org/2025.findings-emnlp.416/

2. **Zhe, T., Liu, R., Memar, F., et al. (2025).**  
   *Constraint-Aware Route Recommendation from Natural Language via Hierarchical LLM Agents.*  
   arXiv:2510.06078.  
   https://arxiv.org/abs/2510.06078

3. **Shao, Z., Wu, J., Chen, W., & Wang, X. (2025).**  
   *Personal Travel Solver: A Preference-Driven LLM-Solver System for Travel Planning.*  
   ACL 2025 Long Papers.  
   https://aclanthology.org/2025.acl-long.1339/

4. **Hao, Y., Chen, Y., Zhang, Y., & Fan, C. (2025).**  
   *Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools.*  
   NAACL 2025 Long Papers.  
   https://aclanthology.org/2025.naacl-long.176/

5. **Kuroki, S., Nakagawa, M., Yoshida, S., Koyama, Y., & Kozuno, T. (2026).**  
   *LAPPI: Interactive Optimization With LLM-Assisted Preference-Based Problem Instantiation.*  
   IEEE Access.  
   https://omron-sinicx.github.io/lappi/

6. **Hamid, K., Cui, C., & Liang, N. (2026).**  
   *ICR-Drive: Instruction Counterfactual Robustness for End-to-End Language-Driven Autonomous Driving.*  
   CVPR 2026 Workshops.  
   https://openaccess.thecvf.com/content/CVPR2026W/WDFM-EAI/html/Hamid_ICR-Drive_Instruction_Counterfactual_Robustness_for_End-to-End_Language-Driven_Autonomous_Driving_CVPRW_2026_paper.html

7. **Luo, X., Fan, D., Chen, R., et al. (2026).**  
   *Who Responds When the Driver Is Gone? A Framework for Human Intent Understanding.*  
   arXiv:2607.04670.  
   https://arxiv.org/abs/2607.04670

8. **Marcelyn, S. C., Gao, Y., Zhang, Y., Gao, X., & Chen, G. (2025).**  
   *PathGPT: Leveraging Large Language Models for Personalized Route Generation.*  
   arXiv:2504.05846.  
   https://arxiv.org/abs/2504.05846

9. **Scherrer, N., Shi, C., Feder, A., & Blei, D. M. (2023).**  
   *Evaluating the Moral Beliefs Encoded in LLMs.*  
   NeurIPS 2023.  
   https://proceedings.neurips.cc/paper_files/paper/2023/hash/a2cf225ba392627529efef14dc857e22-Abstract-Conference.html

---

# 29. Immediate Next Research Task

在开始大量写代码之前，下一步应该只完成三件事：

1. **冻结五维 preference schema 与 hard-constraint schema；**
2. **定义 40 个 latent intent groups 及其 gold \(P^*,C^*\)；**
3. **设计三类 route scenario：stable / decision-boundary / constraint-boundary。**

完成这三件事后，就可以做一个小规模 pilot。

Pilot 的目标不是“先跑漂亮结果”，而是验证整个 proposal 最关键的前提：

> **语言等价表达产生的 grounding variation，是否真的会在部分场景中传播成 meaningful route decision error。**

如果答案是 yes，项目正式进入 full experiment。

如果答案是 no，则应尽早 pivot，而不是继续堆 benchmark 和 prompt。
