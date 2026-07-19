---
name: Flash then Reset
description: After flashing STM32 NOR Flash, must power cycle via USB relay before testing
type: feedback
---

STM32 NOR Flash 燒完後，必須用 USB Relay 重開機才能正常運作。

**Why:** NOR Flash 寫入後 MCU 需要完整 power cycle 才能正確載入新 firmware。只靠 soft reset 不夠，要斷電重啟。

**How to apply:** 每次 flash STM32 後，執行完整的 power cycle：先 off、等 1 秒、再 on（不要只用 pulse）。
```powershell
usb-relay.ps1 -Action off -Port COM3
Start-Sleep -Seconds 1
usb-relay.ps1 -Action on -Port COM3
```
`flash-and-reset-stm32.ps1` 目前用 pulse，但 Alice 偏好完整的 off → 1s → on。
