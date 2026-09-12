# FHL候选模型开发评估

日期：2026-09-09。用途：选择DARC-Route v5.1开发主模型。该结果来自5条手工解析样例和2条手工决策报告复核样例，不是HIPP-DC正式实验，不用于论文性能主张。

所有可用模型使用相同system prompt、JSON模式、temperature省略、urllib传输、并发1、自动重试0。每个模型先完成一次连通探针。完整原始响应和provider usage位于对应run目录。

| FHL模型 | 连通 | 普通解析：schema/硬约束/方向 | 决策报告：schema/硬约束/方向 | 7次有效调用token | 普通解析均时 | 决策复核均时 |
|---|---|---|---|---:|---:|---:|
| gpt-5.6-terra | PASS | 5/5，5/5，5/5 | 2/2，2/2，2/2 | 3,864 | 16.835s | 13.193s |
| gpt-5.6-luna | PASS | 5/5，5/5，5/5 | 2/2，2/2，1/2 | 3,913 | 11.605s | 14.512s |
| gpt-5.5 | PASS | 5/5，5/5，5/5 | 2/2，2/2，2/2 | 4,055 | 8.844s | 12.867s |
| gpt-5.5-mini | FAIL | 未运行 | 未运行 | 无provider usage | — | — |
| deepseek-v4.1-flash临时预览 | PASS | 5/5，5/5，5/5 | 2/2，2/2，2/2 | 6,626 | 1.705s | 3.954s |
| deepseek-v4-flash稳定ID | PASS | 5/5，5/5，5/5 | 2/2，2/2，1/2 | 8,216 | 4.211s | 8.780s |

`gpt-5.5-mini`不在当时鉴权模型目录中；精确别名探针返回HTTP 404 `model_not_found`，不能与`gpt-5.5`混称。

Luna在`resist_route_preference`中正确保留了bank→pharmacy依赖，但把“keep the route short”的0.25预测成0.75，出现本研究最关注的图诱导偏好漂移。Terra与gpt-5.5在两条复核样例均保持原句方向。样本很小，只能作为准入诊断；不能据此估计总体准确率或显著差异。

负责人于2026-09-09确认：**gpt-5.6-terra作为v5.1开发与主实验的主模型，gpt-5.5作为强基线/泛化对照，Luna仅作补充诊断。** Terra通过了核心复核边界，属于当前可用5.6系列；相比gpt-5.5少4.7%总token，但在本小样本中更慢。价格信息尚未取得，因此S2扩量前仍须以冻结后的实际提示补齐token上界和费用表；该预算缺口不改变模型选择。

证据目录：

- Terra解析：`9-AutoDriving-core/results/v5/model_selection/20260909T144148568891Z_gpt_5_6_terra_model_smoke`
- Terra复核：`9-AutoDriving-core/results/v5/model_selection/20260909T144555250190Z_gpt_5_6_terra_review_smoke`
- Luna解析：`9-AutoDriving-core/results/v5/model_selection/20260909T144318673042Z_gpt_5_6_luna_model_smoke`
- Luna复核：`9-AutoDriving-core/results/v5/model_selection/20260909T144650642683Z_gpt_5_6_luna_review_smoke`
- gpt-5.5解析：`9-AutoDriving-core/results/v5/model_selection/20260909T144829973648Z_gpt_5_5_model_smoke`
- gpt-5.5复核：`9-AutoDriving-core/results/v5/model_selection/20260909T144921725030Z_gpt_5_5_review_smoke`
- gpt-5.5-mini失败：`9-AutoDriving-core/results/v5/probes/20260909T144726563175Z_gpt_5_5_mini_probe`
- DeepSeek V4.1预览解析/复核：`20260909T160240157633Z_deepseek_v4_1_flash_expires_on_0910_model_smoke`与`20260909T160248793360Z_deepseek_v4_1_flash_expires_on_0910_review_smoke`
- DeepSeek稳定V4解析/复核：`20260909T160312127308Z_deepseek_v4_flash_model_smoke`与`20260909T160333309606Z_deepseek_v4_flash_review_smoke`

2026-09-10补充：V4.1临时预览在7条开发样例全部通过，且完成一组修正版72/72端到端采集；但该精确ID带`expires-on-0910`，不能作为长期确认性主模型。稳定V4在核心复核样例出现与Luna相同的图诱导偏好漂移。因此Terra主模型决策暂不改变；DeepSeek V4.1结果用于诊断方法链，稳定V4不升格为主模型。
