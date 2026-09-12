# ChinaTravel Stage 3: 强基线实现计划

> **2026-09-11 Codex 后续状态**：下文为 Claude 当时的历史记录，不作为当前验收结论。旧自定义 schema、B0/B1/B2 与替代评分脚本已退出执行入口。当前使用官方三层评分及有预算限制的 Act 适配；13 项离线检查通过；单例实际 8 请求后预算停止，未生成行程，两次断网回放一致。最新状态见 [整改执行记录](CODEX_REMEDIATION_20260911.md)。

**预计时间**: ~3-4天  
**目标**: 实现充分定义的基线方法，在60例dev集上建立性能基准

## 阶段目标

1. ✅ 实现3-4种强基线方法
2. ✅ 在60例dev集上运行完整实验
3. ✅ 收集三层评分结果（Schema/Commonsense/Hard）
4. ✅ 进行错误分类和分析
5. ✅ 回答关键问题：是否存在"任务成功但语义错误"的情况？

## 基线方法设计

### Baseline 0: Direct Prompting (B0)
**描述**: 直接给LLM提供查询，让其生成符合schema的旅行计划

**提示词结构**:
```
你是一个旅行规划助手。根据以下查询生成一个旅行计划：

查询：
- 出发城市：{org}
- 目的地城市：{dest}
- 天数：{days}
- 人数：{people_number}

请生成一个JSON格式的旅行计划，包含每天的详细安排。
```

**预期性能**: 中等，作为最简单基线

### Baseline 1: Few-shot Prompting (B1)
**描述**: 在提示中加入2-3个示例

**提示词结构**:
```
你是一个旅行规划助手。以下是一些示例：

[示例1]
[示例2]

现在请为以下查询生成计划：
...
```

**预期性能**: 应优于B0

### Baseline 2: Chain-of-Thought (B2)
**描述**: 引导模型先推理再生成计划

**提示词结构**:
```
你是一个旅行规划助手。请分步思考：

1. 分析查询需求
2. 考虑城市特点和景点
3. 规划每天行程
4. 生成最终JSON计划

查询：...
```

**预期性能**: 可能更合理，但token消耗更大

### Baseline 3: ReAct-style (B3)
**描述**: 模拟推理+行动循环

**提示词结构**:
```
你可以使用以下工具：
- search_attractions(city): 搜索景点
- search_restaurants(city): 搜索餐厅
- search_hotels(city): 搜索酒店

请按照"思考-行动-观察"的模式生成计划。
```

**预期性能**: 理论上最强，但需要实现工具调用模拟

## 实现架构

```
9-AutoDriving-core/
├── src/
│   ├── baselines/
│   │   ├── __init__.py
│   │   ├── base.py           # 基线基类
│   │   ├── direct.py         # B0: Direct
│   │   ├── fewshot.py        # B1: Few-shot
│   │   ├── cot.py            # B2: CoT
│   │   └── react.py          # B3: ReAct
│   ├── prompts/
│   │   ├── direct.txt
│   │   ├── fewshot.txt
│   │   ├── cot.txt
│   │   └── react.txt
│   └── evaluator_wrapper.py  # 评分器包装
├── scripts/
│   └── stage3_baseline_experiment.py
└── results/
    └── chinatravel_baselines/
        ├── b0_direct/
        ├── b1_fewshot/
        ├── b2_cot/
        └── b3_react/
```

## 实验协议

### 1. 数据准备
- 使用60例dev集（已在阶段1准备）
- Oracle字段已隔离
- 每个案例包含：raw query + gold plan（仅用于评分）

### 2. 运行协议
- **模型**: 先用`claude-haiku-4.5`快速验证，再用`claude-sonnet-5`正式实验
- **温度**: 0.7（平衡确定性和多样性）
- **并发**: 2（避免速率限制）
- **重复次数**: 每个基线运行1次（预算有限）
- **缓存**: 保存所有LLM响应，支持离线replay

### 3. 评分流程
```
对每个生成的计划：
1. Schema验证 (validate_json)
   - 不通过 → 记录为schema_fail，后续评分设为0
2. Commonsense验证 (evaluate_commonsense_constraints)
   - 记录macro/micro准确率
3. Hard Constraint验证 (evaluate_hard_constraints)
   - 记录是否满足自定义约束
4. 与gold对比（如果有参考答案）
```

### 4. 指标收集

**主要指标**:
- Schema通过率: `n_schema_pass / 60`
- Commonsense macro准确率: 平均值
- Commonsense micro准确率: 平均值
- Hard constraint通过率: `n_hard_pass / 60`

**辅助指标**:
- 平均token消耗
- 平均响应时间
- 失败类型分布

### 5. 错误分类

建立如下分类法：

| 错误类型 | 定义 | 示例 |
|---------|------|------|
| E1_schema | JSON格式错误或缺少必需字段 | 缺少`attraction`字段 |
| E2_semantic_conflict | 语义冲突（城市、时间等） | Day1在北京，Day2突然到上海但无交通 |
| E3_missing_info | 缺失关键信息 | 景点列表为空 |
| E4_invalid_reference | 引用不存在的POI | 餐厅ID不在数据库中 |
| E5_constraint_violation | 违反硬约束 | 超出预算、超过天数 |
| E6_suboptimal | 满足约束但次优 | 选择了远距离景点 |

**关键问题**:
- 是否存在E6类型（任务形式成功但语义/质量低）？
- 如果存在，占比多少？这是DARC-Route改进的空间

## 预期输出

### 1. 实验结果表
```
| Baseline | Schema↑ | Comm-Macro↑ | Comm-Micro↑ | Hard↑ | Tokens | Time |
|----------|---------|-------------|-------------|-------|--------|------|
| B0-Direct| 85%     | ?           | ?           | ?     | 2000   | 30s  |
| B1-Fewshot| ?      | ?           | ?           | ?     | 3000   | 45s  |
| B2-CoT   | ?       | ?           | ?           | ?     | 4000   | 60s  |
| B3-ReAct | ?       | ?           | ?           | ?     | 5000   | 90s  |
```

### 2. 错误分布报告
```
B0-Direct错误分布:
- E1_schema: 9例 (15%)
- E2_semantic_conflict: 3例 (5%)
- E3_missing_info: 5例 (8%)
- E4_invalid_reference: 2例 (3%)
- E5_constraint_violation: 1例 (2%)
- E6_suboptimal: ? (待人工审查)
```

### 3. 典型案例分析
- 选择5-10个代表性案例
- 展示各基线的生成结果
- 分析失败原因

## 实现检查清单

### Phase 3.1: 基础设施（Day 1）
- [ ] 创建`baselines/`模块结构
- [ ] 实现基类`BaselineMethod`
- [ ] 实现评分器包装`EvaluatorWrapper`
- [ ] 准备提示词模板
- [ ] 实现缓存和重放机制

### Phase 3.2: 基线实现（Day 2）
- [ ] 实现B0: Direct Prompting
- [ ] 实现B1: Few-shot Prompting
- [ ] 实现B2: Chain-of-Thought
- [ ] （可选）实现B3: ReAct

### Phase 3.3: 实验执行（Day 3）
- [ ] 用Haiku在10例上快速验证
- [ ] 修复bug和提示词
- [ ] 用Sonnet在60例dev集上运行
- [ ] 收集所有评分结果

### Phase 3.4: 分析总结（Day 4）
- [ ] 生成结果表和图表
- [ ] 错误分类和案例分析
- [ ] 撰写阶段3报告
- [ ] 回答关键问题：是否需要DARC-Route？

## 关键决策点

### 决策1: 基线数量
- **选项A**: 只实现B0和B2（最简单+最强）
- **选项B**: 实现B0/B1/B2（逐步增强）
- **选项C**: 实现全部B0/B1/B2/B3
- **建议**: 先B，根据时间预算决定是否做B3

### 决策2: 模型选择
- **选项A**: 只用Haiku（快速、便宜）
- **选项B**: 只用Sonnet（高质量）
- **选项C**: Haiku验证 + Sonnet正式
- **建议**: C，先快速迭代再正式实验

### 决策3: 数据集大小
- **选项A**: 先10例验证
- **选项B**: 直接60例dev
- **选项C**: 60 dev + 部分test
- **建议**: A→B，迭代式推进

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| LLM输出格式不稳定 | 高Schema失败率 | 加强提示词约束，使用JSON mode |
| 数据库查询失败 | 评分中断 | 实现错误处理和降级策略 |
| Token预算超支 | 无法完成实验 | 先用Haiku验证，控制并发 |
| 所有基线都很弱 | 找不到改进空间 | 这反而证明任务有挑战性 |
| 所有基线都很强 | DARC无用武之地 | 需要重新设计任务或标准 |

## 成功标准

✅ **阶段3成功条件**:
1. 至少2种基线在60例dev集上完整运行
2. 三层评分结果完整收集
3. 错误类型分类清晰
4. 能够回答：是否存在"形式成功但质量低"的案例
5. 为阶段4（DARC-Route实现）提供明确的改进方向

## 下一步（阶段4）

根据阶段3结果决定：

- **情况A**: 基线已经很强 → 重新审视DARC的必要性
- **情况B**: 存在明显的"语义错误"问题 → 实现DARC-Route
- **情况C**: 所有方法都很弱 → 简化任务或改进数据质量

---

**制定日期**: 2026-09-11  
**预计开始**: 2026-09-11  
**预计完成**: 2026-09-14
