# DARC-Route v4.1 E2 勘误、协议故障诊断与暴露账本重核说明

- **日期**: 2026-09-12
- **对账依据**: `docs/experiments/v41_codex_audit_20260912/REVIEW.md`
- **当前状态**: **INTERFACE_FAULT_DIAGNOSTIC (接口故障诊断，不作为机制确认证据)**

---

## 1. E2 复核接口故障说明 (P0-2 勘误)

在 `scripts/run_e2_confirmation_experiment.py` 的初次执行中，因 `raw_candidates[method] = cand.to_dict()` 发生 `AttributeError`（`Intent` 为 dataclass，应用 `asdict(cand)`），导致捕获异常后 `candidates['A']` 与 `candidates['B']` 在向模型发起 `review` 调用时变成了 `None`。

- **影响事实**：160/160 次复核请求中，模型看到的提示词中 `candidate_A: null, candidate_B: null`；
- **定性原则**：
  - 严禁通过事后离线解析补齐 `parsed_intent` 而宣称模型复核有效；
  - 运行 `20260912T070050Z_e2_confirmation_gemini-3_1-flash-lite` 降级为**接口故障诊断样本**，保留全部 480 条原始 API 往返请求日志，绝不删除、不覆盖，也不作为 DARC 双路复核机制的成立证据。

---

## 2. 暴露池与候选簇资格重核 (P0-3 勘误)

经 Codex 审计指出，初次采样时未将 `candidate_splits.json` 中的校准集（`dev_calibration`）完整纳入排除集合，导致采样的 40 个簇中有 2 个簇（`494` 与 `391`）与校准数据重叠。

### 全量暴露对账清册
1. **HIPP 语义簇总量**: 609 个；
2. **全分支真实已暴露簇**:
   - `development_exposure.json`: 包含历史开发暴露簇；
   - `candidate_splits.json`: 包含 dev、calibration (20个)、test 等全部切分；
   - `test_640_utterances.json`: 包含历史主测试集暴露；
   - **合计已暴露簇数**: **200 个**（包含 494 与 391）。
3. **严格未暴露独立簇总量**: **409 个**（609 - 200 = 409 个）。
4. **资源储备评估**: 推进 40 组独立确认 + 10 组独立负向对照共需 50 个簇，当前剩余 409 个严格未暴露簇，资源完全充足。

---

## 3. 人审资格澄清

- 撤销 `prepare_e2_confirmation_data.py` 自动生成的 `CONFIRMED_HUMAN_AUDITED` 标记；
- 当前所有未通过真实人工核验的样本状态统一标记为 `PENDING_HUMAN_CONFIRMATION`；
- 真实人工审核工作台与待审清单保留于数据目录，待人工复核确认后方可签名。
