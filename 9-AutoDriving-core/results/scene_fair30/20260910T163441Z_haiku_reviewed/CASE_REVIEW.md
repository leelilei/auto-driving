# Fair30：30 个新案例语义审阅

所有案例 PENDING。参考答案来自程序计算，未声称人工手算或人审通过。
请核对：原句是否唯一表达作者规则；时间含义是否一致；表中计算是否遵守原句；有问题逐例记录。

## F01 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(20,1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_A"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (24,-5) | 500/660 | 2.0 | 7.211 | 11.701 | 587.236 | 597.236 | 621.751 | 无 |
| P_B | (11,3) | 500/660 | 3.4 | 9.220 | 0.596 | 589.245 | 599.245 | 610.646 | 无 |
| P_C | (5,5) | 500/660 | 4.8 | 15.524 | 2.570 | 595.549 | 605.549 | 612.620 | 无 |
| P_D | (3,-6) | 500/660 | 2.2 | 18.385 | 5.068 | 598.410 | 608.410 | 615.118 | 无 |
| P_E | (13,-2) | 500/660 | 4.1 | 7.616 | 0.744 | 587.641 | 597.641 | 610.794 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F02 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(20,4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (12,10) | 500/660 | 2.2 | 10.000 | 5.224 | 590.396 | 600.396 | 616.017 | 无 |
| P_B | (20,6) | 500/660 | 3.3 | 2.000 | 2.485 | 582.396 | 592.396 | 613.277 | 无 |
| P_C | (10,9) | 500/660 | 3.2 | 11.180 | 4.238 | 591.576 | 601.576 | 615.030 | 无 |
| P_D | (12,9) | 500/660 | 2.3 | 9.434 | 4.038 | 589.830 | 599.830 | 614.830 | 无 |
| P_E | (5,4) | 500/660 | 3.8 | 15.000 | 1.007 | 595.396 | 605.396 | 611.799 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F03 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(8,2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (24,-6) | 500/660 | 4.4 | 17.889 | 34.381 | 586.135 | 596.135 | 620.873 | 无 |
| P_B | (22,8) | 500/660 | 4.0 | 15.232 | 30.395 | 583.478 | 593.478 | 616.887 | 无 |
| P_C | (7,-10) | 500/660 | 4.5 | 12.042 | 16.002 | 580.288 | 590.288 | 602.494 | 无 |
| P_D | (3,10) | 500/660 | 2.5 | 9.434 | 11.628 | 577.680 | 587.680 | 598.120 | 无 |
| P_E | (-4,7) | 500/660 | 3.3 | 13.000 | 12.816 | 581.246 | 591.246 | 599.308 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F04 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(11,-2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (-3,7) | 500/660 | 2.5 | 16.643 | 13.079 | 587.824 | 597.824 | 605.439 | 无 |
| P_B | (1,5) | 500/660 | 2.0 | 12.207 | 6.125 | 583.387 | 593.387 | 598.486 | 无 |
| P_C | (0,7) | 500/660 | 4.4 | 14.213 | 10.032 | 585.393 | 595.393 | 602.393 | 无 |
| P_D | (16,7) | 500/660 | 3.9 | 10.296 | 16.580 | 581.476 | 591.476 | 608.940 | 无 |
| P_E | (16,5) | 500/660 | 3.1 | 8.602 | 14.185 | 579.783 | 589.783 | 606.546 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F05 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(18,-2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (6,8) | 500/660 | 4.6 | 15.620 | 7.510 | 593.731 | 603.731 | 613.731 | 无 |
| P_B | (25,-2) | 500/660 | 4.4 | 7.000 | 13.969 | 585.111 | 595.111 | 620.191 | 无 |
| P_C | (2,-5) | 500/660 | 2.3 | 16.279 | 3.553 | 594.390 | 604.390 | 609.775 | 无 |
| P_D | (22,5) | 500/660 | 4.1 | 8.062 | 12.513 | 586.173 | 596.173 | 618.734 | 无 |
| P_E | (20,6) | 500/660 | 4.9 | 8.246 | 11.016 | 586.357 | 596.357 | 617.238 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F06 · open

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(19,1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (12,-8) | 500/660 | 3.1 | 11.402 | 6.798 | 590.428 | 600.428 | 614.850 | 无 |
| P_B | (8,-8) | 500/660 | 2.7 | 14.213 | 6.500 | 593.239 | 603.239 | 614.553 | 无 |
| P_C | (5,-3) | 500/660 | 4.2 | 14.560 | 1.365 | 593.587 | 603.587 | 609.417 | 无 |
| P_D | (19,6) | 500/660 | 3.5 | 5.000 | 5.899 | 584.026 | 594.026 | 613.951 | 无 |
| P_E | (0,3) | 500/660 | 3.0 | 19.105 | 3.079 | 598.131 | 608.131 | 611.131 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F07 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(8,1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (6,7) | 575/660 | 3.8 | 6.325 | 7.482 | 574.387 | 584.387 | 593.606 | pharmacy_not_open_on_arrival, not_open_at_departure |
| P_B | (-1,-9) | 555/660 | 4.4 | 13.454 | 14.447 | 581.516 | 591.516 | 600.571 | not_open_at_departure |
| P_C | (18,6) | 535/660 | 4.0 | 11.180 | 22.092 | 579.243 | 589.243 | 608.216 | 无 |
| P_D | (3,6) | 555/660 | 3.5 | 7.071 | 5.717 | 575.133 | 585.133 | 591.842 | not_open_at_departure |
| P_E | (11,10) | 500/660 | 4.3 | 9.487 | 16.291 | 577.549 | 587.549 | 602.415 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F08 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(11,3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_D"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (21,9) | 555/660 | 3.0 | 11.662 | 23.107 | 583.064 | 593.064 | 615.911 | not_open_at_departure |
| P_B | (18,-4) | 500/660 | 3.9 | 9.899 | 16.937 | 581.301 | 591.301 | 609.740 | 无 |
| P_C | (17,6) | 575/660 | 2.0 | 6.708 | 13.334 | 578.110 | 588.110 | 606.138 | not_open_at_departure |
| P_D | (4,-8) | 500/660 | 2.6 | 13.038 | 10.581 | 584.440 | 594.440 | 603.384 | 无 |
| P_E | (22,2) | 535/660 | 4.4 | 11.045 | 21.734 | 582.447 | 592.447 | 614.538 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F09 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(8,-3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_D"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (3,-9) | 555/660 | 3.0 | 7.810 | 8.753 | 576.354 | 586.354 | 595.841 | not_open_at_departure |
| P_B | (12,-7) | 535/660 | 2.7 | 5.657 | 11.005 | 574.201 | 584.201 | 598.093 | 无 |
| P_C | (9,4) | 500/660 | 2.3 | 7.071 | 8.376 | 575.615 | 585.615 | 595.464 | 无 |
| P_D | (3,-2) | 535/660 | 4.3 | 5.099 | 0.161 | 573.643 | 583.643 | 587.249 | 无 |
| P_E | (14,-10) | 535/660 | 2.8 | 9.220 | 17.880 | 577.764 | 587.764 | 604.968 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F10 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(13,-3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (22,5) | 555/660 | 2.9 | 12.042 | 21.261 | 585.383 | 595.383 | 617.944 | not_open_at_departure |
| P_B | (6,1) | 500/660 | 3.7 | 8.062 | 0.803 | 581.404 | 591.404 | 597.487 | 无 |
| P_C | (20,1) | 555/660 | 4.7 | 8.062 | 14.746 | 581.404 | 591.404 | 611.429 | not_open_at_departure |
| P_D | (17,4) | 500/660 | 4.5 | 8.062 | 12.185 | 581.404 | 591.404 | 608.868 | 无 |
| P_E | (15,2) | 500/660 | 4.6 | 5.385 | 7.176 | 578.727 | 588.727 | 603.860 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F11 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(16,1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (-1,-6) | 500/660 | 4.9 | 18.385 | 8.436 | 594.416 | 604.416 | 610.499 | 无 |
| P_B | (14,-6) | 555/660 | 3.7 | 7.280 | 6.480 | 583.311 | 593.311 | 608.543 | not_open_at_departure |
| P_C | (-5,-8) | 555/660 | 2.1 | 22.847 | 16.250 | 598.879 | 608.879 | 618.313 | not_open_at_departure |
| P_D | (16,-2) | 555/660 | 4.6 | 3.000 | 3.093 | 579.031 | 589.031 | 605.156 | not_open_at_departure |
| P_E | (9,7) | 535/660 | 2.2 | 9.220 | 4.590 | 585.251 | 595.251 | 606.653 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F12 · departure

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "departure", "return_by": null}`
场景：家(0,0)，银行(9,0)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_A"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (13,10) | 500/660 | 4.3 | 10.770 | 18.172 | 579.770 | 589.770 | 606.172 | 无 |
| P_B | (19,3) | 555/660 | 3.8 | 10.440 | 20.676 | 579.440 | 589.440 | 608.676 | not_open_at_departure |
| P_C | (7,8) | 575/660 | 4.2 | 8.246 | 9.876 | 577.246 | 587.246 | 597.876 | not_open_at_departure |
| P_D | (4,-6) | 575/660 | 3.9 | 7.810 | 6.021 | 576.810 | 586.810 | 594.021 | not_open_at_departure |
| P_E | (11,3) | 575/660 | 4.9 | 3.606 | 6.007 | 572.606 | 582.606 | 594.007 | pharmacy_not_open_on_arrival, not_open_at_departure |

裁决：PENDING；问题：____；审核者/时间：____

## F13 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 10:05.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": 605}`
场景：家(0,0)，银行(11,4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (-4,-1) | 500/660 | 4.3 | 15.811 | 8.230 | 587.516 | 597.516 | 601.639 | 无 |
| P_B | (22,8) | 500/660 | 4.5 | 11.705 | 23.409 | 583.409 | 593.409 | 616.819 | return_deadline |
| P_C | (19,-1) | 500/660 | 2.6 | 9.434 | 16.756 | 581.139 | 591.139 | 610.165 | return_deadline |
| P_D | (17,0) | 500/660 | 3.1 | 7.211 | 12.506 | 578.916 | 588.916 | 605.916 | return_deadline |
| P_E | (6,6) | 500/660 | 3.5 | 5.385 | 2.166 | 577.090 | 587.090 | 595.575 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F14 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 09:55.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": 595}`
场景：家(0,0)，银行(18,-4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "INFEASIBLE", "accepted": []}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (21,8) | 500/660 | 4.8 | 12.369 | 16.402 | 590.808 | 600.808 | 623.281 | return_deadline |
| P_B | (-5,-7) | 500/660 | 2.2 | 23.195 | 13.358 | 601.634 | 611.634 | 620.236 | return_deadline |
| P_C | (12,6) | 500/660 | 3.5 | 11.662 | 6.639 | 590.101 | 600.101 | 613.517 | return_deadline |
| P_D | (16,10) | 500/660 | 2.5 | 14.142 | 14.571 | 592.581 | 602.581 | 621.449 | return_deadline |
| P_E | (-1,-4) | 500/660 | 3.0 | 19.000 | 4.684 | 597.439 | 607.439 | 611.562 | return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F15 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 10:20.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 620}`
场景：家(0,0)，银行(15,3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (17,-7) | 500/660 | 3.2 | 10.198 | 13.286 | 585.495 | 595.495 | 613.880 | 无 |
| P_B | (-4,-5) | 500/660 | 4.7 | 20.616 | 11.722 | 595.913 | 605.913 | 612.316 | 无 |
| P_C | (14,10) | 500/660 | 4.8 | 7.071 | 8.979 | 582.368 | 592.368 | 609.573 | 无 |
| P_D | (13,-5) | 500/660 | 3.4 | 8.246 | 6.878 | 583.543 | 593.543 | 607.472 | 无 |
| P_E | (22,-2) | 500/660 | 2.1 | 8.602 | 15.396 | 583.899 | 593.899 | 615.990 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F16 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 10:05.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": 605}`
场景：家(0,0)，银行(9,-3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (21,-9) | 500/660 | 4.1 | 13.416 | 26.777 | 582.903 | 592.903 | 615.751 | return_deadline |
| P_B | (24,-5) | 500/660 | 2.1 | 15.133 | 30.161 | 584.620 | 594.620 | 619.135 | return_deadline |
| P_C | (14,-6) | 500/660 | 2.7 | 5.831 | 11.576 | 575.318 | 585.318 | 600.549 | 无 |
| P_D | (4,1) | 500/660 | 2.0 | 6.403 | 1.039 | 575.890 | 585.890 | 590.013 | 无 |
| P_E | (11,7) | 500/660 | 4.9 | 10.198 | 13.750 | 579.685 | 589.685 | 602.723 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F17 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 10:05.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": 605}`
场景：家(0,0)，银行(8,2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_A"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (1,-2) | 500/660 | 3.7 | 8.062 | 2.052 | 576.308 | 586.308 | 588.545 | 无 |
| P_B | (24,-5) | 500/660 | 4.9 | 17.464 | 33.733 | 585.710 | 595.710 | 620.226 | return_deadline |
| P_C | (20,-6) | 500/660 | 2.8 | 14.422 | 27.057 | 582.668 | 592.668 | 613.549 | return_deadline |
| P_D | (13,-5) | 500/660 | 3.5 | 8.602 | 14.285 | 576.849 | 586.849 | 600.777 | 无 |
| P_E | (19,1) | 500/660 | 4.5 | 11.045 | 21.825 | 579.292 | 589.292 | 608.318 | return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F18 · deadline

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service. Return home no later than 09:55.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": 595}`
场景：家(0,0)，银行(8,-2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_A"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (9,-4) | 500/660 | 2.8 | 2.236 | 3.839 | 570.482 | 580.482 | 590.331 | 无 |
| P_B | (22,-1) | 500/660 | 3.5 | 14.036 | 27.812 | 582.282 | 592.282 | 614.305 | return_deadline |
| P_C | (16,4) | 500/660 | 2.1 | 10.000 | 18.246 | 578.246 | 588.246 | 604.739 | return_deadline |
| P_D | (14,9) | 500/660 | 2.6 | 12.530 | 20.927 | 580.776 | 590.776 | 607.419 | return_deadline |
| P_E | (16,-6) | 500/660 | 3.3 | 8.944 | 17.786 | 577.190 | 587.190 | 604.278 | return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F19 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(8,4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_B"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (1,3) | 500/610 | 2.5 | 7.071 | 1.289 | 576.015 | 586.015 | 589.178 | 无 |
| P_B | (7,2) | 500/585 | 4.6 | 2.236 | 0.572 | 571.180 | 581.180 | 588.460 | 无 |
| P_C | (-5,2) | 500/610 | 4.2 | 13.153 | 9.594 | 582.097 | 592.097 | 597.482 | 无 |
| P_D | (19,9) | 500/610 | 3.7 | 12.083 | 24.163 | 581.027 | 591.027 | 612.051 | 无 |
| P_E | (19,-9) | 500/610 | 3.6 | 17.029 | 29.109 | 585.974 | 595.974 | 616.997 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F20 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(16,-1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (0,-9) | 500/660 | 2.8 | 17.889 | 10.857 | 593.920 | 603.920 | 612.920 | 无 |
| P_B | (17,-4) | 500/595 | 2.9 | 3.162 | 4.595 | 579.193 | 589.193 | 606.658 | 无 |
| P_C | (8,-1) | 500/595 | 3.2 | 8.000 | 0.031 | 584.031 | 594.031 | 602.093 | 无 |
| P_D | (5,7) | 500/660 | 4.6 | 13.601 | 6.173 | 589.633 | 599.633 | 608.235 | 无 |
| P_E | (12,-1) | 500/585 | 4.3 | 4.000 | 0.010 | 580.031 | 590.031 | 602.073 | pharmacy_service_finishes_after_close |

裁决：PENDING；问题：____；审核者/时间：____

## F21 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(17,-2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_D"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (23,3) | 500/595 | 3.4 | 7.810 | 13.888 | 584.927 | 594.927 | 618.122 | 无 |
| P_B | (12,4) | 500/660 | 2.1 | 7.810 | 3.342 | 584.927 | 594.927 | 607.577 | 无 |
| P_C | (8,4) | 500/585 | 2.6 | 10.817 | 2.644 | 587.934 | 597.934 | 606.878 | pharmacy_service_finishes_after_close |
| P_D | (16,7) | 500/610 | 4.7 | 9.055 | 9.402 | 586.173 | 596.173 | 613.637 | 无 |
| P_E | (13,5) | 500/660 | 2.7 | 8.062 | 4.873 | 585.180 | 595.180 | 609.108 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F22 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(20,-3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_B", "P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (-4,1) | 500/595 | 4.6 | 24.331 | 8.230 | 604.555 | 614.555 | 618.678 | pharmacy_service_finishes_after_close |
| P_B | (3,-7) | 500/660 | 3.8 | 17.464 | 4.856 | 597.688 | 607.688 | 615.304 | 无 |
| P_C | (3,1) | 500/610 | 4.2 | 17.464 | 0.403 | 597.688 | 607.688 | 610.850 | 无 |
| P_D | (25,6) | 500/595 | 2.8 | 10.296 | 15.782 | 590.519 | 600.519 | 626.229 | pharmacy_service_finishes_after_close |
| P_E | (8,8) | 500/585 | 3.9 | 16.279 | 7.369 | 596.503 | 606.503 | 617.816 | pharmacy_service_finishes_after_close |

裁决：PENDING；问题：____；审核者/时间：____

## F23 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(17,-4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_B"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (14,-1) | 500/585 | 3.2 | 4.243 | 0.814 | 581.707 | 591.707 | 605.743 | pharmacy_service_finishes_after_close |
| P_B | (9,-10) | 500/610 | 4.4 | 10.000 | 5.989 | 587.464 | 597.464 | 610.918 | 无 |
| P_C | (0,-1) | 500/585 | 3.1 | 17.263 | 0.798 | 594.727 | 604.727 | 605.727 | pharmacy_service_finishes_after_close |
| P_D | (4,0) | 500/585 | 2.2 | 13.601 | 0.137 | 591.066 | 601.066 | 605.066 | pharmacy_service_finishes_after_close |
| P_E | (6,-5) | 500/585 | 2.0 | 11.045 | 1.391 | 588.510 | 598.510 | 606.320 | pharmacy_service_finishes_after_close |

裁决：PENDING；问题：____；审核者/时间：____

## F24 · closing

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Pharmacies need not be open when I leave home; they must be open when I arrive and allow the full service.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "arrival", "return_by": null}`
场景：家(0,0)，银行(13,-1)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_C"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (24,-7) | 500/610 | 4.8 | 12.530 | 24.492 | 585.568 | 595.568 | 620.568 | 无 |
| P_B | (3,2) | 500/585 | 3.4 | 10.440 | 1.007 | 583.479 | 593.479 | 597.084 | pharmacy_service_finishes_after_close |
| P_C | (22,6) | 500/660 | 4.9 | 11.402 | 21.167 | 584.440 | 594.440 | 617.244 | 无 |
| P_D | (23,-7) | 500/660 | 4.6 | 11.662 | 22.665 | 584.700 | 594.700 | 618.742 | 无 |
| P_E | (1,-4) | 500/595 | 3.2 | 12.369 | 3.454 | 585.408 | 595.408 | 599.531 | pharmacy_service_finishes_after_close |

裁决：PENDING；问题：____；审核者/时间：____

## F25 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 10:20.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "departure", "return_by": 620}`
场景：家(0,0)，银行(9,-4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_E"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (13,-9) | 575/595 | 2.9 | 6.403 | 12.366 | 576.252 | 586.252 | 602.063 | not_open_at_departure |
| P_B | (22,-5) | 500/585 | 2.6 | 13.038 | 25.751 | 582.887 | 592.887 | 615.448 | pharmacy_service_finishes_after_close |
| P_C | (22,7) | 555/595 | 3.2 | 17.029 | 30.267 | 586.878 | 596.878 | 619.965 | pharmacy_service_finishes_after_close, not_open_at_departure |
| P_D | (25,9) | 500/595 | 2.3 | 20.616 | 37.337 | 590.464 | 600.464 | 627.035 | pharmacy_service_finishes_after_close, return_deadline |
| P_E | (17,-1) | 535/660 | 2.7 | 8.544 | 15.725 | 578.393 | 588.393 | 605.422 | 无 |

裁决：PENDING；问题：____；审核者/时间：____

## F26 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 10:20.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "departure", "return_by": 620}`
场景：家(0,0)，银行(14,0)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_D"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (1,-4) | 575/585 | 3.2 | 13.601 | 3.725 | 587.601 | 597.601 | 601.725 | pharmacy_service_finishes_after_close, not_open_at_departure |
| P_B | (22,-1) | 555/585 | 2.8 | 8.062 | 16.085 | 582.062 | 592.062 | 614.085 | pharmacy_service_finishes_after_close, not_open_at_departure |
| P_C | (23,-10) | 535/660 | 3.4 | 13.454 | 24.533 | 587.454 | 597.454 | 622.533 | return_deadline |
| P_D | (4,2) | 500/595 | 4.4 | 10.198 | 0.670 | 584.198 | 594.198 | 598.670 | 无 |
| P_E | (5,-4) | 575/595 | 4.9 | 9.849 | 2.252 | 583.849 | 593.849 | 600.252 | not_open_at_departure |

裁决：PENDING；问题：____；审核者/时间：____

## F27 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 09:55.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "departure", "return_by": 595}`
场景：家(0,0)，银行(17,3)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "INFEASIBLE", "accepted": []}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (14,-8) | 500/585 | 2.1 | 11.402 | 10.264 | 588.664 | 598.664 | 614.789 | pharmacy_service_finishes_after_close, return_deadline |
| P_B | (12,-2) | 555/660 | 2.9 | 7.071 | 1.974 | 584.334 | 594.334 | 606.499 | not_open_at_departure, return_deadline |
| P_C | (23,4) | 575/610 | 2.6 | 6.083 | 12.165 | 583.345 | 593.345 | 616.691 | not_open_at_departure, return_deadline |
| P_D | (-1,-4) | 555/610 | 4.1 | 19.313 | 6.174 | 596.576 | 606.576 | 610.699 | not_open_at_departure, return_deadline |
| P_E | (20,-4) | 535/610 | 4.7 | 7.616 | 10.749 | 584.878 | 594.878 | 615.275 | return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F28 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the smallest straight-line distance from bank B. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 09:55.

作者待审规则：`{"selection": "nearest_from_bank", "availability_reference": "departure", "return_by": 595}`
场景：家(0,0)，银行(17,2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "INFEASIBLE", "accepted": []}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (2,5) | 575/610 | 4.4 | 15.297 | 3.565 | 592.414 | 602.414 | 607.799 | not_open_at_departure, return_deadline |
| P_B | (11,5) | 575/595 | 4.0 | 6.708 | 1.674 | 583.825 | 593.825 | 605.908 | not_open_at_departure, return_deadline |
| P_C | (1,5) | 500/585 | 3.9 | 16.279 | 4.261 | 593.396 | 603.396 | 608.495 | pharmacy_service_finishes_after_close, return_deadline |
| P_D | (5,1) | 535/610 | 2.5 | 12.042 | 0.023 | 589.159 | 599.159 | 604.258 | return_deadline |
| P_E | (24,-8) | 500/610 | 3.0 | 12.207 | 20.388 | 589.324 | 599.324 | 624.622 | return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F29 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one adding the least travel distance compared with going directly from bank B to home. Added distance means distance(B, pharmacy) + distance(pharmacy, home) - distance(B, home). Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 10:05.

作者待审规则：`{"selection": "minimum_added_distance", "availability_reference": "departure", "return_by": 605}`
场景：家(0,0)，银行(16,4)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "INFEASIBLE", "accepted": []}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (9,-1) | 555/610 | 3.3 | 8.602 | 1.165 | 585.095 | 595.095 | 604.150 | not_open_at_departure |
| P_B | (-3,-3) | 535/585 | 3.4 | 20.248 | 7.999 | 596.741 | 606.741 | 610.984 | pharmacy_service_finishes_after_close, return_deadline |
| P_C | (21,4) | 555/595 | 4.6 | 5.000 | 9.885 | 581.492 | 591.492 | 612.870 | not_open_at_departure, return_deadline |
| P_D | (-2,-1) | 555/595 | 2.6 | 18.682 | 4.425 | 595.174 | 605.174 | 607.410 | pharmacy_service_finishes_after_close, not_open_at_departure, return_deadline |
| P_E | (-4,-6) | 575/595 | 3.5 | 22.361 | 13.079 | 598.853 | 608.853 | 616.064 | pharmacy_service_finishes_after_close, not_open_at_departure, return_deadline |

裁决：PENDING；问题：____；审核者/时间：____

## F30 · combined

Start at home at 09:00. Visit bank B first, then exactly one pharmacy, then return home. Travel along straight lines at 1 distance unit per minute. Bank service takes 20 minutes and pharmacy service takes 10 minutes. Do not wait for a place to open. Start service immediately on arrival; each service must finish no later than closing time. If no pharmacy can satisfy every requirement, report INFEASIBLE. Among pharmacies satisfying every requirement, choose the one with the highest rating. Restrict the choice to pharmacies already open when I leave home at 09:00; service must also fit their opening hours when visited. Return home no later than 10:20.

作者待审规则：`{"selection": "highest_rating", "availability_reference": "departure", "return_by": 620}`
场景：家(0,0)，银行(17,-2)；09:00出发；银行20分钟、药房10分钟；速度1。
参考计算：`{"status": "OK", "accepted": ["P_B"]}`

| POI | 坐标 | 开门/关门（午夜起分钟） | 评分 | 距银行 | 绕路 | 到达 | 服务结束 | 回家 | 不可行原因 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| P_A | (22,-10) | 575/595 | 2.0 | 9.434 | 16.483 | 586.551 | 596.551 | 620.717 | pharmacy_service_finishes_after_close, not_open_at_departure, return_deadline |
| P_B | (12,-4) | 500/660 | 3.1 | 5.385 | 0.917 | 582.502 | 592.502 | 605.152 | 无 |
| P_C | (13,-9) | 575/610 | 2.9 | 8.062 | 6.756 | 585.180 | 595.180 | 610.991 | not_open_at_departure |
| P_D | (17,7) | 535/660 | 2.7 | 9.000 | 10.268 | 586.117 | 596.117 | 614.502 | 无 |
| P_E | (10,4) | 555/585 | 3.0 | 9.220 | 2.873 | 586.337 | 596.337 | 607.107 | pharmacy_service_finishes_after_close, not_open_at_departure |

裁决：PENDING；问题：____；审核者/时间：____

