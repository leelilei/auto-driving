# ChinaTravel 环境验收记录

**日期**: 2026-09-11  
**目标**: 建立可复现的ChinaTravel评分管线  
**状态**: IN_PROGRESS

---

## 版本固定

### 代码仓库
- **Repository**: https://github.com/LAMDA-NeSy/ChinaTravel
- **Target Commit**: `0936f2727dd102ad811ed015b7bf6f7d6533f28e`
- **实际Commit**: `0936f2727dd102ad811ed015b7bf6f7d6533f28e` ✓
- **Checkout日期**: 2026-09-11
- **本地路径**: `/Users/mac/Documents/6-Research/9-AutoDriving/external/ChinaTravel`

### Python环境
- **要求版本**: >=3.12
- **当前系统**: Python 3.x (待确认实际版本)
- **环境策略**: 独立虚拟环境 `.venv-chinatravel`

---

## 依赖清单

从 `requirements.txt` 和 `pyproject.toml`:

| 包名 | 版本要求 | 用途 |
|---|---|---|
| datasets | 3.3.2 | Hugging Face数据加载 |
| func-timeout | 4.3.5 | 超时控制 |
| fuzzywuzzy | 0.18.0 | 模糊匹配 |
| geopy | 2.4.1 | 地理计算 |
| json-repair | 0.30.0 | JSON修复 |
| jsonschema | 4.23.0 | Schema验证 |
| numpy | 1.26.4 | 数值计算 |
| openai | >=1.66.0 | OpenAI API |
| pandas | 2.2.3 | 数据处理 |
| scikit-learn | 1.5.2 | 机器学习 |
| tqdm | 4.66.6 | 进度条 |

---

## 关键代码结构

### Oracle字段定义 (chinatravel/data/load_datasets.py:48)
```python
ORACLE_FIELDS = {"hard_logic", "hard_logic_py", "hard_logic_nl"}
```

**关键发现**:
- Oracle字段在Hugging Face默认加载时会被自动去除
- 本地加载时需显式检查 `oracle_translation` 参数
- 我们的实验**必须确保**这些字段不进入模型输入

### 评分器模块 (chinatravel/evaluation/)
- `hard_constraint.py`: 硬约束评价（V2评价器）
- `commonsense_constraint.py`: 常识约束
- `preference.py`: 偏好评分
- `schema_constraint.py`: Schema验证

### 数据加载函数
- `_load_huggingface_split()`: 从HF加载（自动去除oracle）
- `_resolve_local_query_paths()`: 本地加载（需手动检查oracle）
- `_strip_oracle_fields()`: 显式去除oracle字段
- `_validate_query_record()`: 验证数据格式

---

## 待验证项

### 任务1: 数据下载与清单
- [ ] 下载Phase 1数据（easy 300 + medium 150 + human 154）
- [ ] 记录数据revision和manifest SHA256
- [ ] 验证数据行数与官方声明一致
- [ ] 下载sandbox（2026.08.1或更新版本）
- [ ] 生成sandbox文件清单

### 任务2: 环境安装
- [ ] 创建独立虚拟环境
- [ ] 安装全部依赖
- [ ] 记录实际安装版本 (`pip freeze`)
- [ ] 验证import无错误

### 任务3: 评分器功能验证
测试用例：
- [ ] 官方示例输出（应全部通过）
- [ ] 空输出（应计为失败）
- [ ] 无效实体（不在sandbox，应失败）
- [ ] 时间冲突（应失败micro约束）
- [ ] 部分缺失预测（验证分母处理）

### 任务4: Oracle隔离验证
- [ ] 实现字段白名单检查
- [ ] 实现哨兵标签测试
- [ ] 验证oracle字段不进入prompt
- [ ] 保存3个实际prompt示例

### 任务5: 开发分区设计
- [ ] 设计dev/hold split方案
- [ ] 固定随机种子
- [ ] 记录分区逻辑
- [ ] 生成split清单文件

---

## 许可证合规

### 代码许可
- **仓库LICENSE**: 待确认（审计文档提到metadata未识别）
- **推测**: 开源许可（基于学术项目性质）
- **验证**: 需查看LICENSE文件或联系作者

### 数据许可
- **Hugging Face数据卡**: CC-BY-NC-SA-4.0
- **限制**: 非商业、相同方式共享
- **允许**: 学术研究、修改、分发（需遵守许可）

**合规策略**:
- ✓ 本项目为学术研究
- ✓ 不商业使用
- ✓ 不重新分发原始数据（仅引用官方源）
- ✓ 结果需标注数据来源

---

## 下一步行动

1. **立即**: 创建虚拟环境并安装依赖
2. **今天**: 下载Phase 1数据，验证清单
3. **明天**: 运行评分器功能测试
4. **本周**: 完成oracle隔离验证

---

## 更新日志

- 2026-09-11 10:00: 仓库clone完成，版本固定
- 2026-09-11 10:15: 代码结构审查完成，识别oracle字段机制
