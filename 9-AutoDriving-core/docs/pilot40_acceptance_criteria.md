# Pilot40 实验结果分析 - 验收标准

## 1. 数据完整性验证

### 必须通过 ✅
- [ ] 所有 40 个测试组（test_001 到 test_040）的 JSON 文件都能成功加载
- [ ] 每个测试组包含 4 个 utterances（V0, V1, V2, V3）
- [ ] 总计 160 个 utterances 被正确统计
- [ ] 没有文件解析错误或格式异常

### 预期容忍 ⚠️
- 部分 method 调用可能因超时或其他错误而缺失（记录但不算作验收失败）
- 部分 routes 可能为空（需记录原因）

---

## 2. 汇总报告质量（pilot40_summary.json）

### 必须包含的顶层字段 ✅
- [ ] `run_info`: 包含 run_dir, total_groups, total_utterances, analysis_date
- [ ] `schema_validity`: A, B, review 三个方法的统计
- [ ] `intent_accuracy`: 意图提取准确性指标
- [ ] `route_quality`: 路由质量指标
- [ ] `errors`: 错误统计
- [ ] `performance`: 性能指标

### Schema 有效性统计 ✅
每个方法（A, B, review）必须包含：
- [ ] `valid`: schema_valid = true 的数量
- [ ] `total`: 尝试调用的总数（不含因超时等未执行的）
- [ ] `rate`: valid / total 的比率

**预期范围**:
- 方法 A 的 schema validity rate ≥ 0.90
- 方法 B 的 schema validity rate ≥ 0.85（可能因超时导致更低）
- Review 的 schema validity rate ≥ 0.90

### 意图准确性指标 ✅
每个方法必须计算：
- [ ] `pois_exact_match`: POIs 数组完全匹配 gold_intent 的比例
- [ ] `time_limit_match`: time_limit 匹配的比例
- [ ] `dependencies_match`: dependencies 数组完全匹配的比例
- [ ] `quality_weight_mae`: quality_weight 的平均绝对误差

**预期范围**:
- POIs exact match ≥ 0.85（高优先级指标）
- Time limit match ≥ 0.90
- Quality weight MAE ≤ 0.15

### 路由质量指标 ✅
方法 A 和 B 必须计算（review 不产生路由）：
- [ ] `task_success_rate`: oracle_check.task_success = true 的比例
- [ ] `full_coverage_rate`: is_full_coverage = true 的比例
- [ ] `avg_utility`: 平均路由效用
- [ ] `avg_utility_gap_vs_oracle`: 与 oracle_route utility 的平均差距
- [ ] `avg_distance_km`: 平均总距离
- [ ] `avg_arrival_minutes`: 平均最终到达时间

**预期范围**:
- Task success rate ≥ 0.80
- Full coverage rate ≥ 0.85
- Avg utility gap vs oracle ≤ 0.10（越小越好）

### 错误统计 ✅
每个方法必须统计：
- [ ] `timeout`: 超时错误数量
- [ ] `other`: 其他类型错误数量

**预期情况**:
- 方法 B 可能有 5-20 个超时（基于 test_001 的观察）
- 方法 A 和 review 超时应少于 5 个

### 性能统计 ✅
每个方法必须包含：
- [ ] `avg_latency_seconds`: 平均响应延迟
- [ ] `total_tokens`: 总 token 消耗
- [ ] `avg_attempts`: 平均重试次数

**预期范围**:
- 方法 A 平均延迟 10-20 秒
- 方法 B 平均延迟 20-60 秒（含超时重试）
- Review 平均延迟 10-30 秒
- 平均重试次数 ≤ 1.5

---

## 3. 详细分析报告质量（pilot40_analysis.md）

### 必须包含的章节 ✅
- [ ] **执行摘要**: 3-5 句话，突出关键发现和结论
- [ ] **数据完整性**: 文件数、utterances 数、缺失或错误情况
- [ ] **Schema 有效性对比**: A vs B vs review 的对比表格
- [ ] **意图准确性分析**: 各方法在 POIs、time_limit、dependencies、quality_weight 上的表现
- [ ] **路由质量分析**: A vs B 的路由成功率、覆盖率、效用对比
- [ ] **错误分析**: 分类统计各类错误，识别模式
- [ ] **性能分析**: 延迟、token 消耗、重试对比
- [ ] **结论和建议**: 基于数据的明确结论（2-4 条）

### 表格格式要求 ✅
- [ ] 使用 Markdown 表格，列对齐清晰
- [ ] 百分比保留 1 位小数（如 92.5%）
- [ ] 数值保留 2-3 位小数（如 0.385, 12.45 km）

### 分析深度 ✅
- [ ] 不仅报告数字，还需解释差异（如"方法 B 的超时率高达 X%，主要集中在 V0 和 V1 变体"）
- [ ] 识别至少 2-3 个关键模式或问题
- [ ] 提供可操作的建议（如"建议增加超时阈值"或"方法 A 已足够，可简化流程"）

---

## 4. 错误案例列表质量（pilot40_errors.json）

### 格式要求 ✅
- [ ] JSON 数组格式，每个元素是一个错误案例
- [ ] 每个案例必须包含: group_id, utterance_id, method, error_type, error_message
- [ ] 可选字段: attempts, latency_seconds, http_status

### 完整性 ✅
- [ ] 记录所有 `schema_valid = false` 的案例
- [ ] 记录所有包含 `transport_error_type` 或 `error_message` 的案例
- [ ] 记录所有 `success = false` 的 telemetry

### 可读性 ✅
- [ ] 错误按 group_id 升序排序
- [ ] Error message 保留原始完整信息
- [ ] 易于快速筛选特定错误类型

---

## 5. 计算正确性验证

### 抽查验证 ✅
从 test_001.json 手动验证以下计算：

#### Schema 有效性（test_001, utterance v0）
- [ ] 方法 A: schema_valid = true ✓
- [ ] 方法 B: schema_valid = false（超时）✓
- [ ] 如果汇总报告中方法 A 的 valid 计数包含此案例，则正确

#### 意图准确性（test_001, utterance v0）
- Gold intent: pois = ["bank", "library"], quality_weight = 0.6
- 方法 A 提取: pois = ["library", "bank"], quality_weight = 0.5
- [ ] POIs exact match 应记为不匹配（顺序不同或集合相同？需明确规则）
- [ ] Quality weight 误差 = |0.5 - 0.6| = 0.1

#### 路由质量（test_001, utterance v2）
- Oracle utility: 0.3923
- 方法 A route utility: 0.6044
- [ ] Utility gap = 0.6044 - 0.3923 = 0.2121

如果以上计算在汇总报告中一致，则验收通过。

---

## 6. 交付物检查清单

### 文件存在性 ✅
- [ ] `results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/pilot40_summary.json` 存在
- [ ] `results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/pilot40_analysis.md` 存在
- [ ] `results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/pilot40_errors.json` 存在

### 文件大小合理性 ✅
- [ ] pilot40_summary.json: 2-10 KB
- [ ] pilot40_analysis.md: 5-50 KB
- [ ] pilot40_errors.json: 1-100 KB（取决于错误数量）

### 可读性 ✅
- [ ] JSON 文件格式化良好（使用 `json.dumps(indent=2)`）
- [ ] Markdown 使用标题层级清晰
- [ ] 没有明显的拼写或语法错误

---

## 7. 关键决策点验收

### 比较逻辑 ✅
- [ ] POIs 比较规则已明确：顺序无关的集合比较 OR 顺序相关的数组比较？
  - **推荐**: 使用集合比较（`set(extracted_pois) == set(gold_pois)`）
- [ ] Dependencies 比较：顺序无关的集合比较
- [ ] Quality weight 允许的误差范围：建议 ±0.05 内视为匹配，超出则计算 MAE

### 缺失数据处理 ✅
- [ ] 如果某个 method 因超时未返回结果，该 utterance 在该 method 的统计中：
  - Schema validity: 不计入分母（total）
  - Intent accuracy: 不计入分母
  - 但在 errors 中计数

### 边界情况 ✅
- [ ] Routes 为空但 schema_valid = true：算作 route 失败，不影响 intent accuracy
- [ ] Gold intent 中 time_limit = null：只要提取结果也是 null 即匹配
- [ ] Candidates 或 routes 字段完全缺失：标记为数据异常并报告

---

## 8. 最终验收判断

### 通过标准 ✅
满足以下所有条件：
1. 三个输出文件都存在且格式正确
2. 数据完整性验证全部通过
3. 汇总报告包含所有必需字段，数值在预期范围内
4. 详细分析报告包含所有必需章节，提供可操作的建议
5. 错误案例列表完整且可读
6. 至少通过一个手动抽查验证（test_001）

### 条件通过 ⚠️
如果出现以下情况，需人工审查后决定：
- Schema validity rate 低于预期范围但有合理解释
- 超过 30% 的 method B 调用超时（可能需要调整超时设置或重跑）
- Intent accuracy 低于预期但发现系统性问题（如 gold_intent 标注错误）

### 不通过 ❌
出现以下任一情况：
- 文件解析错误或数据缺失超过 5%
- 汇总报告缺少关键字段
- 计算结果明显错误（如 rate > 1.0）
- 分析报告缺少必需章节或无实质内容

---

## 验收执行建议

1. **自动化验收脚本**: 编写一个 `validate_pilot40_outputs.py`，检查文件存在性、字段完整性、数值范围
2. **人工审查**: 重点查看 pilot40_analysis.md 的结论和建议部分
3. **交叉验证**: 使用不同方法计算同一指标，确保一致性

---

## 附录：预期输出示例片段

### pilot40_summary.json 示例结构
```json
{
  "run_info": {
    "run_dir": "20260911T181825Z_main_test_gemini-3-flash_pilot40_net",
    "total_groups": 40,
    "total_utterances": 160,
    "analysis_date": "2026-09-12"
  },
  "schema_validity": {
    "A": {"valid": 158, "total": 160, "rate": 0.988},
    "B": {"valid": 145, "total": 152, "rate": 0.954},
    "review": {"valid": 159, "total": 160, "rate": 0.994}
  },
  "intent_accuracy": {
    "A": {
      "pois_exact_match": 0.925,
      "time_limit_match": 0.975,
      "dependencies_match": 0.963,
      "quality_weight_mae": 0.087
    }
  }
}
```

### pilot40_analysis.md 示例片段
```markdown
## 执行摘要

本次分析覆盖 pilot40 实验的 40 个测试组共 160 个 utterances。方法 A 和 review 的 schema 有效性均超过 98%，但方法 B 因超时问题导致 8 个案例失败。意图提取准确性方面，三种方法在 POIs 识别上的准确率均达到 92% 以上，但 quality_weight 存在系统性低估（MAE ≈ 0.09）。路由质量整体良好，task success rate 达到 89%，但与 oracle 路由相比仍有 8-12% 的效用差距。

## 关键发现

1. **方法 B 超时问题显著**: 8/160 个调用超时（5%），集中在 V0 和 V1 变体，建议增加超时阈值或优化提示词。
2. **Quality weight 低估**: 所有方法对高质量偏好的用户指令倾向于给出较保守的权重（如 0.5 而非 0.7-0.8）。
3. **Review 方法增益有限**: Review 在 intent accuracy 上仅比最优单方法提升 1-2%，考虑到额外成本，可简化为单方法流程。
```
