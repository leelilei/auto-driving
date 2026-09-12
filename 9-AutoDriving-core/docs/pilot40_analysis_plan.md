# Pilot40 实验结果分析计划

## 任务背景

ChinaTravel 实验已完成 pilot40 的数据采集（40个测试用例），采集时间为 2026-09-11。需要对原始结果数据进行全面分析，生成评分报告和诊断摘要。

## 数据位置

- **运行目录**: `results/runs/20260911T181825Z_main_test_gemini-3-flash_pilot40_net/`
- **数据格式**: 每个测试用例包含两个文件
  - `test_XXX.json`: 完整的测试结果（包含 utterances, calls, candidates, routes）
  - `test_XXX_graph.json`: 图数据（如果存在）
- **测试用例数量**: 40 个（test_001 到 test_040）

## 任务目标

### 1. 数据完整性检查
- 验证所有 40 个测试文件都存在且格式正确
- 检查每个文件包含的 utterances 数量（应为 4 个变体：V0, V1, V2, V3）
- 统计每个 utterance 的 calls 完成情况（A, B, review）

### 2. 方法评估指标计算

对每个方法（A, B, review）计算以下指标：

#### Schema 有效性
- `schema_valid = true` 的比例
- 按变体类型（V0, V1, V2, V3）分组统计

#### 意图提取准确性
将提取结果与 gold_intent 对比：
- POIs 完全匹配率
- Time limit 匹配率
- Dependencies 匹配率
- Quality weight 误差（计算平均绝对误差 MAE）

#### 路由质量
- Task success 率（基于 oracle_check）
- Full coverage 率
- 平均 utility（与 oracle_route 的 utility 对比）
- 平均距离（total_distance）
- 平均到达时间（final_arrival_time）

### 3. 方法对比分析

#### A vs B 对比
- Schema 有效性差异
- 意图准确性差异
- 是否有显著的性能或质量差异

#### Review 方法效果
- Review 是否修正了 A 或 B 的错误
- Review 的最终准确率

### 4. 错误分析

#### API 调用错误
- 统计超时错误数量（如 test_001 utterance_v0 的 method B 超时）
- 统计其他 transport_error_type
- 按方法和变体类型分组

#### 意图提取错误模式
- POIs 缺失或多余
- Quality weight 系统性偏差
- Dependencies 误判模式

### 5. 延迟和成本统计

- 每个方法的平均 latency_seconds
- Token 使用量统计（input_tokens, output_tokens, total_tokens）
- Attempts 重试统计

## 输出要求

### 1. 汇总报告 (`pilot40_summary.json`)

```json
{
  "run_info": {
    "run_dir": "20260911T181825Z_main_test_gemini-3-flash_pilot40_net",
    "total_groups": 40,
    "total_utterances": 160,
    "analysis_date": "2026-09-12"
  },
  "schema_validity": {
    "A": {"valid": X, "total": Y, "rate": Z},
    "B": {...},
    "review": {...}
  },
  "intent_accuracy": {
    "A": {
      "pois_exact_match": 0.XX,
      "time_limit_match": 0.XX,
      "dependencies_match": 0.XX,
      "quality_weight_mae": 0.XX
    },
    "B": {...},
    "review": {...}
  },
  "route_quality": {
    "A": {
      "task_success_rate": 0.XX,
      "full_coverage_rate": 0.XX,
      "avg_utility": 0.XX,
      "avg_utility_gap_vs_oracle": 0.XX,
      "avg_distance_km": XX.XX,
      "avg_arrival_minutes": XXX
    },
    "B": {...}
  },
  "errors": {
    "A": {"timeout": X, "other": Y},
    "B": {...},
    "review": {...}
  },
  "performance": {
    "A": {
      "avg_latency_seconds": XX.XX,
      "total_tokens": XXXXX,
      "avg_attempts": X.XX
    },
    "B": {...},
    "review": {...}
  }
}
```

### 2. 详细分析报告 (`pilot40_analysis.md`)

Markdown 格式，包含：
- 执行摘要（3-5 句话总结关键发现）
- 数据完整性报告
- 各方法评估结果对比表格
- 错误分析章节
- 性能统计图表（文本表格形式）
- 结论和建议

### 3. 错误案例列表 (`pilot40_errors.json`)

记录所有出现错误的案例：
```json
[
  {
    "group_id": "test_001",
    "utterance_id": "test_001_v0",
    "method": "B",
    "error_type": "RuntimeError",
    "error_message": "provider curl request timed out after 60 seconds",
    "attempts": 4,
    "latency_seconds": 246.083
  },
  ...
]
```

## 实现建议

### 推荐工具
- Python 脚本（使用 json, pandas, numpy）
- 或使用现有的 evaluate.py / score.py 脚本（如果适用）

### 处理步骤
1. 遍历所有 test_XXX.json 文件
2. 解析每个文件的 utterances 数组
3. 对每个 utterance 提取 gold_intent, calls, candidates, routes, oracle_check
4. 计算各项指标并聚合
5. 生成三个输出文件

### 边界情况处理
- 处理缺失的 calls（如 method B 超时导致没有结果）
- 处理 schema_valid = false 的情况
- 处理 routes 为空或失败的情况

## 验收标准

参见配套的 `pilot40_acceptance_criteria.md` 文档。
