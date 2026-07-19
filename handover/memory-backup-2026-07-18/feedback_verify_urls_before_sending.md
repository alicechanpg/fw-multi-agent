---
name: feedback_verify_urls_before_sending
description: 把任何 URL/連結放進對外訊息(Slack/JIRA/PR)前，先實際驗證它有效，不要只信手上的字串
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

任何要送出去給別人的 **URL/連結**（Slack 給主管、JIRA comment、PR body），送之前先**實際驗證它是對的、開得起來**，不要只因為「字串看起來對 / 是某工具吐出來的」就送。

**Why:** 2026-07-16 我把 PR 連結 Slack 給 Teo，用戶事後說「the url u sent to teo is invalid last time? please check url validity this time」。事後查那條 URL 其實是對的（private repo 對未登入者一律回 404，是假 404），但重點是：**我送之前沒獨立驗證過**，只信了 `gh pr view` 的 url 欄位。對外連結出錯的成本高（尤其對主管）。

**How to apply:**
- 送出前用權威來源核對：PR/issue 用 `gh api repos/OWNER/REPO/pulls/N --jq .html_url`（不要自己拼 owner/repo/number）。
- 知道**假 404 陷阱**：private repo / org SSO 沒授權時，正確連結對訪客也會顯示 404 —— curl 未登入打到 404 不代表連結壞。要用 authenticated 方式判斷。
- 若對方可能開不了，主動附「需登入有權限的帳號 / 過 org SSO」，或附 PR 標題讓對方在 repo 內自己找。
- 這是 [[feedback_evidence_based]] 用在「對外連結」上的具體版。
