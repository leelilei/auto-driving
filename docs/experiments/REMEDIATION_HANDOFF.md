# DARC-Route 第二轮整改交付与验收报告 (REMEDIATION_HANDOFF)

> **当前阶段**：第二轮独立审阅整改完成，提交 Codex 独立复验。  
> **基准审阅**：[`docs/experiments/CODEX_REMEDIATION_REVIEW_20260907.md`](CODEX_REMEDIATION_REVIEW_20260907.md)  
> **研究原则**：严格执行 [`docs/project/EXPERIMENT_FIRST_POLICY.md`](../project/EXPERIMENT_FIRST_POLICY.md)。实验完整落地 → Codex 独立验收通过 → 研究负责人明确认可 → 最后写论文。当前论文写作门禁：**`CLOSED`**。  
> **更新时间**：2026-09-07  

---

## 1. 整改推进总看板 (Tasks A ~ F)

| 任务编号 | 任务名称 | 状态 | 关键交付物 / 证据链 |
|---|---|---|---|
| **Task A** | **撤回程序生成的人审声明** | **DONE / 人审 PENDING** | 彻底撤回脚本代签的 Annotator_A/B、固定时间戳与 100% 一致率声明；队列文件明确分离 `machine_verification_status: "machine_checked"` 与 `human_annotation_status: "pending_human_review"`（Test 640 条全量 pending，Pilot 80 条全量 pending）；产出真实审计报告 [`annotation_audit_report.md`](annotation_audit_report.md) |
| **Task B** | **数据与缓存版本严格绑定** | **DONE** | 恢复 `data/test/test_640_utterances.json` 为 `1.0.0-exploratory`，与历史 5 模型运行（`20260906T051339Z_main_test` 等）输入文本与 gold 权重 **100% 严格一致（0 diff）**；14 组语义漂移改写独立暂存为候选集 `data/test/test_640_utterances_v2_proposed.json`（版本 `2.0.0-proposed`，保留原始 `w_synthetic` 与拟修订 `w_proposed`）；产出详细变更日志 `data/test/test_640_v1_to_v2_changelog.json` |
| **Task C** | **修正式 Replay 与完整性验证** | **DONE / PASS** | `scripts/experiment.py replay` 补齐四大硬拦截：① 预期组数检查（缺 159 组必退出码 1）；② 强制验证 `summary.json`（缺失必退出码 1）；③ 强制验证缓存候选与路线（清空必退出码 1）；④ 数据集文本与权重逐例一致性校验（篡改必退出码 1）；引入 `NetworkBlocker` 上下文管理器确保严格零网络且异常时安全恢复；**59 项单元与集成测试 100% 通过** |
| **Task D** | **修门禁判定与成本账本** | **DONE / 准入 BLOCKED** | 重构 `scripts/run_pilot_gate_admission.py`：纠正 Pilot 两条失败根因为 Call A 网络超时 `RuntimeError`（schema_valid=False，oracle 确认路径可行），彻底排除“时间窗不可解”推论；如实报告 Ours Regret（0.002463 vs B0 0.001822，+35.2% 变差）与 Route Flip（0.1417 vs B0 0.1833，-22.7% 改善）的经验权衡；输出结构化 JSON `results/reports/pilot_gate_admission.json`，程序化条件判定 Gate A 为 `NOT_MET_TSR_NET_GAIN`，总体准入判定为 **`BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION`**；披露历史 Sol runner 重试账本丢失项为 `historical_attempts_unrecoverable` |
| **Task E** | **重新冻结未来实验协议** | **DONE / PASS** | 修订 [`protocol_v2.md`](protocol_v2.md)：修正 Dev 校准集规模为 20 组（80 句；Dev 总计 40 组）；严格定义 Route Flip 分母为双侧成功有效对（Valid Pairs）；补齐基线 B3/B4 门控中的 $h=1$ 硬保护触发；明确界定历史 5 模型结果为探索性再分析，确认性基准待未来人审与新采集就绪后执行 |
| **Task F** | **提交 Codex 独立验收** | **READY** | 提供单一交接入口与完整命令行复现清单；所有破坏性试验与正常流程具备确定性退出码与断言保护；论文写作严格处于 **CLOSED** 状态 |

---

## 2. 针对第二轮审阅 4 项 P0 阻断问题的整改详情

### P0-1: 撤回程序生成的人工审核（Task A）
- **事实整改**：
  1. 在 `9-AutoDriving-core/scripts/remediate_data_audit.py` 中，彻底删除了为 640 条记录批量写入 `Annotator_A`、`Annotator_B`、固定时间戳 `2026-09-07T12:00:00Z` 和虚构“100% agreement”的代签循环。
  2. 在 `data/test/annotation_test_640_review_queue.json` 中：
     - `machine_verification_status`: `"machine_checked"`（已完成 POI 命名、截止时间边界及 DAG 依赖拓扑的自动化规则校验）。
     - `human_annotation_status`: `"pending_human_review"`（全部 640 条处于真实待审核状态）。
     - `annotation_status`: `"pending"`。
     - `primary_reviewer`: `null`，`secondary_auditor`: `null`，无任何虚假签名。
     - 14 组漂移数据明确标记 `drift_candidate_flag: true`，`remediation_proposal_status: "candidate_available"`。
  3. `docs/experiments/annotation_audit_report.md` 全文修正为《测试集机器自动化核验与候选改写报告》，明确声明前期代签已撤回，当前人审状态为 pending。

### P0-2: 数据与旧响应版本解绑（Task B）
- **事实整改**：
  1. **历史探索集恢复**：通过 `prepare_test_dataset.py` 重新生成原始未漂移的 `data/test/test_640_utterances.json`（SHA256: `82ec91230a1901a9bb36e51afdf0800e1e1a50713d7c5a9d8de737d824e3ec2f`）。经逐句比对，其 640 条 prompt 文本与 gold 权重与历史 5 模型运行（`20260906T051339Z_main_test`）记录 **0 差异**。
  2. **候选改写独立存放**：14 组表达 balance 但标签误标 quality 的改写文本与权重，独立保存在 `data/test/test_640_utterances_v2_proposed.json`（版本 `2.0.0-proposed`）。原 synthetic 权重与 proposed 权重分字段保存，绝不覆盖。
  3. **完整变更清单**：产出 `data/test/test_640_v1_to_v2_changelog.json`，详细记录 14 组（42 处文本改写、56 处权重归正）的逐条前后对比与整改理由。
  4. **版本边界澄清**：明确历史 5 模型在 Metric v2 下的评估为“探索期历史重算”，不得声称代表了 v2 改写后的新测试集；新测试集的有效性待真实人审与未来新响应采集后方可成立。

### P0-3: 门禁报告事实纠正与程序化自动判定（Task D）
- **事实整改**：
  1. **错误根因纠正**：读取原始调用日志发现，`pilot_03_v2` 与 `pilot_06_v0` 在 Call A 中均记录了 `transport_error_type: RuntimeError`，导致 `schema_valid: False`；而 oracle 校验均为 `task_success: True`。因此两例失败系真实的 API 传输/网络中断，**并非**“不可解时间窗冲突”。门禁报告与脚本对此事实完成彻底纠正。
  2. **Regret 恶化如实披露**：在 Metric v2 下历史 Pilot 重算指标：
     - B0: TSR = 0.9750, Route Flip = 0.1833, Regret = 0.001822
     - B6: TSR = 0.9750, Route Flip = 0.0583, Regret = 0.002375 (+30.4%)
     - Ours: TSR = 0.9750, Route Flip = 0.1417, Regret = 0.002463 (+35.2%)
     Ours 与 B6 均呈现“Route Flip 改善、Regret 恶化”的典型权衡；且因两例网络错误无法通过复核纠正，净纠错数严格为 0。报告彻底删除“Regret 从 0.0031 改善至 0.0022”的虚假描述，如实报告经验权衡。
  3. **程序化自动判定**：重构 `scripts/run_pilot_gate_admission.py`，所有判定均由 Python 布尔逻辑基于阈值与观测值实时求得，直接写入 `results/reports/pilot_gate_admission.json`，Markdown 报告仅为 JSON 的只读渲染：
     - Gate A: `NOT_MET_TSR_NET_GAIN`
     - Gate B: `PASS_FLIP_REDUCTION` (注明与 B5 成本及 B4 regret 的权衡)
     - Data Leakage: `PASS` (0 cluster, 0 index, 0 closure)
     - Overall Admission: **`BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION`**

### P0-4: Replay 完整性硬拦截与零网络加固（Task C）
- **事实整改**：
  1. **组数完整性检查**：检测到组数少于预期（测试集 160 组、Pilot/Calib 20 组）且未传 `--allow-partial` 时，打印 `[FAIL] Incomplete run integrity check` 并返回非零退出码（1）。
  2. **强制 summary.json 检查**：未传 `--allow-missing-summary` 且缺少 `summary.json` 时，打印 `[FAIL] Mandatory summary.json missing` 并返回非零退出码（1）。
  3. **强制 cached candidates / routes 检查**：若 `u['candidates']` 或 `u['routes']` 为空或缺少成功调用的对应条目，记录 integrity issue，打印 `[FAIL] Found ... integrity/execution issues` 并返回非零退出码（1）。
  4. **数据集绑定一致性检查**：对比 run 中 prompt 文本与绑定的数据集，检测到篡改立即报错退出（非零退出码 1）。
  5. **网络安全上下文**：实现 `NetworkBlocker` 上下文管理器，阻断 `socket.connect` 与 `create_connection`，并在 `__exit__` 中安全恢复原有方法，杜绝环境污染。
  6. **路径安全**：使用 `try...except ValueError` 保护 `relative_to(ROOT.parent)`，在临时目录或任意外部目录运行时不会异常崩溃。

---

## 3. Codex 独立复验命令清单 (CLI Verification)

Codex 复验时可直接运行以下命令验证本轮整改的完整性与真实性：

### 1. 完整单元与集成测试（59 项全过）
```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/pytest 9-AutoDriving-core/tests
# 预期结果：59 passed, 退出码 0
```

### 2. 正式离线 Replay 纯代码回放（零 API、全部指标一致）
```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment.py replay
# 预期结果：
# [✓] Verification against saved summary PASSED (TSR, GTSR, RouteFlip, MeanCalls match exactly).
# [✓] Offline replay completed for 640 utterances across all 8 methods.
# 退出码 0
```

### 3. Replay 完整性负向破坏测试（必以非零退出码失败）
```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python -c "
import os, sys, shutil, tempfile, subprocess, json
from pathlib import Path

CORE = Path('9-AutoDriving-core')
cli = [str(CORE / '.venv/bin/python'), str(CORE / 'scripts/experiment.py'), 'replay']
run = CORE / 'results/runs/20260906T051339Z_main_test'
env = dict(os.environ, PYTHONPATH=str(CORE))

# Case 1: 缺少 159 组与 summary
with tempfile.TemporaryDirectory() as td:
    shutil.copy2(run / 'test_001_graph.json', Path(td) / 'test_001_graph.json')
    shutil.copy2(run / 'test_001.json', Path(td) / 'test_001.json')
    p = subprocess.run(cli + ['--run-dir', td, '--output-dir', td + '/out'], env=env, capture_output=True, text=True)
    assert p.returncode == 1, f'Expected exit 1 on missing groups, got {p.returncode}'

# Case 2: 缺少 summary.json
with tempfile.TemporaryDirectory() as td:
    for f in run.glob('test_*.json'): shutil.copy2(f, Path(td) / f.name)
    p = subprocess.run(cli + ['--run-dir', td, '--output-dir', td + '/out'], env=env, capture_output=True, text=True)
    assert p.returncode == 1, f'Expected exit 1 on missing summary, got {p.returncode}'

# Case 3: 缺少 cached candidates 与 routes
with tempfile.TemporaryDirectory() as td:
    for f in run.glob('test_*.json'): shutil.copy2(f, Path(td) / f.name)
    shutil.copy2(run / 'summary.json', Path(td) / 'summary.json')
    d = json.loads((Path(td) / 'test_001.json').read_text())
    for u in d['utterances']: u['candidates'] = {}; u['routes'] = {}
    (Path(td) / 'test_001.json').write_text(json.dumps(d))
    p = subprocess.run(cli + ['--run-dir', td, '--output-dir', td + '/out'], env=env, capture_output=True, text=True)
    assert p.returncode == 1, f'Expected exit 1 on missing candidates/routes, got {p.returncode}'

# Case 4: 文本被篡改
with tempfile.TemporaryDirectory() as td:
    for f in run.glob('test_*.json'): shutil.copy2(f, Path(td) / f.name)
    shutil.copy2(run / 'summary.json', Path(td) / 'summary.json')
    d = json.loads((Path(td) / 'test_001.json').read_text())
    d['utterances'][0]['text'] = 'Tampered text'
    (Path(td) / 'test_001.json').write_text(json.dumps(d))
    p = subprocess.run(cli + ['--run-dir', td, '--output-dir', td + '/out'], env=env, capture_output=True, text=True)
    assert p.returncode == 1, f'Expected exit 1 on tampered dataset text, got {p.returncode}'

print('All 4 negative integrity tests successfully rejected with exit code 1!')
"
```

### 4. 门禁重算与程序化准入校验
```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/run_pilot_gate_admission.py
# 预期结果：
# => Gate A: NOT_MET_TSR_NET_GAIN
# => Gate B: PASS_FLIP_REDUCTION
# => Data Leakage: PASS
# => Overall Decision: BLOCKED_PENDING_HUMAN_REVIEW_AND_FRESH_COLLECTION
# 产出 results/reports/pilot_gate_admission.json
```

### 5. 数据集与审核队列真实性核查
```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python -c "
import json
from pathlib import Path
from collections import Counter

CORE = Path('9-AutoDriving-core')
run = CORE / 'results/runs/20260906T051339Z_main_test'
test_data = json.loads((CORE / 'data/test/test_640_utterances.json').read_text())
lookup = {u['utterance_id']: u for u in test_data}

# 验证输入文本与 gold 权重与历史 run 0 差异
diff, wdiff = [], []
for f in sorted(run.glob('test_*.json')):
    if f.name.endswith('_graph.json'): continue
    for u in json.loads(f.read_text())['utterances']:
        if u['text'] != lookup[u['utterance_id']]['text']: diff.append(u['utterance_id'])
        if u['gold_intent']['quality_weight'] != lookup[u['utterance_id']]['w_synthetic']: wdiff.append(u['utterance_id'])
assert len(diff) == 0, f'Text diff: {len(diff)}'
assert len(wdiff) == 0, f'Weight diff: {len(wdiff)}'
print('Dataset vs Historical Run: 100% Match (0 diff).')

# 验证审核队列真实状态（无假签名）
q = json.loads((CORE / 'data/test/annotation_test_640_review_queue.json').read_text())
assert Counter(x['human_annotation_status'] for x in q) == {'pending_human_review': 640}
assert Counter(x['machine_verification_status'] for x in q) == {'machine_checked': 640}
assert all(x['primary_reviewer'] is None for x in q)
print('Review Queue: 640 machine_checked, 640 pending_human_review, 0 fake signatures.')
"
```

---

## 4. 论文写作门禁状态确认

- **当前论文写作门禁**：**`CLOSED`**。
- **依据**：[`docs/project/EXPERIMENT_FIRST_POLICY.md`](../project/EXPERIMENT_FIRST_POLICY.md)。
- **承诺**：在本次整改推进全过程中，未改写、排版、压缩或修改任何 `paper/` 目录下的论文文本与图表。所有历史论文草稿完整保留为未经实验验收的历史文档。只有在 Codex 独立验收通过且研究负责人正式明确认可后，方可打开写作阶段。
