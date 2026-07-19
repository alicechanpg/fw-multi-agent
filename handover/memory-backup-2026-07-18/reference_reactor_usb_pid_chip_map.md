---
name: reference-reactor-usb-pid-chip-map
description: Reactor 50 PID_0503 USB Audio 是 Actions BT Audio chip 產生的，不是 STM32 MCU
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7b26a649-6ac4-49d5-8d14-003107877db9
---

Reactor 50 的 USB 設備由不同晶片產生：

| PID | 設備 | 晶片 |
|-----|------|------|
| 0503 | Reactor 50 USB Audio (composite: Audio + HID) | **Actions BT Audio chip**（不是 MCU！） |
| 0506 | Reactor 50 CDC COM port（舊 FW） | STM32 MCU |
| 0507 | Reactor 50 CDC COM port（新 FW 升級後） | STM32 MCU |
| 0504 | Reactor 50 DFU | STM32 MCU |

**How to apply:** PID_0503 active 不代表 STM32 MCU 活著。判斷 STM32 是否正常運行要看 CDC COM port (PID_0506/0507) 是否出現。

相關：[[reference_reactor_updater_bundle]]
