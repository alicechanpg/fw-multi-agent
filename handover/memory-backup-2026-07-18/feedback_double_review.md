---
name: self-review
description: 每次回報前要自己做 2 輪 review，第一輪審核初稿，第二輪審核修正後的版本
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd7103a4-dec0-4a23-a425-d54ad0523f8a
---

每次回報前要**自己**做 **2 輪** review（2026-07-07 起從 subagent 改為自己 review，兩輪保留）。

**Why:** 用戶認為一輪不夠充分，需要第二輪來驗證第一輪的修正是否正確。改自己 review 是為了省 token（見 [[feedback_ai_collab_mode]]），但兩輪的紀律保留。

**How to apply:**
1. 第一輪：站在資深審稿人角度審初稿（正確性/效能/可維護性/潛在問題），並**用工具驗證事實**
2. 根據發現修正
3. 第二輪：對修正後的版本再審一次，確認沒引入新錯誤、沒遺漏
4. 兩輪都過後才回報用戶
