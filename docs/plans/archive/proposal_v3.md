# Research Proposal v3 — Architecture + Benchmark Locked
## DARC-Route: Decision-Aware Robust Consistency Grounding for Trustworthy Route Planning

**Target Venue:** CCEAI 2027  
**Primary Benchmark Basis:** HIPP (Human Instructions with Preferences for route Planning) from LLMAP  
**Secondary External Validation:** TransitLM Personalized Planning Benchmark (optional but recommended)  
**Project Codename:** DARC-Route  
**Version:** v3

---

# 1. Core Positioning

经过三轮 reference screening 和 CCEAI 2027 venue alignment，本项目不再把以下内容作为主要创新：

- Natural language → structured route preference；
- Soft / hard constraint representation；
- LLM + deterministic route solver；
- General paraphrase robustness；
- 普通 synthetic route benchmark。

本项目现在正式收敛为两个核心贡献：

1. **一个新的 Decision-Aware Robust Grounding Architecture；**
2. **一个建立在公开 HIPP benchmark 上的 robustness / error-propagation extension。**

核心研究链路：

\[
\text{Implicit User Language}
\rightarrow
\text{Robust Preference Grounding}
\rightarrow
\text{Decision-Aware Verification}
\rightarrow
\text{Route Planner}
\]

以及：

\[
\text{Language Variation}
\rightarrow
\text{Preference Drift}
\rightarrow
\text{Constraint Flip}
\rightarrow
\text{Route Flip}
\rightarrow
\text{Downstream Regret}
\]

---

# 2. Why HIPP Should Be the Primary Benchmark

## 2.1 HIPP Is the Closest Existing Public Benchmark

HIPP was introduced with LLMAP and is explicitly designed for:

> **Human Instructions with Preferences for route Planning**

It contains:

- 1,000 evaluation samples；
- one synthetic gold label per sample；
- one natural-language human instruction；
- LLM-as-Parser estimations；
- route-planning constraints and user preference weights。

The public LLMAP repository includes:

```text
data/
├── HIPP.py
└── HIPP.json
```

and provides the benchmark generation pipeline as well as the route-planning implementation.

Therefore, HIPP gives us three important advantages:

### Advantage 1 — Existing Academic Baseline

We are not inventing a benchmark in isolation.

Our work can clearly say:

> **We build upon HIPP, an existing benchmark for natural-language route preference grounding.**

### Advantage 2 — Gold Structured Labels

HIPP already has a structured gold representation containing:

- requested POI types；
- time constraints；
- dependency constraints；
- preference weights。

Therefore, robustness can be measured against known latent semantics.

### Advantage 3 — Existing Solver Pipeline

LLMAP already provides the MSGS route-planning solver.

This allows a controlled experiment:

```text
LLMAP:
User Language
→ Single LLM Parser
→ Structured Preference
→ MSGS

Ours:
User Language
→ DARC Grounder
→ Structured Preference
→ Same MSGS
```

The downstream planner remains unchanged.

Thus:

> any performance difference can be attributed primarily to the grounding architecture rather than a stronger routing algorithm.

---

# 3. Why Not Use TravelPlanner as the Primary Benchmark

TravelPlanner is an excellent planning benchmark, but it focuses on:

- multi-day itineraries；
- flights；
- restaurants；
- attractions；
- hotels；
- multiple real-world constraints。

Its planning unit is much broader than a route-preference grounding problem.

Using TravelPlanner as the primary benchmark would introduce many confounding factors:

\[
\text{Tool Use}
+
\text{Search}
+
\text{Long-Horizon Planning}
+
\text{Constraint Tracking}
+
\text{Language Grounding}
\]

This makes it difficult to isolate the phenomenon we want to study:

\[
\text{Language Grounding Error}
\rightarrow
\text{Route Decision Error}
\]

Therefore:

> **TravelPlanner should remain related work, not our main experimental substrate.**

---

# 4. Why Not Use MM-Route as the Primary Benchmark

MM-Route / SMAP focuses on multimodal semantic route planning using:

- user queries；
- POI metadata；
- map tiles；
- multimodal LLMs。

Using it would introduce visual/map grounding as another major source of error.

Our research question is specifically about:

> **language-induced preference instability**

not multimodal geographic hallucination.

Therefore MM-Route is not ideal for the main benchmark.

---

# 5. Why TransitLM Is a Good Secondary Benchmark

TransitLM is a large-scale public transit route benchmark with:

- over 13 million route-planning records；
- four Chinese cities；
- 120,845 stations；
- 13,666 transit lines；
- public Hugging Face data；
- public evaluation code。

Its personalized planning benchmark explicitly evaluates preference compliance for requests such as:

- fewer transfers；
- no subway；
- subway first；
- shorter travel time。

This is valuable because it gives us an external benchmark where:

\[
\text{Preference}
\rightarrow
\text{Route Compliance}
\]

is already defined.

However, TransitLM is public-transit routing rather than road-driving routing.

Therefore the recommended experimental hierarchy is:

```text
Primary:
HIPP / LLMAP

        ↓

Our extension:
HIPP-Robust

        ↓

Secondary external validation:
TransitLM Personalized Planning
```

If time is limited, HIPP-Robust is mandatory and TransitLM is optional.

---

# 6. Proposed Benchmark Extension: HIPP-Robust

We should not claim to build an unrelated benchmark from scratch.

Instead, we introduce:

# **HIPP-Robust**

> A semantic-equivalence and decision-robustness extension of HIPP.

---

# 7. HIPP-Robust Construction

For each original HIPP sample:

\[
s_i=
(y_i,x_i)
\]

where:

- \(y_i\) is the original structured synthetic label；
- \(x_i\) is the original human instruction。

We construct:

\[
E_i=
\{x_i^{(1)},x_i^{(2)},...,x_i^{(K)}\}
\]

such that every expression preserves:

\[
y_i
\]

That is:

\[
Sem(x_i^{(1)})
=
Sem(x_i^{(2)})
=
...
=
Sem(x_i^{(K)})
=
y_i
\]

---

# 8. Recommended HIPP-Robust Scale

Do not expand all 1,000 HIPP samples immediately.

For CCEAI 2027, use a stratified subset.

Recommended:

- 200 original HIPP samples；
- 5 equivalent expressions per sample；
- 1,000 total user utterances。

This already matches the scale of the original HIPP benchmark while adding a new group structure.

Sampling should cover:

- different POI counts；
- with / without time constraints；
- with / without dependency constraints；
- low / medium / high preference-weight imbalance。

---

# 9. HIPP-Robust Language Variants

Each HIPP sample receives five views:

## V0 — Original HIPP Instruction

The original benchmark instruction.

## V1 — Direct Semantic Paraphrase

Surface form changes while maintaining all intent components.

## V2 — Implicit Preference Expression

Preference is expressed indirectly.

Example:

Original:

> “I prefer a shorter route.”

Implicit:

> “I do not want to spend too much time walking between places.”

## V3 — Pragmatic / Contextual Expression

Preference is conveyed via context.

Example:

> “I have already walked a lot today, so I would rather keep the route compact.”

## V4 — Colloquial / Mild Noise

Natural spoken variation, minor omission or typo, without changing gold semantics.

---

# 10. Separate Contrastive Stress Set

Semantic-equivalent tests and semantic-change tests must remain separate.

Create an auxiliary:

# HIPP-Contrast

It includes minimal pairs such as:

### Soft → Hard

> “I would prefer to be back before 7 PM.”

vs.

> “I absolutely must be back before 7 PM.”

### Preference Strength

> quality weight high

vs.

> distance weight high

### Constraint Removal

one paraphrase intentionally drops a constraint.

### Conflict

> high POI quality preference + strict route-length requirement.

These are not part of semantic consistency evaluation.

They are used for **decision-boundary analysis**.

---

# 11. New Architecture: DARC-Route

# **DARC-Route**
## Decision-Aware Robust Consistency Grounding for Route Planning

The key architectural idea is:

> **Do not verify language grounding only at the representation level. Verify whether alternative plausible groundings would actually change the downstream route decision.**

This distinguishes DARC-Route from generic:

- self-consistency；
- verifier agents；
- parser ensembles；
- semantic rewriting。

---

# 12. Architecture Overview

```text
                     ┌──────────────────────┐
                     │ Raw User Utterance x │
                     └──────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        Raw Preference Grounder       Semantic Canonicalizer
                 │                             │
                 │                             ▼
                 │                   Canonical Preference
                 │                       Grounder
                 │                             │
                 ▼                             ▼
            (P_raw,C_raw)                (P_can,C_can)
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                     Grounding Consistency
                           Estimator
                                │
                                ▼
                    Counterfactual Planner
                           Probe
                                │
               ┌────────────────┴────────────────┐
               │                                 │
        Same Route Decision                Route / Constraint
          under both views                    Disagreement
               │                                 │
               ▼                                 ▼
         Accept Consensus              Decision-Aware Verifier
                                                │
                                                ▼
                                      Robust Grounding Arbiter
                                                │
                                                ▼
                                          Final (P*,C*)
                                                │
                                                ▼
                                             MSGS
                                                │
                                                ▼
                                          Final Route
```

---

# 13. Module A — Raw Preference Grounder

The first branch directly parses the original user utterance:

\[
G_r(x)
=
(P_r,C_r)
\]

This branch preserves all original linguistic information.

It acts similarly to LLMAP's parser and is therefore a direct baseline-compatible component.

---

# 14. Module B — Semantic Canonicalizer

The second branch first converts the user utterance into a controlled route-intent statement:

\[
x
\rightarrow
x^{can}
\]

Example:

```text
Raw:
“I have already walked a lot today and still want to see the best places.”

Canonical:
“Prefer shorter travel distance while maintaining relatively high POI quality.”
```

Important:

> the canonicalizer does not decide the route.

Its purpose is to reduce irrelevant wording variation.

---

# 15. Module C — Canonical Preference Grounder

The canonical representation is independently parsed:

\[
G_c(x^{can})
=
(P_c,C_c)
\]

Now we have two independent semantic views:

\[
(P_r,C_r)
\]

and:

\[
(P_c,C_c)
\]

---

# 16. Module D — Grounding Consistency Estimator

Calculate representation disagreement.

For preference weights:

\[
D_P
=
\frac{1}{d}
\|P_r-P_c\|_1
\]

For hard constraints:

\[
D_C
=
\mathbb{1}(C_r\neq C_c)
\]

A naive architecture would trigger re-grounding whenever \(D_P\) is large.

DARC-Route does **not** stop here.

---

# 17. Module E — Counterfactual Planner Probe

Both candidate groundings are passed through the same deterministic planner:

\[
r_r=
\pi(P_r,C_r,R)
\]

\[
r_c=
\pi(P_c,C_c,R)
\]

Then measure:

\[
D_R
=
\mathbb{1}(r_r\neq r_c)
\]

This is the key architectural module.

It asks:

> **Does the semantic disagreement actually matter to planning?**

If:

\[
P_r\neq P_c
\]

but:

\[
r_r=r_c
\]

then the representation disagreement is considered **planning-benign**.

No additional expensive verification is necessary.

---

# 18. Module F — Decision-Aware Risk Gate

Define a risk score:

\[
Risk(x)
=
\alpha D_P
+
\beta D_C
+
\gamma D_R
+
\delta S_M
\]

where:

- \(D_P\): preference disagreement；
- \(D_C\): constraint disagreement；
- \(D_R\): route-decision disagreement；
- \(S_M\): planning-margin sensitivity。

For the top two routes:

\[
M
=
U(r_1)-U(r_2)
\]

Define:

\[
S_M
=
\frac{1}{M+\epsilon}
\]

so low-margin planning situations receive higher risk.

Therefore:

\[
Risk
\uparrow
\]

when:

- grounding disagreement increases；
- hard constraints disagree；
- alternative groundings choose different routes；
- route decision margin is small。

---

# 19. Module G — Decision-Aware Verifier

Only high-risk cases invoke an additional verifier.

Input:

```text
Original user utterance
Candidate grounding A
Candidate grounding B
Their implied route decisions
```

The verifier is asked:

> Which grounding is better supported by the original utterance?

It must output only:

\[
(P_v,C_v)
\]

No direct route recommendation is allowed.

This maintains the architecture principle:

> language model interprets user intent; deterministic planner makes route decisions.

---

# 20. Module H — Robust Grounding Arbiter

The arbiter combines:

- raw grounding；
- canonical grounding；
- verifier grounding if triggered。

For numeric preference values:

\[
P^*
=
Medoid(
P_r,P_c,P_v
)
\]

or weighted consensus.

For constraints:

- majority agreement when three views exist；
- verifier result resolves raw/canonical disagreement。

The resulting:

\[
(P^*,C^*)
\]

is passed to MSGS.

---

# 21. Why DARC-Route Is More Than Self-Consistency

A standard self-consistency system asks:

> “Do multiple LLM outputs agree?”

DARC-Route asks:

> **“Does disagreement between plausible semantic interpretations change the downstream planning decision?”**

This gives a two-level verification process:

\[
\text{Semantic Consistency}
+
\text{Decision Sensitivity}
\]

The verifier is triggered by **planning consequence**, not merely textual or JSON disagreement.

This architecture directly operationalizes the paper's core research finding:

\[
\boxed{
Representation\ Instability
\neq
Decision\ Instability
}
\]

---

# 22. Relationship to Prior Architectures

## LLMAP

```text
Language
→ Single Parser
→ Preference
→ MSGS
```

DARC-Route replaces the single parser with a decision-aware robust grounding layer.

---

## RouteLLM

RouteLLM uses specialized agents and a final verifier to improve constraint-aware routing.

DARC-Route differs in that:

> verification is explicitly triggered by **cross-view grounding inconsistency and downstream route sensitivity**.

The research target is not generic route-quality improvement but robustness to language variation.

---

## SMAP

SMAP uses a second multimodal model to verify geographic plausibility.

DARC-Route verifies:

> **semantic preference consistency and its planning consequence**,

not spatial hallucination.

---

## ICR-Drive

ICR-Drive diagnoses:

\[
Instruction\ Variation
\rightarrow
Driving\ Performance
\]

DARC-Route explicitly models:

\[
Instruction
\rightarrow
Preference
\rightarrow
Constraint
\rightarrow
Route
\]

making the error source interpretable.

---

# 23. Architecture Hypotheses

## H1

DARC-Route reduces Preference Drift relative to a single LLM parser.

## H2

DARC-Route reduces hard-constraint disagreement.

## H3

DARC-Route reduces Route Flip Rate on HIPP-Robust.

## H4

Decision-aware gating achieves similar robustness to always-on verification while using fewer additional LLM calls.

This is especially useful as a CCEAI engineering contribution.

## H5

The largest benefit occurs in low-margin / constraint-sensitive planning cases.

---

# 24. Primary Experimental Comparison

Use the same underlying LLM backbone where possible.

| Method | Architecture |
|---|---|
| Direct LLM Agent | Language → Route |
| LLMAP Parser | Language → Single Parse → MSGS |
| CoT Parser | Language → CoT Parse → MSGS |
| Canonicalize + Parse | Language → Canonical → Parse → MSGS |
| Self-Consistency Parse | Multiple Parses → Consensus → MSGS |
| **DARC-Route** | Dual-View Grounding → Counterfactual Planner Probe → Risk Gate → Verifier → MSGS |

This table creates a clear architecture story.

---

# 25. Main Benchmark Metrics

## Grounding Level

- POI F1；
- Time Constraint Accuracy；
- Dependency F1；
- Preference Weight Similarity；
- Preference Drift。

## Consistency Level

- Equivalent-Group Consistency；
- Constraint Flip Rate。

## Planning Level

- Route Flip Rate；
- Task Completion；
- Constraint Violation；
- Route Quality / Distance；
- Downstream Regret。

## Architecture Efficiency

- additional LLM calls；
- verification trigger rate；
- robustness gain per additional call。

The last metric is particularly suitable for DARC-Route.

---

# 26. Secondary TransitLM Evaluation

If schedule permits, adapt TransitLM personalized prompts into semantic-equivalent groups.

For example:

Gold preference:

> fewer transfers

Variants:

```text
“I would like to change lines as little as possible.”

“Too many transfers are inconvenient for me.”

“Please keep the number of line changes low.”

“I am carrying luggage, so fewer transfers would help.”
```

Then evaluate:

- Preference Compliance；
- route structure consistency；
- travel time / fare estimation；
- route flip under equivalent wording。

This demonstrates that DARC-Route is not tied only to HIPP's city-tour formulation.

---

# 27. Final Benchmark Strategy

The paper should state:

> **Our primary experiments build on HIPP, the public preference-grounded route-planning benchmark introduced by LLMAP. We extend HIPP into HIPP-Robust by organizing semantically equivalent user expressions around the original gold preference labels. We retain the original route solver to isolate the effects of language grounding. We additionally evaluate on the preference-aware subset of TransitLM to test cross-domain generalization.**

This is substantially stronger than saying:

> “We generated our own 200 synthetic prompts.”

---

# 28. Updated Contributions

## Contribution 1 — DARC-Route Architecture

> We propose DARC-Route, a decision-aware robust grounding architecture that combines multi-view preference interpretation with counterfactual planner probing and risk-gated verification.

## Contribution 2 — HIPP-Robust

> We extend the existing HIPP benchmark with controlled semantic-equivalent user expressions and contrastive preference-boundary cases.

## Contribution 3 — Multi-Level Error Propagation Evaluation

> We jointly measure representation drift, constraint flips, route flips and downstream planning regret.

## Contribution 4 — Decision-Aware Efficiency

> We show that downstream decision-aware verification can focus additional reasoning on planning-sensitive cases instead of verifying every grounding indiscriminately.

---

# 29. Recommended Paper Title

## Preferred

**DARC-Route: Decision-Aware Robust Grounding of Implicit User Preferences for Trustworthy Route Planning**

## Alternative

**DARC-Route: Robust Implicit Preference Grounding with Decision-Aware Verification for Language-Conditioned Route Planning**

The first is more concise and better aligned with CCEAI's trustworthiness theme.

---

# 30. Immediate Execution Plan

## Step 1 — Reproduce HIPP / LLMAP

Before generating any new data:

```text
clone LLMAP
run HIPP
run baseline parser
run MSGS
```

Confirm that original evaluation works.

## Step 2 — Inspect HIPP Schema

Lock:

- gold label fields；
- preference weights；
- constraints；
- route output；
- metrics。

## Step 3 — Build HIPP-Robust Generator

Start with only:

- 20 original samples；
- 5 variants each；
- 100 utterances。

## Step 4 — Implement Architecture

Implement:

1. Raw Grounder；
2. Canonicalizer；
3. Canonical Grounder；
4. Consistency Estimator；
5. Planner Probe；
6. Risk Gate；
7. Verifier；
8. Arbiter。

## Step 5 — Pilot

Compare:

```text
LLMAP Parser
vs
Canonicalization
vs
Self-Consistency
vs
DARC-Route
```

on the first 100 utterances.

## Step 6 — Go / No-Go

If DARC-Route reduces Route Flip / Constraint Violation meaningfully:

> expand HIPP-Robust.

If not:

> simplify or change the risk-gating logic before scaling the dataset.

---

# 31. Current Recommendation

At this stage, the project should no longer be described as only an evaluation paper.

The most coherent CCEAI 2027 paper is:

\[
\boxed{
\text{Existing Benchmark}
+
\text{New Robust Grounding Architecture}
+
\text{New Robustness Extension}
+
\text{Planning-Level Error Analysis}
}
\]

Specifically:

```text
Benchmark Base:
HIPP / LLMAP

New Benchmark Extension:
HIPP-Robust

New Architecture:
DARC-Route

External Validation:
TransitLM Personalized Planning

Core Scientific Question:
When does linguistic grounding instability actually change route decisions?
```

This should now be treated as the locked research direction unless the pilot results invalidate it.
