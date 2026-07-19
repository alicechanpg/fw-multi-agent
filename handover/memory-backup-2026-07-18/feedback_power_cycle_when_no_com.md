---
name: feedback-power-cycle-when-no-com
description: COM port 找不到時自動用 USB Relay power cycle，不要問用戶手動上電
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7b26a649-6ac4-49d5-8d14-003107877db9
---

找不到 ESP32 COM port 時，自動用 USB Relay (COM3) 做 power cycle，不要停下來問用戶手動上電。

**Why:** Reactor 的 ESP32 EN pin 由 STM32 控制，STM32 開機後 ESP32 才會出現。USB Relay 就是用來做 power cycle 的。

**How to apply:** flash ESP32 前如果 COM19 不在，先跑 USB Relay power cycle → 等 COM19 出現 → 再 flash。參考 [[reference_usb_relay_pulse_off_state]] 和 [[feedback_check_voltage_after_power_cycle]]。
