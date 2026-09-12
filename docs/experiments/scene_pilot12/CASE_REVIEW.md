# Scene-Pilot12逐例审阅表

2026-09-10。作者构造的开发候选；API调用0；全部人审PENDING。以下预期为作者规则＋参考算术，不能冒充人审结论。

## 统一约定

家H=(0,0)，银行B=(10,0)，09:00出发，每分钟1距离单位；银行09:10抵达，服务20分钟，09:30离开。先银行、后恰好一家药房、最后回家。药房服务10分钟，禁止等待，服务结束等于关门允许。银行营业08:00—18:00。位置是合成平面，不是真实路网。

每例请检查原句是否无歧义、作者规则是否忠实、计算和预期是否正确。审核记录字段保持空白，不能由脚本填写审核人。

## S01 / F1 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies where service can be completed during opening hours, choose the one closest to bank B.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (15, 0) | 08:00—09:40 | 4 |
| P_beta | (22, 0) | 08:00—10:20 | 4 |

作者规则：selection=`nearest_from_bank`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | pharmacy_service_finishes_after_close |
| P_beta | 09:42 | 09:52 | 10:14 | 12.000 | 24.000 | 可行 |

**作者手算预期：P_beta**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S02 / F1 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies where service can be completed during opening hours, choose the one closest to bank B.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (15, 0) | 08:00—10:00 | 4 |
| P_beta | (22, 0) | 08:00—10:20 | 4 |

作者规则：selection=`nearest_from_bank`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | 可行 |
| P_beta | 09:42 | 09:52 | 10:14 | 12.000 | 24.000 | 可行 |

**作者手算预期：P_alpha**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S03 / F2 / instruction_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the highest-rated feasible pharmacy and return home by 09:55.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 08:00—18:00 | 4 |
| P_beta | (15, 0) | 08:00—18:00 | 4.9 |

作者规则：selection=`highest_rating`；availability_reference=`arrival`；return_by=09:55。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | 可行 |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | return_deadline |

**作者手算预期：P_alpha**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S04 / F2 / instruction_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the highest-rated feasible pharmacy and return home by 10:05.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 08:00—18:00 | 4 |
| P_beta | (15, 0) | 08:00—18:00 | 4.9 |

作者规则：selection=`highest_rating`；availability_reference=`arrival`；return_by=10:05。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | 可行 |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | 可行 |

**作者手算预期：P_beta**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S05 / F3 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the feasible pharmacy that adds the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (10, 2) | 08:00—18:00 | 4 |
| P_beta | (5, 0) | 08:00—18:00 | 4 |

作者规则：selection=`minimum_added_distance`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:32 | 09:42 | 592.198分钟 | 2.000 | 2.198 | 可行 |
| P_beta | 09:35 | 09:45 | 09:50 | 5.000 | 0.000 | 可行 |

**作者手算预期：P_beta**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S06 / F3 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the feasible pharmacy that adds the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (10, 2) | 08:00—18:00 | 4 |
| P_beta | (5, 5) | 08:00—18:00 | 4 |

作者规则：selection=`minimum_added_distance`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:32 | 09:42 | 592.198分钟 | 2.000 | 2.198 | 可行 |
| P_beta | 577.071分钟 | 587.071分钟 | 594.142分钟 | 7.071 | 4.142 | 可行 |

**作者手算预期：P_alpha**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S07 / F4 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the highest-rated pharmacy among those whose full service can finish by closing time.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (12, 0) | 08:00—09:41 | 4.9 |
| P_beta | (8, 0) | 08:00—10:00 | 4 |

作者规则：selection=`highest_rating`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:32 | 09:42 | 09:54 | 2.000 | 4.000 | pharmacy_service_finishes_after_close |
| P_beta | 09:32 | 09:42 | 09:50 | 2.000 | 0.000 | 可行 |

**作者手算预期：P_beta**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S08 / F4 / scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the highest-rated pharmacy among those whose full service can finish by closing time.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (12, 0) | 08:00—09:42 | 4.9 |
| P_beta | (8, 0) | 08:00—10:00 | 4 |

作者规则：selection=`highest_rating`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:32 | 09:42 | 09:54 | 2.000 | 4.000 | 可行 |
| P_beta | 09:32 | 09:42 | 09:50 | 2.000 | 0.000 | 可行 |

**作者手算预期：P_alpha**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S09 / F5 / instruction_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Restrict the choice to pharmacies already open when I leave home at 09:00. Among those that can also complete service when visited, choose the one closest to bank B.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 09:25—10:00 | 4 |
| P_beta | (15, 0) | 08:20—10:50 | 4 |

作者规则：selection=`nearest_from_bank`；availability_reference=`departure`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | not_open_at_departure |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | 可行 |

**作者手算预期：P_beta**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S10 / F5 / instruction_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. A pharmacy need not be open at 09:00; it must be open when I reach it after the bank visit and allow the full service. Choose the one closest to bank B.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 09:25—10:00 | 4 |
| P_beta | (15, 0) | 08:20—10:50 | 4 |

作者规则：selection=`nearest_from_bank`；availability_reference=`arrival`；return_by=无。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | 可行 |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | 可行 |

**作者手算预期：P_alpha**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S11 / F6 / irrelevant_scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the feasible pharmacy closest to bank B and return home by 09:10.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 08:00—18:00 | 4 |
| P_beta | (15, 0) | 08:00—18:00 | 4.9 |

作者规则：selection=`nearest_from_bank`；availability_reference=`arrival`；return_by=09:10。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | return_deadline |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | return_deadline |

**作者手算预期：INFEASIBLE**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## S12 / F6 / irrelevant_scene_change

**原始英文指令：** Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Choose the feasible pharmacy closest to bank B and return home by 09:10.

| 药房 | 坐标 | 营业时间 | 评分 |
|---|---|---|---:|
| P_alpha | (11, 0) | 08:00—18:00 | 4 |
| P_beta | (15, 0) | 08:00—18:00 | 1 |

作者规则：selection=`nearest_from_bank`；availability_reference=`arrival`；return_by=09:10。

| 药房 | 抵达 | 服务完成 | 回家 | 距银行 | 额外距离 | 可行性原因 |
|---|---|---|---|---:|---:|---|
| P_alpha | 09:31 | 09:41 | 09:52 | 1.000 | 2.000 | return_deadline |
| P_beta | 09:35 | 09:45 | 10:00 | 5.000 | 10.000 | return_deadline |

**作者手算预期：INFEASIBLE**。参考计算与此一致；选择理由按可行性过滤后再执行原句目标。

人审状态：PENDING；审核人：____；审核时间：____；判定/修改意见：____。

## 配对审核重点

| 对 | 唯一变更 | 预期 |
|---|---|---|
| F1 S01/S02 | P_alpha关门从09:40变10:00 | P_beta→P_alpha；抵达不等于能办完 |
| F2 S03/S04 | 回家截止从09:55变10:05 | P_alpha→P_beta；最高评分先满足回家条件 |
| F3 S05/S06 | P_beta的y从0变5 | P_beta→P_alpha；额外距离不同于距银行最近 |
| F4 S07/S08 | 高分药房关门从09:41变09:42 | P_beta→P_alpha；服务完成等号边界 |
| F5 S09/S10 | 已在出发时营业→访问抵达时营业 | P_beta→P_alpha；时间参照点不同 |
| F6 S11/S12 | P_beta评分4.9变1.0 | INFEASIBLE保持；09:10不可能做完20分钟银行服务并完成后续任务 |

审核通过前保持候选状态，后续任何修订另存版本并重新算术核验。
