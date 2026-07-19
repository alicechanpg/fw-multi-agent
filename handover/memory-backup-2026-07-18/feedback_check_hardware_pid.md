---
name: 不要停下來問硬體狀態，用 PID/VID 確認
description: 硬體是否接好不要問用戶，用 Get-PnpDevice 或 python serial.tools 查 PID/VID 自己確認
type: feedback
originSessionId: 133d04a5-1220-4481-ba56-08d42f7297e4
---
不要停下來問用戶「硬體接好了嗎」，自己用工具確認。

**Why:** 用戶已經說過接好了，反覆問浪費時間。硬體狀態可以程式化確認。

**How to apply:**
- 用 `Get-PnpDevice -Class Ports` 查 COM port 和 PID/VID
- 用 `python -c "import serial.tools.list_ports; ..."` 查特定 VID
- USB Relay: COM3
- STLink: COM50
- ESP32: COM19
- 確認完直接做，不要停下來問
