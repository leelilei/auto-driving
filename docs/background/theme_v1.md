对，这个方向我仍然认为很适合作为你这篇“保毕业 EI 小论文”的切口，而且现在可以继续把它压缩到**Codex 两三天就能搭出完整实验框架**的程度。

关键是不要把它做成“一个路线规划系统”，而是做成一个非常明确的研究问题：

> **隐式自然语言表达经过 LLM 解析后，能否稳定、正确、可验证地映射为路线偏好，并最终选出符合用户真实意图的路线？**

这样论文的重点就在 **Implicit Preference Grounding**，路线规划只是一个非常容易验证的下游载体。

---

# 1. 我建议把整个问题进一步形式化

输入一句用户自然语言：

> “我不太喜欢开高速，晚个十几分钟也没关系。”

我们不让 LLM 直接回答：

> “推荐路线 B。”

而是强制它先转成一个**结构化 Preference Vector**：

```json
{
  "time": 0.3,
  "distance": 0.4,
  "toll": 0.5,
  "highway": 0.1,
  "traffic": 0.6
}
```

这里可以统一规定：

```text
0 = 强烈不偏好
1 = 强烈偏好
```

或者更适合论文表达一点：

[
P=[w_t,w_d,w_c,w_h,w_g]
]

分别表示：

* travel time
* distance
* toll cost
* highway preference
* congestion avoidance

然后地图程序返回若干候选路线：

[
R={r_1,r_2,\dots,r_k}
]

每条路线本身也有结构化属性：

```json
{
  "time": 31,
  "distance": 24.5,
  "toll": 0,
  "highway_ratio": 0.10,
  "traffic_level": 0.25
}
```

最后再通过一个**确定性的 scorer** 做选择：

[
Score(r_i|P)
============

\sum_j w_j f_j(r_i)
]

于是整个论文结构非常干净：

```text
Implicit Natural Language
          ↓
       LLM Parser
          ↓
 Structured Preference Vector
          ↓
    Route Candidates
          ↓
 Deterministic Preference Scorer
          ↓
     Selected Route
```

这里最重要的是：

> **LLM 只负责“理解人”，不负责“决定路线”。**

这是论文很容易讲清楚的第一个卖点。

---

# 2. 但如果只是「LLM → JSON → 打分」，创新还是稍弱

所以我建议加入一个成本非常低，但论文味道明显强很多的模块：

# **Constraint-Aware Preference Grounding**

也就是把用户表达区分成：

### Soft Preference

例如：

> “尽量别走高速。”

对应：

```json
{
  "highway_preference": "low"
}
```

可以权衡。

---

### Hard Constraint

例如：

> “绝对不要走高速。”

对应：

```json
{
  "avoid_highway": true
}
```

候选路线直接过滤。

于是：

[
\text{Natural Language}
\rightarrow
(P,C)
]

其中：

[
P=\text{soft preferences}
]

[
C=\text{hard constraints}
]

路线选择变成：

[
R'={r_i\in R\mid r_i\models C}
]

然后：

[
r^*
===

\arg\max_{r_i\in R'}
Score(r_i|P)
]

这个改变特别划算，因为**代码量几乎没有增加多少，但论文表达一下子规范很多**。

---

# 3. 第二个创新点：鲁棒解析

论文题目里面的 **Robust**，不能只是装饰词。

我们可以专门研究：

> **同一个偏好换不同说法，LLM 是否还能得到稳定的结果？**

例如真实意图都是：

> Avoid highway

但生成：

### Explicit

> Avoid highways.

### Implicit-1

> I don't feel comfortable driving fast.

### Implicit-2

> High-speed roads make me nervous.

### Implicit-3

> I'm not in a hurry. I'd rather take an easier road.

### Implicit-4

> My parents are in the car, so I'd like a calmer drive.

这就是一个很好做的实验。

---

# 4. 所以我现在会把论文定义成两个核心问题

不需要三个、四个创新点。

就两个。

## Innovation 1：Structured Preference Grounding

不是让 LLM 直接 route selection，而是：

> 将隐式自然语言转换成结构化、可解释、可验证的软偏好与硬约束。

即：

[
x\rightarrow(P,C)
]

解决的是：

**LLM 黑盒直接做路线决策难验证的问题。**

---

## Innovation 2：Robustness-Aware Grounding

同一用户意图构造多种：

* explicit expression
* implicit expression
* paraphrase
* noisy expression
* conflicting expression

验证：

[
G(x_1)\approx G(x_2)\approx G(x_3)
]

也就是：

> **语义等价表达是否产生一致的路线偏好。**

解决的是：

**LLM 对 wording 敏感的问题。**

这两个创新对于 EI 小论文，我认为已经够用了。

---

# 5. 数据集甚至可以自己造，而且非常容易造

这是这个题最大的优势之一。

你甚至不需要找公开自动驾驶数据集。

做一个：

# **ImplicitRoute-Bench**

比如只有 **500–1000 条自然语言指令**。

设 5 个路线属性：

| 属性       | 示例   |
| -------- | ---- |
| Time     | 尽快到  |
| Distance | 少绕路  |
| Toll     | 少花钱  |
| Highway  | 避免高速 |
| Traffic  | 避免拥堵 |

然后设计 20–30 个基础意图模板。

例如：

### TIME_HIGH

Explicit：

> Choose the fastest route.

Implicit：

> I'm already running late.

---

### HIGHWAY_LOW

Explicit：

> Avoid highways.

Implicit：

> Driving at high speed makes me nervous.

---

### TOLL_LOW

Explicit：

> Avoid toll roads.

Implicit：

> I'd rather not spend extra money on the road.

---

### TRAFFIC_LOW

Explicit：

> Avoid congested roads.

Implicit：

> I really don't want to get stuck in traffic today.

---

再让 GPT 批量 paraphrase。

例如：

```text
20 intentions
×
5 semantic variations
×
5 paraphrases
=
500 samples
```

Codex 很快就能生成。

而且 gold label 不需要人工一条条标。

因为模板本身就带 label：

```json
{
  "intent": "HIGHWAY_LOW",
  "preference": {
    "highway": 0.1
  }
}
```

这叫：

> **template-controlled synthetic benchmark**

论文完全讲得通。

---

# 6. 我甚至建议第一版不要调用真实地图 API

这是我现在比之前更想强调的一点。

最开始完全可以自己生成：

```json
Route A
time = 25
distance = 30
toll = 10
highway_ratio = 0.8

Route B
time = 32
distance = 25
toll = 0
highway_ratio = 0.1

Route C
time = 28
distance = 27
toll = 5
highway_ratio = 0.4
```

然后问：

> 根据用户隐式偏好，应该选哪条路线？

这样路线属性完全可控。

这对于科研实验其实**比地图 API 更干净**。

例如：

> “高速让我有点紧张，慢一点没事。”

gold：

```text
Route B
```

你能够非常清楚地知道为什么。

---

# 7. 实验于是简单得离谱

论文实验可以直接分成三个层次。

## Experiment 1：Preference Grounding Accuracy

只测：

```text
Natural Language
↓
Preference Vector
```

例如评价：

### Category Accuracy

高速：

```text
Gold: Low
Pred: Low
→ correct
```

可以报告：

[
Accuracy
]

以及 Macro-F1。

---

# 8. Experiment 2：Route Selection Accuracy

给定候选路线：

```text
用户意图
+
3 条候选路线
↓
选择路线
```

看最终有没有选中 gold route。

指标直接：

[
Route\ Selection\ Accuracy
]

这是最直观的结果。

---

# 9. Experiment 3：Robustness

这个反而可能是论文最好看的实验。

同一意图：

```text
x1 = Don't take highway.
x2 = High-speed roads make me uncomfortable.
x3 = I'd rather drive slowly today.
x4 = My parents are with me, so let's take an easier road.
```

看预测路线：

```text
B
B
B
B
```

定义：

[
Consistency
===========

\frac{\text{same decisions}}
{\text{semantic equivalent inputs}}
]

比如：

| Method     | Explicit | Implicit | Paraphrase | Consistency |
| ---------- | -------: | -------: | ---------: | ----------: |
| Direct LLM |     91.2 |     76.3 |       80.1 |        72.5 |
| CoT        |     92.0 |     81.4 |       84.3 |        79.8 |
| Structured | **94.1** | **88.7** |   **90.2** |    **87.6** |

这种表就已经非常像一篇正常论文了。

数字当然到时候跑实验。

---

# 10. Baseline 特别容易

完全不用复现别人代码。

我们可以设计：

### B1 Direct LLM

```text
User request + routes
→ choose route
```

这是最核心 baseline。

---

### B2 CoT LLM

```text
Analyze preferences first,
then select a route.
```

---

### B3 Explicit Structured Parsing

```text
User
→ preference JSON
→ scorer
```

---

### Ours

```text
User
→ soft preference + hard constraint
→ normalization / verification
→ scorer
```

甚至：

```text
Direct
CoT
Structured
Ours
```

四个方法。

全部调用同一个 LLM。

这样一个非常重要的实验控制成立：

> **Performance improvements come from the decision framework rather than a stronger LLM.**

这个表述很适合论文。

---

# 11. 消融实验也自动有了

比如：

| Method                     | Intent Acc | Route Acc | Consistency |
| -------------------------- | ---------: | --------: | ----------: |
| Full                       |       92.4 |      94.1 |        90.2 |
| w/o constraint distinction |       89.2 |      90.3 |        86.1 |
| w/o normalization          |       87.8 |      88.9 |        82.4 |
| Direct decision            |       81.5 |      84.2 |        75.6 |

三四行就够了。

---

# 12. 我现在最推荐的完整论文框架

### 1 Introduction

讲：

导航系统通常需要用户显式指定：

```text
fastest
shortest
avoid toll
avoid highway
```

但真实用户往往说：

> “我今天赶时间。”

> “高速让我有点紧张。”

> “今天不想交高速费。”

LLM 虽然有隐式语义理解能力，但：

1. 直接路线决策缺乏可解释性；
2. 对表达方式敏感；
3. 难以保证硬约束不被违反。

于是提出 Implicit2Route。

---

### 2 Related Work

只写三个小节：

```text
LLM-based Route Planning
Implicit Intent Understanding
LLM Structured Decision Making
```

不用展开太多。

---

### 3 Method

3.1 Problem Formulation

[
x,R\rightarrow r^*
]

3.2 Implicit Preference Grounding

[
x\rightarrow P
]

3.3 Soft Preference and Hard Constraint Extraction

[
x\rightarrow(P,C)
]

3.4 Constraint-Aware Route Selection

[
r^*=\arg\max_{r_i\models C}Score(r_i|P)
]

差不多。

---

### 4 Benchmark

ImplicitRoute-Bench。

介绍：

```text
intent taxonomy
expression types
route scenarios
ground-truth generation
```

---

### 5 Experiments

5.1 Setup

5.2 Preference Grounding

5.3 Route Selection

5.4 Robustness

5.5 Ablation

---

### 6 Conclusion

结束。

---

# 13. 这个题和你毕业论文的关系也非常舒服

它不是另起炉灶。

你的毕业论文是：

> **隐式意图理解 → 长距离复杂任务规划 → 自动驾驶智能体**

而这篇小论文实际上就是里面：

[
\boxed{\text{隐式意图理解}}
]

这个模块单独拆出来。

以后毕业论文里可以自然写：

```text
Implicit User Instruction
        ↓
Implicit2Route ← 小论文
        ↓
Task Graph
        ↓
Long-horizon Planner
        ↓
DriveAgent
```

所以你现在做的代码、数据和实验，以后都不是浪费。

---

# 14. 而且它非常适合 Codex

我甚至已经能想象 repo：

```text
Implicit2Route/
│
├── data/
│   ├── intents.json
│   ├── routes.json
│   └── benchmark.json
│
├── prompts/
│   ├── direct.md
│   ├── cot.md
│   └── implicit2route.md
│
├── src/
│   ├── llm_client.py
│   ├── parser.py
│   ├── scorer.py
│   ├── route_generator.py
│   └── evaluator.py
│
├── experiments/
│   ├── run_direct.py
│   ├── run_cot.py
│   ├── run_structured.py
│   └── run_ours.py
│
├── results/
│
└── README.md
```

核心代码量可能也就**几百行 Python**。

没有模型训练。

没有 CUDA。

没有环境搭建地狱。

甚至 GPT/Qwen API 都能并行测试。

---

# 15. 但我会注意一个最大的论文风险

现在这个方案最容易被审稿人问：

> **“这不就是 prompt engineering 吗？”**

所以我们后面设计论文时，一定不能把贡献写成：

> 我们设计了一个 prompt，让 LLM 输出 JSON。

而应该把论文包装成：

> **一个将自然语言隐式偏好与路线优化空间解耦的、可验证的决策框架。**

核心表达是：

[
\boxed{
\text{Language Space}
\rightarrow
\text{Preference Space}
\rightarrow
\text{Optimization Space}
}
]

而不是：

[
Prompt\rightarrow JSON
]

这个区别非常重要。

---

我现在对这个题的判断大致是：

**开发难度：★☆☆☆☆**
**算力需求：★☆☆☆☆**
**与你毕业论文相关度：★★★★★**
**实验可控性：★★★★★**
**Codex 可完成度：★★★★★**
**EI 小会议可包装程度：★★★★☆**

下一步实际上就应该把 **Implicit2Route 的“偏好空间”彻底定死**。这是整个题最关键的一步——到底选 **5 个维度还是 6–8 个维度、每个维度如何定义、哪些属于 hard constraint、哪些属于 soft preference、ground truth 怎么生成**。这部分一旦定下来，后面的数据生成、prompt、代码、实验基本都能直接开干。
