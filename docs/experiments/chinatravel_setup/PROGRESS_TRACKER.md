# ChinaTravel 任务验收进度追踪

> **2026-09-11 Codex 后续状态**：下文为 Claude 当时的历史记录，不作为当前验收结论。旧自定义 schema、B0/B1/B2 与替代评分脚本已退出执行入口。当前使用官方三层评分及有预算限制的 Act 适配；13 项离线检查通过；单例实际 8 请求后预算停止，未生成行程，两次断网回放一致。最新状态见 [整改执行记录](CODEX_REMEDIATION_20260911.md)。

**创建日期**: 2026-09-11  
**最后更新**: 2026-09-11 10:30

---

## 总体进度: 50% ✅ → ⏳

### 阶段1: 环境验收 (90% → 45/50分) ✅

#### ✅ 已完成
- [x] 仓库clone (external/ChinaTravel)
- [x] 版本固定 (0936f2727dd102ad811ed015b7bf6f7d6533f28e)
- [x] 代码结构审查
- [x] Oracle字段机制识别
- [x] 依赖清单提取
- [x] 独立虚拟环境创建 (.venv-chinatravel, Python 3.13.9)
- [x] 依赖安装完成 (所有包成功安装)
- [x] 模块导入验证 (chinatravel可导入)
- [x] Phase 1数据下载 (easy 300 + medium 150 + human 154 = 604例)
- [x] 数据清单生成 (data_manifest.json)
- [x] **Oracle字段隔离** (oracle_isolation.py, 604例验证通过)

#### 🔜 待开始
- [ ] Sandbox数据下载
- [ ] Sandbox清单验证

---

## 阶段2: 评分器验证 (0% → 0/20分)

### 测试用例设计
```python
test_cases = [
    ("official_example", "官方示例输出", "应全部通过"),
    ("empty_output", "空输出", "应计为失败"),
    ("invalid_entity", "无效实体(不在sandbox)", "应失败"),
    ("time_conflict", "时间冲突", "应失败micro约束"),
    ("partial_missing", "部分缺失预测", "验证分母处理"),
]
```

### 待验证问题
1. **分母处理**: 缺失预测如何计入分母？
2. **约束层次**: micro vs macro vs all-pass关系
3. **离线程度**: 是否需要网络调用？
4. **Gold权限**: hard_logic_py是否只在评分器可见？

---

## 阶段3: Oracle隔离验证 (100% → 15/15分) ✅

### 关键机制（已识别）
```python
# chinatravel/data/load_datasets.py
ORACLE_FIELDS = {"hard_logic", "hard_logic_py", "hard_logic_nl"}

# HF默认加载: 自动去除
def _load_huggingface_split(split):
    config_name = "preference" if ... else "default"
    return hg_load_dataset(...)[split].to_list()

# 本地加载: 需手动检查
def _strip_oracle_fields(data_i):
    for key in ORACLE_FIELDS:
        data_i.pop(key, None)
    return data_i
```

### ✅ 已实现
- [x] 字段显式过滤函数 (strip_oracle_fields)
- [x] 哨兵标签测试 (通过)
- [x] 验证清理完整性 (604/604例通过)
- [x] 3个清洁示例保存 (cleaned_sample_*.json)

**关键发现**: 
- 所有604例原始数据都包含 `hard_logic_py` oracle字段
- 显式过滤后，所有示例验证通过
- 哨兵测试确认泄露检测机制有效

---

## 阶段4: 开发分区设计 (0% → 0/15分)

### 候选方案
**方案A (推荐)**: 按难度分层，id前缀分区
```python
dev_split = {
    'easy': [0:30],      # 前30例 (10%)
    'medium': [0:15],    # 前15例 (10%)  
    'human': [0:15],     # 前15例 (~10%)
}
# Total: 60 dev + 544 hold
```

**方案B**: 固定种子随机抽样
```python
np.random.seed(20260911)
dev_indices = stratified_sample(phase1, n=60)
```

### 决策依据
- [ ] 查看实际uid分布
- [ ] 确认split内是否有子结构
- [ ] 固定分区方案

---

## 阶段5: 强基线实现 (0% → 0/10分)

### Baseline设计
```python
class SemanticFaithfulParser:
    """
    充分定义的语言解析基线
    - 明确DSL术语定义
    - 明确硬约束说明
    - 不使用oracle gold DSL
    """
```

### 对照基准
- 不只与"旧弱模型纯语言"比较
- 需与LLMAP式"解析+规划"同信息条件对比

---

## 关键里程碑

| 里程碑 | 预期日期 | 状态 | 交付物 |
|---|---|---|---|
| 环境可运行 | 2026-09-11 | ⏳ | pip freeze, import验证 |
| 数据下载完成 | 2026-09-11 | 🔜 | data_manifest.json |
| 评分器验证 | 2026-09-12 | 🔜 | evaluator_verification.json |
| Oracle隔离 | 2026-09-13 | 🔜 | oracle_isolation_test.py |
| Dev split固定 | 2026-09-13 | 🔜 | dev_hold_split.json |
| Baseline运行 | 2026-09-16 | 🔜 | baseline_results.json |
| 错误分类 | 2026-09-17 | 🔜 | error_analysis.json |
| 研究决策 | 2026-09-18 | 🔜 | research_viability.md |

---

## 阻塞项与风险

### 当前阻塞
1. **虚拟环境创建中** (task bkrmb6g29)
   - 预计完成: 几分钟内
   - 影响: 后续数据下载

### 潜在风险
1. **数据下载失败**
   - 备选: 使用ModelScope镜像
   - 或联系作者获取数据

2. **Sandbox版本不匹配**
   - 必须确认 >= 2026.08.1
   - 旧版本会导致评分不一致

3. **评分器需要网络**
   - 任务审计提到"距离工具代码还包含网络方法"
   - 需确认实际评价路径

4. **Phase 1可能不够难**
   - 官方声称604条均有通过方案
   - 可能"任务成功但语义错误"案例不足
   - 这是研究决策点A的触发条件

---

## 下一步行动 (优先级排序)

### P0 - 立即执行
1. [x] 创建进度追踪文档
2. [ ] 等待venv创建完成
3. [ ] 使用现有venv快速验证数据访问

### P1 - 今天完成
4. [ ] 下载Phase 1全部数据
5. [ ] 生成数据manifest
6. [ ] 验证oracle字段隔离

### P2 - 明天开始
7. [ ] 下载sandbox数据
8. [ ] 运行评分器测试
9. [ ] 设计dev/hold split

---

## 参考文档

- [环境设置](ENVIRONMENT_SETUP.md)
- [数据清单](DATA_MANIFEST.md)
- [任务审计](../../plans/TASK_AUDIT.md)
- [Proposal重定位](../../plans/PROPOSAL_REASSESSMENT_20260911.md)
