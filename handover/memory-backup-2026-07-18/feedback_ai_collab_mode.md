---
name: ai-collaboration-mode-review
description: 【最重要的規則】強制 review 機制 — 不管大小事都必須先自己 review（兩輪）再回報，無例外
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd7103a4-dec0-4a23-a425-d54ad0523f8a
---

# 這是用戶認為最重要的規則（2026-07-07 從 subagent 改為自己 review）

AI Collaboration Mode 的討論機制**從 Agent Subagent 改成主 agent 自己 review**。原因：subagent 討論太耗 token。不管大小事都必須先自己 review 再回報用戶，無例外。範圍：全域（所有專案）。

**Why:** 用戶的核心工作方法論。每一個產出都必須經過 review 才能回報，這是品質保證的基礎。但 subagent 每次討論吃掉大量 token，改由主 agent 自己扮演資深審稿人做嚴格 self-review，成本大幅下降、品質標準不變。

**How to apply:**
- **不再開 subagent**；由主 agent 自己 review。
- 保留**兩輪**：第一輪審初稿、第二輪審修正版（見 [[feedback_double_review]]）。
- ⚠️ **關鍵不可省：** 事實性結論必須用工具（讀 source、grep、跑指令、看 log）實際驗證，不能只重讀自己寫的字。看起來對 ≠ 已驗證（見 [[feedback_subagent_must_verify]]）。
- 即使是簡單查詢、小改動、狀態回報等，都要先 self-review 再回報。
- 跳過 self-review = 違規，沒有例外。
- 唯一例外：用戶明確說「快速」或「不用討論」。
