# DARC-Route v5.1 实操启动记录

日期：2026-09-09（Asia/Shanghai）。执行范围：S0盘点与S1首批离线核心；执行者：Codex。论文写作：CLOSED。

绑定版本：Proposal SHA256 `8711391ae946b74fde9c66da6531772f9e37f302984dbc54c9a9c7a783e4db2c`；实验指导书 SHA256 `12ffa4138bf236d814776965ae66e5c3321752fa8bb6ad347acdfbe921582841`。

## 本批结论

已新增隔离的v5模块、开发配置和分阶段CLI，完成配对图、图结构验证、决策对比报告、数据资格计数、8组诊断计划和候选模型开发评估。负责人已确认`gpt-5.6-terra`为主模型；四类复核提示及边界快照已冻结，前8组人工审核工作台与审核准入校验器已生成。全量现有测试加新增测试共74项通过；最终复跑为`74 passed in 2.29s`。

真实诊断尚未启动。当前唯一不可由执行者代替完成的前置条件是前8组32句的真实人工审核；另需完成采集完整性与断网回放实现。旧`gpt-5.4-mini`两次502和模型目录缺失均已留档；Terra探针及开发准入样例已成功，模型身份阻断已经解除。

## 已完成

| 项目 | 状态 | 证据 |
|---|---|---|
| 现有工程基线 | PASS | `74 passed in 2.29s` |
| v5配对图生成 | DEVELOPMENT PASS | `9-AutoDriving-core/src/v5/graph_family.py` |
| 8组图结构 | PASS | `9-AutoDriving-core/results/v5/development/20260909_s1_graphs_v3/manifest.json` |
| 对比报告原型 | DEVELOPMENT PASS | `9-AutoDriving-core/src/v5/contrast.py`及`20260909_contrast_smoke.json` |
| 数据资格计数 | BLOCKED_ON_ANNOTATION | `20260909_data_qualification.json` |
| 8组调用计划 | PLANNED/BLOCKED | `20260909_diagnostic8_plan/plan.json`及576条`expected_units.jsonl` |
| 主模型与FHL连通性 | PASS | `gpt-5.6-terra`已确认；探针、解析与复核准入样例成功 |
| 四类复核提示 | DEVELOPMENT FROZEN | `9-AutoDriving-core/prompts/v5/FREEZE_MANIFEST.json` |
| 前8组人工审核界面 | READY/PENDING HUMAN | `docs/experiments/v5_1/pilot8_review_workspace.html` |
| 审核准入校验 | PASS | `experiment_v5.py validate-review`完整性与非通过项硬拦截 |

## 配对图检查结果

8组均满足：aligned→tradeoff只改变`POI.quality`；tradeoff→time_sensitive只改变远端POI的`close_time`；aligned的质量最优集和距离最优集有交集；tradeoff两集合不相交；time_sensitive完整可行集是tradeoff的严格非空子集。

各组完整可行路线数依次为：`4/4/1, 4/4/1, 8/8/2, 8/8/2, 24/24/3, 24/24/3, 48/48/6, 24/24/3`，顺序为aligned/tradeoff/time_sensitive。这是开发结构证据，不是方法效果。

## 数据资格

- 历史候选划分200组、200个source index、200个语义簇均视为开发暴露。
- 剩余候选语义簇409个，共648条HIPP记录；这里只做计数，没有挑选或查看新测试内容。
- Pilot为20组/80句，`annotation_status=pending`共80句。预定诊断8组对应32句，也全部pending。
- 因此不能把历史`test_640_utterances_v2_confirmed.json`用作v5未见确认集，也不能启动8组真模型效果诊断。

## FHL探针

| UTC run | transport | 调用 | 结果 | provider usage |
|---|---|---:|---|---|
| `20260909T142504Z_fhl_probe` | curl | 1 | HTTP 502，8.703s | 未返回；字符估计不能当账单 |
| `20260909T142653Z_fhl_probe` | urllib | 1 | HTTP 502，7.943s | 未返回；字符估计不能当账单 |

未暴露API key。无自动重试。未取得有效模型输出，不能推断模型能力或算法效果。

鉴权模型目录查询于`2026-09-09T14:35:03Z`返回HTTP 200；当前列出`gpt-5.5`、`gpt-5.6-luna/sol/terra`、`gpt-6-astra`等9个ID，但没有`gpt-5.4-mini`。证据见`evidence/fhl_model_inventory_20260909.json`。不能静默切换模型；需更新主模型决策和预算后重新做单次探针。

后续候选评估显示Terra、Luna和gpt-5.5均可连通。三者在5条普通解析上均为5/5；2条决策报告复核中Terra和gpt-5.5为2/2，Luna为1/2并出现图诱导偏好漂移。`gpt-5.5-mini`精确别名返回404 model_not_found。负责人已据此确认Terra为主模型，gpt-5.5为强基线，Luna为补充诊断。详见`MODEL_SELECTION_20260909.md`。

## 实际命令

```bash
PYTHONPATH=9-AutoDriving-core 9-AutoDriving-core/.venv/bin/python -m pytest 9-AutoDriving-core/tests -q
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py preflight
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py audit-data --out 9-AutoDriving-core/results/v5/development/20260909_data_qualification.json
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py build-graphs --dataset 9-AutoDriving-core/data/pilot/pilot_80_utterances.json --groups 8 --out 9-AutoDriving-core/results/v5/development/20260909_s1_graphs_v3
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py contrast-smoke --out 9-AutoDriving-core/results/v5/development/20260909_contrast_smoke.json
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py plan-diagnostic --out 9-AutoDriving-core/results/v5/development/20260909_diagnostic8_plan
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py probe
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/experiment_v5.py probe --transport urllib
```

## 尚未完成

S1还缺真实collect/resume、分析、断网replay/package、LLMAP兼容评分和篡改拒绝链，因此不能签S1整体PASS。四review提示和前8组审核界面已经补齐。

下一实施批应完成collect/resume及断网replay/package链，并取得前8组32句的真实审核导出。只有这些证据通过独立复查，才执行576次上限内的S2；首次S2拆成1组72调用的端到端小批，确认四review和usage记录后再扩到8组。
