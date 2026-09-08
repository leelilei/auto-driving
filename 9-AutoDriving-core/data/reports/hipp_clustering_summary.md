# HIPP 数据集预处理与语义聚类去重审计报告

> 生成日期：2026-09-06  
> 数据源：`data/raw/HIPP.json`（公开 LLMAP 冻结提交 `281f6ad95f42ca386400e5288f006aeffa2ac282`）

## 1. 聚类去重核心统计

- **原始记录总数**：`1000` 条
- **去重后合成标签簇（待文本语义审核）**：`609` 簇
- **平均每簇样本数**：`1.64` 条（簇大小分布：{1: 469, 2: 71, 3: 30, 4: 11, 6: 6}）
- **边界**：这些簇由合成硬标签与合成权重方向分组，尚未通过文本人工审核，不能直接称为 609 个独立真实意图。正式抽样前还需核对文本偏好与近重复。

---

## 2. 独立意图簇属性分布

### 2.1 请求 POI 数量分布
| POI 数量 | 语义簇数量 | 占比 |
|:---:|---:|---:|
| 1 类 POI | 70 | 11.5% |
| 2 类 POI | 109 | 17.9% |
| 3 类 POI | 139 | 22.8% |
| 4 类 POI | 146 | 24.0% |
| 5 类 POI | 145 | 23.8% |

### 2.2 时间约束与先后依赖分布
| 约束维度 | 具有该约束的簇数 | 占比 |
|---|---:|---:|
| 含最晚截止时间 ($T \neq \text{null}$) | 284 | 46.6% |
| 无截止时间约束 | 325 | 53.4% |
| 含先后顺序依赖 ($D \neq \emptyset$) | 374 | 61.4% |
| 无先后顺序依赖 | 235 | 38.6% |

### 2.3 偏好方向分布
| 偏好方向 | 语义簇数量 | 占比 |
|---|---:|---:|
| 质量优先 (Quality First, $w > 0.5$) | 259 | 42.5% |
| 距离优先 (Distance First, $w < 0.5$) | 269 | 44.2% |
| 均衡偏好 (Balanced, $w = 0.5$) | 81 | 13.3% |

---

## 3. 代表性语义簇样例

| 簇 ID | POI 集合 | 截止时间 | 依赖关系 | 偏好方向 | 样本数 | 样例指令 |
|:---:|---|---|---|:---:|:---:|---|
| 0 | `supermarket` | None | `None` | distance_first | 8 | Let's head to the supermarket today. It would be great to be efficient with our route. |
| 1 | `bank, library, shopping_mall, supermarket` | None | `None` | quality_first | 6 | Today, you'll be visiting the library, shopping mall, bank, and supermarket. Although there's no specific time to finish by, try to focus on exploring places with higher ratings. Enjoy your trip without any specific order to follow! |
| 2 | `bank, library, supermarket` | 1020 min | `None` | quality_first | 1 | Today, make sure to visit the library, the supermarket, and the bank. Please be home by 17:00. It's important to focus on places with higher ratings, so prioritize them even if it takes a little longer. |
| 3 | `bank, library, pharmacy, shopping_mall` | None | `bank->pharmacy` | quality_first | 1 | Today, make sure to visit the shopping mall, bank, pharmacy, and library. While planning your trip, prioritize going to high-rated places. It's important to stop by the bank before heading to the pharmacy. |
| 4 | `bank, library, pharmacy, shopping_mall, supermarket` | None | `library->shopping_mall` | balanced | 1 | Today, let's visit the bank, the library, the shopping mall, the supermarket, and the pharmacy. I hope we can find a balance between visiting some well-rated places without making our route too long. Make sure to stop by the library before heading over to the shopping mall. |
| 5 | `bank, library, pharmacy, shopping_mall, supermarket` | None | `library->supermarket; shopping_mall->pharmacy` | quality_first | 1 | Today, make sure you visit the bank, library, supermarket, shopping mall, and pharmacy. Focus on visiting places with high ratings. Start by going to the library before heading to the supermarket, and ensure you visit the shopping mall before going to the pharmacy. |
| 6 | `bank, pharmacy, shopping_mall` | None | `pharmacy->bank; shopping_mall->bank; shopping_mall->pharmacy` | distance_first | 1 | Today, you need to visit the shopping mall, pharmacy, and bank. Since there is a need for efficiency, it's important to prioritize a shorter route. Start at the shopping mall, make your way to the pharmacy next, and finally head to the bank. |
| 7 | `bank, pharmacy, supermarket` | 1260 min | `pharmacy->supermarket` | balanced | 1 | Today, you need to visit the bank, pharmacy, and supermarket. Be sure to return by 21:00. While you're out, try to balance both visiting well-rated places and keeping the route efficient. Remember to stop by the pharmacy before heading to the supermarket. |