---
name: review-review
description: Self-review 時必須用工具查原始資料驗證事實，不能只重讀自己整理好的文字
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd7103a4-dec0-4a23-a425-d54ad0523f8a
---

Self-review 時必須做「實際驗證」，不能只做「表面 review」（2026-07-07 起機制從 subagent 改為自己 review，本原則不變 — 見 [[feedback_ai_collab_mode]]）。

**Why:** 用戶發現之前的 AI 討論流於形式——只是看整理好的文字給建議，沒有回去查原始資料，等於「我說什麼就信什麼」，失去雙重確認的意義。改成自己 review 後，同樣的陷阱更容易發生（重讀自己的字最容易自我說服），所以這條更要嚴守。

**How to apply:**

### 不好的 review（表面）
只重讀自己寫好的方案/結論，覺得「看起來對」就回報。

### 好的 review（實際驗證）
針對每個事實性結論，回去查原始資料：
1. 讀取具體資料來源（給明確的 file path / channel ID / message_ts / 指令）
2. 搜尋具體關鍵字確認具體事實（grep、跑指令、看 log、binary compare）
3. 確認具體資源是否存在

### 核心原則
- 每個結論標記驗證依據（file:line 或工具輸出），不是只說「看起來對」
- 無法驗證的項目明確標「待驗證」，不當成事實回報，也不跳過
- 看起來對 ≠ 已驗證
