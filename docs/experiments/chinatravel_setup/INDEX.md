# ChinaTravel 环境验收 - 文档索引

> **当前执行入口**：[Travel 工程收尾与下一阶段执行书](TRAVEL_READINESS_CLOSEOUT_20260911.md)。受限实验底座已打通：固定六例官方 3/6，另外三例明确澄清；66 项测试及断网评分回放通过。进入基线错误分布诊断；以下旧状态仅作历史记录。

> **最新进度**：[DS 六例官方评分、整改与下一步](DS6_PROGRESS_20260911.md)。


> **下一步执行入口（2026-09-11）**：[Claude / agy 交接任务单](NEXT_HANDOFF_20260911.md)。包含 v2 修改范围、预算、1—3 例试跑规则及 Codex 独立验收要求。

**阶段**: 阶段1完成 ✅  
**日期**: 2026-09-11  
**状态**: 验收通过，可进入阶段2

---

## 快速导航

### 🎯 我想了解...

- **当前做到哪了？** → [README.md](README.md)
- **有哪些关键发现？** → [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
- **详细验收报告？** → [STAGE1_COMPLETION_REPORT.md](STAGE1_COMPLETION_REPORT.md)
- **Oracle问题是什么？** → [ORACLE_LEAK_ISSUE.md](ORACLE_LEAK_ISSUE.md)
- **环境怎么配置的？** → [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **数据从哪来？** → [DATA_MANIFEST.md](DATA_MANIFEST.md)
- **每天进度如何？** → [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md)

---

## 文档层次

```
docs/experiments/chinatravel_setup/
│
├─ 📋 INDEX.md (本文档)               ← 文档导航
│
├─ 🎯 核心文档 (必读)
│  ├─ README.md                      ← 当前状态与下一步
│  ├─ EXECUTIVE_SUMMARY.md           ← 执行摘要
│  └─ STAGE1_COMPLETION_REPORT.md    ← 详细验收报告
│
├─ 🔍 问题分析
│  └─ ORACLE_LEAK_ISSUE.md           ← Oracle泄露问题分析与解决
│
├─ 📊 技术文档
│  ├─ ENVIRONMENT_SETUP.md           ← 环境配置记录
│  ├─ DATA_MANIFEST.md               ← 数据清单文档
│  └─ PROGRESS_TRACKER.md            ← 进度追踪
│
└─ 📈 上级文档
   ├─ ../WORK_SUMMARY_20260911.md    ← 今日工作总结
   ├─ ../task_audit_20260911/        ← 任务审计
   └─ ../../plans/                   ← Proposal重评
```

---

## 数据文件

```
external/ChinaTravel/
│
├─ 📊 清单与配置
│  ├─ data_manifest.json             ← 604例元数据
│  ├─ oracle_isolation_report.json   ← Oracle验证报告
│  └─ dev_hold_split.json            ← Dev/Hold分区配置
│
├─ 🆔 分区列表
│  ├─ dev_uids.json                  ← 60例开发集uid
│  └─ hold_uids.json                 ← 544例保留集uid
│
├─ 🧪 示例数据
│  ├─ cleaned_sample_easy.json       ← Easy split样本
│  ├─ cleaned_sample_medium.json     ← Medium split样本
│  └─ cleaned_sample_human.json      ← Human split样本
│
└─ 🛠️ 工具脚本
   ├─ oracle_isolation.py            ← Oracle隔离工具
   ├─ design_dev_hold_split.py       ← 分区设计脚本
   └─ generate_manifest.py           ← 清单生成脚本
```

---

## 按角色阅读

### 如果你是研究者...
1. [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - 了解整体状态
2. [ORACLE_LEAK_ISSUE.md](ORACLE_LEAK_ISSUE.md) - 了解关键问题
3. [STAGE1_COMPLETION_REPORT.md](STAGE1_COMPLETION_REPORT.md) - 深入细节

### 如果你要复现实验...
1. [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - 环境配置
2. [DATA_MANIFEST.md](DATA_MANIFEST.md) - 数据获取
3. `external/ChinaTravel/*.py` - 运行工具脚本

### 如果你要继续开发...
1. [README.md](README.md) - 当前状态与下一步
2. [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) - 进度追踪
3. `external/ChinaTravel/dev_uids.json` - 使用开发集

---

## 关键数字速查

| 指标 | 数值 |
|---|---:|
| Phase 1总数 | 604例 |
| Dev集 | 60例 (10%) |
| Hold集 | 544例 (90%) |
| Oracle隔离验证 | 604/604 ✓ |
| 文档总数 | 23个文件 |
| 当前进度 | 20% (1/5阶段) |

---

## 验收状态

- [x] 环境可运行
- [x] 数据完整（604例）
- [x] Oracle隔离验证
- [x] Dev/Hold分区
- [ ] 评分器验证（阶段2）
- [ ] 问题存在验证（阶段4）

**验收结果**: ✅ 通过  
**阻塞项**: 无  
**可进入阶段2**: 是

---

## 下一步行动

### 立即执行
```bash
cd external/ChinaTravel
.venv-chinatravel/bin/python download_sandbox.py
```

### 本周内
- 运行5种评分器测试
- 字段权限隔离验证
- 保存3个完整prompt示例

---

## 相关资源

- **ChinaTravel官方**: https://github.com/LAMDA-NeSy/ChinaTravel
- **数据集**: https://huggingface.co/datasets/LAMDA-NeSy/ChinaTravel
- **Sandbox**: https://huggingface.co/datasets/LAMDA-NeSy/ChinaTravel-Sandbox
- **论文**: https://openreview.net/forum?id=0YRVlxY9BH

---

**最后更新**: 2026-09-11 11:30  
**维护者**: DARC-Route研究团队
