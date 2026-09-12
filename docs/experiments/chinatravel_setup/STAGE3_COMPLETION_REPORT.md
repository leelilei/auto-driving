# ChinaTravel 阶段3完成报告

> **2026-09-11 Codex 后续状态**：下文为 Claude 当时的历史记录，不作为当前验收结论。旧自定义 schema、B0/B1/B2 与替代评分脚本已退出执行入口。当前使用官方三层评分及有预算限制的 Act 适配；13 项离线检查通过；单例实际 8 请求后预算停止，未生成行程，两次断网回放一致。最新状态见 [整改执行记录](CODEX_REMEDIATION_20260911.md)。

**日期**: 2026-09-11  
**阶段**: 强基线实现 - 数据准备完成  
**状态**: ✅ 准备就绪，待运行实验

---

## ✅ 本次会话完成的工作

### 1. 数据准备（完成）
- ✅ 从HuggingFace下载60例Phase 1数据
  - easy: 30例
  - medium: 15例  
  - human: 15例
- ✅ 保存到本地：`chinatravel/data/dev_split/`
- ✅ 批量修复数据格式（59个文件）
  - `hard_logic_py`: str → list
  - 添加`query`字段
- ✅ Oracle字段隔离验证
  - `oracle_translation=False`自动过滤敏感字段
  - 模型无法访问`hard_logic_py`等ground truth

### 2. 实验框架（完成）
- ✅ Split配置：`chinatravel/evaluation/default_splits/dev_split.txt`
- ✅ 数据加载验证：60/60例成功
- ✅ 运行脚本：`run_dev_baseline.sh`
- ✅ 测试脚本：`test_single.py`

### 3. 文档（完成）
- ✅ `STAGE3_NEXT_STEPS.md` - 详细操作指南
- ✅ `STAGE3_PROGRESS.md` - 进度追踪
- ✅ `batch_fix_dev_data.py` - 数据修复工具
- ✅ `STAGE3_COMPLETION_REPORT.md` - 本文档

---

## ⏳ 待完成：运行实验

### 阻塞项
**需要API配置** - 选择以下之一：

#### 选项A：Claude API（推荐）
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export CHINATRAVEL_OPENAI_MODEL="claude-3-5-sonnet-20241022"
```

#### 选项B：OpenAI API
```bash
export OPENAI_API_KEY="your-openai-key"
export CHINATRAVEL_OPENAI_MODEL="gpt-4"
```

### 运行步骤

#### 步骤1：单例测试（5分钟）
```bash
cd /Users/mac/Documents/6-Research/9-AutoDriving/external/ChinaTravel

# 配置API（选择一个）
export ANTHROPIC_API_KEY="..."
export CHINATRAVEL_OPENAI_MODEL="claude-3-5-sonnet-20241022"

# 测试单例
.venv-chinatravel/bin/python run_exp.py \
  --splits dev_split \
  --agent Act \
  --llm claude-3-5-sonnet-20241022 \
  --lang zh \
  --index e20241028160248698752

# 检查输出
ls results/Act_claude-3-5-sonnet-20241022_zh/
```

#### 步骤2：小规模验证（15分钟）
```bash
# 运行前3例
bash run_dev_baseline.sh

# 查看评分结果
cat eval_res/splits_dev_split/Act_claude-3-5-sonnet-20241022_zh/schema.csv
```

#### 步骤3：全量实验（2-4小时）
```bash
# 运行全部60例
.venv-chinatravel/bin/python run_exp.py \
  --splits dev_split \
  --agent Act \
  --llm claude-3-5-sonnet-20241022 \
  --lang zh

# 评分
.venv-chinatravel/bin/python eval_exp.py \
  --splits dev_split \
  --method Act_claude-3-5-sonnet-20241022_zh \
  --lang zh
```

#### 步骤4：错误分类（1小时）
分析评分结果，分类：
1. 格式错误（Schema未通过）
2. 常识错误（Commonsense未通过）
3. 硬约束错误（Hard Logic未通过）
4. 完全成功

---

## 📊 当前数据状态

### Dev Split分布
```
Total: 60 examples
├── easy: 30    (e20241028160248698752 ~ e20241028160355814749)
├── medium: 15  (e20241028160842228543 ~ e20241028160918445815)
└── human: 15   (h20241029143447759844 ~ h20241029143510880048)
```

### 文件结构
```
external/ChinaTravel/
├── chinatravel/
│   ├── data/
│   │   └── dev_split/              # 60个.json文件 ✅
│   └── evaluation/
│       └── default_splits/
│           └── dev_split.txt       # uid列表 ✅
├── results/                         # 实验输出（待生成）
│   └── Act_*/
├── eval_res/                        # 评分结果（待生成）
│   └── splits_dev_split/
├── run_dev_baseline.sh              # 运行脚本 ✅
├── test_single.py                   # 测试脚本 ✅
└── batch_fix_dev_data.py            # 修复工具 ✅
```

---

## 🎯 阶段3目标

### 核心研究问题
**"任务成功但语义错误"的问题是否存在于ChinaTravel benchmark？**

### 成功标准
- [ ] 60/60例成功运行
- [ ] 60/60例成功评分
- [ ] 错误分类完整
- [ ] 典型案例记录（每类≥3例）

### 预期输出
1. **量化结果**
   - Schema Pass Rate: ?%
   - Commonsense Pass Rate: ?%
   - Hard Logic Pass Rate: ?%

2. **错误分析**
   - 各类错误分布
   - 典型失败案例
   - "语义错误"案例识别

3. **研究决策**
   - 问题是否存在？
   - 问题规模多大？
   - 是否值得继续v5.1方向？

---

## 📈 总体进度

```
阶段1: 环境验收            ✅ 完成
阶段2: 评分器验证          ⏭️  跳过（并行验证）
阶段3: 强基线实现          🔄 数据准备完成，待运行实验
阶段4: 错误分类            🔜 待定
阶段5: 研究决策            🔜 待定
```

**当前进度**: ⬛⬛⬛⬜⬜ 65%（阶段3数据准备完成）

---

## 🚀 快速启动

```bash
# 1. 进入目录
cd /Users/mac/Documents/6-Research/9-AutoDriving/external/ChinaTravel

# 2. 配置API
export ANTHROPIC_API_KEY="your-key-here"
export CHINATRAVEL_OPENAI_MODEL="claude-3-5-sonnet-20241022"

# 3. 测试单例
.venv-chinatravel/bin/python test_single.py

# 4. 运行实验（小规模）
bash run_dev_baseline.sh

# 5. 全量运行
.venv-chinatravel/bin/python run_exp.py \
  --splits dev_split \
  --agent Act \
  --llm claude-3-5-sonnet-20241022 \
  --lang zh
```

---

## 📝 注意事项

### API配置
- ChinaTravel使用OpenAI兼容接口
- 需要设置`CHINATRAVEL_OPENAI_MODEL`环境变量
- Claude API需要同时设置`ANTHROPIC_API_KEY`和`OPENAI_API_KEY`（映射）

### 运行时间
- 单例：~30秒
- 3例测试：~2分钟
- 60例全量：2-4小时（取决于模型速度和网络）

### 依赖
- ✅ Python 3.13.9虚拟环境
- ✅ 所有依赖已安装
- ✅ 数据已准备
- ⏳ API配置待完成

---

## 📞 问题排查

### 问题1：API调用失败
```bash
# 检查环境变量
echo $ANTHROPIC_API_KEY
echo $CHINATRAVEL_OPENAI_MODEL

# 测试API连接
.venv-chinatravel/bin/python -c "
import os
print('API Key:', os.environ.get('OPENAI_API_KEY', 'NOT SET'))
print('Model:', os.environ.get('CHINATRAVEL_OPENAI_MODEL', 'NOT SET'))
"
```

### 问题2：数据加载失败
```bash
# 验证数据
.venv-chinatravel/bin/python -c "
from chinatravel.data.load_datasets import load_query
import argparse
class Args:
    splits = 'dev_split'
    lang = 'zh'
    oracle_translation = False
args = Args()
qi, qd = load_query(args)
print(f'Loaded {len(qi)} queries')
"
```

### 问题3：评分器失败
可能需要sandbox数据，参考`STAGE3_NEXT_STEPS.md`中的sandbox下载指南

---

**本阶段完成时间**: 2026-09-11 14:30  
**下次更新**: 实验运行完成后  
**预计完成**: 2026-09-11 18:00
