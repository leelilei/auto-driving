# 5.6-terra 新场景试跑

2026-09-10。根据用户“用5.6-terra”，以与 Luna 相同的 S01 Direct 任务，先测试 FHL，再测试 xcode。人审仍 PENDING，属于开发烟测。

| 节点 | 请求模型 | 尝试 | 有效输出 | 延迟 | 结果 |
|---|---|---:|---:|---:|---|
| FHL | gpt-5.6-terra | 1 | 0 | 10.076秒 | HTTP 502 |
| xcode | gpt-5.6-terra | 1 | 0 | 120.007秒 | 请求超时 |

每节点计划 S01/S02 × 三方法，共6次；首个传输或schema失败停止。实际总计2次请求、0重试、0复核，没有全量采集。

使用对应节点120秒配置，仅替换请求模型名：curl、JSON模式、输出上限1600、省略temperature、串行、客户端重试0。两个节点完整提示相同，输入1624字符。已核查manifest冻结文件哈希及请求文本一致性。

无模型正文及provider usage；客户端406 tokens为字符估计，不代表真实计费。后端实际模型身份未验证。不能据此评价Terra能力或DARC效果，也不能仅凭两次失败确定服务端根因。当前不启动72次全量，节点恢复后先做单请求检查。

证据目录（相对项目根目录）：

- `9-AutoDriving-core/results/scene_pilot12/20260910T063453Z_terra_fhl_smoke/`
- `9-AutoDriving-core/results/scene_pilot12/20260910T063539Z_terra_xcode_smoke/`

入口：`9-AutoDriving-core/scripts/scene_luna_smoke.py --provider fhl --model terra`；xcode用 `--provider xcode`。脚本保留历史名称，支持luna/terra，每次新建结果目录。
