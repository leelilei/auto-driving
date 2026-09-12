# Luna 新方案连通性试跑

2026-09-10。根据用户“用luna模型试下”，以新方案 S01 完整 Direct 提示测试两个节点。数据仍为 PENDING 语义人审，本次属于开发烟测。

| 节点 | 请求模型 | 尝试 | 有效输出 | 用时 | 结果 |
|---|---|---:|---:|---:|---|
| FHL | gpt-5.6-luna | 1 | 0 | 8.461秒 | HTTP 502 |
| xcode | gpt-5.6-luna | 1 | 0 | 120.006秒 | 请求超时 |

每节点预定 S01/S02 各三方法共6次；首个传输或schema失败即停止。本轮总计2次尝试、0次复核、0次重试。串行、120秒超时、1600输出token上限、JSON模式、省略temperature。两个请求的完整提示相同。

两端均未收到模型正文或provider usage。日志中的406 tokens为字符估计，不能当成真实计费，也不能宣称无费用。请求模型名称未获得后端实际身份验证。

本时段两个节点均未完成首个请求，不能判断Luna能力、任务天花板或DARC效果。暂不启动72次全量；节点恢复后先重做单请求检查。跨节点结果分开存储。

证据目录（相对项目根目录）：

- `9-AutoDriving-core/results/scene_pilot12/20260910T062917Z_luna_fhl_smoke/`
- `9-AutoDriving-core/results/scene_pilot12/20260910T063013Z_luna_xcode_smoke/`

包含配置、公开输入、独立gold、采集器源码、manifest、失败请求及summary。采集脚本：`9-AutoDriving-core/scripts/scene_luna_smoke.py --provider fhl` 或 `--provider xcode`。每次另建目录。
