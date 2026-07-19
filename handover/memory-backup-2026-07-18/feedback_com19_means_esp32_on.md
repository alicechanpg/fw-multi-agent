---
name: COM19 出現 = ESP32 已開機
description: COM19 USB serial port 出現在系統就代表 ESP32 已通電開機，不需要額外確認
type: feedback
originSessionId: 93dd3b66-6914-4739-b251-dd3b8db1150f
---
COM19 出現在 `Get-WmiObject Win32_SerialPort` 結果中，就代表 ESP32 已經通電開機了。不需要再等或懷疑 ESP32 是否啟動。

**Why:** ESP32 的 USB-UART bridge (CP2102/CH340) 只有在 ESP32 板子通電時才會被 Windows 列舉為 COM port。如果 COM19 存在，ESP32 一定已經跑起來了。

**How to apply:** 看到 COM19 列在 COM port 清單中，就確認 ESP32 已開機。如果 serial 讀不到 log 輸出但 port 存在，代表 ESP32 已跑完開機/連線流程，不是還沒開機。
