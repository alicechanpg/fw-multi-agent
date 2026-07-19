---
name: feedback_check_pr_bot_feedback
description: push PR 之後幾分鐘要回去看 PR 上有沒有 bot 回饋（CI / review bot）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5478b7d1-f3c9-4d30-ba24-bf7bb13251a4
---

每次 push PR 之後，隔幾分鐘要主動回去看該 PR 上有沒有 **bot 回饋**（CI checks 結果、code review bot 的留言/建議），有 fail 或建議就跟進處理，不要 push 完就當結束。

**Why:** user 要求（2026-07-09）——PR 上常有 bot 自動回饋，要收。

**How to apply:** push 後等幾分鐘 → `gh pr checks <n>` 看 CI、`gh pr view <n> --comments` 看 bot/reviewer 留言 → 有紅燈或建議就處理再回報。與 [[feedback_dont_stop_to_ask]] 一致（收尾要自動做完）。
