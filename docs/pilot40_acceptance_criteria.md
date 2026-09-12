# Pilot40 实验结果分析验收标准 (DARC-Route v4)

本验收文档为 DARC-Route v4 体系下 Pilot40（`gemini-3-flash` 模型，40 组意图 × 4 变体 = 160 条自然语言指令）分析任务的质量标准。
分析必须产出 3 个标准化交付物，并按以下 8 大验收维度逐项核验。

---

## 1. 八大验收维度与判断标准

### 维度 1：数据完整性验证 (Data Integrity)
- **必须通过 ✅**：
  - 40 组测试文件（`test_001.json` 至 `test_040.json`）及对应的 `test_XXX_graph.json` 全部成功加载；
  - 每个测试组严格包含 4 个变体（$V_0, V_1, V_2, V_3$），累计处理且统计的 utterance 总数精确等于 160；
  - 没有任何文件存在 JSON 截断、乱码或结构破坏。
- **预期容忍 ⚠️**：
  - 个别调用因提供商网络或超时导致缺失（如方法 B 的超时），只要保留原始 telemetry 记录，不判定为数据丢失。
- **不通过 ❌**：
  - 测试组数量不足 40 个，或 utterance 统计总数偏离 160。

---

### 维度 2：汇总报告质量 (`pilot40_summary.json`)
- **必须通过 ✅**：
  - 顶层必须包含完整的 6 个基础对象：`run_info`、`schema_validity`、`intent_accuracy`、`route_quality`、`errors`、`performance`；
  - 每个对象下均需对方法 A、方法 B、Review 进行严格统计；
  - 所有比率和概率指标落在 $[0.0, 1.0]$ 区间内，无除以零错误（NaN / null）。
- **预期容忍 ⚠️**：
  - 若 Review 方法未参与路线规划，其 `route_quality` 字段标记为 `null` 或予以显式说明。
- **不通过 ❌**：
  - 缺失任一核心顶层字段；
  - 数值逻辑倒挂（例如 `valid > total`、`rate > 1.0` 或 MAE 为负数）。

---

### 维度 3：详细分析报告质量 (`pilot40_analysis.md`)
- **必须通过 ✅**：
  - 结构必须完整包含：执行摘要、数据完整性审计、各方法评估指标对比表格、路由质量分析、错误分类剖析、性能开销统计、结论与后续建议；
  - 所有对比表格采用标准 Markdown 表格排版，百分比保留 1 位小数（如 `93.8%`），浮点数值保留 2~4 位小数（如 `0.4521`, `15.34 km`）；
  - 分析报告具备实质性洞察，明确解释方法 B 的超时成因与方法 A/Review 的差异。
- **预期容忍 ⚠️**：
  - 图表采用格式化的 Markdown 文本表格替代图形图片。
- **不通过 ❌**：
  - 缺失关键章节；
  - 仅罗列空洞文字或未提供对比数据表格。

---

### 维度 4：错误案例列表质量 (`pilot40_errors.json`)
- **必须通过 ✅**：
  - 采用标准 JSON 数组结构，每个元素表示一个异常记录；
  - 必填字段齐全：`group_id`、`utterance_id`、`method`、`error_type`、`error_message`；
  - 按 `group_id` 升序与变体编号稳定排序；
  - 完整保留所有 `schema_valid = false`、网络超时及 `transport_error_type` 存在的实例。
- **预期容忍 ⚠️**：
  - `http_status` 在超时等本地异常情况下允许为 `null`。
- **不通过 ❌**：
  - 存在遗漏的失败调用；
  - 异常信息被简写丢弃，导致无法追溯原始错误详情。

---

### 维度 5：计算正确性验证（手动抽查 `test_001`）
以 `test_001.json` 为基准抽样验证指标计算逻辑的精确性：
- **抽查点 1：Schema 有效性（`test_001_v0`）**
  - 方法 A：`schema_valid = true` ✅
  - 方法 B：`schema_valid = false`（触发 60 秒超时异常）✅
- **抽查点 2：意图准确性（`test_001_v0`）**
  - `gold_intent`: `pois` = `["bank", "library"]`, `quality_weight` = `0.6`
  - 方法 A 提取: `pois` = `["library", "bank"]`, `quality_weight` = `0.5`
  - POIs 集合判定：无序集合相等（`set == set`），计为匹配 ✅
  - Quality weight 误差：$|0.5 - 0.6| = 0.1$ ✅
- **抽查点 3：路由质量与 Utility Gap（`test_001_v2`）**
  - Oracle 效用：`0.3923`
  - 方法 A 规划效用：`0.6044`
  - 效用差值（Utility Gap）：$|0.6044 - 0.3923| = 0.2121$ ✅
- **判定标准**：
  - **必须通过 ✅**：抽查计算与汇总报告中对应样本统计结果完全吻合。
  - **不通过 ❌**：抽查发现指标计算口径矛盾或公式错误。

---

### 维度 6：交付物检查清单 (Deliverables Checklist)
- **必须通过 ✅**：
  - 3 个目标交付文件均真实生成于运行目录 `9-AutoDriving-core/results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/` 中：
    1. `pilot40_summary.json`
    2. `pilot40_analysis.md`
    3. `pilot40_errors.json`
  - 文件大小处于合理范围：
    - `pilot40_summary.json`: 2 KB ~ 15 KB
    - `pilot40_analysis.md`: 5 KB ~ 50 KB
    - `pilot40_errors.json`: 1 KB ~ 100 KB
  - 格式良好，JSON 文件经 `indent=2` 美化，无解析报错。
- **不通过 ❌**：
  - 文件缺失、空文件或格式非法。

---

### 维度 7：关键决策点验收 (Key Decision Points)
- **POIs 比较逻辑**：
  - 必须采用**顺序无关的集合比较**（`set(extracted) == set(gold)`），不得因为类别书写先后（如 `["bank", "library"]` vs `["library", "bank"]`）误判为错误。
- **缺失与异常数据处理**：
  - 因网络超时未返回结果的方法调用，该 utterance 在计算该方法的有效精度时不计入分子，但在分母账本与 `errors` 统计中必须显式保留，同时记录完整分母（Total Attempts）与有效分母（Successful Responses）。
- **规划边界情况**：
  - 意图提取成功但路线求解未找到可行解（`routes[method] == null`）时，计为 `task_success = false`，不影响其作为意图解析成功的评定。

---

### 维度 8：最终判断结论标准

| 结论等级 | 判定准则 |
|---|---|
| **完全通过 (PASS) ✅** | 全部 6 个交付物指标与 8 个维度完全满足，抽查一致，指标在合理预期区间内。 |
| **条件通过 (CONDITIONAL) ⚠️** | 核心文件齐全，抽查正确，但指标轻微超出预期（如方法 B 超时率略高，或某变体表现异常），附带详细归因解释。 |
| **不通过 (FAIL) ❌** | 数据条目缺失、文件格式崩溃、计算逻辑错误（如集合匹配按序列判错）、或缺少关键交付文件。 |

---

## 2. 核心指标预期数值范围

在 `gemini-3-flash` 模型下，依据 v4 受控实验经验，指标应满足以下基准范围：

| 评估指标 | 预期基准范围 | 关注说明 |
|---|---|---|
| **Schema Validity Rate** | $\ge 90.0\%$ | 格式必须高度稳健，方法 A 与 Review 通常应接近 95%~100% |
| **POIs Exact Match** | $\ge 85.0\%$ | 核心类别识别能力，集合匹配通常达 90% 以上 |
| **Time Limit Match** | $\ge 90.0\%$ | 截止时间数字及 null 状态提取能力 |
| **Task Success Rate** | $\ge 80.0\%$ | 求解器在提取约束下规划出的路线合法率 |
| **Quality Weight MAE** | $\le 0.15$ | 连续偏好权重评估偏差 |
| **方法 B 超时数量** | **预期 5 ~ 20 个** | 证据抽取长文本提示词可能导致部分网络超时，属预期已知边界 |

---

## 3. 交付物示例片段

### 3.1 `pilot40_summary.json` 示例片段
```json
{
  "run_info": {
    "run_dir": "20260911T181825Z_main_test_gemini-3-flash_pilot40_net",
    "total_groups": 40,
    "total_utterances": 160,
    "analysis_date": "2026-09-12"
  },
  "schema_validity": {
    "A": { "valid": 160, "total": 160, "rate": 1.0 },
    "B": { "valid": 146, "total": 160, "rate": 0.9125 },
    "review": { "valid": 160, "total": 160, "rate": 1.0 }
  },
  "intent_accuracy": {
    "A": {
      "pois_exact_match": 0.9375,
      "time_limit_match": 0.975,
      "dependencies_match": 0.9875,
      "quality_weight_mae": 0.0825
    }
  }
}
```

### 3.2 `pilot40_analysis.md` 执行摘要与关键发现片段
```markdown
## 执行摘要

本报告对 DARC-Route v4 体系下的 Pilot40 基准实验（`gemini-3-flash` 模型）进行了全面验收。全量 40 组共 160 条变体指令均成功导入。在方法评估中，方法 A 保持了 100% 的 Schema 有效性与 93.8% 的 POI 识别准确率；方法 B 因提示词包含逐字段短语引用证据要求，出现了 14 次网络 curl 超时（占 8.8%），但在完成响应的样本中意图质量依然优异。整体路线规划成功率（Task Success Rate）达到 88.8%，验证了 v4 精确枚举求解器与直接解析接口的有效衔接。

## 关键发现

1. **证据提示词对 API 稳定性的影响**：方法 B 要求输出带原文短语证据的 JSON，导致输出 Token 明显增加，在并发或长链路上诱发了 14 次超时；而简洁的方法 A 无任何超时。
2. **POI 识别表现稳健**：无论是原句（V0）还是口语化噪声句（V3），Gemini 3 Flash 对五类基础 POI 的提取准确率均稳定在 90% 以上。
3. **连续权重倾向中值**：模型提取的 quality_weight 大多集中在 0.5 与 0.8 附近，存在微小的中庸化平滑效应，但下游路线规划受其影响在可控范围内。
```

### 3.3 `pilot40_errors.json` 示例片段
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
