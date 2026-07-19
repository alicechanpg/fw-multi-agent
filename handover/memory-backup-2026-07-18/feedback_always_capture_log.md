---
name: Always Capture Log After Flash
description: Always start serial log capture after flash+power cycle, don't ask
type: feedback
---

Flash + power cycle 後一律自動抓 log，不要問。

**Why:** 每次燒完都要看 log 驗證，問一次就是浪費時間。

**How to apply:** flash-and-reset 完成後，直接啟動 serial logger（COM4, 921600, 60秒），不需確認。
