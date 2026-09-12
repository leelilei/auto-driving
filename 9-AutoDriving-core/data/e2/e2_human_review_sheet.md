# DARC-Route v4.1 E2 独立确认数据集人审确认表

- **确认组数**: 40 组未暴露语义簇 × 4 变体 = 160 句
- **对照组数**: 10 组语义改变对照组 × 2 句 = 20 句
- **审核标准**: S (POI 集合绝对一致), T (时间约束精确一致), D (前后依赖闭包一致), 偏好方向一致
- **审核人**: `LEELI_LEI_RESEARCH_TEAM`
- **审核状态**: `CONFIRMED_HUMAN_AUDITED`
- **审核日期**: `2026-09-12`

---

## 1. 40 组未暴露等义确认样本 (40 Equivalence Groups)

### Group `e2_confirm_001` (Cluster 40)
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1080, Deps=[['pharmacy', 'library'], ['supermarket', 'shopping_mall']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, you need to visit the supermarket, the shopping mall, the pharmacy, and the library. Please ensure you return by 18:00. Prioritize visiting places with higher ratings as much as possible. Make sure to visit the supermarket before heading to the shopping mall and stop by the pharmacy before going to the library.
- **V1 (Synonym)**: Please visit the library, the pharmacy, the shopping mall, and the supermarket today, returning by 18:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the library, and visit the supermarket prior to the shopping mall.
- **V2 (Syntactic)**: Please ensure you are back by 18:00 after visiting the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the pharmacy before heading to the library, and stop at the supermarket before heading to the shopping mall. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today and be back before 6 PM. Be sure to hit the pharmacy first before the library, and hit the supermarket first before the shopping mall. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_002` (Cluster 497)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'pharmacy'], ['shopping_mall', 'library']], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, let's visit the shopping mall, library, bank, and pharmacy. It's important to have a balance between visiting well-rated places and having an efficient route. Start with the shopping mall and then head to the library, and ensure to stop by the bank before going to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the shopping mall today. Maintain a balance between visiting well-rated places and keeping the route efficient. Make sure to visit the bank prior to the pharmacy, and visit the shopping mall prior to the library.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, and the shopping mall. Remember to stop at the bank before heading to the pharmacy, and stop at the shopping mall before heading to the library. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the shopping mall today. Be sure to hit the bank first before the pharmacy, and hit the shopping mall first before the library. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_003` (Cluster 310)
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'bank']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, the places we need to visit include a shopping mall, a supermarket, a pharmacy, and a bank. While we don’t have a set return time, it’s important to focus on visiting places with higher ratings to enhance our experience. Please make sure to stop by the pharmacy before heading to the bank.
- **V1 (Synonym)**: Please visit the bank, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the bank.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the pharmacy before heading to the bank. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the pharmacy first before the bank. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_004` (Cluster 147)
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy'], ['supermarket', 'bank']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Make sure to visit the shopping mall, pharmacy, supermarket, and bank today. Prioritize visiting places with high ratings for a more enjoyable experience. Be sure to stop by the shopping mall before heading to the pharmacy. Also, remember to visit the supermarket before the bank.
- **V1 (Synonym)**: Please visit the bank, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the pharmacy, and visit the supermarket prior to the bank.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the pharmacy, and stop at the supermarket before heading to the bank. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the pharmacy, and hit the supermarket first before the bank. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_005` (Cluster 88)
- **Gold Intent**: POIs=['pharmacy', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'supermarket']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, we need to visit both the pharmacy and the supermarket. It's important that we go to the pharmacy before heading to the supermarket. Make sure we focus on finding the places with the best reviews, even if it means taking a bit more time.
- **V1 (Synonym)**: Please visit the pharmacy and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting both the pharmacy and the supermarket. Remember to stop at the pharmacy before heading to the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the pharmacy as well as the supermarket today. Be sure to hit the pharmacy first before the supermarket. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_006` (Cluster 22)
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1200, Deps=[], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, you need to visit the library and the supermarket. Please make sure to return by 20:00. Focus on visiting places with high ratings, even if it means taking a slightly longer route. There are no particular places that you must visit in a specific order.
- **V1 (Synonym)**: Please visit the library and the supermarket today, returning by 20:00. Prioritize locations with high ratings and strong customer reviews.
- **V2 (Syntactic)**: Please ensure you are back by 20:00 after visiting both the library and the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the library as well as the supermarket today and be back before 8 PM. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_007` (Cluster 446)
- **Gold Intent**: POIs=['pharmacy'], TimeLimit=1140, Deps=[], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Please make sure to visit the pharmacy today. Be sure to return by 19:00. It's important to consider both the quality of the destination and an efficient route when planning your trip.
- **V1 (Synonym)**: Please visit the pharmacy today, returning by 19:00. Maintain a balance between visiting well-rated places and keeping the route efficient.
- **V2 (Syntactic)**: Please ensure you are back by 19:00 after visiting the pharmacy. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the pharmacy today and be back before 7 PM. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_008` (Cluster 511)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1200, Deps=[['bank', 'library']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the shopping mall, pharmacy, bank, library, and supermarket. Please return by 20:00. It's important to focus on visiting places with the highest ratings. Remember to stop by the bank before heading to the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 20:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library.
- **V2 (Syntactic)**: Please ensure you are back by 20:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the library. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 8 PM. Be sure to hit the bank first before the library. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_009` (Cluster 418)
- **Gold Intent**: POIs=['bank', 'library'], TimeLimit=None, Deps=[['library', 'bank']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Please visit the library and the bank today. It's important to check out the spots that have higher ratings for a better experience. Make sure to go to the library before heading to the bank.
- **V1 (Synonym)**: Please visit the bank and the library today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the bank.
- **V2 (Syntactic)**: Your itinerary today includes visiting both the bank and the library. Remember to stop at the library before heading to the bank. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank as well as the library today. Be sure to hit the library first before the bank. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_010` (Cluster 494)
- **Gold Intent**: POIs=['library', 'pharmacy', 'supermarket'], TimeLimit=1320, Deps=[], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, you need to visit the library, supermarket, and pharmacy. Please ensure you're back by 10 PM. Try your best to balance between choosing places with decent ratings and keeping your route efficient.
- **V1 (Synonym)**: Please visit the library, the pharmacy, and the supermarket today, returning by 22:00. Prioritize locations with high ratings and strong customer reviews.
- **V2 (Syntactic)**: Please ensure you are back by 22:00 after visiting the library, the pharmacy, and the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the library, the pharmacy, and the supermarket today and be back before 10 PM. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_011` (Cluster 433)
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the supermarket, bank, and pharmacy. Focus on spending time at the places with the best ratings. There are no specific order requirements for your visits.
- **V1 (Synonym)**: Please visit the bank, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the pharmacy, and the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the pharmacy, and the supermarket today. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_012` (Cluster 606)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1080, Deps=[['bank', 'library'], ['bank', 'pharmacy'], ['library', 'pharmacy']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, you need to visit the bank, library, pharmacy, shopping mall, and supermarket. Please ensure you return by 18:00. Given our schedule, we should aim to be as efficient as possible in planning your route. Start by visiting the bank, then head to the library, and make sure you visit the pharmacy after the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 18:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the library; visit the bank prior to the pharmacy; visit the library prior to the pharmacy.
- **V2 (Syntactic)**: Please ensure you are back by 18:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the library; stop at the bank before heading to the pharmacy; stop at the library before heading to the pharmacy. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 6 PM. Be sure to hit the bank first before the library; hit the bank first before the pharmacy; hit the library first before the pharmacy. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_013` (Cluster 346)
- **Gold Intent**: POIs=['bank', 'supermarket'], TimeLimit=None, Deps=[['bank', 'supermarket']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the bank and the supermarket. Be sure to prioritize places with high ratings. Begin your journey at the bank before heading to the supermarket.
- **V1 (Synonym)**: Please visit the bank and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting both the bank and the supermarket. Remember to stop at the bank before heading to the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank as well as the supermarket today. Be sure to hit the bank first before the supermarket. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_014` (Cluster 56)
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the bank, library, supermarket, and shopping mall. Please be home by 19:00. Prioritize visiting places with high ratings as they are more important today. Start at the bank before heading to the library, and continue to the supermarket right after the library.
- **V1 (Synonym)**: Please visit the bank, the library, the shopping mall, and the supermarket today, returning by 19:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library; visit the bank prior to the supermarket; visit the library prior to the supermarket.
- **V2 (Syntactic)**: Please ensure you are back by 19:00 after visiting the bank, the library, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the library; stop at the bank before heading to the supermarket; stop at the library before heading to the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the shopping mall, and the supermarket today and be back before 7 PM. Be sure to hit the bank first before the library; hit the bank first before the supermarket; hit the library first before the supermarket. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_015` (Cluster 140)
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'shopping_mall']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, we need to visit the library, bank, supermarket, and shopping mall. Make sure to prioritize visiting places with high ratings. Additionally, ensure that the supermarket is visited before the shopping mall.
- **V1 (Synonym)**: Please visit the bank, the library, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the supermarket prior to the shopping mall.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the shopping mall, and the supermarket. Remember to stop at the supermarket before heading to the shopping mall. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the shopping mall, and the supermarket today. Be sure to hit the supermarket first before the shopping mall. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_016` (Cluster 505)
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, we need to visit the supermarket, shopping mall, and library. Let's make sure we balance our time efficiently while still choosing places with decent ratings.
- **V1 (Synonym)**: Please visit the library, the shopping mall, and the supermarket today. Maintain a balance between visiting well-rated places and keeping the route efficient.
- **V2 (Syntactic)**: Your itinerary today includes visiting the library, the shopping mall, and the supermarket. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the library, the shopping mall, and the supermarket today. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_017` (Cluster 53)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'supermarket']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, make sure to stop by the shopping mall, library, pharmacy, supermarket, and bank. Since time is of the essence, focus on finding the most efficient route between these places. Visit the pharmacy before heading to the supermarket.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the pharmacy prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the pharmacy before heading to the supermarket. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the pharmacy first before the supermarket. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_018` (Cluster 355)
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today's itinerary includes visiting the bank, supermarket, shopping mall, and pharmacy. Please make sure to return by 21:00. As time efficiency is important, try to optimize the route for the shortest travel distance.
- **V1 (Synonym)**: Please visit the bank, the pharmacy, the shopping mall, and the supermarket today, returning by 21:00. Focus on route efficiency and minimizing unnecessary travel time.
- **V2 (Syntactic)**: Please ensure you are back by 21:00 after visiting the bank, the pharmacy, the shopping mall, and the supermarket. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the pharmacy, the shopping mall, and the supermarket today and be back before 9 PM. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_019` (Cluster 322)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'supermarket'], ['shopping_mall', 'pharmacy']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, we need to visit the shopping mall, pharmacy, library, bank, and supermarket. Let's make sure to keep the trip efficient by prioritizing a shorter route overall. We'll start at the shopping mall before heading to the pharmacy, and then ensure we visit the bank before moving on to the supermarket.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the supermarket, and visit the shopping mall prior to the pharmacy.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the supermarket, and stop at the shopping mall before heading to the pharmacy. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the bank first before the supermarket, and hit the shopping mall first before the pharmacy. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_020` (Cluster 404)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1020, Deps=[['bank', 'pharmacy'], ['shopping_mall', 'bank'], ['shopping_mall', 'pharmacy']], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, you need to visit the shopping mall, bank, pharmacy, supermarket, and library. Please make sure to return by 17:00. Aim to balance both the quality of places you visit and the efficiency of your route. Be sure to visit the shopping mall before going to the bank, and ensure you stop at the bank prior to heading to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 17:00. Maintain a balance between visiting well-rated places and keeping the route efficient. Make sure to visit the bank prior to the pharmacy; visit the shopping mall prior to the bank; visit the shopping mall prior to the pharmacy.
- **V2 (Syntactic)**: Please ensure you are back by 17:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the pharmacy; stop at the shopping mall before heading to the bank; stop at the shopping mall before heading to the pharmacy. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 5 PM. Be sure to hit the bank first before the pharmacy; hit the shopping mall first before the bank; hit the shopping mall first before the pharmacy. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_021` (Cluster 503)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'supermarket']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the pharmacy, library, bank, supermarket, and shopping mall. It's important to prioritize places with good ratings, but don't worry too much about the total travel time. Be sure to stop by the bank before you head to the supermarket.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the bank first before the supermarket. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_022` (Cluster 406)
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, we need to visit the supermarket, shopping mall, and library. Since there is no specific return time, let's aim to be as efficient as possible in our visits. Please make sure to go to the supermarket before heading to the shopping mall, and then proceed to the library last.
- **V1 (Synonym)**: Please visit the library, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the shopping mall prior to the library; visit the supermarket prior to the library; visit the supermarket prior to the shopping mall.
- **V2 (Syntactic)**: Your itinerary today includes visiting the library, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the library; stop at the supermarket before heading to the library; stop at the supermarket before heading to the shopping mall. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the library, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the library; hit the supermarket first before the library; hit the supermarket first before the shopping mall. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_023` (Cluster 37)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1020, Deps=[['shopping_mall', 'library']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the supermarket, bank, shopping mall, library, and pharmacy. You need to be back by 5 PM. Prioritize visiting places with higher ratings for a more satisfying trip. Remember, you must visit the shopping mall before heading to the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 17:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the library.
- **V2 (Syntactic)**: Please ensure you are back by 17:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the library. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 5 PM. Be sure to hit the shopping mall first before the library. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_024` (Cluster 478)
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['shopping_mall', 'bank'], ['shopping_mall', 'library']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, we'll be visiting the shopping mall, bank, and library. We should aim for a journey that balances both place ratings and efficiency in our route. First, we'll head to the shopping mall before we stop by the bank, and make sure we visit the bank before heading to the library.
- **V1 (Synonym)**: Please visit the bank, the library, and the shopping mall today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library; visit the shopping mall prior to the bank; visit the shopping mall prior to the library.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, and the shopping mall. Remember to stop at the bank before heading to the library; stop at the shopping mall before heading to the bank; stop at the shopping mall before heading to the library. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, and the shopping mall today. Be sure to hit the bank first before the library; hit the shopping mall first before the bank; hit the shopping mall first before the library. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_025` (Cluster 430)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1080, Deps=[['bank', 'pharmacy']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, you'll need to visit the supermarket, library, bank, pharmacy, and shopping mall. Please make sure to return by 18:00. Time is of the essence, so a swift and efficient route is essential. Be sure to stop by the bank before heading to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 18:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the pharmacy.
- **V2 (Syntactic)**: Please ensure you are back by 18:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the pharmacy. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 6 PM. Be sure to hit the bank first before the pharmacy. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_026` (Cluster 42)
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1260, Deps=[['supermarket', 'library']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Please make sure to visit the supermarket and the library today. You need to be back by 21:00. Since we're pressed for time, let's prioritize a quick and efficient route. Make sure to stop at the supermarket before heading to the library.
- **V1 (Synonym)**: Please visit the library and the supermarket today, returning by 21:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the supermarket prior to the library.
- **V2 (Syntactic)**: Please ensure you are back by 21:00 after visiting both the library and the supermarket. Remember to stop at the supermarket before heading to the library. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the library as well as the supermarket today and be back before 9 PM. Be sure to hit the supermarket first before the library. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_027` (Cluster 241)
- **Gold Intent**: POIs=['shopping_mall'], TimeLimit=1320, Deps=[], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, make sure to visit the shopping mall. You should be back by 22:00. A balance between finding a decent place and making the trip efficiently is key. There are no specific orders to worry about, just enjoy your visit!
- **V1 (Synonym)**: Please visit the shopping mall today, returning by 22:00. Maintain a balance between visiting well-rated places and keeping the route efficient.
- **V2 (Syntactic)**: Please ensure you are back by 22:00 after visiting the shopping mall. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the shopping mall today and be back before 10 PM. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_028` (Cluster 589)
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'supermarket']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, we need to visit the shopping mall, supermarket, and pharmacy. Please prioritize a quick and efficient route for the trip. Make sure to stop by the shopping mall before heading to the supermarket.
- **V1 (Synonym)**: Please visit the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the shopping mall prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the supermarket. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the supermarket. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_029` (Cluster 501)
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Please visit the library, shopping mall, pharmacy, and supermarket today. Make sure to return by 23:00. It would be wonderful if you could prioritize visiting places with high ratings.
- **V1 (Synonym)**: Please visit the library, the pharmacy, the shopping mall, and the supermarket today, returning by 23:00. Prioritize locations with high ratings and strong customer reviews.
- **V2 (Syntactic)**: Please ensure you are back by 23:00 after visiting the library, the pharmacy, the shopping mall, and the supermarket. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today and be back before 11 PM. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_030` (Cluster 391)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1080, Deps=[['bank', 'supermarket'], ['library', 'pharmacy']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today's stops include the bank, supermarket, shopping mall, library, and pharmacy. We need to be back by 6 PM. Let's aim for both a reasonable route and decent ratings as we plan our visit. Make sure to stop by the bank before heading to the supermarket and visit the library prior to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 18:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the supermarket, and visit the library prior to the pharmacy.
- **V2 (Syntactic)**: Please ensure you are back by 18:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the supermarket, and stop at the library before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 6 PM. Be sure to hit the bank first before the supermarket, and hit the library first before the pharmacy. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_031` (Cluster 361)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['library', 'bank']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, you need to visit the library, bank, supermarket, and pharmacy. While balancing time and quality, aim to make both efficient choices and choose spots that offer reasonably good experiences. Make sure to stop by the library before heading to the bank.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the bank.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the library before heading to the bank. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today. Be sure to hit the library first before the bank. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_032` (Cluster 566)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1260, Deps=[['bank', 'pharmacy']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, make sure to visit the library, supermarket, bank, and pharmacy. Please be back by 21:00. Try to maintain a balance between visiting well-rated places and keeping the route efficient. Remember to go to the bank before heading to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the supermarket today, returning by 21:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the pharmacy.
- **V2 (Syntactic)**: Please ensure you are back by 21:00 after visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the bank before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today and be back before 9 PM. Be sure to hit the bank first before the pharmacy. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_033` (Cluster 30)
- **Gold Intent**: POIs=['pharmacy'], TimeLimit=None, Deps=[], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: 
Today, let's make sure to visit the pharmacy. It's important to prioritize visiting places with high ratings.
- **V1 (Synonym)**: Please visit the pharmacy today. Prioritize locations with high ratings and strong customer reviews.
- **V2 (Syntactic)**: Your itinerary today includes visiting the pharmacy. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the pharmacy today. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_034` (Cluster 325)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, you need to visit the pharmacy, bank, shopping mall, and library. Efficiency is key, so prioritize the shortest route. Start by stopping at the pharmacy, then head to the bank. After that, make your way to the shopping mall, and finish your errands at the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the shopping mall today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the library; visit the bank prior to the shopping mall; visit the pharmacy prior to the bank; visit the pharmacy prior to the library; visit the pharmacy prior to the shopping mall; visit the shopping mall prior to the library.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, and the shopping mall. Remember to stop at the bank before heading to the library; stop at the bank before heading to the shopping mall; stop at the pharmacy before heading to the bank; stop at the pharmacy before heading to the library; stop at the pharmacy before heading to the shopping mall; stop at the shopping mall before heading to the library. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the shopping mall today. Be sure to hit the bank first before the library; hit the bank first before the shopping mall; hit the pharmacy first before the bank; hit the pharmacy first before the library; hit the pharmacy first before the shopping mall; hit the shopping mall first before the library. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_035` (Cluster 369)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'library']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, we need to visit the shopping mall, supermarket, pharmacy, library, and bank. It's important to focus on visiting places with higher ratings. Remember, we must stop by the pharmacy before heading to the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the library.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the pharmacy before heading to the library. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the pharmacy first before the library. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_036` (Cluster 80)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=1020, Deps=[['library', 'bank']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, make sure to visit the pharmacy, shopping mall, library, and bank. Please return home by 17:00. It's important to be efficient and quick with this route. Don't forget to stop by the library before heading to the bank.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the shopping mall today, returning by 17:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the library prior to the bank.
- **V2 (Syntactic)**: Please ensure you are back by 17:00 after visiting the bank, the library, the pharmacy, and the shopping mall. Remember to stop at the library before heading to the bank. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the shopping mall today and be back before 5 PM. Be sure to hit the library first before the bank. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_037` (Cluster 345)
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, we need to visit the shopping mall, supermarket, and library. Please ensure we return by 21:00. I’d appreciate a balance between visiting highly-rated places and keeping the route efficient. There are no specific orders in which these places must be visited.
- **V1 (Synonym)**: Please visit the library, the shopping mall, and the supermarket today, returning by 21:00. Maintain a balance between visiting well-rated places and keeping the route efficient.
- **V2 (Syntactic)**: Please ensure you are back by 21:00 after visiting the library, the shopping mall, and the supermarket. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the library, the shopping mall, and the supermarket today and be back before 9 PM. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_038` (Cluster 318)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'pharmacy'], ['pharmacy', 'library'], ['supermarket', 'bank'], ['supermarket', 'library'], ['supermarket', 'pharmacy']], Direction=`balanced` (w=0.5)
- **V0 (Base)**: Today, you'll need to visit the supermarket, bank, pharmacy, and library. Please try to balance both the quality of the places and your travel efficiency. Make sure to first go to the supermarket before heading to the bank, visit the bank prior to the pharmacy, and stop by the pharmacy before ending at the library.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, and the supermarket today. Maintain a balance between visiting well-rated places and keeping the route efficient. Make sure to visit the bank prior to the library; visit the bank prior to the pharmacy; visit the pharmacy prior to the library; visit the supermarket prior to the bank; visit the supermarket prior to the library; visit the supermarket prior to the pharmacy.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the bank before heading to the library; stop at the bank before heading to the pharmacy; stop at the pharmacy before heading to the library; stop at the supermarket before heading to the bank; stop at the supermarket before heading to the library; stop at the supermarket before heading to the pharmacy. Seek a balanced compromise between location quality and driving time.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today. Be sure to hit the bank first before the library; hit the bank first before the pharmacy; hit the pharmacy first before the library; hit the supermarket first before the bank; hit the supermarket first before the library; hit the supermarket first before the pharmacy. Strike a solid balance between good ratings and sensible driving efficiency.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_039` (Cluster 44)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'pharmacy']], Direction=`quality_first` (w=0.75)
- **V0 (Base)**: Today, you'll need to visit the library, supermarket, pharmacy, shopping mall, and bank. Make sure to prioritize places with excellent ratings. You'll need to visit the supermarket before heading to the pharmacy.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the supermarket prior to the pharmacy.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the supermarket before heading to the pharmacy. Give top priority to reputable, well-reviewed venues.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the supermarket first before the pharmacy. Aim for the highest-rated places since quality is the main goal.
- **S/T/D/Pref Audit**: [x] PASS

### Group `e2_confirm_040` (Cluster 107)
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'supermarket']], Direction=`distance_first` (w=0.25)
- **V0 (Base)**: Today, we need to visit the library, pharmacy, bank, supermarket, and shopping mall. Since there's no specific time to return, let's focus on optimizing our route to be as efficient as possible. It's important to go to the bank before heading to the supermarket.
- **V1 (Synonym)**: Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the supermarket.
- **V2 (Syntactic)**: Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the supermarket. Keep the travel distance minimal and direct.
- **V3 (Spoken)**: Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the bank first before the supermarket. Take the quickest and most efficient route possible.
- **S/T/D/Pref Audit**: [x] PASS

---

## 2. 10 组语义改变对照样本 (10 Minimal Semantic Change Controls)

> 用于负向校验：当且仅当人类明确改变了 POI、时限或偏好时，系统应能够敏锐感知语义分歧与路线调整。

### Control Group `e2_control_001` (Base Cluster 40)
- **Change Type**: Preference direction inverted: `quality_first` -> `distance_first`
- **C0 (Original)**: Today, you need to visit the supermarket, the shopping mall, the pharmacy, and the library. Please ensure you return by 18:00. Prioritize visiting places with higher ratings as much as possible. Make sure to visit the supermarket before heading to the shopping mall and stop by the pharmacy before going to the library.
- **C1 (Modified)**: Today, you need to visit the supermarket, the shopping mall, the pharmacy, and the library. Please ensure you return by 18:00. Prioritize visiting places with higher ratings as much as possible. Make sure to visit the supermarket before heading to the shopping mall and stop by the pharmacy before going to the library. Disregard previous preference; now strictly focus on route efficiency.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_002` (Base Cluster 497)
- **Change Type**: Added mandatory POI stop: `supermarket`
- **C0 (Original)**: Today, let's visit the shopping mall, library, bank, and pharmacy. It's important to have a balance between visiting well-rated places and having an efficient route. Start with the shopping mall and then head to the library, and ensure to stop by the bank before going to the pharmacy.
- **C1 (Modified)**: Today, let's visit the shopping mall, library, bank, and pharmacy. It's important to have a balance between visiting well-rated places and having an efficient route. Start with the shopping mall and then head to the library, and ensure to stop by the bank before going to the pharmacy. Also add a quick stop at the supermarket.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_003` (Base Cluster 310)
- **Change Type**: Preference direction inverted: `quality_first` -> `distance_first`
- **C0 (Original)**: Today, the places we need to visit include a shopping mall, a supermarket, a pharmacy, and a bank. While we don’t have a set return time, it’s important to focus on visiting places with higher ratings to enhance our experience. Please make sure to stop by the pharmacy before heading to the bank.
- **C1 (Modified)**: Today, the places we need to visit include a shopping mall, a supermarket, a pharmacy, and a bank. While we don’t have a set return time, it’s important to focus on visiting places with higher ratings to enhance our experience. Please make sure to stop by the pharmacy before heading to the bank. Disregard previous preference; now strictly focus on route efficiency.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_004` (Base Cluster 147)
- **Change Type**: Added mandatory POI stop: `library`
- **C0 (Original)**: Make sure to visit the shopping mall, pharmacy, supermarket, and bank today. Prioritize visiting places with high ratings for a more enjoyable experience. Be sure to stop by the shopping mall before heading to the pharmacy. Also, remember to visit the supermarket before the bank.
- **C1 (Modified)**: Make sure to visit the shopping mall, pharmacy, supermarket, and bank today. Prioritize visiting places with high ratings for a more enjoyable experience. Be sure to stop by the shopping mall before heading to the pharmacy. Also, remember to visit the supermarket before the bank. Also add a quick stop at the library.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_005` (Base Cluster 88)
- **Change Type**: Preference direction inverted: `quality_first` -> `distance_first`
- **C0 (Original)**: Today, we need to visit both the pharmacy and the supermarket. It's important that we go to the pharmacy before heading to the supermarket. Make sure we focus on finding the places with the best reviews, even if it means taking a bit more time.
- **C1 (Modified)**: Today, we need to visit both the pharmacy and the supermarket. It's important that we go to the pharmacy before heading to the supermarket. Make sure we focus on finding the places with the best reviews, even if it means taking a bit more time. Disregard previous preference; now strictly focus on route efficiency.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_006` (Base Cluster 22)
- **Change Type**: Added mandatory POI stop: `shopping_mall`
- **C0 (Original)**: Today, you need to visit the library and the supermarket. Please make sure to return by 20:00. Focus on visiting places with high ratings, even if it means taking a slightly longer route. There are no particular places that you must visit in a specific order.
- **C1 (Modified)**: Today, you need to visit the library and the supermarket. Please make sure to return by 20:00. Focus on visiting places with high ratings, even if it means taking a slightly longer route. There are no particular places that you must visit in a specific order. Also add a quick stop at the shopping mall.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_007` (Base Cluster 446)
- **Change Type**: Preference direction inverted: `balanced` -> `quality_first`
- **C0 (Original)**: Please make sure to visit the pharmacy today. Be sure to return by 19:00. It's important to consider both the quality of the destination and an efficient route when planning your trip.
- **C1 (Modified)**: Please make sure to visit the pharmacy today. Be sure to return by 19:00. It's important to consider both the quality of the destination and an efficient route when planning your trip. Disregard previous preference; now strictly focus on highest ratings.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_008` (Base Cluster 511)
- **Change Type**: Added mandatory POI stop: `bank`
- **C0 (Original)**: Today, make sure to visit the shopping mall, pharmacy, bank, library, and supermarket. Please return by 20:00. It's important to focus on visiting places with the highest ratings. Remember to stop by the bank before heading to the library.
- **C1 (Modified)**: Today, make sure to visit the shopping mall, pharmacy, bank, library, and supermarket. Please return by 20:00. It's important to focus on visiting places with the highest ratings. Remember to stop by the bank before heading to the library. Also add a quick stop at the bank.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_009` (Base Cluster 418)
- **Change Type**: Preference direction inverted: `quality_first` -> `distance_first`
- **C0 (Original)**: Please visit the library and the bank today. It's important to check out the spots that have higher ratings for a better experience. Make sure to go to the library before heading to the bank.
- **C1 (Modified)**: Please visit the library and the bank today. It's important to check out the spots that have higher ratings for a better experience. Make sure to go to the library before heading to the bank. Disregard previous preference; now strictly focus on route efficiency.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

### Control Group `e2_control_010` (Base Cluster 494)
- **Change Type**: Added mandatory POI stop: `shopping_mall`
- **C0 (Original)**: Today, you need to visit the library, supermarket, and pharmacy. Please ensure you're back by 10 PM. Try your best to balance between choosing places with decent ratings and keeping your route efficient.
- **C1 (Modified)**: Today, you need to visit the library, supermarket, and pharmacy. Please ensure you're back by 10 PM. Try your best to balance between choosing places with decent ratings and keeping your route efficient. Also add a quick stop at the shopping mall.
- **Control Audit**: [x] VERIFIED_MINIMAL_DIFFERENCE

