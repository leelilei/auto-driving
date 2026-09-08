# DARC-Route Research Protocol v2

> **2026-09-08 版本提示**：当前研究主线以 [Proposal v5](../plans/proposal.md) 为准。本文件以下内容保留为旧方案记录，不能直接用作 v5 执行协议或完成证明。旧阶段三暂停扩量；需落实新数据资格、对比报告、配对图与对照协议。论文写作仍 CLOSED。

> **独立审阅状态（2026-09-07）：本稿尚未验收，不能追溯性地为已暴露的历史测试建立预注册。** 当前数据/响应版本不一致，需按 [第二轮审阅](CODEX_REMEDIATION_REVIEW_20260907.md) 修订并为未来确认实验重新冻结。执行 [实验先行、验收后写作原则](../project/EXPERIMENT_FIRST_POLICY.md)。

**Pre-Registered Evaluation Protocol, Metric Hierarchy, and Operational Constraints**

> **Version**: 2.0.0 (Remediation Freeze)  
> **Date**: 2026-09-07  
> **Supersedes**: Protocol v1 (Exploratory Prototype)  
> **Scope**: Confirmatory Benchmark on 160 Groups (640 Test Utterances) across Frontier LLMs

---

## 1. Core Principles: Confirmatory vs. Exploratory Separation

1. **Strict No-Peeking Principle**:
   - The confirmatory test split (`data/test/test_640_utterances.json`, 160 groups, 640 utterances) is strictly quarantined from hyperparameter search, threshold calibration, and heuristic rule tuning.
   - Any tuning on the test set is categorized as data snooping and renders experimental claims invalid.
2. **Pre-Freezing on Development Calibration**:
   - All gate operating parameters ($\tau^*, \tau_{\text{sem}}^*, p^*$) are frozen exclusively on `dev_calibration` (20 groups, 80 utterances; Dev set total = 40 groups: 20 pilot + 20 calibration) prior to running confirmatory test evaluation.
   - Frozen parameters are immutable and committed in `data/calibration/frozen_config.json`:
     - $\tau^* = 0.020$ (utility discrepancy threshold)
     - $\tau_{\text{sem}}^* = 0.100$ (semantic preference difference threshold)
     - $p_{\text{review}}^* = 0.481$ (matched-budget random review probability)
3. **Offline Zero-API Execution**:
   - Confirmatory evaluation of decision gating (B0–B6 and Ours) operates in strictly offline replay mode.
   - Network calls are prohibited via socket-level enforcement (`NetworkBlocker` context manager). All evaluations replay from auditable cached responses.
4. **Exploratory Re-Analysis vs. Confirmatory Benchmark**:
   - Historical runs on the 5 frontier models (`results/runs/20260906T051339Z_main_test` etc.) are designated as **exploratory-v1 re-analyses** under Metric v2.
   - They cannot be retroactively claimed as pre-registered confirmatory trials.
   - This Protocol v2 pre-registers the frozen hypotheses, baselines, and gate criteria for **future confirmatory data collection** on the audited dataset once human verification and fresh model API calls are authorized.

---

## 2. Metric Hierarchy & Definitions

To prevent selective reporting, metrics are organized into a strict three-tier hierarchy:

### Tier 1: Primary Feasibility Metrics (Hard Constraints)
- **Task Success Rate (TSR)**:
  $$\text{TSR} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(\text{Route } r_i \text{ satisfies all hard constraints of } g_i)$$
  Hard constraints: complete POI category coverage, arrival before strict deadline $T_{\text{max}}$, and strict adherence to topological order dependencies $(u \prec v)$.
- **Group Task Success Rate (GTSR)**:
  $$\text{GTSR} = \frac{1}{|G|} \sum_{g \in G} \prod_{v \in \{V0, V1, V2, V3\}} \mathbb{I}(\text{TSR}(g_v) = 1)$$
  Measures whether an agent succeeds across all 4 linguistic variants of a scenario.

### Tier 2: Secondary Behavioral Metrics (Robustness & Optimality)
- **Route Flip (Paraphrase Robustness on Valid Pairs)**:
  $$\text{Route Flip}(g) = \frac{\sum_{u < v, \, \text{valid}(u) \land \text{valid}(v)} \mathbb{I}(\text{Route}(g_u) \neq \text{Route}(g_v))}{\sum_{u < v, \, \text{valid}(u) \land \text{valid}(v)} 1}$$
  - *Denominator Definition*: Computed strictly over pairwise combinations where **both** variants successfully satisfy all hard constraints (`task_success == True`). If fewer than 2 variants succeed, the group's flip is undefined/excluded from the flip denominator.
  - Measures decision stability under semantically invariant prompt rewriting. Two routes are identical if and only if their ordered POI node sequence is identical.
- **Normalized Decision Regret (Utility Optimality)**:
  $$\text{Regret}(r_{\text{chosen}}, r_{\text{oracle}}) = \max\left(0, \frac{U_{w_{\text{gold}}}(r_{\text{oracle}}) - U_{w_{\text{gold}}}(r_{\text{chosen}})}{2.0}\right)$$
  - **Critical Invariant (P0-3 Remediation)**: Both the oracle route and the chosen route **must** be evaluated under the *exact same gold quality weight* $w_{\text{gold}}$ and exact coordinate travel distances. Cross-scale subtraction between different weight objectives is strictly prohibited.
  - Normalization: Because utility $U_w \in [-1.0, 1.0]$, the maximum theoretical gap is $2.0$, normalizing regret strictly to $[0.0, 1.0]$.
  - Identical Route Identity: If $r_{\text{chosen}}$ and $r_{\text{oracle}}$ visit the identical sequence of POIs, regret is identically $0.000000$.

### Tier 3: Compute & Cost Metrics (P0-5 Remediation)
To prevent inflated or misleading claims of 'compute reduction':
1. **Review Call Rate ($q$)**:
   The empirical proportion of queries that trigger the 3rd review call ($q \in [0.0, 1.0]$).
2. **Review Stage Reduction vs. B6 (Always Review)**:
   $$\text{Review Reduction} = 1 - q$$
   *Reporting Constraint*: Must explicitly be labeled as "review call reduction", never conflated with total compute or token savings.
3. **Total Logical Call Reduction vs. B6**:
   $$\text{Total Logic Call Reduction} = \frac{3 - (2 + q)}{3} = \frac{1 - q}{3}$$
   (E.g., $q = 4.22\% \implies 31.93\%$ total call reduction vs B6).
4. **Logical Call Overhead vs. B0 (Single Turn)**:
   $$\text{Overhead vs B0} = \frac{(2 + q) - 1}{1} = 1 + q$$
   (E.g., Ours consumes $104.22\%$ more logical calls than unverified B0).
5. **Physical Resource Accounting**:
   Every reported evaluation must record actual provider input tokens, output tokens, total tokens, and end-to-end latency.

---

## 3. Baseline Inventory & Invariant Guarantees

| Identifier | Name | Logical Calls | Gating Logic | Theoretical Property |
|---|---|---|---|---|
| **B0** | Single Turn (Unverified) | 1 | Accept Candidate A | Lower bound on cost, vulnerable to prompt noise |
| **B1** | Sampled Medoid | 3 | Select medoid of $\{A, A_2, A_3\}$ | Standard majority voting / self-consistency |
| **B2** | Paired Dual-Turn (Unverified) | 2 | Generate A and B; always accept A | **Property C01 Invariant**: $B2 \equiv B0$ in route & TSR |
| **B3** | Random Review Gate | $2 + q$ | Trigger review if $h=1$ or with prob $p^*$ | Budget-matched stochastic review baseline |
| **B4** | Semantic Weight Discrepancy Gate | $2 + q$ | Trigger review if $h=1$ or $\|w_A - w_B\| > \tau_{\text{sem}}^*$ | Pure semantic-space discrepancy baseline |
| **B5** | Hard Protection Gate Only | $2 + q$ | Trigger review if $h(A, B) = 1$ | Hard-constraint disagreement baseline without $\Delta_U$ |
| **B6** | Full Verification (Always Review) | 3 | Always trigger review ($q = 1.0$) | Upper bound on verification cost |
| **Ours** | DARC Dual-Space Gated Verification | $2 + q$ | Trigger review if $h=1$ or $\Delta_U > \tau^*$ | Proposed dual-space gated consensus |

### Property C01 Invariant Verification:
$$\forall \text{ utterance } u, \quad \text{Route}_{\text{B2}}(u) \equiv \text{Route}_{\text{B0}}(u) \quad \land \quad \text{TSR}_{\text{B2}}(u) \equiv \text{TSR}_{\text{B0}}(u)$$
Any deviation between B0 and B2 indicates an implementation bug and immediately causes replay failure.

---

## 4. Pre-Registered Hypotheses & Statistical Tests

All statistical tests use paired non-parametric bootstrap resampling ($B = 10,000$, seed = 42) grouped at the scenario group level ($N = 160$):

- **Hypothesis 1 (Robustness Superiority)**:
  $$\Delta \text{RouteFlip} = \text{RouteFlip}(\text{B0}) - \text{RouteFlip}(\text{Ours}) > 0, \quad p < 0.05$$
- **Hypothesis 2 (Pareto Efficiency vs Full Review)**:
  $$\text{TSR}(\text{Ours}) \ge \text{TSR}(\text{B6}) - 0.01 \quad \land \quad q(\text{Ours}) \le 0.20$$
  $$\text{Robustness Gain Retention} = \frac{\text{RouteFlip}(\text{B0}) - \text{RouteFlip}(\text{Ours})}{\text{RouteFlip}(\text{B0}) - \text{RouteFlip}(\text{B6})} \ge 0.90 \quad (\text{when } \text{Flip}(\text{B0}) > \text{Flip}(\text{B6}))$$
  Ours retains $\ge 90\%$ of B6's empirical robustness gains while saving $\ge 80\%$ of B6's review calls ($q \le 0.20$).
- **Hypothesis 3 (Utility Regret Control)**:
  $$\text{Regret}(\text{Ours}) \le \text{Regret}(\text{B0})$$
  Dual-space gating avoids suboptimal route choices caused by unverified preference hallucinations. Observed empirical trade-offs where regret increases while Flip decreases must be explicitly reported as trade-offs.

---

## 5. Execution Budget & Stopping Conditions

1. **Candidate Generation Budget**:
   - Maximum 5 attempts per utterance across collection phases: A, B, review (if triggered), A2, A3 (for B1).
   - Rate limit retry budget: maximum 3 retries on HTTP 429 or 5xx with backoff sleep $\ge 2.0$s.
   - All attempts must be preserved in telemetry logs (`attempts` field).
2. **Stopping Criteria**:
   - Replay fails immediately with non-zero exit code if:
     - Any group JSON or graph JSON is missing.
     - Any candidate re-parsing fails.
     - Any solved route node sequence diverges from cached route.
     - Property C01 ($B2 \equiv B0$) is violated on any case.
     - Saved summary metrics diverge from recomputed metrics.
3. **Artifact Immutability**:
   - Historical exploratory runs are archived under `results/reports/history_exploratory_v1/` and indexed in `docs/experiments/exploratory_v1_run_registry.json`.
   - Recomputed results are versioned under `metric_version: v2` and indexed in `docs/experiments/v1_vs_v2_comparison.md`.
