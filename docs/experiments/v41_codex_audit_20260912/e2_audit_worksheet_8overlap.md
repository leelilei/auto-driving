> **当前审核状态：USER_APPROVED（2026-09-12）**。负责人在对话中明确确认“你直接推进吧； 人工审核我已经都通过了”。[当前收尾结果](closeout/RESULTS_AND_NEXT.md)及冻结包 human_approval.json 为新凭证；下方 PENDING 与逐行栏位保留为提交时的历史记录，不再代表待审批。32/8 是已识别暴露簇分层；“纯净未见”不作为绝对来源保证，人工确认不追溯恢复预注册资格。

# E2 开发与迁移验证人工审核工作表 (8 个历史暴露重叠簇)

- **审计状态**: `PENDING_HUMAN_AUDIT` (必须由人类专家独立审查，严禁自动化脚本伪造勾选)
- **组数**: 8 组 (32 条 Utterances)
- **数据集类型**: 开发/迁移重叠组 (旧 E2 已暴露)
- **基准模型**: GPT-5.6-luna (主资产) & Gemini-3.1-flash-lite
- **说明**: 本工作表列出全部指令文本、真实意图标注、候选提取结果与复核输出。重点关注语义偏差、意图幻觉与复核改坏。

---

## Group `e2_clean_001` (Cluster `42`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_001_v0` (V0)
- **Instruction**: "Please make sure to visit the supermarket and the library today. You need to be back by 21:00. Since we're pressed for time, let's prioritize a quick and efficient route. Make sure to stop at the supermarket before heading to the library."
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1260, Deps=[['supermarket', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.2
- **Luna Cand B**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.2
- **Luna Review**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.2
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_001_v1` (V1)
- **Instruction**: "Please visit the library and the supermarket today, returning by 21:00. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the supermarket prior to the library."
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1260, Deps=[['supermarket', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.0
- **Luna Cand B**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.2
- **Luna Review**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_001_v2` (V2)
- **Instruction**: "Please ensure you are back by 21:00 after visiting both the library and the supermarket. Remember to stop at the supermarket before heading to the library. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1260, Deps=[['supermarket', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.25
- **Luna Cand B**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.0
- **Luna Review**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.25
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_001_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library as well as the supermarket today and be back before 9 PM. Be sure to hit the supermarket first before the library. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['library', 'supermarket'], TimeLimit=1260, Deps=[['supermarket', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.0
- **Luna Cand B**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.2
- **Luna Review**: POIs=['library', 'supermarket'], Deps=[['supermarket', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_003` (Cluster `325`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_003_v0` (V0)
- **Instruction**: "Today, you need to visit the pharmacy, bank, shopping mall, and library. Efficiency is key, so prioritize the shortest route. Start by stopping at the pharmacy, then head to the bank. After that, make your way to the shopping mall, and finish your errands at the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_003_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the shopping mall today. Focus on route efficiency and minimizing unnecessary travel time. Make sure to visit the bank prior to the library; visit the bank prior to the shopping mall; visit the pharmacy prior to the bank; visit the pharmacy prior to the library; visit the pharmacy prior to the shopping mall; visit the shopping mall prior to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.2
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_003_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, and the shopping mall. Remember to stop at the bank before heading to the library; stop at the bank before heading to the shopping mall; stop at the pharmacy before heading to the bank; stop at the pharmacy before heading to the library; stop at the pharmacy before heading to the shopping mall; stop at the shopping mall before heading to the library. Keep the travel distance minimal and direct."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_003_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the shopping mall today. Be sure to hit the bank first before the library; hit the bank first before the shopping mall; hit the pharmacy first before the bank; hit the pharmacy first before the library; hit the pharmacy first before the shopping mall; hit the shopping mall first before the library. Take the quickest and most efficient route possible."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], TimeLimit=None, Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QWeight=0.25
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall'], Deps=[['bank', 'library'], ['bank', 'shopping_mall'], ['pharmacy', 'bank'], ['pharmacy', 'library'], ['pharmacy', 'shopping_mall'], ['shopping_mall', 'library']], QW=0.0
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_009` (Cluster `433`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_009_v0` (V0)
- **Instruction**: "Today, make sure to visit the supermarket, bank, and pharmacy. Focus on spending time at the places with the best ratings. There are no specific order requirements for your visits."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=1.0
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=1.0
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_009_v1` (V1)
- **Instruction**: "Please visit the bank, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_009_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the pharmacy, and the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=1.0
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.75
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.75
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_009_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the pharmacy, and the supermarket today. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.6
- **Luna Review**: POIs=['bank', 'pharmacy', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_012` (Cluster `361`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_012_v0` (V0)
- **Instruction**: "Today, you need to visit the library, bank, supermarket, and pharmacy. While balancing time and quality, aim to make both efficient choices and choose spots that offer reasonably good experiences. Make sure to stop by the library before heading to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.5
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.5
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_012_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the library prior to the bank."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_012_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, and the supermarket. Remember to stop at the library before heading to the bank. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.6
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_012_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, and the supermarket today. Be sure to hit the library first before the bank. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], TimeLimit=None, Deps=[['library', 'bank']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=1.0
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'supermarket'], Deps=[['library', 'bank']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_016` (Cluster `56`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_016_v0` (V0)
- **Instruction**: "Today, make sure to visit the bank, library, supermarket, and shopping mall. Please be home by 19:00. Prioritize visiting places with high ratings as they are more important today. Start at the bank before heading to the library, and continue to the supermarket right after the library."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['library', 'supermarket']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['library', 'supermarket']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['library', 'supermarket']], QW=0.6
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_016_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the shopping mall, and the supermarket today, returning by 19:00. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the bank prior to the library; visit the bank prior to the supermarket; visit the library prior to the supermarket."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.6
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_016_v2` (V2)
- **Instruction**: "Please ensure you are back by 19:00 after visiting the bank, the library, the shopping mall, and the supermarket. Remember to stop at the bank before heading to the library; stop at the bank before heading to the supermarket; stop at the library before heading to the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=1.0
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_016_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the shopping mall, and the supermarket today and be back before 7 PM. Be sure to hit the bank first before the library; hit the bank first before the supermarket; hit the library first before the supermarket. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], TimeLimit=1140, Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=1.0
- **Luna Cand B**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'shopping_mall', 'supermarket'], Deps=[['bank', 'library'], ['bank', 'supermarket'], ['library', 'supermarket']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_017` (Cluster `369`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_017_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall, supermarket, pharmacy, library, and bank. It's important to focus on visiting places with higher ratings. Remember, we must stop by the pharmacy before heading to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'library']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.6
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.8
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_017_v1` (V1)
- **Instruction**: "Please visit the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Prioritize locations with high ratings and strong customer reviews. Make sure to visit the pharmacy prior to the library."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'library']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.7
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.8
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.7
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_017_v2` (V2)
- **Instruction**: "Your itinerary today includes visiting the bank, the library, the pharmacy, the shopping mall, and the supermarket. Remember to stop at the pharmacy before heading to the library. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'library']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.75
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=1.0
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_017_v3` (V3)
- **Instruction**: "Hey, need you to stop by the bank, the library, the pharmacy, the shopping mall, and the supermarket today. Be sure to hit the pharmacy first before the library. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=None, Deps=[['pharmacy', 'library']], QWeight=0.75
- **Luna Cand A**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.8
- **Luna Cand B**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.75
- **Luna Review**: POIs=['bank', 'library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[['pharmacy', 'library']], QW=0.6
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_023` (Cluster `501`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_023_v0` (V0)
- **Instruction**: "Please visit the library, shopping mall, pharmacy, and supermarket today. Make sure to return by 23:00. It would be wonderful if you could prioritize visiting places with high ratings."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.6
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.6
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_023_v1` (V1)
- **Instruction**: "Please visit the library, the pharmacy, the shopping mall, and the supermarket today, returning by 23:00. Prioritize locations with high ratings and strong customer reviews."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_023_v2` (V2)
- **Instruction**: "Please ensure you are back by 23:00 after visiting the library, the pharmacy, the shopping mall, and the supermarket. Give top priority to reputable, well-reviewed venues."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.75
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.75
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.75
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_023_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library, the pharmacy, the shopping mall, and the supermarket today and be back before 11 PM. Aim for the highest-rated places since quality is the main goal."
- **Gold Intent**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], TimeLimit=1380, Deps=[], QWeight=0.75
- **Luna Cand A**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Cand B**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Luna Review**: POIs=['library', 'pharmacy', 'shopping_mall', 'supermarket'], Deps=[], QW=0.8
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---

## Group `e2_clean_032` (Cluster `345`)
**暴露状态**: 旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)

### Utterance: `e2_clean_032_v0` (V0)
- **Instruction**: "Today, we need to visit the shopping mall, supermarket, and library. Please ensure we return by 21:00. I’d appreciate a balance between visiting highly-rated places and keeping the route efficient. There are no specific orders in which these places must be visited."
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_032_v1` (V1)
- **Instruction**: "Please visit the library, the shopping mall, and the supermarket today, returning by 21:00. Maintain a balance between visiting well-rated places and keeping the route efficient."
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Gemini Review 状态**: 有效 JSON 解析
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_032_v2` (V2)
- **Instruction**: "Please ensure you are back by 21:00 after visiting the library, the shopping mall, and the supermarket. Seek a balanced compromise between location quality and driving time."
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

### Utterance: `e2_clean_032_v3` (V3)
- **Instruction**: "Hey, need you to stop by the library, the shopping mall, and the supermarket today and be back before 9 PM. Strike a solid balance between good ratings and sensible driving efficiency."
- **Gold Intent**: POIs=['library', 'shopping_mall', 'supermarket'], TimeLimit=1260, Deps=[], QWeight=0.5
- **Luna Cand A**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Cand B**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Luna Review**: POIs=['library', 'shopping_mall', 'supermarket'], Deps=[], QW=0.5
- **Gemini Review 状态**: 无效格式回退至 Candidate A (Markdown 代码块/Extra data)
- **人工审核背书**:
  - [ ] 指令语义清晰无歧义
  - [ ] Gold Intent 标注准确
  - [ ] 候选差异判断合理
  - **审核人签署**: `____________________` | **日期**: `____-__-__`
  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`

---
