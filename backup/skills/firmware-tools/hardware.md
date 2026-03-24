# Hardware Control Tools

硬體控制工具，包含 USB Relay 和 COM Port 管理。

## USB Relay (usb-relay.ps1)

控制 LCUS-1 USB Relay 模組，用於遠端重置 MCU。

### 裝置資訊

| 項目 | 值 |
|------|-----|
| **型號** | LCUS-1 USB Relay |
| **預設 Port** | COM3 |
| **Baud rate** | 9600 |
| **協議** | A0 01 XX CS |

### 開啟 Relay
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action on
```

### 關閉 Relay
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action off
```

### 脈衝 (Reset 用)
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action pulse
```

### 自訂參數
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 `
    -Action pulse `
    -Port COM3 `
    -PulseMs 200
```

### 參數
| 參數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `-Action` | 是 | - | on / off / pulse |
| `-Port` | 否 | COM3 | COM port |
| `-PulseMs` | 否 | 200 | 脈衝時間 (ms)，僅 pulse 使用 |

### LCUS-1 協議

| 動作 | 命令 (Hex) |
|------|------------|
| ON | A0 01 01 A2 |
| OFF | A0 01 00 A1 |

格式：`A0 01 XX CS`
- XX = 01 (ON) / 00 (OFF)
- CS = Checksum (A0 + 01 + XX)

### 應用場景

#### STM32 遠端重置
Relay 連接 STM32 的 RESET 腳位：
```powershell
# 燒錄後自動重置
.\flash-and-reset-stm32.ps1

# 單獨重置
.\usb-relay.ps1 -Action pulse -PulseMs 200
```

#### 電源控制
Relay 控制電源開關：
```powershell
# 開機
.\usb-relay.ps1 -Action on

# 關機
.\usb-relay.ps1 -Action off

# 重開機
.\usb-relay.ps1 -Action pulse -PulseMs 1000
```

## COM Port 列表 (list-ports.ps1)

### 用法
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\list-ports.ps1
```

### 輸出範例
```
Name                                    DeviceID
----                                    --------
USB Serial Port (COM4)                  USB\VID_0483&PID_5740\...
Silicon Labs CP210x (COM19)             USB\VID_303A&PID_1001\...
USB-SERIAL CH340 (COM3)                 USB\VID_1A86&PID_7523\...
```

### 常見裝置 VID/PID

| 裝置 | VID | PID | 說明 |
|------|-----|-----|------|
| ESP32-S3 | 303A | 1001 | Espressif |
| STM32 VCP | 0483 | 5740 | ST-Link Virtual COM |
| CH340 | 1A86 | 7523 | USB Relay / 一般 USB Serial |

## 硬體配置總覽

| 裝置 | Port | 用途 | 備註 |
|------|------|------|------|
| **STM32** | COM4 | Debug Serial | 921600 baud |
| **ESP32** | COM19 | Debug Serial | 115200 baud |
| **USB Relay** | COM3 | MCU Reset | 9600 baud |
| **ST-Link** | - | SWD 燒錄 | 非 Serial |

## 常見問題

### Relay 不動作
**症狀**：命令執行但 Relay 沒反應

**解決**：
1. 確認 COM port 正確（執行 `list-ports.ps1`）
2. 確認 Relay 模組有供電（LED 應亮起）
3. 確認 USB 線連接正常

### 找不到 COM Port
**症狀**：list-ports.ps1 沒顯示預期的裝置

**解決**：
1. 重新插拔 USB
2. 安裝對應驅動程式：
   - CH340: [CH340 Driver](https://www.wch.cn/download/CH341SER_EXE.html)
   - CP210x: [Silicon Labs Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
3. 檢查 Device Manager

### Port 被占用
**症狀**：無法開啟 port

**解決**：
1. 關閉其他使用該 port 的程式
2. 關閉 serial-logger.ps1 視窗
3. 重新插拔 USB
