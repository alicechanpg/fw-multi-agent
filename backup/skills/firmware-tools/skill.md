# Firmware Development Tools

ESP32 / STM32 韌體開發工具集，包含編譯、燒錄、Serial 監聽、硬體控制等功能。

## 工具總覽

| 功能 | Script | 說明 |
|------|--------|------|
| **ESP32 編譯** | `build-esp32.ps1` | 使用 ESP-IDF 編譯 |
| **ESP32 燒錄** | `flash-esp32.ps1` | 使用 esptool 燒錄 |
| **STM32 編譯** | `build-stm32.ps1` | 使用 STM32CubeIDE headless build |
| **STM32 燒錄** | `flash-and-reset-stm32.ps1` | 燒錄 + USB Relay 重置 |
| **一鍵全部** | `build-and-flash-all.ps1` | Build + Flash 全部平台 |
| **COM Port** | `list-ports.ps1` | 列出所有 COM ports |
| **Serial Log** | `serial-logger.ps1` | 監聽 Serial 並記錄 log |
| **USB Relay** | `usb-relay.ps1` | LCUS-1 Relay 控制 |

## 路徑

```
TOOL_DIR = D:\mybot\git\tool\
ESP32_PROJECT = D:\mybot\git\pg-reactor-esp32-wifi-bt\
STM32_PROJECT = D:\mybot\git\reactor-fw\
STM32_PROJECT_NEW = D:\mybot\git\reactor-50-100-fw\
```

## 使用場景

### 開發 ESP32
```powershell
# 編譯
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-esp32.ps1

# 編譯 (clean build)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-esp32.ps1 -Clean

# 燒錄 (自動偵測 port)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-esp32.ps1

# 燒錄 (指定 port)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-esp32.ps1 -Port COM19
```

### 開發 STM32
```powershell
# 編譯
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-stm32.ps1

# 編譯 (clean build)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-stm32.ps1 -Clean

# 燒錄 + 重置
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-and-reset-stm32.ps1
```

### 一鍵 Build & Flash
```powershell
# 全部 build + flash
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-and-flash-all.ps1

# 只 ESP32
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-and-flash-all.ps1 -SkipSTM32

# 只 STM32
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-and-flash-all.ps1 -SkipESP32

# 不開 log window
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-and-flash-all.ps1 -NoLog
```

### Serial 監聽
```powershell
# 監聽 STM32 (COM4, 921600)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\serial-logger.ps1 -PortName COM4 -BaudRate 921600 -LogFile D:\mybot\git\tool\logs\stm32.txt

# 監聽 ESP32 (COM19, 115200)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\serial-logger.ps1 -PortName COM19 -BaudRate 115200 -LogFile D:\mybot\git\tool\logs\esp32.txt
```

### 硬體控制
```powershell
# 列出 COM ports
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\list-ports.ps1

# USB Relay 開
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action on -Port COM3

# USB Relay 關
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action off -Port COM3

# USB Relay 脈衝 (重置用)
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\usb-relay.ps1 -Action pulse -Port COM3 -PulseMs 200
```

## 環境需求

| 平台 | 需求 |
|------|------|
| **ESP32** | ESP-IDF 5.0+ @ `C:\Users\alice\esp\esp-idf` |
| **STM32** | STM32CubeIDE 1.16.1 @ `C:\ST\STM32CubeIDE_1.16.1` |
| **Serial** | PowerShell 5.1+, System.IO.Ports |
| **Relay** | LCUS-1 USB Relay on COM3 |

## 預設 COM Ports

| 裝置 | Port | Baud Rate |
|------|------|-----------|
| ESP32 | COM19 | 115200 |
| STM32 | COM4 | 921600 |
| USB Relay | COM3 | 9600 |

## 故障排除

### ESP32 Build 失敗
1. 確認 ESP-IDF 環境正確安裝
2. 嘗試 `-Clean` 參數重新編譯
3. 檢查 MSYS/MinGW 環境變數衝突

### STM32 Build 失敗
1. 確認 STM32CubeIDE 版本正確
2. 確認 workspace 目錄存在
3. 嘗試 `-Clean` 參數

### 燒錄失敗
1. 執行 `list-ports.ps1` 確認 COM port
2. 確認裝置已連接
3. 確認驅動程式已安裝

### Relay 不動作
1. 確認 COM3 是 LCUS-1 Relay
2. 確認 Relay 有供電
