# Pilot40 实验结果分析计划 (DARC-Route v4)

## 1. 任务背景

根据项目核心决策，本项目统一以 **DARC-Route v4**（面向自然语言 POI 路线规划的决策感知选择性复核）为基准。在 v4 研究体系下，针对 HIPP-Robust 数据集的前 40 组代表性意图（Pilot40），已使用真实网络 API 调用完成了 `gemini-3-flash` 模型的基准测试采集。

为了全面评估该批次真实运行数据的质量、模型的意图解析表现、下游规划鲁棒性以及方法 A（直接解析）、方法 B（证据短语抽取）与 Review（复核）的相对表现，特制定本分析计划。

### 数据位置与格式说明

- **运行目录**: `9-AutoDriving-core/results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/`
- **测试用例数量**: 共 40 组测试用例（`test_001` 到 `test_040`）
- **文件组成**:
  - `test_XXX.json`: 完整的测试组执行与评测数据。包含 `group_id`、`utterances_count`（固定为 4），以及 4 个变体（$V_0$: 原句, $V_1$: 同义替换, $V_2$: 句式语序变异, $V_3$: 口语化拼写噪声）的详细记录。每条变体包含：
    - `text`: 自然语言输入文本；
    - `gold_intent`: 人工校验的基准意图（包含 `pois` 集合、`time_limit` 截止时间、`dependencies` 访问先后拓扑闭包、`quality_weight` 偏好权重）；
    - `oracle_route` & `oracle_check`: 完美意图下的离线枚举参考路线及可达性检查；
    - `calls`: 模型 API 调用详情（按 `A`, `B`, `review` 分列，记录 `raw_response`, `schema_valid`, 以及包含重试、延迟、Token、传输错误等的 `telemetry`）；
    - `candidates`: 各方法解析出的意图结构；
    - `routes`: 对应候选意图代入固定 POI 图求解器后的实际规划路线与效用。
  - `test_XXX_graph.json`: 对应意图组的固定离线 POI 场景拓扑图（包含 10 个候选 POI、类别、营业时隙与距离矩阵）。

---

## 2. 任务目标：五大分析维度

对全量 40 组 × 4 变体 = 160 条自然语言指令进行深入分析，覆盖以下五大核心维度：

### 2.1 数据完整性检查
- 验证全量 40 组 JSON 文件及对应图文件是否存在且能无损加载；
- 检查每个测试组是否严格包含 4 个变体（$V_0, V_1, V_2, V_3$），总计 160 个 utterance；
- 统计各方法（A、B、Review）在 160 个 utterance 上的调用状态（执行成功、格式失败、网络超时/断连）。

### 2.2 方法评估指标计算
对方法 A、方法 B 和 Review（以及对应的规划路线），分别计算以下三类指标：
1. **Schema 有效性**：
   - 统计 JSON 解析及字段合规的比例（`schema_valid = true`）；
   - 按变体类型（$V_0, V_1, V_2, V_3$）分层统计，评估句式扰动对格式解析稳定性的影响。
2. **意图准确性（Intent Accuracy）**：将提取结果与 `gold_intent` 对齐：
   - **POIs 集合匹配率**：比较提取类别集合与标准集合是否完全一致（`set(extracted) == set(gold)`）；
   - **Time limit 匹配率**：截止时间（分钟数或 null）完全匹配率；
   - **Dependencies 匹配率**：先后拓扑依赖对集合完全匹配率；
   - **Quality weight MAE**：偏好权重的平均绝对误差 $|w_{\text{pred}} - w_{\text{gold}}|$。
3. **路由质量（Route Quality）**（针对产出路线的方法 A、B 及 Oracle）：
   - **Task Success Rate (TSR)**：满足所有硬约束的可行路线比例（基于 `oracle_check.task_success`）；
   - **Full Coverage Rate**：完全覆盖所有目标 POI 的比例；
   - **平均 Utility**：求解路线的目标函数效用；
   - **Utility Gap vs Oracle**：相对完美意图规划的最优路线效用差距；
   - **物理规划指标**：平均总路程（`distance_km`）与最终到达时间（`final_arrival_time`）。

### 2.3 方法对比分析
- **A vs B 对比**：对比直接提取（A）与要求证据短语抽取（B）在格式合规率、意图准确率和网络调用稳定性上的差异，检验显式证据对 Gemini 3 Flash 是否产生负担；
- **Review 方法增益与纠错能力**：
  - 统计 Review 触发情况及最终有效性；
  - 判定 Review 究竟是实现了“纠正错误”（Correction）、“维持正确”（Preservation），还是产生了“改坏”（Degradation）。

### 2.4 错误分析
- **API 与传输错误分析**：
  - 统计超时错误数量（如网络 curl 60 秒超时）；
  - 统计 HTTP/传输异常（`transport_error_type`、重试耗尽等）；
  - 分析错误在方法（A/B/Review）与变体（$V_0 \sim V_3$）上的分布聚集模式。
- **意图与语义错误模式**：
  - POIs 类别遗漏、过度臆造或幻觉；
  - Quality weight 的系统性偏差（例如过度偏向 0.5 中庸权重）；
  - 依赖拓扑误判（将文本叙述先后误当作硬先后约束）。

### 2.5 延迟与成本统计
- **时间延迟**：统计各方法的平均响应延迟（`avg_latency_seconds`）与耗时分布；
- **Token 消耗**：统计 `input_tokens`、`output_tokens`、`total_tokens` 的总量与单次平均值；
- **重试开销**：统计平均请求重试次数（`avg_attempts`）及失败调用产生的额外开销。

---

## 3. 输出要求：三大交付物详细规范

分析流程需自动化产出三个标准化交付物，存放于运行目录中：

### 3.1 汇总指标 (`pilot40_summary.json`)
结构规范严格如下：
```json
{
  "run_info": {
    "run_dir": "20260911T181825Z_main_test_gemini-3-flash_pilot40_net",
    "model": "gemini-3-flash",
    "total_groups": 40,
    "total_utterances": 160,
    "analysis_date": "2026-09-12"
  },
  "schema_validity": {
    "A": { "valid": 160, "total": 160, "rate": 1.0 },
    "B": { "valid": 142, "total": 160, "rate": 0.8875 },
    "review": { "valid": 160, "total": 160, "rate": 1.0 }
  },
  "intent_accuracy": {
    "A": {
      "pois_exact_match": 0.9375,
      "time_limit_match": 0.975,
      "dependencies_match": 0.9875,
      "quality_weight_mae": 0.0825
    },
    "B": {
      "pois_exact_match": 0.9125,
      "time_limit_match": 0.9625,
      "dependencies_match": 0.975,
      "quality_weight_mae": 0.091
    },
    "review": {
      "pois_exact_match": 0.9375,
      "time_limit_match": 0.975,
      "dependencies_match": 0.9875,
      "quality_weight_mae": 0.0825
    }
  },
  "route_quality": {
    "A": {
      "task_success_rate": 0.8875,
      "full_coverage_rate": 0.9125,
      "avg_utility": 0.4521,
      "avg_utility_gap_vs_oracle": 0.0612,
      "avg_distance_km": 15.34,
      "avg_arrival_minutes": 652.4
    },
    "B": {
      "task_success_rate": 0.825,
      "full_coverage_rate": 0.8625,
      "avg_utility": 0.4312,
      "avg_utility_gap_vs_oracle": 0.0821,
      "avg_distance_km": 15.82,
      "avg_arrival_minutes": 661.1
    }
  },
  "errors": {
    "A": { "timeout": 0, "transport_error": 0, "schema_error": 0, "other": 0 },
    "B": { "timeout": 14, "transport_error": 0, "schema_error": 4, "other": 0 },
    "review": { "timeout": 0, "transport_error": 0, "schema_error": 0, "other": 0 }
  },
  "performance": {
    "A": {
      "avg_latency_seconds": 16.82,
      "total_tokens": 82450,
      "avg_attempts": 1.02
    },
    "B": {
      "avg_latency_seconds": 45.31,
      "total_tokens": 71200,
      "avg_attempts": 1.48
    },
    "review": {
      "avg_latency_seconds": 18.25,
      "total_tokens": 84100,
      "avg_attempts": 1.01
    }
  }
}
```

### 3.2 详细分析报告 (`pilot40_analysis.md`)
Markdown 格式，必须包含以下六个章节：
1. **执行摘要**：3~5 句话总结数据规模、关键发现（如方法 B 超时率、意图准确率及路由质量结论）；
2. **数据完整性审计**：统计文件数、变体数、各方法成功调用的有效样本数与缺失情况；
3. **方法评估指标对比**：使用清晰的 Markdown 表格对比 A、B、Review 在 Schema、POIs 匹配、时间、依赖及权重 MAE 上的表现；
4. **路由质量与下游规划影响**：对比规划成功率、路线覆盖率及效用偏差；
5. **错误归因与系统性模式**：深度分类统计超时异常、Schema 格式失败及权重中庸化偏误；
6. **结论与 v4 下一步推进建议**：基于 Pilot40 数据，提出针对全量测试、超时重试策略或 Prompt 优化的具体建议。

### 3.3 错误案例清单 (`pilot40_errors.json`)
记录所有出现异常（API 失败、网络超时、Schema 校验失败或求解异常）的案例数组：
```json
[
  {
    "group_id": "test_001",
    "utterance_id": "test_001_v0",
    "variant_type": "V0",
    "method": "B",
    "error_type": "RuntimeError",
    "error_message": "provider curl request timed out after 60 seconds",
    "attempts": 4,
    "latency_seconds": 246.083,
    "http_status": null
  }
]
```

---

## 4. 实现建议与处理步骤

### 推荐工具
- 使用标准 Python 3.12+ 脚本，利用标准库 `json`、`pathlib`、`math` 处理，保证环境轻量无外部强依赖。

### 处理流程
1. **扫描遍历**：按组号排序遍历 `test_001.json` 至 `test_040.json`；
2. **逐项解析**：提取每个变体的 `gold_intent`、`oracle_route`、`calls`、`candidates` 与 `routes`；
3. **指标计算**：
   - POIs 对比使用集合匹配：`set(candidate.get("pois", [])) == set(gold.get("pois", []))`；
   - 依赖对比使用标准化集合匹配；
   - 权重 MAE 仅统计有效输出的差值绝对值；
4. **边界与容错处理**：
   - 若某方法因超时或网络错误未返回有效 candidate，该样本计入该方法的 `errors`，在计算有效精度时正确维护完整分母与有效分母；
   - 路线为 null 但 candidate 存在时，正确记录为规划失败（Task Success = False），不抛出 KeyError。
5. **输出持久化**：格式化写入三个目标文件。
