# ⚠️ Oracle字段泄露问题报告

**发现日期**: 2026-09-11  
**严重性**: HIGH - 阻塞实验公平性  
**状态**: 已识别，待解决

---

## 问题描述

从Hugging Face下载的ChinaTravel Phase 1数据中，**oracle字段 `hard_logic_py` 仍然存在**。

### 预期行为（来自审计文档）
```python
# chinatravel/data/load_datasets.py
ORACLE_FIELDS = {"hard_logic", "hard_logic_py", "hard_logic_nl"}

# HF默认加载应自动去除这些字段
def _load_huggingface_split(split):
    # 默认config应该去除oracle字段
    return hg_load_dataset(...)[split].to_list()
```

### 实际行为
```json
{
  "splits": {
    "easy": {
      "fields": [..., "hard_logic_py", ...],
      "oracle_fields_present": ["hard_logic_py"]
    },
    "medium": {
      "fields": [..., "hard_logic_py", ...],
      "oracle_fields_present": ["hard_logic_py"]
    },
    "human": {
      "fields": [..., "hard_logic_py", ...],
      "oracle_fields_present": ["hard_logic_py"]
    }
  },
  "oracle_isolation_verified": false
}
```

---

## 影响分析

### 实验公平性风险
1. **模型可能意外访问Gold DSL**
   - `hard_logic_py` 是可执行的Python约束
   - 如果进入prompt，模型可以直接看到正确答案

2. **无法与oracle模式公平对比**
   - 官方区分普通模式 vs `oracle_translation=True`
   - 如果普通模式已含oracle字段，对比失效

3. **评分器权限混淆**
   - 评分器应该独立执行 `hard_logic_py`
   - 模型不应该在生成时看到它

---

## 根因分析

### 可能原因1: 数据版本更新
- 2026.08.20修订了28条记录
- 可能同时改变了字段发布策略
- 旧的"默认去除oracle"假设不再成立

### 可能原因2: 加载方式不同
代码中有两种加载方式：
```python
# 方式1: HF默认（我们使用的）
load_dataset('LAMDA-NeSy/ChinaTravel', name='default', split='easy')

# 方式2: 本地加载 + 显式过滤
_strip_oracle_fields(data_i)
```

可能只有方式2才去除oracle字段。

### 可能原因3: Config选择错误
代码中提到 `config_name = "preference" if ... else "default"`，可能需要特定config？

---

## 解决方案

### 方案A: 显式过滤（推荐）⭐
```python
from chinatravel.data.load_datasets import _strip_oracle_fields, ORACLE_FIELDS

def load_phase1_safe(split_name):
    """加载数据并显式去除oracle字段"""
    dataset = load_dataset('LAMDA-NeSy/ChinaTravel', 
                          name='default', 
                          split=split_name)
    
    # 显式去除oracle字段
    cleaned = []
    for example in dataset:
        example_dict = dict(example)
        for oracle_field in ORACLE_FIELDS:
            example_dict.pop(oracle_field, None)
        cleaned.append(example_dict)
    
    return cleaned
```

**优点**:
- 显式、透明
- 可验证（生成前后对比）
- 与代码库提供的工具一致

### 方案B: 使用代码库的加载器
```python
# 查看chinatravel.data.load_datasets是否有正确的公开函数
# 可能需要使用本地加载路径 + oracle_translation=False
```

### 方案C: 白名单字段
```python
ALLOWED_FIELDS = {
    'uid', 'days', 'people_number', 'start_city', 'target_city',
    'nature_language', 'nature_language_en', 
    'limit_rooms', 'limits_room_type', 'tag'
}

def extract_allowed_only(example):
    return {k: v for k, v in example.items() if k in ALLOWED_FIELDS}
```

**优点**: 最严格，完全控制模型可见字段

---

## 实施计划

### 立即行动（P0）
1. [x] 记录oracle泄露问题
2. [ ] 实现方案A（显式过滤函数）
3. [ ] 验证过滤后的数据不含oracle字段
4. [ ] 更新数据清单，标记"已过滤"

### 实验设计要求（P0）
1. **所有实验必须使用过滤后的数据**
2. **生成3个实际prompt示例，验证不含oracle字段**
3. **在prompt中添加哨兵测试**：
   ```python
   # 如果某个查询的hard_logic_py accidentally出现在prompt中
   # 哨兵字符串应该被检测到
   ```

### 文档更新（P1）
- [ ] 更新ENVIRONMENT_SETUP.md
- [ ] 更新DATA_MANIFEST.md
- [ ] 在论文方法部分明确说明oracle隔离机制

---

## 验收标准

实验可以继续的条件：
1. ✅ 实现了显式oracle过滤函数
2. ✅ 生成的manifest显示 `oracle_isolation_verified: true`
3. ✅ 3个实际prompt示例不含任何oracle字段
4. ✅ 哨兵测试通过（故意泄露会被检测）

---

## 与Oracle模式的对比

如果将来需要oracle诊断（评估求解器上限）：

| 模式 | 模型可见 | 用途 | 如何报告 |
|---|---|---|---|
| **普通模式** | query + sandbox（无oracle） | 主实验 | 与同信息条件基线对比 |
| **Oracle模式** | query + sandbox + hard_logic_py | 诊断上限 | 单独表格，不混入主结果 |

当前任务：先完成普通模式的公平实验。

---

## 更新日志

- 2026-09-11 10:30: 发现oracle字段泄露
- 2026-09-11 10:35: 分析根因，设计解决方案
