# CODEX 验收请求书 (DARC-Route v4.1 E0 + E1 + E2)

状态: **READY_FOR_CODEX_REVIEW**
产物主目录: `results/v4_1/20260912T063836Z_e0_e1`
Gemini全量目录: `results/v4_1/20260912T065625Z_gemini31_full160_e0_e1`
E2确认运行目录: `results/runs/20260912T070050Z_e2_confirmation_gemini-3_1-flash-lite`
跨模型报告: `results/reports/cross_model_capability_boundary_report.md`
E2确认报告: `results/reports/e2_confirmation_report.md`

## 可直接执行的离线核验命令

```bash
cd /Users/mac/Documents/6-Research/9-AutoDriving/9-AutoDriving-core

# 1. 执行 v4.1 核心自动化审计套件 (8项测试，断网拦截与篡改测试全覆盖)
PYTHONPATH=. .venv/bin/python -m pytest tests/test_v41_master.py -v

# 2. 验证所有产物 SHA256 完整性 (断网可用)
python3 -c '
import json, hashlib
from pathlib import Path
d = Path("results/v4_1/20260912T063836Z_e0_e1")
hashes = json.loads((d / "hashes.json").read_text())
for rel, exp in hashes.items():
    cur = hashlib.sha256((d / rel).read_bytes()).hexdigest()
    assert cur == exp, f"Mismatch in {rel}"
print("[✓] All deliverable hashes verified successfully.")
'

# 3. 检查 E1 GPT 同配额主指标与置信区间 (10% 主配额，净增益 +11.10%, p < 0.001)
python3 -c '
import json
from pathlib import Path
d = Path("results/v4_1/20260912T063836Z_e0_e1")
m = json.loads((d / "e1/metrics.json").read_text())
ci = json.loads((d / "e1/confidence_intervals.json").read_text())
print("10% Quota DARC Flip:", m["10%"]["flip_darc"])
print("10% Quota B4 Semantic Flip:", m["10%"]["flip_b4_semantic"])
print("10% Quota B3 Random Mean:", m["10%"]["flip_b3_random_mean"])
print("10% Quota CI vs B3:", ci["10%"]["ci_95_vs_b3"])
'

# 4. 检查 Gemini 全量 160 组基准与 E2 独立确认结果
python3 -c '
import json
from pathlib import Path
gem = json.loads(Path("results/v4_1/20260912T065625Z_gemini31_full160_e0_e1/e0/metrics_clean_subset.json").read_text())
e2 = json.loads(Path("results/runs/20260912T070050Z_e2_confirmation_gemini-3_1-flash-lite/summary.json").read_text())
print("[✓] Gemini Clean 146 Subset B0 Flip:", gem["gemini-3.1-flash-lite"]["B0"]["route_flip"])
print("[✓] E2 Unexposed 40 Groups B0 Flip:", e2["online_methods"]["B0"]["route_flip"])
'
```
