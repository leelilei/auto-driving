# Luna统一提示机制消融复跑

2026-09-10。负责人要求继续用Luna推进实验。本轮复跑DeepSeek的完整受控信息消融，以检验结果是否依赖模型；未新增候选、改标签或挑错例。论文写作CLOSED。

## 预先固定的设计

- 数据：相同24个受控候选案例，8个母意图。案例文件和全部请求与DeepSeek轮逐字节相同。
- 比较：fields、route_order、full；每例每方法2次请求，共144个逻辑单元。前3项真实请求串行验证后4路并发，预检答案直接计入冻结账本。
- 模型：FHL节点`gpt-5.6-luna`；HTTP/1.1、120秒，输出上限1600，自动重试0。配置沿用FHL要求省略temperature，与DeepSeek显式temperature=0不同；跨模型差异不能直接归因于模型能力。
- 失败：传输错误每项最多恢复1次、总恢复最多16次；鉴权失败或整批连续4项传输失败停止。有效答案和schema失败不重跑。schema失败按原协议回退A，并保留原始失败。
- 主比较：full−route_order语义正确率；另报route_order−fields、full−fields、TSR、相对A纠正/改坏、token及两次重复。全部144逻辑单元完整且无未解决传输失败才汇总方法排名。
- 解释边界：错误是人工注入的；24例复用8个母意图，两次重复不增加独立样本数。结果只支持机制开发判断，不替代自然错误测试或主模型Terra确认性实验。

## 资产和执行

目录：`9-AutoDriving-core/results/v5/diagnostic/20260910_fhl_luna_mechanism_ablation24/`。

脚本：`9-AutoDriving-core/scripts/luna_mechanism_ablation.py`，复用冻结信息消融及评分代码。`manifest.json`记录配置与文件摘要，`attempts/`保留请求、原始响应与遥测，`summary.json`记录完整性及结果。密钥从环境读取，不写入实验资产。

离线复算：

```bash
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/luna_mechanism_ablation.py analyze
9-AutoDriving-core/.venv/bin/python 9-AutoDriving-core/scripts/luna_mechanism_ablation.py audit
```

审计核对144请求、原始输出独立评分、信息层级、原句出现次数和8张评分图；若采集不完整，审计必须拒绝验收方法结果。

## 节点预检与独立后备采集

FHL首条实际复核请求连续两次HTTP502（29.738秒和15.459秒），未返回模型输出。账本为1个失败逻辑单元、2次物理尝试、143项未调用。触发预检停止，不做部分方法排名。

随后按照负责人使用Luna推进实验的授权，切换既有xcode配置及钥匙串密钥，独立创建`20260910_xcode_luna_mechanism_ablation24`；模型仍为`gpt-5.6-luna`，相同144请求，120秒、零自动重试。不会拼接FHL响应。此次切换为Codex在现有授权内的实施选择，并非负责人另行批准了新实验方法。

入口为`9-AutoDriving-core/scripts/xcode_luna_mechanism_ablation.py`，支持`prepare/collect/analyze/audit`。后备run保留来源、配置、切换原因及独立原始账本；同样先检查3项冻结真实请求，预检失败则停止全量。

## 本轮结论：采集受阻，尚无Luna效果结果

xcode首条实际请求两次均超过120秒（120.009秒、120.004秒），未返回模型答案。两个节点均在首项预检按预算停止；所有进程结束，没有后台继续烧调用。

| 节点 | 物理请求 | 有效模型输出 | 首项失败原因 | 后续未调用 |
|---|---:|---:|---|---:|
| FHL | 2 | 0 | HTTP502，两次 | 143项 |
| xcode | 2 | 0 | 120秒超时，两次 | 143项 |

两个目录均为`collection_complete=false`，不生成方法排名。总共4次物理尝试，未返回provider usage，费用未知，不能写成免费。当前不能判断Luna是否更容易出错，也不能估计DARC在Luna上的提升。

本轮已完成：144请求冻结及与DeepSeek轮字节一致性检查、Luna独立运行入口、真实提示连通性预检、失败预算执行及账本落盘。未完成：三组×两次的Luna采集和方法效果验收。论文门禁保持CLOSED。

恢复应先确认至少一个节点能够返回同模型的实际复核请求，再在独立新run中按冻结144请求采集；不能将本轮两次预检失败反复当作新启动去突破每项重试上限。已有`collect`入口对本轮记录不会新增第3次尝试。只有更换已确认可用的入口或明确记录新的传输恢复方案后才再次采集，方法、数据和评分无需修改。
