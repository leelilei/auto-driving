# DARC-Route 实验核心

当前可执行：HIPP 预处理、精确小图求解、独立 gold 路线检查，以及原始指令的 A/B/一次复核开发试跑。
正式 20×4 等义 Pilot、人工标注与门控比较尚未完成。`scripts/run_pilot.py` 的结果不能作为 Gate A 已通过或正式论文数据。

## 环境

使用 Python 3.12，项目隔离环境为 `.venv`。系统默认 `python3` 是 3.9，不能用于本项目的全部代码。

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock.txt
.venv/bin/python -m pytest tests -q
```

运行时代码使用标准库；pytest 用于测试，tiktoken 已安装用于后续 token 核对。当前遥测优先读取服务商 usage，缺失时的字符估算不当作真实账单。

真实模型配置见 `configs/llm_config.json`，凭据仅从 `FHL_API_KEY` 环境变量读取；不要写入配置、日志或版本库。当前使用已配置的 FHL / gpt-5.4-mini，本地只能验证请求与响应，不能独立认证中转服务背后的模型权重版本。

## 可重复运行

```bash
.venv/bin/python -m src.preprocess_hipp
.venv/bin/python scripts/run_pilot.py --limit 1 --workers 1
# 连通与输出确认后，最多 20 个开发组、并发最多 3、每组最多三次调用：
.venv/bin/python scripts/run_pilot.py --limit 20 --workers 3
```

每次运行创建独立的 `results/runs/<UTC时间>_original_smoke/`，保存 manifest、代码/输入哈希、提示、完整响应、每次调用遥测、冻结图、逐例 gold 检查和汇总。脚本不自动重试，输出预算为 1,600 tokens/调用；传输失败保留并计入失败率，不静默删除。再次运行会重新调用 API；它不是缓存恢复命令。

主任务成功按独立 gold 检查器计算，不能靠解析器自己输出的约束判定。偏好方向仍待人工审核，当前不报告真实偏好恢复率。共享输出的评估账单与各方法部署成本需要分别计算。
