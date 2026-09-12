# Scene-Rule30：术语定义语言复核对照

> 后续更新：已于2026-09-11补齐60单元并通过离线核验，术语组最终60/60、原始57/60。见[完整结果](GLOSSARY60_RESULTS_20260911.md)。以下保留当时的状态与预定协议。


> 实际采集状态：截至2026-09-11，21/60取得有效回答，39待补，TLS故障导致中断；传输与预算修订见[采集状态](GLOSSARY60_STATUS_20260911.md)。尚无完整效果结论。

2026-09-10，采集前记录。用户授权推进上一轮提出的60次术语定义对照。

研究问题：计算证据相对原语言复核的增益，能否被明确说明DSL术语的简单复核取代？本次新增术语组，保留原30例及两次重复的Direct候选，新增60次复核；没有重新采Direct，没有将旧复核响应当新响应。

参考运行：`results/scene_rule30/20260910T152533Z_haiku_c16_development`。已有Direct/Language/Evidence任务成功分别42/60、42/60、48/60，数据仍PENDING语义人审。本组是利用既有开发结果提出的后续对照，不是独立确认性研究。

## 唯一提示改动

保持旧Language的system提示及统一输出合同，追加以下固定定义；user消息逐字保持一致，包含原句、原scene、同一个Direct候选、`computed_scene_facts: null`。

```text
Definitions of the three selection values:
- nearest_from_bank: minimize the straight-line distance d(B, P) from bank B to the pharmacy P among eligible pharmacies.
- minimum_added_distance: minimize d(B, P) + d(P, H) - d(B, H) among eligible pharmacies, where H is home.
- highest_rating: maximize the pharmacy rating among eligible pharmacies.
These definitions specify the selection field. Read which objective is requested from the instruction; the availability_reference and return_by fields retain their definitions above.
```

定义不给候选计算数值、推荐对象、gold、错误标志或案例定向提示；对全部60个请求完全相同。没有规则生成器参与构造补充文本。

## 固定执行与评分

- xcode `claude-haiku-4-5-20251001`，Anthropic Messages；复制参考运行配置：temperature0、输出上限1600、超时120秒、客户端重试0。
- 初始8路，先运行计划内首个请求。出现传输故障降至4路，只重试传输失败，每单元最多1次恢复，总恢复上限6；401/403/429停止。最多66次实际请求。语义错误及schema失败不重试。
- 原始响应及provider usage完整留存；schema失败统一回退对应的原Direct。原始正确率、回退后正确率、任务纠正/改坏、主集36/控制24以及两次重复分开报告。
- 主比较Glossary与历史Evidence的任务成功；同时列出二者不一致案例，不能仅看总分是否相同。若追平/超过Evidence，则目前没有证明计算事实表的额外价值；若低于Evidence，只支持进一步做同时采集、含术语定义的公平证据对照，不能直接宣布计算必要。
- 采集前已冻结数据、旧响应摘要、Direct/Language原始记录、60请求、固定术语文本、源码及配置。测试包含同候选/同原句、无事实表、固定分母、回退、缺失/篡改/跳过尝试编号等，当前全项目156项通过。

## 解释限制

本轮只有Glossary重新采集。旧Language/Evidence不是同一时段新采集，已有运行还发生过16→8并发恢复；因此属于匹配候选的开发对照，不能将差异完全归因为术语定义。不同提示长度也会产生不同token成本，需报告缓存分项。

不得看到第一次重复后修改第二次提示或重选案例；不得改gold追随回答；人审继续如实PENDING。此轮不写论文、不声称SOTA。

入口：`9-AutoDriving-core/scripts/scene_rule30_glossary.py run`。完成后用`replay --run-dir <目录>`断网复算；结果另文追加，本文保留预定规则。
