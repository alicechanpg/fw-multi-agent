---
name: feedback_prompt_self_review
description: 每次 user 下 prompt，先自己 review 並在心裡把 prompt 精修得更清楚再執行
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5478b7d1-f3c9-4d30-ba24-bf7bb13251a4
---

每次收到 user 的 prompt，動手前先自己 review：用一句話重述「你真正要的是什麼（範圍 / 輸出 / 限制）」，把口語、簡短或含糊的 prompt 補成更精確的內部版本，再執行。目的是更貼近真實意圖、少誤解、少來回。

**Why:** user 明確要求「你都會自己 review 把 prompt 寫得更好、你聽得更懂」（2026-07-09）。

**How to apply:** prompt 進來 → 內部重述意圖與範圍 → 只有當某一項關鍵歧義會實質改變輸出時，才先點出那一項確認；其餘用合理預設直接做，不為小事反覆問。這是「精修理解後就做」，不是「停下來問」的藉口。與 [[feedback_ai_collab_mode]]、[[feedback_dont_stop_to_ask]] 一致。
