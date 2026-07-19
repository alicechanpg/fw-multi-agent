---
name: feedback-check-voltage-after-power-cycle
description: Always verify power state (USB devices / voltage) after relay power cycle
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b7741786-95b1-48f2-afcc-5232fd4db290
---

做 power cycle 之後必須檢查電壓/通電狀態。

**Why:** 用戶明確要求。relay 操作後不能假設成功，要實際驗證 Reactor 是否通電。

**How to apply:** 每次執行 USB Relay power cycle 後，立刻用 `Get-PnpDevice` 檢查 Reactor USB 裝置是否出現（Reactor USB Audio、CDC COM port），確認通電才能回報完成。
