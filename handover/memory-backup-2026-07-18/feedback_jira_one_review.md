---
name: JIRA comment 只需一輪 review
description: 發 JIRA comment 時只需一輪 self-review，不需要兩輪。覆蓋 L1 規則中 JIRA 的部分。
type: feedback
originSessionId: 96c15cdc-a1a3-4ab9-93a5-dd71363036c3
---
JIRA comment 只需一輪 self-review（L2），不需要兩輪（L1）。（2026-07-07 起 review 機制從 subagent 改為自己做 — 見 [[feedback_ai_collab_mode]]）

**Why:** 兩輪太慢，JIRA comment 不需要像 git push 或 Slack 訊息那樣謹慎。一輪審核已足夠確保正確性。

**How to apply:** 發 JIRA comment 前只做一輪 self-review（仍要用工具查證 ticket、內容正確性），通過就直接貼，不需要第二輪。其他 L1 項目（git push、Slack、Jenkins trigger）仍維持兩輪。
