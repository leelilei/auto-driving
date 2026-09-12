# ChinaTravel 数据清单

**下载日期**: 2026-09-11  
**数据源**: Hugging Face `LAMDA-NeSy/ChinaTravel`  
**配置**: `name='default'`

---

## Phase 1 数据统计

### 官方声明（来自数据卡）
- easy: 300 examples
- medium: 150 examples  
- human: 154 examples
- **总计**: 604 examples

### 实际下载验证
**状态**: PENDING（下载中）

| Split | 预期数量 | 实际数量 | 状态 |
|---|---:|---:|---|
| easy | 300 | TBD | ⏳ |
| medium | 150 | TBD | ⏳ |
| human | 154 | TBD | ⏳ |
| **总计** | 604 | TBD | ⏳ |

---

## Oracle字段隔离验证

### 预期行为（来自代码审查）
```python
# chinatravel/data/load_datasets.py:48
ORACLE_FIELDS = {"hard_logic", "hard_logic_py", "hard_logic_nl"}

# Hugging Face默认加载应自动去除这些字段
```

### 实际验证
**状态**: PENDING

- [ ] 确认HF加载时oracle字段被去除
- [ ] 记录可用字段清单
- [ ] 验证uid、query等关键字段存在

---

## 数据修订历史（来自数据卡）

### 2026.08.20 修订
- 修订了28条Phase 1记录
- 要求sandbox版本 >= 2026.08.1
- 声称修订后604条Phase 1均有通过当前评分器的计划

**重要**: 不能使用旧版sandbox或旧版数据

---

## Sandbox数据

### 要求
- **最低版本**: 2026.08.1
- **来源**: Hugging Face `LAMDA-NeSy/ChinaTravel-Sandbox`
- **内容**: 城市、交通、住宿、餐饮、景点信息

### 下载状态
**状态**: NOT_STARTED

- [ ] 下载sandbox数据
- [ ] 验证版本日期
- [ ] 生成文件清单和SHA256
- [ ] 确认实体覆盖范围

---

## 数据完整性

### Manifest生成
待生成以下清单：

1. **数据清单**: `data_manifest.json`
   - 各split的SHA256
   - 实际行数
   - 字段清单
   - uid范围

2. **Sandbox清单**: `sandbox_manifest.json`
   - 文件列表和大小
   - SHA256哈希
   - 实体统计

---

## 开发/Hold分区设计

### 原则
- Phase 1总计604例，无官方train/dev split
- Phase 2的human1000保留不访问（确认集候选）
- 需要设计透明的dev/hold分区

### 候选方案

#### 方案A: 按难度分层抽样（推荐）
```python
dev_split = {
    'easy': 30,      # 10% of 300
    'medium': 15,    # 10% of 150
    'human': 15,     # ~10% of 154
}
# Total dev: 60 examples
# Total hold: 544 examples
```

**优点**:
- 保持难度分布
- 开发集规模合理（60例）
- 按id前缀分区（透明、可重现）

#### 方案B: 随机抽样（固定种子）
```python
np.random.seed(20260911)
# 按uid分层抽样60例
```

**优点**:
- 真正随机
- 可重现

**缺点**:
- 需要完整uid列表才能确定

### 决策
**待定** - 需要先看到实际数据和uid分布

---

## 许可证与引用

### 数据许可
- **License**: CC-BY-NC-SA-4.0
- **限制**: 非商业使用、相同方式共享
- **允许**: 学术研究、修改、本地缓存

### 引用信息
```bibtex
@inproceedings{chinatravel2026,
  title={ChinaTravel: An Open-Ended Travel Planning Benchmark with Compositional Constraint Validation for Language Agents},
  author={Shao, Junjie and others},
  booktitle={ICLR},
  year={2026}
}
```

---

## 下一步

1. **等待数据下载完成**
2. **生成完整manifest**
3. **设计并固定dev/hold split**
4. **下载sandbox数据**
5. **更新本文档验证状态**
