---
name: Reactor 50/100 ESP32 EN pin 由 STM32 控制 — 燒錄時序
description: ESP32 EN 由 STM32 boot 後拉 high；STM32 cold boot 後是燒 ESP32 的時序窗，app mode 跑久了再燒會 PermissionError
type: reference
originSessionId: 35cd0476-617e-42bb-bde4-9473c38909e6
---
## Hardware 事實

Reactor 50/100 的 **ESP32 EN pin 由 STM32 控制**。STM32 boot 後才把 EN 拉 high，ESP32 才通電 enumerate（USB JTAG, VID 0x303A）。

## 燒 ESP32 的 timing

| 情境 | 結果 |
|------|------|
| ✅ STM32 cold boot 後立刻燒（COM enumerate 後 ~數秒內） | 成功 |
| ❌ STM32 app mode 跑久了再燒 | `PermissionError(13, '裝置無法執行命令')` 中途斷（曾在 62% fail） |

推測：STM32 firmware active 時跟 ESP32 SPI/IPC 通訊，干擾 USB JTAG。

## 正確 baseline restore 順序

1. STLink 燒 STM32：`flash-and-reset-stm32.ps1 -BinFile ...reactor50-fw-X.X.X.X.bin`（內含 relay pulse 200ms reset）
2. Relay ON 通電 → STM32 cold boot → 拉 high ESP32 EN → COM19 enumerate
3. 等 ~2 秒，立刻 esptool 燒 ESP32（趁時序窗）

## 錯誤順序

- 在 device app mode 跑了一陣子之後才燒 ESP32 → 高機率 fail
- 正解：先 reset device → 立刻燒
