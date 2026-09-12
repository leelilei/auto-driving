# DS 固定六例的端到端复核与推进

2026-09-11。当前阶段是小批开发实验的官方评价与错误归因。DS 已接通，完整实验尚未完成，论文 CLOSED。

## 核查到的实际进度

原 `collection_deepseek_report.json` 保存六份官方接口响应。请求模型为 `deepseek-v4-flash`，响应标识为 `deepseek-flash`，二者分别记录，不把别名推断为已验证的模型架构。六次原始响应的 provider usage 合计 input 749、output 430、total 1,179 token。

原先的“6/6 JSON_VALID”仅说明基本输出合同检查通过。它没有证明所有必要字段已确定、规划成功或满足官方约束。原 stage4 的两个 search_success 中，有一个酒店房型被保存成字符串，官方 schema 不通过；另有三例未确定人数，一例在限定搜索预算内失败。

## 本轮完成的工作

1. 新增 `9-AutoDriving-core/scripts/audit_chinatravel_ds6.py`，补齐完整六例的官方 schema、commonsense、hard v2 和 all-pass。缺失或未执行预测保留为失败，不缩小分母。
2. 复用既有 DS 解析，对三个必要字段已确定的案例重新执行离线后端。每例仍为 30 秒、search_width=10，模型调用为 0；其余三例不猜测人数。
3. 新版序列化把 NumPy 数值标量转换为等值的 Python 数值，而不是 `default=str`。不把已有字符串“2”事后改成数字，不修改原句、gold 或行程逻辑。旧代码与结果不覆盖。
4. 在规划结束后的独立评分阶段读取原始 dev 记录，核对 start_city 等完整字段，避免沿用旧合并文件的字段遗漏。
5. 对原结果与新版结果均完成断网官方评分回放，六例分母一致；新增三个序列化回归测试通过。

新运行目录为 `9-AutoDriving-core/results/chinatravel_baselines/20260911_ds6_offline_audit/`。它是同一批模型响应的工程重放与离线重算，不是新增六个模型样本。

## 逐例结果

| 案例 | 当前状态 | 解释边界 |
|---|---|---|
| e20241028160248698752，上海→杭州一天 | 官方 all-pass | 原基线回归例，本轮保留成功 |
| e20241028160845920703，深圳→广州两天 | 人数 null，未规划 | 原句“我打算去”没有显式人数；不能直接当模型误读，也不从 gold 回填 |
| e20241028160848776495，广州→杭州两天四人 | 限定预算内搜索未成功 | 需要核查后端对交通、房间与预算的支持及剪枝；不能仅凭搜索失败证明不可行 |
| e20241028160913165493，杭州→北京三天 | 人数 null，未规划 | “我和朋友”的人数约定需要明确，不能用参考标签替模型补齐 |
| e20241028160902013119，北京→武汉三天 | 人数 null，未规划 | 不根据一间单床房自动推断人数 |
| h20241029143455115600，北京→重庆五天两人 | 官方 all-pass | 未指定预算保持 null；修复了数值序列化导致的 schema 失败 |

| 完整六例分母 | 原保存结果的官方复算 | 新版离线重算 |
|---|---:|---:|
| All-pass | 1/6，16.67% | 2/6，33.33% |
| 本轮新增模型请求 | 0 | 0 |

新版 schema、commonsense macro、hard macro 均为 2/6。不能报告为“可规划子集 2/3”来替代全体结果。需要子集分析时另列分母，并保留全体主表。

这不是 DARC 的 +16.67 个百分点收益。它是工程整改前后记录的变化，包含离线搜索重新执行，不能当作一次严格的方法消融。当前尚没有 DARC 与充分定义语言对照的同场实验，也没有语义忠实性人工终审结论。

## 当前剩余瓶颈与下一步顺序

**连接问题已不再是首要瓶颈。** 先处理以下三个问题，再增加调用。

1. **必要字段缺省政策。** 原句未明确人数时，保留 unresolved 或走显式澄清流程；若选择约定性默认值，必须在新协议中公开，并把“模型原解析”与“宿主默认后的系统”分开。不得从官方 metadata 或 gold 偷填。当前三例保持失败分母，不删样本。
2. **后端对预测约束的落实。** 对四人两房两床、火车和预算组合，逐项核对编译器与 RuleNeSy 的候选选择、房间数量、交通方式和剪枝。先用已有预测做离线单约束诊断，保留完整组合的原结果，不能放宽原始要求后称原任务成功。
3. **研究问题与指标。** 目前发现主要是接口缺省和搜索/序列化问题。两例 all-pass 仅证明某些输入可跑通，不能证明“成功但误读”的现象已经成立。下一轮需要明确原句语义审核标准与联合评价；不为了支持 DARC 制造模型错误。

未扩量到 60 例，未使用 hold/human1000 调试，也没有追加 API 以追求正结果。本轮任务已推进到“六例有完整官方结论”，不再停留在 JSON 有响应的连接验证阶段。

## 可复核命令

项目根目录执行：

```bash
external/ChinaTravel/.venv-chinatravel/bin/python \
  9-AutoDriving-core/scripts/audit_chinatravel_ds6.py replay \
  --out 9-AutoDriving-core/results/chinatravel_baselines/20260911_ds6_offline_audit

external/ChinaTravel/.venv-chinatravel/bin/python -m unittest discover \
  -s 9-AutoDriving-core/tests -p test_chinatravel_ds6_serialization.py -v
```

`original_official_score.json`、`official_score.json`、`rows.json`、`summary.json`、逐例 search 与 `hashes.json` 均在新运行目录。重放验证的是保存结果的评价一致性；不承诺受时间限制的搜索过程在不同机器上逐节点相同。
