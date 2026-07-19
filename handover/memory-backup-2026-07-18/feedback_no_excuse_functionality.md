---
name: feedback-no-excuse-functionality
description: "Never use 'doesn't affect functionality' as an excuse to skip fixing visible issues"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b7741786-95b1-48f2-afcc-5232fd4db290
---

不可以用「不影響功能」當藉口來容忍可見的問題。

**Why:** 用戶明確表示不能接受。Ghost artifact 雖然不影響 build 結果，但出現在 Jenkins 頁面上就是不對的，必須修到乾淨為止。

**How to apply:** 任何用戶可見的異常（UI 上的多餘項目、錯誤的顯示、ghost data）都必須修復，不能用「功能正常」來合理化跳過。修不了要找到根因再回報，不能直接標 PASS。
