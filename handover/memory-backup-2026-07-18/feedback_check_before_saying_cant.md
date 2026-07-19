---
name: 說做不到之前先跟 agent 討論
description: 認為做不到的事要先跟 subagent 討論找方法，不要直接跟用戶說做不到
type: feedback
originSessionId: 5b348822-934f-4f0f-a91e-ee39def595ce
---
說做不到之前，先跟 subagent 討論有沒有其他方法，確認真的做不到才跟用戶說。

**Why:** 用戶要改 GitLab MR assignee，我直接說「沒有 GitLab MCP 工具，需要你手動操作」，但其實 `D:\mybot\git\tool\.gitlab-token` 就在那裡，用 curl + GitLab API 就能做到。是我自己沒去找就放棄了。

**How to apply:** 當你覺得某件事「做不到」時：
1. 先跟 subagent 討論：有沒有替代方案？（API token、CLI tool、workaround）
2. 搜尋 workspace 裡有沒有相關 credentials 或工具
3. 確認真的沒辦法後，才跟用戶說做不到
4. 永遠不要因為「沒有專用 MCP tool」就放棄 — curl/API 往往能解決
