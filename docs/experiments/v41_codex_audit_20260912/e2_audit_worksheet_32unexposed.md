> **当前审核状态：USER_APPROVED（2026-09-12）**。负责人在对话中明确确认“你直接推进吧； 人工审核我已经都通过了”。[当前收尾结果](closeout/RESULTS_AND_NEXT.md)及冻结包 human_approval.json 为新凭证；下方 PENDING 与逐行栏位保留为提交时的历史记录，不再代表待审批。32/8 是已识别暴露簇分层；“纯净未见”不作为绝对来源保证，人工确认不追溯恢复预注册资格。

# E2 独立确认实验人工审核工作表 (32 个纯净未见簇)

- **审计状态**: `PENDING_HUMAN_AUDIT` (必须由人类专家独立审查，严禁自动化脚本伪造勾选)
- **组数**: 32 组 (128 条 Utterances)
- **数据集类型**: 真正未见纯净组 (完全排除历史暴露源)
- **基准模型**: GPT-5.6-luna (主资产) & Gemini-3.1-flash-lite
- **说明**: 本工作表列出全部指令文本、真实意图标注、候选提取结果与复核输出。重点关注语义偏差、意图幻觉与复核改坏。

---

## Group `e2_clean_002` (Cluster `522`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_002_v0` (V0)
- **Instruction**: "Today, we need to visit both the shopping mall and the pharmacy. We'll need to be back by 17:00. Let's aim for a balance between visiting well-rated places and keeping our route efficient. There are no specific dependencies, so we can visit them in any order that suits us best."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1020, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_002_v1` (V1)
- **Instruction**: "Please visit the pharmacy and the shopping mall today, returning by 17:00. Maintain a balance between visiting well-rated places and keeping the route efficient."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1020, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_002_v2` (V2)
- **Instruction**: "Please ensure you are back by 17:00 after visiting both the pharmacy and the shopping mall. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1020, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_002_v3` (V3)
- **Instruction**: "Hey, need you to stop by the pharmacy as well as the shopping mall today and be back before 5 PM. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1020, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_004` (Cluster `152`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_004_v0` (V0)
- **Instruction**: "Today, make sure to visit the supermarket, pharmacy, and bank. Aim to be back by 24:00. It's important to balance both visiting places with good ratings and not extending the route too much. Please ensure to go to the pharmacy before heading to the bank."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['pharmacy', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_004_v1` (V1)
- **Instruction**: "Please visit the bank, the pharmacy, and the supermarket today, returning by 24:00. Maintain a balance between visiting well-rated places and keeping the route efficient. Make sure to visit the pharmacy prior to the bank."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['pharmacy', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_004_v2` (V2)
- **Instruction**: "Please ensure you are back by 24:00 after visiting the bank, the pharmacy, and the supermarket. Remember to stop at the pharmacy before heading to the bank. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['pharmacy', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_004_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the pharmacy, and the supermarket today and be back before midnight. Be sure to hit the pharmacy first before the bank. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['pharmacy', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[['pharmacy', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_005` (Cluster `89`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_005_v0` (V0)
- **Instruction**: "We need to visit the library, pharmacy, shopping mall, supermarket, and bank today. Make sure we focus on visiting highly rated places as a priority. Remember to go to the library before heading to the pharmacy, and visit the shopping mall prior to the supermarket."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.6
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.6
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_005_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the pharmacy, and visit the shopping mall prior to the supermarket."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.7
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.7
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_005_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the library before heading to the pharmacy, and stop at the shopping mall before heading to the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_005_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the library first before the pharmacy, and hit the shopping mall first before the supermarket. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['library', 'pharmacy'], ['shopping_mall', 'supermarket']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_006` (Cluster `23`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_006_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall and the bank. Let's prioritize places with high ratings to ensure a great experience. Remember, we must stop by the shopping mall before heading to the bank."
- **Gold Intent**: POIs=['bank', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.75
- **Luna Review**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_006_v1` (V1)
- **Instruction**: "Please visit the bank and the shopping mall today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the bank."
- **Gold Intent**: POIs=['bank', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.6
- **Luna Cand B**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.8
- **Luna Review**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_006_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the bank and the shopping mall. Remember to stop at the shopping mall before heading to the bank. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=1.0
- **Luna Cand B**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.8
- **Luna Review**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_006_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank as well as the shopping mall today. Be sure to hit the shopping mall first before the bank. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=1.0
- **Luna Review**: POIs=['bank', 'shopping_mall'], Deps=[['shopping_mall', 'bank']], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_007` (Cluster `471`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_007_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall and the library. I'd like to balance between exploring well-rated places and maintaining an efficient route. There are no specific order requirements for our stops."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_007_v1` (V1)
- **Instruction**: "Please visit the library and the shopping mall today. Maintain a balance between visiting well-rated places and keeping the route efficient."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_007_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the library and the shopping mall. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_007_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library as well as the shopping mall today. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_008` (Cluster `533`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_008_v0` (V0)
- **Instruction**: "Today, we need to visit the supermarket, shopping mall, pharmacy, bank, and library. While time isn't a concern, let's focus on enjoying some of the higher-rated spots. Make sure to go to the shopping mall before heading to the pharmacy and visit the bank before going to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_008_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library, and visit the shopping mall prior to the pharmacy."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_008_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the library, and stop at the shopping mall before heading to the pharmacy. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_008_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the bank first before the library, and hit the shopping mall first before the pharmacy. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['shopping_mall', 'pharmacy']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_010` (Cluster `520`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_010_v0` (V0)
- **Instruction**: "Today, you need to visit the shopping mall and the library. Be sure to return by 21:00. Aim for a balance between visiting places that are reasonably rated and keeping your journey efficient. There are no specific dependencies, so you can visit them in any order you prefer."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_010_v1` (V1)
- **Instruction**: "Please visit the library and the shopping mall today, returning by 21:00. Maintain a balance between visiting well-rated places and keeping the route efficient."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_010_v2` (V2)
- **Instruction**: "Please ensure you are back by 21:00 after visiting both the library and the shopping mall. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_010_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library as well as the shopping mall today and be back before 9 PM. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_011` (Cluster `449`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_011_v0` (V0)
- **Instruction**: "Today, make sure to visit the shopping mall, supermarket, pharmacy, and bank. Since we need to be efficient with our route, let's keep it quick and straightforward. Start by going to the shopping mall before heading to the supermarket, and then stop by the supermarket before visiting the pharmacy."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.3
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.3
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_011_v1` (V1)
- **Instruction**: "Please visit the bank, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the shopping mall prior to the pharmacy; visit the shopping mall prior to the supermarket; visit the supermarket prior to the pharmacy."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.25
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.2
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.25
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_011_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the pharmacy; stop at the shopping mall before heading to the supermarket; stop at the supermarket before heading to the pharmacy. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_011_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the pharmacy; hit the shopping mall first before the supermarket; hit the supermarket first before the pharmacy. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'pharmacy'], ['shopping_mall', 'supermarket'], ['supermarket', 'pharmacy']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_013` (Cluster `57`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_013_v0` (V0)
- **Instruction**: "
Please make sure to visit the bank today. I'd like you to find a balance between visiting a well-rated place and not taking too long on your route."
- **Gold Intent**: POIs=['bank'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Review**: POIs=['bank'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_013_v1` (V1)
- **Instruction**: "Please visit the bank today. Maintain a balance between visiting well-rated places and keeping the route efficient."
- **Gold Intent**: POIs=['bank'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Review**: POIs=['bank'], Deps=[], QW=0.5
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_013_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['bank'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Review**: POIs=['bank'], Deps=[], QW=0.5
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_013_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank today. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['bank'], TimeLimit=None, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['bank'], Deps=[], QW=0.5
- **Luna Review**: POIs=['bank'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_014` (Cluster `143`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_014_v0` (V0)
- **Instruction**: "Today, make sure to visit the supermarket, library, bank, and pharmacy. Pay special attention to visiting places with higher ratings. Enjoy your day with these stops!"
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_014_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_014_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, and the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_014_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=1.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_015` (Cluster `529`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_015_v0` (V0)
- **Instruction**: "Today, please visit the pharmacy, supermarket, shopping mall, and library. Make sure to return by 19:00. Do make it a priority to visit highly-rated places when possible. It's important that you stop by the supermarket before heading to the shopping mall, and be sure to visit the shopping mall before you go to the library."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'shopping_mall']], QW=0.6
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_015_v1` (V1)
- **Instruction**: "Please visit the library, the pharmacy, the shopping mall, and the supermarket today, returning by 19:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the library; visit the supermarket prior to the library; visit the supermarket prior to the shopping mall."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.6
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_015_v2` (V2)
- **Instruction**: "Please ensure you are back by 19:00 after visiting the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the library; stop at the supermarket before heading to the library; stop at the supermarket before heading to the shopping mall. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.6
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_015_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today and be back before 7 PM. Be sure to hit the shopping mall first before the library; hit the supermarket first before the library; hit the supermarket first before the shopping mall. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.6
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'library'], ['supermarket', 'shopping_mall']], QW=0.7
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_018` (Cluster `342`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_018_v0` (V0)
- **Instruction**: "Today, you'll need to visit the shopping mall and the library. Since there’s no specific return time, ensure the journey is efficient and quick. Start by going to the shopping mall before heading to the library."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_018_v1` (V1)
- **Instruction**: "Please visit the library and the shopping mall today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the shopping mall prior to the library."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.25
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.3
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.25
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_018_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the library and the shopping mall. Remember to stop at the shopping mall before heading to the library. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_018_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library as well as the shopping mall today. Be sure to hit the shopping mall first before the library. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['library', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['library', 'shopping_mall'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_019` (Cluster `425`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_019_v0` (V0)
- **Instruction**: "Today we'll need to visit the library, supermarket, bank, and pharmacy. Please ensure to return by 20:00. It's important to prioritize a quick and efficient route today. Remember, you must visit the supermarket before heading to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1200, Deps=[['supermarket', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.3
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_019_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the supermarket today, returning by 20:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the supermarket prior to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1200, Deps=[['supermarket', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_019_v2` (V2)
- **Instruction**: "Please ensure you are back by 20:00 after visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the supermarket before heading to the bank. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1200, Deps=[['supermarket', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_019_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today and be back before 8 PM. Be sure to hit the supermarket first before the bank. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1200, Deps=[['supermarket', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['supermarket', 'bank']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_020` (Cluster `528`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_020_v0` (V0)
- **Instruction**: "Today, make sure to visit the supermarket, library, bank, and pharmacy. Please be back by midnight. We should focus on keeping the route as efficient as possible. Remember to head to the bank before the pharmacy."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['bank', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_020_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the supermarket today, returning by 24:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the pharmacy."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['bank', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_020_v2` (V2)
- **Instruction**: "Please ensure you are back by 24:00 after visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the bank before heading to the pharmacy. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['bank', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_020_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today and be back before midnight. Be sure to hit the bank first before the pharmacy. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=1440, Deps=[['bank', 'pharmacy']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['bank', 'pharmacy']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_021` (Cluster `428`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_021_v0` (V0)
- **Instruction**: "Today, you'll need to visit the shopping mall and the pharmacy. Please make sure to return by 18:00. Try to be efficient in planning your route to accommodate all the stops effectively."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1080, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.3
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.3
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_021_v1` (V1)
- **Instruction**: "Please visit the pharmacy and the shopping mall today, returning by 18:00. Focus on route efficiency and minimizing unnecessary travel time."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1080, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.25
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.3
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.25
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_021_v2` (V2)
- **Instruction**: "Please ensure you are back by 18:00 after visiting both the pharmacy and the shopping mall. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1080, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.2
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.25
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_021_v3` (V3)
- **Instruction**: "Hey, need you to stop by the pharmacy as well as the shopping mall today and be back before 6 PM. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=1080, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_022` (Cluster `38`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_022_v0` (V0)
- **Instruction**: "Today, make sure to visit the bank, shopping mall, library, supermarket, and pharmacy. Since efficiency is key, aim to follow the most efficient route possible. Remember to stop by the shopping mall before heading to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_022_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the shopping mall prior to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_022_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the library. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.3
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_022_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the library. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.25
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_024` (Cluster `444`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_024_v0` (V0)
- **Instruction**: "Today, make sure to visit the library, bank, and pharmacy. Please return by 20:00. It would be great to prioritize places with high ratings. There are no specific order requirements for the visits."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy'], TimeLimit=1200, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.6
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_024_v1` (V1)
- **Instruction**: "Please visit the bank, the library, and the pharmacy today, returning by 20:00. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy'], TimeLimit=1200, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_024_v2` (V2)
- **Instruction**: "Please ensure you are back by 20:00 after visiting the bank, the library, and the pharmacy. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy'], TimeLimit=1200, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_024_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, and the pharmacy today and be back before 8 PM. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy'], TimeLimit=1200, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=1.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_025` (Cluster `43`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_025_v0` (V0)
- **Instruction**: "We need to visit the pharmacy and the shopping mall today. I really want to make sure we visit places with high ratings. Let's stop by the pharmacy first before heading to the shopping mall."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.75
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.8
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_025_v1` (V1)
- **Instruction**: "Please visit the pharmacy and the shopping mall today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the shopping mall."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.7
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=1.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_025_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the pharmacy and the shopping mall. Remember to stop at the pharmacy before heading to the shopping mall. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.8
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=1.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_025_v3` (V3)
- **Instruction**: "Hey, need you to stop by the pharmacy as well as the shopping mall today. Be sure to hit the pharmacy first before the shopping mall. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=1.0
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.8
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_026` (Cluster `253`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_026_v0` (V0)
- **Instruction**: "Today, make sure to visit the library and the bank. Please ensure you return by 21:00. Prioritize visiting places with high ratings as we value quality experiences. Remember, you need to go to the library before heading to the bank."
- **Gold Intent**: POIs=['bank', 'library'], TimeLimit=1260, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.75
- **Luna Review**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_026_v1` (V1)
- **Instruction**: "Please visit the bank and the library today, returning by 21:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the bank."
- **Gold Intent**: POIs=['bank', 'library'], TimeLimit=1260, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.7
- **Luna Review**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_026_v2` (V2)
- **Instruction**: "Please ensure you are back by 21:00 after visiting both the bank and the library. Remember to stop at the library before heading to the bank. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library'], TimeLimit=1260, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=1.0
- **Luna Review**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_026_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank as well as the library today and be back before 9 PM. Be sure to hit the library first before the bank. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library'], TimeLimit=1260, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=0.8
- **Luna Review**: POIs=['bank', 'library'], Deps=[['library', 'bank']], QW=1.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_027` (Cluster `527`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_027_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall and the pharmacy. We're looking for a balance between well-rated places and an efficient route. Make sure to head to the shopping mall before going to the pharmacy."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.5
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.5
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_027_v1` (V1)
- **Instruction**: "Please visit the pharmacy and the shopping mall today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the pharmacy."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.8
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.7
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_027_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the pharmacy and the shopping mall. Remember to stop at the shopping mall before heading to the pharmacy. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.75
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.8
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_027_v3` (V3)
- **Instruction**: "Hey, need you to stop by the pharmacy as well as the shopping mall today. Be sure to hit the shopping mall first before the pharmacy. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['shopping_mall', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=1.0
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=1.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall'], Deps=[['shopping_mall', 'pharmacy']], QW=1.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_028` (Cluster `405`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_028_v0` (V0)
- **Instruction**: "Today, you'll be visiting the library, the bank, and the shopping mall. Make sure to focus on an efficient route to get through these locations quickly. Start your day by heading to the library before the bank to ensure everything goes smoothly."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.3
- **Luna Review**: POIs=['shopping_mall', 'supermarket'], Deps=[], QW=0.3
- **⚠️ [审计焦点/改坏警报]**: Candidate A 满足所有 POI (bank, library, shopping_mall) 成功；但 Review 严重幻觉输出 supermarket，遗漏 bank 和 library，导致规划任务失败 (TSR: True -> False)！
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_028_v1` (V1)
- **Instruction**: "Please visit the bank, the library, and the shopping mall today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the library prior to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.3
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_028_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, and the shopping mall. Remember to stop at the library before heading to the bank. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_028_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, and the shopping mall today. Be sure to hit the library first before the bank. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall'], Deps=[['library', 'bank']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_029` (Cluster `377`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_029_v0` (V0)
- **Instruction**: "Today, we need to visit the supermarket, pharmacy, shopping mall, and library. It's important that we prioritize visiting highly-rated places. Make sure to stop by the supermarket before heading to the pharmacy, and visit the shopping mall before the library."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.6
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.8
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_029_v1` (V1)
- **Instruction**: "Please visit the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the shopping mall prior to the library, and visit the supermarket prior to the pharmacy."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.75
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_029_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the library, and stop at the supermarket before heading to the pharmacy. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.8
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.8
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_029_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the library, and hit the supermarket first before the pharmacy. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=1.0
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'library'], ['supermarket', 'pharmacy']], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_030` (Cluster `599`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_030_v0` (V0)
- **Instruction**: "Today, visit the pharmacy, shopping mall, and supermarket. Make sure to be back by midnight. It’s important to keep the route as short as possible while still visiting each location."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1440, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Luna Review**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_030_v1` (V1)
- **Instruction**: "Please visit the pharmacy, the shopping mall, and the supermarket today, returning by 24:00. Focus on route efficiency and minimizing unnecessary travel time."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1440, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.3
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_030_v2` (V2)
- **Instruction**: "Please ensure you are back by 24:00 after visiting the pharmacy, the shopping mall, and the supermarket. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1440, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_030_v3` (V3)
- **Instruction**: "Hey, need you to stop by the pharmacy, the shopping mall, and the supermarket today and be back before midnight. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1440, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_031` (Cluster `31`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_031_v0` (V0)
- **Instruction**: "Today, you'll need to visit both the pharmacy and the library. Make sure to prioritize going to places with high ratings even if it means taking a bit longer."
- **Gold Intent**: POIs=['library', 'pharmacy'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy'], Deps=[], QW=0.75
- **Luna Cand B**: POIs=['library', 'pharmacy'], Deps=[], QW=1.0
- **Luna Review**: POIs=['library', 'pharmacy'], Deps=[], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_031_v1` (V1)
- **Instruction**: "Please visit the library and the pharmacy today. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['library', 'pharmacy'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['library', 'pharmacy'], Deps=[], QW=0.7
- **Luna Review**: POIs=['library', 'pharmacy'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_031_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting both the library and the pharmacy. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['library', 'pharmacy'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy'], Deps=[], QW=0.75
- **Luna Cand B**: POIs=['library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Review**: POIs=['library', 'pharmacy'], Deps=[], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_031_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library as well as the pharmacy today. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['library', 'pharmacy'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy'], Deps=[], QW=0.7
- **Luna Cand B**: POIs=['library', 'pharmacy'], Deps=[], QW=0.8
- **Luna Review**: POIs=['library', 'pharmacy'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_033` (Cluster `387`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_033_v0` (V0)
- **Instruction**: "Today, we need to visit the bank, library, and supermarket. Since there is no specific time for returning, let’s try to make our trip as efficient as possible. Please make sure to stop by the library before heading to the supermarket."
- **Gold Intent**: POIs=['bank', 'library', 'supermarket'], TimeLimit=None, Deps=[['library', 'supermarket']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.25
- **Luna Review**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_033_v1` (V1)
- **Instruction**: "Please visit the bank, the library, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the library prior to the supermarket."
- **Gold Intent**: POIs=['bank', 'library', 'supermarket'], TimeLimit=None, Deps=[['library', 'supermarket']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.3
- **Luna Review**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_033_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, and the supermarket. Remember to stop at the library before heading to the supermarket. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'supermarket'], TimeLimit=None, Deps=[['library', 'supermarket']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_033_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, and the supermarket today. Be sure to hit the library first before the supermarket. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'supermarket'], TimeLimit=None, Deps=[['library', 'supermarket']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'supermarket'], Deps=[['library', 'supermarket']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_034` (Cluster `81`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_034_v0` (V0)
- **Instruction**: "Let's visit the pharmacy, bank, supermarket, and shopping mall today. It's important to prioritize places with high ratings. We'll need to stop by the supermarket before heading over to the shopping mall."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.7
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_034_v1` (V1)
- **Instruction**: "Please visit the bank, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the supermarket prior to the shopping mall."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.7
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_034_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the supermarket before heading to the shopping mall. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.75
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=1.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_034_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the supermarket first before the shopping mall. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=1.0
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=0.8
- **Luna Review**: POIs=['bank', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['supermarket', 'shopping_mall']], QW=1.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_035` (Cluster `360`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_035_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall, pharmacy, library, and supermarket. Since there is no specific return time, please focus on making the journey as efficient as possible."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_035_v1` (V1)
- **Instruction**: "Please visit the library, the pharmacy, the shopping mall, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.25
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_035_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the library, the pharmacy, the shopping mall, and the supermarket. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_035_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.2
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_036` (Cluster `336`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_036_v0` (V0)
- **Instruction**: "Today, we need to visit the bank, library, shopping mall, pharmacy, and supermarket. Please make sure to be back by 23:00. It's important to prioritize visiting places with good reviews, even if it takes a little more time. Since there are no specific visit orders, feel free to plan the sequence that works best."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.7
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_036_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today, returning by 23:00. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_036_v2` (V2)
- **Instruction**: "Please ensure you are back by 23:00 after visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=1.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_036_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today and be back before 11 PM. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_037` (Cluster `45`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_037_v0` (V0)
- **Instruction**: "Today's itinerary includes visiting the pharmacy, shopping mall, library, and bank. Given our preference for efficiency, let's try to keep our route quick and straightforward. Start by going to the pharmacy before heading to the shopping mall."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.4
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_037_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the shopping mall today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the pharmacy prior to the shopping mall."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_037_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, and the shopping mall. Remember to stop at the pharmacy before heading to the shopping mall. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_037_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the shopping mall today. Be sure to hit the pharmacy first before the shopping mall. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['pharmacy', 'shopping_mall']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['pharmacy', 'shopping_mall']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_038` (Cluster `109`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_038_v0` (V0)
- **Instruction**: "Today, you'll need to visit the pharmacy, supermarket, library, and bank. With efficiency being a priority, aim for a route that saves time and energy while still hitting all these spots."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.3
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.4
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.3
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_038_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the supermarket today. Focus on route efficiency and minimizing unnecessary travel time."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.2
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_038_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, and the supermarket. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.2
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_038_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_039` (Cluster `162`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_039_v0` (V0)
- **Instruction**: "Today, we need to visit the library, bank, pharmacy, supermarket, and the shopping mall. Let's focus on visiting the places with the highest ratings. Begin by going to the library, then head over to the bank before making your way to the pharmacy. After that, visit the supermarket and finally the shopping mall."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['pharmacy', 'supermarket'], ['supermarket', 'shopping_mall']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['pharmacy', 'supermarket'], ['supermarket', 'shopping_mall']], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['pharmacy', 'supermarket'], ['supermarket', 'shopping_mall']], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_039_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the pharmacy; visit the library prior to the bank; visit the library prior to the pharmacy; visit the supermarket prior to the shopping mall."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_039_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the pharmacy; stop at the library before heading to the bank; stop at the library before heading to the pharmacy; stop at the supermarket before heading to the shopping mall. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_039_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the bank first before the pharmacy; hit the library first before the bank; hit the library first before the pharmacy; hit the supermarket first before the shopping mall. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=1.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['bank', 'pharmacy'], ['library', 'bank'], ['library', 'pharmacy'], ['supermarket', 'shopping_mall']], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_040` (Cluster `96`)
**暴露状态**: 纯净未见簇

### Utterance: `e2_clean_040_v0` (V0)
- **Instruction**: "Today, you need to visit the library, supermarket, shopping mall, bank, and pharmacy. Aim for a day that's both efficient and includes places that are reasonably well-rated. Make sure to stop by the shopping mall before heading to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_040_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Maintain a balance between visiting well-rated places and keeping the route efficient. Make sure to visit the shopping mall prior to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_040_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the shopping mall before heading to the bank. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_040_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the shopping mall first before the bank. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['shopping_mall', 'bank']], QWeight=0.5
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['shopping_mall', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---
