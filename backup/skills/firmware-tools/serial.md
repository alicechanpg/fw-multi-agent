# Serial Tools

Serial port 監聽與記錄工具。

## 監聽 (serial-logger.ps1)

### 基本用法
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\serial-logger.ps1 `
    -PortName COM4 `
    -BaudRate 921600 `
    -LogFile D:\mybot\git\tool\logs\output.txt
```

### 參數
| 參數 | 必填 | 說明 |
|------|------|------|
| `-PortName` | 是 | COM port (例: COM4) |
| `-BaudRate` | 是 | Baud rate (例: 115200, 921600) |
| `-LogFile` | 是 | Log 檔案路徑 |
| `-Title` | 否 | 視窗標題 |

### 預設配置

| 裝置 | Port | Baud Rate | 用途 |
|------|------|-----------|------|
| **STM32** | COM4 | 921600 | Debug log |
| **ESP32** | COM19 | 115200 | Debug log |

### STM32 監聽
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\serial-logger.ps1 `
    -PortName COM4 `
    -BaudRate 921600 `
    -LogFile D:\mybot\git\tool\logs\stm32_log.txt `
    -Title "STM32-LOG-COM4"
```

### ESP32 監聽
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\serial-logger.ps1 `
    -PortName COM19 `
    -BaudRate 115200 `
    -LogFile D:\mybot\git\tool\logs\esp32_log.txt `
    -Title "ESP32-LOG-COM19"
```

### Log 格式
```
[2024-01-15 14:30:45.123] Hello from STM32
[2024-01-15 14:30:45.456] Sensor reading: 123
```

每行包含：
- 時間戳記 (yyyy-MM-dd HH:mm:ss.fff)
- 原始 Serial 資料

### Serial 參數
| 項目 | 值 |
|------|-----|
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Read timeout | 1000ms |

## 列出 Ports (list-ports.ps1)

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

### 過濾條件
列出符合以下任一條件的裝置：
- 名稱包含 "COM"
- 名稱包含 "Serial"
- 名稱包含 "CH340"

## 常見問題

### Port 被占用
**症狀**：Cannot open port

**解決**：
1. 關閉其他使用該 port 的程式
2. 確認 port 號碼正確

### 亂碼
**症狀**：Log 顯示亂碼

**解決**：
1. 確認 baud rate 正確
2. 確認裝置端 baud rate 設定一致

### 找不到 Port
**症狀**：Port not found

**解決**：
1. 執行 `list-ports.ps1` 確認 port
2. 確認 USB 已連接
3. 確認驅動程式已安裝
