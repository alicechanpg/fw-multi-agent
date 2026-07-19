---
name: feedback-check-jenkins-web
description: "Always verify Jenkins results by checking the actual web page (HTML), not just the API JSON"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b7741786-95b1-48f2-afcc-5232fd4db290
---

Jenkins 結果驗證時，必須用 curl 抓取實際網頁 HTML 來看，不能只看 API JSON。

**Why:** 用戶和所有人都是看 Jenkins 網頁 UI，不是看 API response。API 顯示的 artifact 數量可能跟網頁一致，但如果只看 API 就宣稱「只有 2 個」而網頁明明顯示 3 個，會失去信任。

**How to apply:** 每次 Jenkins build 完成後，除了 API 查詢外，也要 `curl` 抓取 build 頁面 HTML，用 grep 提取 artifact 列表、build status 等關鍵資訊，確認跟 API 結果一致。用 `--user` 認證即可。
