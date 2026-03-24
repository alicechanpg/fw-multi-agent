# ESP32 Development Tools

ESP32 韌體開發工具，使用 ESP-IDF 5.0 框架。

## 專案資訊

| 項目 | 值 |
|------|-----|
| **專案路徑** | `D:\mybot\git\pg-reactor-esp32-wifi-bt\` |
| **Build 輸出** | `D:\mybot\git\pg-reactor-esp32-wifi-bt\build\` |
| **ESP-IDF** | `C:\Users\alice\esp\esp-idf\` |
| **Python 環境** | `C:\Users\alice\.espressif\python_env\idf5.0_py3.11_env\` |
| **晶片** | ESP32-S3 |

## 編譯 (build-esp32.ps1)

### 基本用法
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-esp32.ps1
```

### Clean Build
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-esp32.ps1 -Clean
```

### 參數
| 參數 | 說明 |
|------|------|
| `-Clean` | 執行 fullclean 後再 build |

### 輸出檔案
- `build\bootloader\bootloader.bin` - Bootloader
- `build\wifi_and_bt_core_on_esp32.bin` - 主程式
- `build\partition_table\partition-table.bin` - Partition table
- `build\ota_data_initial.bin` - OTA 資料

### 注意事項
- Script 會自動清除 MSYS/MinGW 環境變數，避免衝突
- 如果 build 失敗，會自動嘗試 fullclean 再 rebuild

## 燒錄 (flash-esp32.ps1)

### 基本用法 (自動偵測 Port)
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-esp32.ps1
```

### 指定 Port
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-esp32.ps1 -Port COM19
```

### 參數
| 參數 | 預設值 | 說明 |
|------|--------|------|
| `-Port` | (自動偵測) | COM port |

### Flash 參數
| 項目 | 值 |
|------|-----|
| Baud rate | 460800 |
| Flash mode | DIO |
| Flash freq | 80MHz |
| Flash size | 4MB |

### Flash 地址配置
| 檔案 | 地址 |
|------|------|
| bootloader.bin | 0x0 |
| partition-table.bin | 0x8000 |
| ota_data_initial.bin | 0xd000 |
| wifi_and_bt_core_on_esp32.bin | 0x10000 |

### 自動偵測邏輯
使用 Python serial 套件，偵測 VID = 0x303a (Espressif) 的裝置。

## 常見問題

### Build 失敗：MSYS 環境衝突
**症狀**：錯誤訊息提到 MSYS 或 MinGW

**解決**：Script 已自動處理，如果還是失敗，手動執行：
```powershell
$env:MSYSTEM = $null
$env:MINGW_PREFIX = $null
```

### Build 失敗：Project mismatch
**症狀**：CMake 報錯說專案不匹配

**解決**：使用 `-Clean` 參數重新編譯

### 燒錄失敗：找不到 ESP32
**症狀**：ESP32 not found

**解決**：
1. 確認 USB 已連接
2. 確認驅動程式已安裝
3. 執行 `list-ports.ps1` 確認 port
4. 手動指定 `-Port` 參數

### 燒錄失敗：檔案不存在
**症狀**：Bootloader not found / App not found

**解決**：先執行 `build-esp32.ps1` 編譯
