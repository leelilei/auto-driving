# 模型身份与接口可用性核查表 (MODEL_IDENTITY)

- **审查日期**: `2026-09-13`
- **审查基准**: [`docs/guides/AGY_NEXT_ACTION_DS_QWEN_TRANSFER_20260913.md`](file:///Users/mac/Documents/6-Research/9-AutoDriving/docs/guides/AGY_NEXT_ACTION_DS_QWEN_TRANSFER_20260913.md) 第 3 节 (P0 阶段规范)
- **执行团队**: Antigravity (AGY) 研发实施团队

---

## 1. DeepSeek 身份核验事实

| 检查项 | 官方节点 (Primary) | 聚合备用节点 (Apilio) |
| :--- | :--- | :--- |
| **配置路径** | `9-AutoDriving-core/configs/v5/deepseek_official_v4_flash.json` | `9-AutoDriving-core/configs/llm_config_deepseek.json` |
| **基础 URL** | `https://api.deepseek.com` | `https://api.apilio.ai` |
| **环境变量** | `DEEPSEEK_API_KEY` (已就绪: True) | `APILIO_API_KEY` (已就绪: True) |
| **请求模型名** | `deepseek-v4-flash` | `deepseek-v4-flash` |
| **返回模型名** | `deepseek-flash` | `deepseek-v4-flash` |
| **HTTP 状态码** | `200 OK` (连通测试成功) | `200 OK` (连通测试成功) |
| **Wire 协议** | `chat_completions` (OpenAI 兼容) | `chat_completions` |
| **判定结论** | **`VERIFIED_AND_ACTIVE` (主执行选用)** | `STANDBY` (仅作审计比对，主 run 严禁混流) |

**说明**：
在官方 `api.deepseek.com` 接口中，发送 `model: "deepseek-v4-flash"`，服务端正常响应并返回 `model: "deepseek-flash"`，与官方版本路由策略一致。本次实验严格遵照指引，将使用该官方节点，并将逐 HTTP 尝试的请求体与响应头（含 `x-request-id`、`created`、`usage`）实时落盘。

---

## 2. Qwen 身份核验事实与决断

| 检查项 | 阿里云 DashScope 原生 | 聚合节点 (Apilio) |
| :--- | :--- | :--- |
| **环境变量** | `DASHSCOPE_API_KEY` (未配置: False) | `APILIO_API_KEY` (已就绪: True) |
| **目录可用模型** | 无法直接访问 | 包含 `qwen3.8-max`，但**无 `qwen3.8-flash`** |
| **尝试别名检索** | N/A | 检索到 `qwen-flash`, `qwen3-coder-flash`, `qwen3-vl-flash`，无纯文本 `qwen3.8-flash` |
| **判定状态** | `MODEL_UNAVAILABLE` | `MODEL_UNAVAILABLE` |

**合规决断（严格遵循指引 3.2 节）**：
> “禁止把 Max 的结果标成 Flash，禁止猜测模型名后持续试遍别名。Flash 不可用时，该项记 `MODEL_UNAVAILABLE`，向负责人报告‘Flash 不可用，是否改用 Max’，同时继续 DS 与迁移可行性检查。”

因此，Qwen 3.8 Flash 状态如实冻结为 **`MODEL_UNAVAILABLE`**，不猜测别名，不冒用 Max 充当 Flash。

---

## 3. 逐调用持久化与容灾重试协议 (P0 Contract)

1. **落盘粒度**：
   - 每次 HTTP 尝试独立落盘于 `attempts/{call_id}_attempt_{idx}.json`。
   - 包含：`request_time`, `end_time`, `request_payload`, `status_code`, `raw_response`, `error_type`, `usage`。
2. **重试约束**：
   - 传输层失败（网络断开、502/503/504、超时）最多重试 **1 次**（禁止客户端与外层叠加）。
   - Schema 解析失败、逻辑错误保留为显式失败，**严禁为了格式不断重采**。
3. **熔断阈值**：
   - 若最近 20 次 HTTP 尝试中传输失败率达到 20%，立即触发断点熔断，暂停任务。
