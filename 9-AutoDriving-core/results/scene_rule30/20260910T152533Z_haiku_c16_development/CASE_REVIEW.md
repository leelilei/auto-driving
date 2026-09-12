# Scene-Rule30 候选案例审阅表

状态：PENDING。仅离线作者计算，尚未模型调用。审核应核对原句、规则、场景时刻与预期，而非只认可计算结果。
这是根据既有开发诊断补充的数据，不是未暴露的确认性测试集。

## R01 · G1 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (10, 2) | 500–660 | 4 | 2.000 | 2.198 | 572.000 | 582.000 | 592.198 | True |
| P_beta | (4, 0) | 500–660 | 3.5 | 6.000 | 0.000 | 576.000 | 586.000 | 590.000 | True |
| P_gamma | (15, 6) | 500–660 | 4.9 | 7.810 | 13.966 | 577.810 | 587.810 | 603.966 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R02 · G1 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (10, 2) | 500–660 | 4 | 2.000 | 2.198 | 572.000 | 582.000 | 592.198 | True |
| P_beta | (4, 0) | 500–660 | 3.5 | 6.000 | 0.000 | 576.000 | 586.000 | 590.000 | True |
| P_gamma | (15, 6) | 500–660 | 4.9 | 7.810 | 13.966 | 577.810 | 587.810 | 603.966 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R03 · G1 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (10, 2) | 500–660 | 4 | 2.000 | 2.198 | 572.000 | 582.000 | 592.198 | True |
| P_beta | (4, 0) | 500–660 | 3.5 | 6.000 | 0.000 | 576.000 | 586.000 | 590.000 | True |
| P_gamma | (15, 6) | 500–660 | 4.9 | 7.810 | 13.966 | 577.810 | 587.810 | 603.966 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R04 · G2 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (6, 6) | 500–660 | 4.9 | 7.211 | 5.696 | 577.211 | 587.211 | 595.696 | True |
| P_beta | (11, 1) | 500–660 | 4 | 1.414 | 2.460 | 571.414 | 581.414 | 592.460 | True |
| P_gamma | (6, 0) | 500–660 | 3.5 | 4.000 | 0.000 | 574.000 | 584.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R05 · G2 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (6, 6) | 500–660 | 4.9 | 7.211 | 5.696 | 577.211 | 587.211 | 595.696 | True |
| P_beta | (11, 1) | 500–660 | 4 | 1.414 | 2.460 | 571.414 | 581.414 | 592.460 | True |
| P_gamma | (6, 0) | 500–660 | 3.5 | 4.000 | 0.000 | 574.000 | 584.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R06 · G2 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (6, 6) | 500–660 | 4.9 | 7.211 | 5.696 | 577.211 | 587.211 | 595.696 | True |
| P_beta | (11, 1) | 500–660 | 4 | 1.414 | 2.460 | 571.414 | 581.414 | 592.460 | True |
| P_gamma | (6, 0) | 500–660 | 3.5 | 4.000 | 0.000 | 574.000 | 584.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R07 · G3 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (2, 0) | 500–660 | 3.5 | 8.000 | 0.000 | 578.000 | 588.000 | 590.000 | True |
| P_beta | (13, -4) | 500–660 | 4.9 | 5.000 | 8.601 | 575.000 | 585.000 | 598.601 | True |
| P_gamma | (9, 2) | 500–660 | 4 | 2.236 | 1.456 | 572.236 | 582.236 | 591.456 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R08 · G3 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (2, 0) | 500–660 | 3.5 | 8.000 | 0.000 | 578.000 | 588.000 | 590.000 | True |
| P_beta | (13, -4) | 500–660 | 4.9 | 5.000 | 8.601 | 575.000 | 585.000 | 598.601 | True |
| P_gamma | (9, 2) | 500–660 | 4 | 2.236 | 1.456 | 572.236 | 582.236 | 591.456 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R09 · G3 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (2, 0) | 500–660 | 3.5 | 8.000 | 0.000 | 578.000 | 588.000 | 590.000 | True |
| P_beta | (13, -4) | 500–660 | 4.9 | 5.000 | 8.601 | 575.000 | 585.000 | 598.601 | True |
| P_gamma | (9, 2) | 500–660 | 4 | 2.236 | 1.456 | 572.236 | 582.236 | 591.456 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R10 · G4 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, 1) | 500–660 | 4 | 2.236 | 4.278 | 572.236 | 582.236 | 594.278 | True |
| P_beta | (7, 0) | 500–660 | 3.5 | 3.000 | 0.000 | 573.000 | 583.000 | 590.000 | True |
| P_gamma | (0, 5) | 500–660 | 4.9 | 11.180 | 6.180 | 581.180 | 591.180 | 596.180 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R11 · G4 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, 1) | 500–660 | 4 | 2.236 | 4.278 | 572.236 | 582.236 | 594.278 | True |
| P_beta | (7, 0) | 500–660 | 3.5 | 3.000 | 0.000 | 573.000 | 583.000 | 590.000 | True |
| P_gamma | (0, 5) | 500–660 | 4.9 | 11.180 | 6.180 | 581.180 | 591.180 | 596.180 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R12 · G4 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, 1) | 500–660 | 4 | 2.236 | 4.278 | 572.236 | 582.236 | 594.278 | True |
| P_beta | (7, 0) | 500–660 | 3.5 | 3.000 | 0.000 | 573.000 | 583.000 | 590.000 | True |
| P_gamma | (0, 5) | 500–660 | 4.9 | 11.180 | 6.180 | 581.180 | 591.180 | 596.180 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R13 · G5 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, -6) | 500–660 | 4.9 | 6.325 | 9.741 | 576.325 | 586.325 | 599.741 | True |
| P_beta | (8, -1) | 500–660 | 4 | 2.236 | 0.298 | 572.236 | 582.236 | 590.298 | True |
| P_gamma | (3, 0) | 500–660 | 3.5 | 7.000 | 0.000 | 577.000 | 587.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R14 · G5 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, -6) | 500–660 | 4.9 | 6.325 | 9.741 | 576.325 | 586.325 | 599.741 | True |
| P_beta | (8, -1) | 500–660 | 4 | 2.236 | 0.298 | 572.236 | 582.236 | 590.298 | True |
| P_gamma | (3, 0) | 500–660 | 3.5 | 7.000 | 0.000 | 577.000 | 587.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R15 · G5 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, -6) | 500–660 | 4.9 | 6.325 | 9.741 | 576.325 | 586.325 | 599.741 | True |
| P_beta | (8, -1) | 500–660 | 4 | 2.236 | 0.298 | 572.236 | 582.236 | 590.298 | True |
| P_gamma | (3, 0) | 500–660 | 3.5 | 7.000 | 0.000 | 577.000 | 587.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R16 · G6 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (5, 1) | 500–660 | 3.5 | 5.099 | 0.198 | 575.099 | 585.099 | 590.198 | True |
| P_beta | (16, 2) | 500–660 | 4.9 | 6.325 | 12.449 | 576.325 | 586.325 | 602.449 | True |
| P_gamma | (10, -3) | 500–660 | 4 | 3.000 | 3.440 | 573.000 | 583.000 | 593.440 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R17 · G6 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (5, 1) | 500–660 | 3.5 | 5.099 | 0.198 | 575.099 | 585.099 | 590.198 | True |
| P_beta | (16, 2) | 500–660 | 4.9 | 6.325 | 12.449 | 576.325 | 586.325 | 602.449 | True |
| P_gamma | (10, -3) | 500–660 | 4 | 3.000 | 3.440 | 573.000 | 583.000 | 593.440 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R18 · G6 · objective_triple

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (5, 1) | 500–660 | 3.5 | 5.099 | 0.198 | 575.099 | 585.099 | 590.198 | True |
| P_beta | (16, 2) | 500–660 | 4.9 | 6.325 | 12.449 | 576.325 | 586.325 | 602.449 | True |
| P_gamma | (10, -3) | 500–660 | 4 | 3.000 | 3.440 | 573.000 | 583.000 | 593.440 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R19 · C1 · availability_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "departure", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (10, 2) | 565–660 | 4 | 2.000 | 2.198 | 572.000 | 582.000 | 592.198 | False |
| P_beta | (4, 0) | 500–660 | 3.5 | 6.000 | 0.000 | 576.000 | 586.000 | 590.000 | True |
| P_gamma | (15, 6) | 500–660 | 4.9 | 7.810 | 13.966 | 577.810 | 587.810 | 603.966 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R20 · C1 · availability_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home at 09:00; they must be open when I arrive and allow the full service.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (10, 2) | 565–660 | 4 | 2.000 | 2.198 | 572.000 | 582.000 | 592.198 | True |
| P_beta | (4, 0) | 500–660 | 3.5 | 6.000 | 0.000 | 576.000 | 586.000 | 590.000 | True |
| P_gamma | (15, 6) | 500–660 | 4.9 | 7.810 | 13.966 | 577.810 | 587.810 | 603.966 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R21 · C2 · deadline_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Return home no later than 09:55.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 595}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (11, 0) | 500–660 | 4 | 1.000 | 2.000 | 571.000 | 581.000 | 592.000 | True |
| P_beta | (8, 0) | 500–660 | 3.5 | 2.000 | 0.000 | 572.000 | 582.000 | 590.000 | True |
| P_gamma | (15, 0) | 500–660 | 4.9 | 5.000 | 10.000 | 575.000 | 585.000 | 600.000 | False |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R22 · C2 · deadline_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Return home no later than 10:00.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 600}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (11, 0) | 500–660 | 4 | 1.000 | 2.000 | 571.000 | 581.000 | 592.000 | True |
| P_beta | (8, 0) | 500–660 | 3.5 | 2.000 | 0.000 | 572.000 | 582.000 | 590.000 | True |
| P_gamma | (15, 0) | 500–660 | 4.9 | 5.000 | 10.000 | 575.000 | 585.000 | 600.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R23 · C3 · closing_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, 0) | 500–581 | 4.9 | 2.000 | 4.000 | 572.000 | 582.000 | 594.000 | False |
| P_beta | (8, 0) | 500–660 | 4 | 2.000 | 0.000 | 572.000 | 582.000 | 590.000 | True |
| P_gamma | (15, 0) | 500–660 | 3.5 | 5.000 | 10.000 | 575.000 | 585.000 | 600.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R24 · C3 · closing_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, 0) | 500–582 | 4.9 | 2.000 | 4.000 | 572.000 | 582.000 | 594.000 | True |
| P_beta | (8, 0) | 500–660 | 4 | 2.000 | 0.000 | 572.000 | 582.000 | 590.000 | True |
| P_gamma | (15, 0) | 500–660 | 3.5 | 5.000 | 10.000 | 575.000 | 585.000 | 600.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R25 · C4 · irrelevant_rating_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (6, 6) | 500–660 | 4.9 | 7.211 | 5.696 | 577.211 | 587.211 | 595.696 | True |
| P_beta | (11, 1) | 500–660 | 4 | 1.414 | 2.460 | 571.414 | 581.414 | 592.460 | True |
| P_gamma | (6, 0) | 500–660 | 3.5 | 4.000 | 0.000 | 574.000 | 584.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R26 · C4 · irrelevant_rating_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B.

作者规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_beta"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (6, 6) | 500–660 | 4.9 | 7.211 | 5.696 | 577.211 | 587.211 | 595.696 | True |
| P_beta | (11, 1) | 500–660 | 0.5 | 1.414 | 2.460 | 571.414 | 581.414 | 592.460 | True |
| P_gamma | (6, 0) | 500–660 | 3.5 | 4.000 | 0.000 | 574.000 | 584.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R27 · C5 · id_permutation_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_gamma"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (12, -6) | 500–660 | 4.9 | 6.325 | 9.741 | 576.325 | 586.325 | 599.741 | True |
| P_beta | (8, -1) | 500–660 | 4 | 2.236 | 0.298 | 572.236 | 582.236 | 590.298 | True |
| P_gamma | (3, 0) | 500–660 | 3.5 | 7.000 | 0.000 | 577.000 | 587.000 | 590.000 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R28 · C5 · id_permutation_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home).

作者规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
手定预期：`["P_alpha"]`；参考状态：OK

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (3, 0) | 500–660 | 3.5 | 7.000 | 0.000 | 577.000 | 587.000 | 590.000 | True |
| P_beta | (12, -6) | 500–660 | 4.9 | 6.325 | 9.741 | 576.325 | 586.325 | 599.741 | True |
| P_gamma | (8, -1) | 500–660 | 4 | 2.236 | 0.298 | 572.236 | 582.236 | 590.298 | True |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R29 · C6 · infeasible_invariance_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Return home no later than 09:10.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 550}`
手定预期：`[]`；参考状态：INFEASIBLE

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (2, 0) | 500–660 | 3.5 | 8.000 | 0.000 | 578.000 | 588.000 | 590.000 | False |
| P_beta | (13, -4) | 500–660 | 4.9 | 5.000 | 8.601 | 575.000 | 585.000 | 598.601 | False |
| P_gamma | (9, 2) | 500–660 | 4 | 2.236 | 1.456 | 572.236 | 582.236 | 591.456 | False |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

## R30 · C6 · infeasible_invariance_pair

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Return home no later than 09:10.

作者规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 550}`
手定预期：`[]`；参考状态：INFEASIBLE

| POI | 坐标 | 开门–关门（分钟） | 评分 | 距银行 | 增加距离 | 到达 | 服务结束 | 回家 | 可行 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_alpha | (2, 0) | 500–660 | 3.5 | 8.000 | 0.000 | 578.000 | 588.000 | 590.000 | False |
| P_beta | (13, -4) | 500–660 | 1 | 5.000 | 8.601 | 575.000 | 585.000 | 598.601 | False |
| P_gamma | (9, 2) | 500–660 | 4 | 2.236 | 1.456 | 572.236 | 582.236 | 591.456 | False |

审核者：____；时间：____；裁决：PENDING；问题/修订：____

