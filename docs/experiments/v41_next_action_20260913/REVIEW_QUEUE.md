# LLMAP 迁移实验指令与改写审核队列 (REVIEW_QUEUE)

- **审核日期**: `2026-09-13`
- **执行环境**: `9-AutoDriving-core`
- **样本规模**: 5 组开发集 (20 句) + 40 组评估集 (160 句)
- **历史暴露核验**: 所有选中源索引与历史 160 组完全正交（0 交集）

---

## 1. 5 组开发用例清单 (Dev 5 Groups / 20 Utterances)

### 组 dev_001 (HIPP Source Index: 0)
- **Gold POIs**: `['supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.4` (distance_first)
- **4 变体文本**:
  - **V0** (`dev_001_v0`): Let's head to the supermarket today. It would be great to be efficient with our route.
  - **V1** (`dev_001_v1`): Please visit the supermarket today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`dev_001_v2`): Your itinerary today includes visiting the supermarket. Keep the travel distance minimal and direct.
  - **V3** (`dev_001_v3`): Hey, need you to stop by the supermarket today. Take the quickest and most efficient route possible.

### 组 dev_002 (HIPP Source Index: 1)
- **Gold POIs**: `['library', 'shopping_mall', 'bank', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`dev_002_v0`): Today, you'll be visiting the library, shopping mall, bank, and supermarket. Although there's no specific time to finish by, try to focus on exploring places with higher ratings. Enjoy your trip without any specific order to follow!
  - **V1** (`dev_002_v1`): Please visit the library, the shopping mall, the bank, and the supermarket today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`dev_002_v2`): Your itinerary today includes visiting the library, the shopping mall, the bank, and the supermarket. Give top priority to reputable, well-reviewed venues.
  - **V3** (`dev_002_v3`): Hey, need you to stop by the library, the shopping mall, the bank, and the supermarket today. Aim for the highest-rated places since quality is the main goal.

### 组 dev_003 (HIPP Source Index: 3)
- **Gold POIs**: `['shopping_mall', 'bank', 'pharmacy', 'library']`
- **Time Limit**: `None`
- **Dependencies**: `[['bank', 'pharmacy']]`
- **Quality Weight ($w$)**: `0.8` (quality_first)
- **4 变体文本**:
  - **V0** (`dev_003_v0`): Today, make sure to visit the shopping mall, bank, pharmacy, and library. While planning your trip, prioritize going to high-rated places. It's important to stop by the bank before heading to the pharmacy.
  - **V1** (`dev_003_v1`): Please visit the shopping mall, the bank, the pharmacy, and the library today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the pharmacy.
  - **V2** (`dev_003_v2`): Your itinerary today includes visiting the shopping mall, the bank, the pharmacy, and the library. Remember to stop at the bank before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`dev_003_v3`): Hey, need you to stop by the shopping mall, the bank, the pharmacy, and the library today. Be sure to hit the bank first before the pharmacy. Aim for the highest-rated places since quality is the main goal.

### 组 dev_004 (HIPP Source Index: 8)
- **Gold POIs**: `['shopping_mall', 'pharmacy', 'supermarket', 'library']`
- **Time Limit**: `None`
- **Dependencies**: `[['supermarket', 'library']]`
- **Quality Weight ($w$)**: `0.2` (distance_first)
- **4 变体文本**:
  - **V0** (`dev_004_v0`): Today, make sure to visit the shopping mall, pharmacy, supermarket, and library. Please prioritize an efficient route to get everything done swiftly. Remember, you need to stop by the supermarket before heading to the library.
  - **V1** (`dev_004_v1`): Please visit the shopping mall, the pharmacy, the supermarket, and the library today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the supermarket prior to the library.
  - **V2** (`dev_004_v2`): Your itinerary today includes visiting the shopping mall, the pharmacy, the supermarket, and the library. Remember to stop at the supermarket before heading to the library. Keep the travel distance minimal and direct.
  - **V3** (`dev_004_v3`): Hey, need you to stop by the shopping mall, the pharmacy, the supermarket, and the library today. Be sure to hit the supermarket first before the library. Take the quickest and most efficient route possible.

### 组 dev_005 (HIPP Source Index: 12)
- **Gold POIs**: `['pharmacy', 'library', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`dev_005_v0`): Make sure to visit the pharmacy, library, and supermarket today. It's important to prioritize locations that are well-rated as we go. Enjoy your day!
  - **V1** (`dev_005_v1`): Please visit the pharmacy, the library, and the supermarket today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`dev_005_v2`): Your itinerary today includes visiting the pharmacy, the library, and the supermarket. Give top priority to reputable, well-reviewed venues.
  - **V3** (`dev_005_v3`): Hey, need you to stop by the pharmacy, the library, and the supermarket today. Aim for the highest-rated places since quality is the main goal.

---

## 2. 40 组评估用例清单 (Eval 40 Groups / 160 Utterances)

### 组 transfer_001 (HIPP Source Index: 13)
- **Gold POIs**: `['library', 'bank', 'supermarket', 'shopping_mall']`
- **Time Limit**: `23:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_001_v0`): Today, make sure to visit the library, bank, supermarket, and shopping mall. Please return home by 23:00. Prioritize visiting the highest-rated places on your list for a rewarding experience.
  - **V1** (`transfer_001_v1`): Please visit the library, the bank, the supermarket, and the shopping mall today. Ensure that you return home by 23:00. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_001_v2`): Your itinerary today includes visiting the library, the bank, the supermarket, and the shopping mall. All visits must be completed with return by 23:00. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_001_v3`): Hey, need you to stop by the library, the bank, the supermarket, and the shopping mall today. Make sure we are back by 23:00. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_002 (HIPP Source Index: 14)
- **Gold POIs**: `['bank', 'pharmacy', 'supermarket', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.6` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_002_v0`): Today, we need to visit the bank, pharmacy, supermarket, and shopping mall. I'd like to keep the route reasonably efficient while ensuring we visit worthwhile places. Let's plan the day accordingly without any specific order to follow.
  - **V1** (`transfer_002_v1`): Please visit the bank, the pharmacy, the supermarket, and the shopping mall today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_002_v2`): Your itinerary today includes visiting the bank, the pharmacy, the supermarket, and the shopping mall. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_002_v3`): Hey, need you to stop by the bank, the pharmacy, the supermarket, and the shopping mall today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_003 (HIPP Source Index: 15)
- **Gold POIs**: `['pharmacy', 'library', 'shopping_mall', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_003_v0`): Today, please visit the pharmacy, library, shopping mall, and supermarket. It's important that we prioritize visiting places with the best ratings. Enjoy your day!
  - **V1** (`transfer_003_v1`): Please visit the pharmacy, the library, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_003_v2`): Your itinerary today includes visiting the pharmacy, the library, the shopping mall, and the supermarket. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_003_v3`): Hey, need you to stop by the pharmacy, the library, the shopping mall, and the supermarket today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_004 (HIPP Source Index: 16)
- **Gold POIs**: `['shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_004_v0`): Let's make sure to visit the shopping mall today. Since the quality of our destinations is quite important, we should prioritize a place with a high rating for a better experience. There's no specific order needed for our visit, so we have flexibility in our schedule.
  - **V1** (`transfer_004_v1`): Please visit the shopping mall today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_004_v2`): Your itinerary today includes visiting the shopping mall. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_004_v3`): Hey, need you to stop by the shopping mall today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_005 (HIPP Source Index: 17)
- **Gold POIs**: `['bank', 'pharmacy', 'supermarket', 'library', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[['supermarket', 'library']]`
- **Quality Weight ($w$)**: `0.6` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_005_v0`): Today, you'll need to make stops at the bank, pharmacy, supermarket, library, and shopping mall. While visiting these places, try to balance getting to some enjoyable spots with not taking too long on the route. Remember to stop by the supermarket before heading to the library.
  - **V1** (`transfer_005_v1`): Please visit the bank, the pharmacy, the supermarket, the library, and the shopping mall today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the supermarket prior to the library.
  - **V2** (`transfer_005_v2`): Your itinerary today includes visiting the bank, the pharmacy, the supermarket, the library, and the shopping mall. Remember to stop at the supermarket before heading to the library. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_005_v3`): Hey, need you to stop by the bank, the pharmacy, the supermarket, the library, and the shopping mall today. Be sure to hit the supermarket first before the library. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_006 (HIPP Source Index: 18)
- **Gold POIs**: `['supermarket', 'shopping_mall', 'library', 'pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_006_v0`): Today, you'll be visiting the supermarket, the shopping mall, the library, and the pharmacy. Make sure to prioritize places with higher ratings as they are more important. No specific visiting order is required, so feel free to plan your stops as you see fit.
  - **V1** (`transfer_006_v1`): Please visit the supermarket, the shopping mall, the library, and the pharmacy today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_006_v2`): Your itinerary today includes visiting the supermarket, the shopping mall, the library, and the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_006_v3`): Hey, need you to stop by the supermarket, the shopping mall, the library, and the pharmacy today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_007 (HIPP Source Index: 19)
- **Gold POIs**: `['supermarket', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_007_v0`): Today, make sure to visit both the supermarket and the shopping mall. Aim for a balance between visiting places of interest with reasonable ratings and keeping the journey efficient. Enjoy your day!
  - **V1** (`transfer_007_v1`): Please visit the supermarket and the shopping mall today. Try to balance good quality with route efficiency.
  - **V2** (`transfer_007_v2`): Your itinerary today includes visiting the supermarket and the shopping mall. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_007_v3`): Hey, need you to stop by the supermarket and the shopping mall today. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_008 (HIPP Source Index: 22)
- **Gold POIs**: `['bank', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_008_v0`): Today, you need to visit the bank and the shopping mall. Focus on visiting places with a good reputation to ensure a pleasant experience. There are no specific order or dependencies for these visits, so you can plan your day as you like.
  - **V1** (`transfer_008_v1`): Please visit the bank and the shopping mall today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_008_v2`): Your itinerary today includes visiting the bank and the shopping mall. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_008_v3`): Hey, need you to stop by the bank and the shopping mall today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_009 (HIPP Source Index: 23)
- **Gold POIs**: `['library', 'supermarket']`
- **Time Limit**: `20:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_009_v0`): Today, you need to visit the library and the supermarket. Please make sure to return by 20:00. Focus on visiting places with high ratings, even if it means taking a slightly longer route. There are no particular places that you must visit in a specific order.
  - **V1** (`transfer_009_v1`): Please visit the library and the supermarket today. Ensure that you return home by 20:00. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_009_v2`): Your itinerary today includes visiting the library and the supermarket. All visits must be completed with return by 20:00. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_009_v3`): Hey, need you to stop by the library and the supermarket today. Make sure we are back by 20:00. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_010 (HIPP Source Index: 27)
- **Gold POIs**: `['shopping_mall', 'supermarket', 'library', 'pharmacy', 'bank']`
- **Time Limit**: `18:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_010_v0`): Today, we need to visit the shopping mall, supermarket, library, pharmacy, and bank. Please make sure to return by 18:00. Aim for visiting places that are known for good ratings on our list. No particular order is required for visiting these locations.
  - **V1** (`transfer_010_v1`): Please visit the shopping mall, the supermarket, the library, the pharmacy, and the bank today. Ensure that you return home by 18:00. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_010_v2`): Your itinerary today includes visiting the shopping mall, the supermarket, the library, the pharmacy, and the bank. All visits must be completed with return by 18:00. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_010_v3`): Hey, need you to stop by the shopping mall, the supermarket, the library, the pharmacy, and the bank today. Make sure we are back by 18:00. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_011 (HIPP Source Index: 28)
- **Gold POIs**: `['library']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `1.0` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_011_v0`): Today, make sure to visit the library. It's most important to ensure it's a top-rated place, so focus on the quality of the experience rather than the travel time. There are no specific places to visit in sequence, just enjoy your time there.
  - **V1** (`transfer_011_v1`): Please visit the library today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_011_v2`): Your itinerary today includes visiting the library. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_011_v3`): Hey, need you to stop by the library today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_012 (HIPP Source Index: 29)
- **Gold POIs**: `['shopping_mall']`
- **Time Limit**: `20:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_012_v0`): Today, you need to visit the shopping mall. Please ensure you're back by 20:00. Try to find a balance between visiting places with reasonable ratings and an efficient route. There are no specific visit order requirements for today.
  - **V1** (`transfer_012_v1`): Please visit the shopping mall today. Ensure that you return home by 20:00. Try to balance good quality with route efficiency.
  - **V2** (`transfer_012_v2`): Your itinerary today includes visiting the shopping mall. All visits must be completed with return by 20:00. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_012_v3`): Hey, need you to stop by the shopping mall today. Make sure we are back by 20:00. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_013 (HIPP Source Index: 31)
- **Gold POIs**: `['pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `1.0` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_013_v0`): 
Today, let's make sure to visit the pharmacy. It's important to prioritize visiting places with high ratings.
  - **V1** (`transfer_013_v1`): Please visit the pharmacy today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_013_v2`): Your itinerary today includes visiting the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_013_v3`): Hey, need you to stop by the pharmacy today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_014 (HIPP Source Index: 32)
- **Gold POIs**: `['pharmacy', 'library']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_014_v0`): Today, you'll need to visit both the pharmacy and the library. Make sure to prioritize going to places with high ratings even if it means taking a bit longer.
  - **V1** (`transfer_014_v1`): Please visit the pharmacy and the library today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_014_v2`): Your itinerary today includes visiting the pharmacy and the library. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_014_v3`): Hey, need you to stop by the pharmacy and the library today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_015 (HIPP Source Index: 33)
- **Gold POIs**: `['shopping_mall', 'bank', 'pharmacy']`
- **Time Limit**: `17:00`
- **Dependencies**: `[['bank', 'pharmacy']]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_015_v0`): Today, you need to visit the shopping mall, the bank, and the pharmacy. Make sure to return by 17:00. Aim to visit places that are highly rated for the best experience. Be sure to go to the bank before heading to the pharmacy.
  - **V1** (`transfer_015_v1`): Please visit the shopping mall, the bank, and the pharmacy today. Ensure that you return home by 17:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the pharmacy.
  - **V2** (`transfer_015_v2`): Your itinerary today includes visiting the shopping mall, the bank, and the pharmacy. Remember to stop at the bank before heading to the pharmacy. All visits must be completed with return by 17:00. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_015_v3`): Hey, need you to stop by the shopping mall, the bank, and the pharmacy today. Be sure to hit the bank first before the pharmacy. Make sure we are back by 17:00. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_016 (HIPP Source Index: 36)
- **Gold POIs**: `['bank']`
- **Time Limit**: `20:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.3` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_016_v0`): Today, you'll need to visit the bank and be back by 20:00. Let's aim for the most efficient route to get this done promptly.
  - **V1** (`transfer_016_v1`): Please visit the bank today. Ensure that you return home by 20:00. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_016_v2`): Your itinerary today includes visiting the bank. All visits must be completed with return by 20:00. Keep the travel distance minimal and direct.
  - **V3** (`transfer_016_v3`): Hey, need you to stop by the bank today. Make sure we are back by 20:00. Take the quickest and most efficient route possible.

### 组 transfer_017 (HIPP Source Index: 37)
- **Gold POIs**: `['pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.3` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_017_v0`): We need to visit the pharmacy today. Let's aim to make the trip as quick as possible since time is of the essence.
  - **V1** (`transfer_017_v1`): Please visit the pharmacy today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_017_v2`): Your itinerary today includes visiting the pharmacy. Keep the travel distance minimal and direct.
  - **V3** (`transfer_017_v3`): Hey, need you to stop by the pharmacy today. Take the quickest and most efficient route possible.

### 组 transfer_018 (HIPP Source Index: 43)
- **Gold POIs**: `['supermarket', 'library']`
- **Time Limit**: `21:00`
- **Dependencies**: `[['supermarket', 'library']]`
- **Quality Weight ($w$)**: `0.2` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_018_v0`): Please make sure to visit the supermarket and the library today. You need to be back by 21:00. Since we're pressed for time, let's prioritize a quick and efficient route. Make sure to stop at the supermarket before heading to the library.
  - **V1** (`transfer_018_v1`): Please visit the supermarket and the library today. Ensure that you return home by 21:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the supermarket prior to the library.
  - **V2** (`transfer_018_v2`): Your itinerary today includes visiting the supermarket and the library. Remember to stop at the supermarket before heading to the library. All visits must be completed with return by 21:00. Keep the travel distance minimal and direct.
  - **V3** (`transfer_018_v3`): Hey, need you to stop by the supermarket and the library today. Be sure to hit the supermarket first before the library. Make sure we are back by 21:00. Take the quickest and most efficient route possible.

### 组 transfer_019 (HIPP Source Index: 45)
- **Gold POIs**: `['library', 'supermarket', 'pharmacy', 'shopping_mall', 'bank']`
- **Time Limit**: `None`
- **Dependencies**: `[['supermarket', 'pharmacy']]`
- **Quality Weight ($w$)**: `1.0` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_019_v0`): Today, you'll need to visit the library, supermarket, pharmacy, shopping mall, and bank. Make sure to prioritize places with excellent ratings. You'll need to visit the supermarket before heading to the pharmacy.
  - **V1** (`transfer_019_v1`): Please visit the library, the supermarket, the pharmacy, the shopping mall, and the bank today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the supermarket prior to the pharmacy.
  - **V2** (`transfer_019_v2`): Your itinerary today includes visiting the library, the supermarket, the pharmacy, the shopping mall, and the bank. Remember to stop at the supermarket before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_019_v3`): Hey, need you to stop by the library, the supermarket, the pharmacy, the shopping mall, and the bank today. Be sure to hit the supermarket first before the pharmacy. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_020 (HIPP Source Index: 47)
- **Gold POIs**: `['shopping_mall', 'library', 'bank', 'pharmacy', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[['library', 'bank'], ['bank', 'pharmacy']]`
- **Quality Weight ($w$)**: `0.8` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_020_v0`): Today, you need to visit the shopping mall, library, bank, pharmacy, and supermarket. It's important to prioritize places with high ratings along the journey. Make sure you go to the library before heading to the bank, and visit the bank before the pharmacy.
  - **V1** (`transfer_020_v1`): Please visit the shopping mall, the library, the bank, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the bank. Make sure to visit the bank prior to the pharmacy.
  - **V2** (`transfer_020_v2`): Your itinerary today includes visiting the shopping mall, the library, the bank, the pharmacy, and the supermarket. Remember to stop at the library before heading to the bank. Remember to stop at the bank before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_020_v3`): Hey, need you to stop by the shopping mall, the library, the bank, the pharmacy, and the supermarket today. Be sure to hit the library first before the bank. Be sure to hit the bank first before the pharmacy. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_021 (HIPP Source Index: 51)
- **Gold POIs**: `['shopping_mall', 'pharmacy']`
- **Time Limit**: `23:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_021_v0`): Today, we need to visit the shopping mall and the pharmacy. Make sure you're back by 23:00. Let's aim for a balance between visiting worthwhile places and maintaining a reasonably efficient route.
  - **V1** (`transfer_021_v1`): Please visit the shopping mall and the pharmacy today. Ensure that you return home by 23:00. Try to balance good quality with route efficiency.
  - **V2** (`transfer_021_v2`): Your itinerary today includes visiting the shopping mall and the pharmacy. All visits must be completed with return by 23:00. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_021_v3`): Hey, need you to stop by the shopping mall and the pharmacy today. Make sure we are back by 23:00. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_022 (HIPP Source Index: 54)
- **Gold POIs**: `['shopping_mall', 'library', 'pharmacy', 'supermarket', 'bank']`
- **Time Limit**: `None`
- **Dependencies**: `[['pharmacy', 'supermarket']]`
- **Quality Weight ($w$)**: `0.3` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_022_v0`): Today, make sure to stop by the shopping mall, library, pharmacy, supermarket, and bank. Since time is of the essence, focus on finding the most efficient route between these places. Visit the pharmacy before heading to the supermarket.
  - **V1** (`transfer_022_v1`): Please visit the shopping mall, the library, the pharmacy, the supermarket, and the bank today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the pharmacy prior to the supermarket.
  - **V2** (`transfer_022_v2`): Your itinerary today includes visiting the shopping mall, the library, the pharmacy, the supermarket, and the bank. Remember to stop at the pharmacy before heading to the supermarket. Keep the travel distance minimal and direct.
  - **V3** (`transfer_022_v3`): Hey, need you to stop by the shopping mall, the library, the pharmacy, the supermarket, and the bank today. Be sure to hit the pharmacy first before the supermarket. Take the quickest and most efficient route possible.

### 组 transfer_023 (HIPP Source Index: 56)
- **Gold POIs**: `['shopping_mall', 'supermarket', 'bank', 'library', 'pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.2` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_023_v0`): Today, the plan is to visit the shopping mall, supermarket, bank, library, and pharmacy. Make sure to focus on completing this efficiently as there is no particular time to return. Prioritize the shortest route possible to save time.
  - **V1** (`transfer_023_v1`): Please visit the shopping mall, the supermarket, the bank, the library, and the pharmacy today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_023_v2`): Your itinerary today includes visiting the shopping mall, the supermarket, the bank, the library, and the pharmacy. Keep the travel distance minimal and direct.
  - **V3** (`transfer_023_v3`): Hey, need you to stop by the shopping mall, the supermarket, the bank, the library, and the pharmacy today. Take the quickest and most efficient route possible.

### 组 transfer_024 (HIPP Source Index: 57)
- **Gold POIs**: `['pharmacy', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_024_v0`): Today, make sure to visit the pharmacy and the shopping mall. It's important to focus on visiting places with high ratings.
  - **V1** (`transfer_024_v1`): Please visit the pharmacy and the shopping mall today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_024_v2`): Your itinerary today includes visiting the pharmacy and the shopping mall. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_024_v3`): Hey, need you to stop by the pharmacy and the shopping mall today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_025 (HIPP Source Index: 59)
- **Gold POIs**: `['pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.2` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_025_v0`): Please make sure to visit the pharmacy today. Try to make the trip as quick and efficient as possible.
  - **V1** (`transfer_025_v1`): Please visit the pharmacy today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_025_v2`): Your itinerary today includes visiting the pharmacy. Keep the travel distance minimal and direct.
  - **V3** (`transfer_025_v3`): Hey, need you to stop by the pharmacy today. Take the quickest and most efficient route possible.

### 组 transfer_026 (HIPP Source Index: 60)
- **Gold POIs**: `['bank', 'library', 'supermarket', 'shopping_mall']`
- **Time Limit**: `19:00`
- **Dependencies**: `[['bank', 'library'], ['library', 'supermarket']]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_026_v0`): Today, make sure to visit the bank, library, supermarket, and shopping mall. Please be home by 19:00. Prioritize visiting places with high ratings as they are more important today. Start at the bank before heading to the library, and continue to the supermarket right after the library.
  - **V1** (`transfer_026_v1`): Please visit the bank, the library, the supermarket, and the shopping mall today. Ensure that you return home by 19:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library. Make sure to visit the library prior to the supermarket.
  - **V2** (`transfer_026_v2`): Your itinerary today includes visiting the bank, the library, the supermarket, and the shopping mall. Remember to stop at the bank before heading to the library. Remember to stop at the library before heading to the supermarket. All visits must be completed with return by 19:00. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_026_v3`): Hey, need you to stop by the bank, the library, the supermarket, and the shopping mall today. Be sure to hit the bank first before the library. Be sure to hit the library first before the supermarket. Make sure we are back by 19:00. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_027 (HIPP Source Index: 61)
- **Gold POIs**: `['bank']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_027_v0`): 
Please make sure to visit the bank today. I'd like you to find a balance between visiting a well-rated place and not taking too long on your route.
  - **V1** (`transfer_027_v1`): Please visit the bank today. Try to balance good quality with route efficiency.
  - **V2** (`transfer_027_v2`): Your itinerary today includes visiting the bank. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_027_v3`): Hey, need you to stop by the bank today. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_028 (HIPP Source Index: 67)
- **Gold POIs**: `['bank', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_028_v0`): Today, we need to visit the bank and the supermarket. Make sure to prioritize going to the bank and supermarket with the highest ratings available.
  - **V1** (`transfer_028_v1`): Please visit the bank and the supermarket today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_028_v2`): Your itinerary today includes visiting the bank and the supermarket. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_028_v3`): Hey, need you to stop by the bank and the supermarket today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_029 (HIPP Source Index: 68)
- **Gold POIs**: `['library', 'pharmacy', 'supermarket', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_029_v0`): Today, we need to visit the library, pharmacy, supermarket, and shopping mall. We should try to find a balance between visiting places with good ratings and maintaining an efficient route.
  - **V1** (`transfer_029_v1`): Please visit the library, the pharmacy, the supermarket, and the shopping mall today. Try to balance good quality with route efficiency.
  - **V2** (`transfer_029_v2`): Your itinerary today includes visiting the library, the pharmacy, the supermarket, and the shopping mall. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_029_v3`): Hey, need you to stop by the library, the pharmacy, the supermarket, and the shopping mall today. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_030 (HIPP Source Index: 69)
- **Gold POIs**: `['supermarket', 'bank', 'shopping_mall', 'pharmacy', 'library']`
- **Time Limit**: `23:00`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.1` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_030_v0`): Today, we need to visit the supermarket, bank, shopping mall, pharmacy, and library. Please ensure that you return by 23:00. Given the preference for a shorter route, let's aim to be as efficient as possible with our travel between these locations.
  - **V1** (`transfer_030_v1`): Please visit the supermarket, the bank, the shopping mall, the pharmacy, and the library today. Ensure that you return home by 23:00. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_030_v2`): Your itinerary today includes visiting the supermarket, the bank, the shopping mall, the pharmacy, and the library. All visits must be completed with return by 23:00. Keep the travel distance minimal and direct.
  - **V3** (`transfer_030_v3`): Hey, need you to stop by the supermarket, the bank, the shopping mall, the pharmacy, and the library today. Make sure we are back by 23:00. Take the quickest and most efficient route possible.

### 组 transfer_031 (HIPP Source Index: 74)
- **Gold POIs**: `['library', 'supermarket']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.2` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_031_v0`): Today, we need to go to the library and the supermarket. Please ensure that the trip is efficient and quick.
  - **V1** (`transfer_031_v1`): Please visit the library and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_031_v2`): Your itinerary today includes visiting the library and the supermarket. Keep the travel distance minimal and direct.
  - **V3** (`transfer_031_v3`): Hey, need you to stop by the library and the supermarket today. Take the quickest and most efficient route possible.

### 组 transfer_032 (HIPP Source Index: 75)
- **Gold POIs**: `['library', 'shopping_mall']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.8` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_032_v0`): Today, you need to visit the library and the shopping mall. Make sure to prioritize visiting high-rated places during your trip.
  - **V1** (`transfer_032_v1`): Please visit the library and the shopping mall today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_032_v2`): Your itinerary today includes visiting the library and the shopping mall. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_032_v3`): Hey, need you to stop by the library and the shopping mall today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_033 (HIPP Source Index: 79)
- **Gold POIs**: `['bank']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.6` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_033_v0`): Today we need to visit the bank. I'd like to make sure we choose a route that balances a reasonable place to focus on good ratings and reasonable travel efficiency.
  - **V1** (`transfer_033_v1`): Please visit the bank today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_033_v2`): Your itinerary today includes visiting the bank. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_033_v3`): Hey, need you to stop by the bank today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_034 (HIPP Source Index: 83)
- **Gold POIs**: `['pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_034_v0`): Today, we need to visit the pharmacy. There's no specific time by which we have to return. It's important that we choose a pharmacy with a good rating over the shortest route.
  - **V1** (`transfer_034_v1`): Please visit the pharmacy today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_034_v2`): Your itinerary today includes visiting the pharmacy. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_034_v3`): Hey, need you to stop by the pharmacy today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_035 (HIPP Source Index: 85)
- **Gold POIs**: `['pharmacy', 'shopping_mall', 'library', 'bank']`
- **Time Limit**: `17:00`
- **Dependencies**: `[['library', 'bank']]`
- **Quality Weight ($w$)**: `0.3` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_035_v0`): Today, make sure to visit the pharmacy, shopping mall, library, and bank. Please return home by 17:00. It's important to be efficient and quick with this route. Don't forget to stop by the library before heading to the bank.
  - **V1** (`transfer_035_v1`): Please visit the pharmacy, the shopping mall, the library, and the bank today. Ensure that you return home by 17:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the library prior to the bank.
  - **V2** (`transfer_035_v2`): Your itinerary today includes visiting the pharmacy, the shopping mall, the library, and the bank. Remember to stop at the library before heading to the bank. All visits must be completed with return by 17:00. Keep the travel distance minimal and direct.
  - **V3** (`transfer_035_v3`): Hey, need you to stop by the pharmacy, the shopping mall, the library, and the bank today. Be sure to hit the library first before the bank. Make sure we are back by 17:00. Take the quickest and most efficient route possible.

### 组 transfer_036 (HIPP Source Index: 87)
- **Gold POIs**: `['library']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.7` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_036_v0`): Please make sure to visit the library today. I would appreciate it if you prioritize destinations with higher ratings, so take your time to enjoy the visit. There are no specific sequences required for your visit today.
  - **V1** (`transfer_036_v1`): Please visit the library today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_036_v2`): Your itinerary today includes visiting the library. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_036_v3`): Hey, need you to stop by the library today. Aim for the highest-rated places since quality is the main goal.

### 组 transfer_037 (HIPP Source Index: 88)
- **Gold POIs**: `['library', 'bank', 'pharmacy']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.1` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_037_v0`): Today, visit the library, bank, and pharmacy. Since there's no set time to return, aim to make the trip quick and efficient.
  - **V1** (`transfer_037_v1`): Please visit the library, the bank, and the pharmacy today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_037_v2`): Your itinerary today includes visiting the library, the bank, and the pharmacy. Keep the travel distance minimal and direct.
  - **V3** (`transfer_037_v3`): Hey, need you to stop by the library, the bank, and the pharmacy today. Take the quickest and most efficient route possible.

### 组 transfer_038 (HIPP Source Index: 89)
- **Gold POIs**: `['bank']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.4` (distance_first)
- **4 变体文本**:
  - **V0** (`transfer_038_v0`): Today, you need to visit the bank. It's important to make this trip efficient and quick.
  - **V1** (`transfer_038_v1`): Please visit the bank today. Focus on route efficiency and minimizing unnecessary travel time.
  - **V2** (`transfer_038_v2`): Your itinerary today includes visiting the bank. Keep the travel distance minimal and direct.
  - **V3** (`transfer_038_v3`): Hey, need you to stop by the bank today. Take the quickest and most efficient route possible.

### 组 transfer_039 (HIPP Source Index: 90)
- **Gold POIs**: `['library', 'pharmacy']`
- **Time Limit**: `22:00`
- **Dependencies**: `[['library', 'pharmacy']]`
- **Quality Weight ($w$)**: `0.5` (balanced)
- **4 变体文本**:
  - **V0** (`transfer_039_v0`): Today, visit the library and the pharmacy. Make sure to return by 22:00. Aim for a route that strikes a balance between visiting good places and keeping the trip short. Be sure to stop by the library before heading to the pharmacy.
  - **V1** (`transfer_039_v1`): Please visit the library and the pharmacy today. Ensure that you return home by 22:00. Try to balance good quality with route efficiency. Make sure to visit the library prior to the pharmacy.
  - **V2** (`transfer_039_v2`): Your itinerary today includes visiting the library and the pharmacy. Remember to stop at the library before heading to the pharmacy. All visits must be completed with return by 22:00. Maintain a fair balance between venue ratings and overall travel time.
  - **V3** (`transfer_039_v3`): Hey, need you to stop by the library and the pharmacy today. Be sure to hit the library first before the pharmacy. Make sure we are back by 22:00. Balance quality and distance so we visit decent spots without taking too long.

### 组 transfer_040 (HIPP Source Index: 91)
- **Gold POIs**: `['bank']`
- **Time Limit**: `None`
- **Dependencies**: `[]`
- **Quality Weight ($w$)**: `0.9` (quality_first)
- **4 变体文本**:
  - **V0** (`transfer_040_v0`): Today, make sure to visit the bank. It's really important to choose a bank with a high rating, even if it means a longer route.
  - **V1** (`transfer_040_v1`): Please visit the bank today. Prioritize locations with high ratings and strong customer reviews.
  - **V2** (`transfer_040_v2`): Your itinerary today includes visiting the bank. Give top priority to reputable, well-reviewed venues.
  - **V3** (`transfer_040_v3`): Hey, need you to stop by the bank today. Aim for the highest-rated places since quality is the main goal.
