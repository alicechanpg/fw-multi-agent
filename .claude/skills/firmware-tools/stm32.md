# STM32 Development Tools

STM32 韌體開發工具，使用 STM32CubeIDE headless build。

## 專案資訊

| 項目 | 值 |
|------|-----|
| **專案路徑 (舊)** | `D:\mybot\git\reactor-fw\` |
| **專案路徑 (新)** | `D:\mybot\git\reactor-50-100-fw\` |
| **Workspace** | `D:\mybot\git\tool\stm32-workspace\` |
| **STM32CubeIDE** | `C:\ST\STM32CubeIDE_1.16.1\` |
| **Binary 輸出** | `Appli\Debug\reactor-fw_Appli.bin` |

## 編譯 (build-stm32.ps1)

### 基本用法
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-stm32.ps1
```

### Clean Build
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\build-stm32.ps1 -Clean
```

### 參數
| 參數 | 說明 |
|------|------|
| `-Clean` | 執行 cleanBuild 而非 incremental build |

### Build 輸出
- Binary: `D:\mybot\git\reactor-fw\Appli\Debug\reactor-fw_Appli.bin`
- 會顯示 binary 大小和修改時間

### 注意事項
- 使用 STM32CubeIDE headless mode
- 會自動 import 專案到 workspace
- 第一次 build 可能較慢（需要 import）

## 燒錄 (flash-and-reset-stm32.ps1)

### 基本用法
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-and-reset-stm32.ps1
```

### 自訂參數
```powershell
powershell -ExecutionPolicy Bypass -File D:\mybot\git\tool\flash-and-reset-stm32.ps1 `
    -BinFile "D:\mybot\git\reactor-50-100-fw\Appli\Debug\reactor-fw_Appli.bin" `
    -RelayPort COM3 `
    -ResetPulseMs 200
```

### 參數
| 參數 | 預設值 | 說明 |
|------|--------|------|
| `-BinFile` | `reactor-50-100-fw\...\reactor-fw_Appli.bin` | Firmware 檔案 |
| `-RelayPort` | COM3 | USB Relay 的 COM port |
| `-ResetPulseMs` | 200 | Reset 脈衝時間 (ms) |

### 燒錄流程
1. **Flash** - 使用 STM32_Programmer_CLI 透過 SWD 燒錄
2. **Reset** - 透過 USB Relay 發送 pulse 重置 MCU

### Flash 配置
| 項目 | 值 |
|------|-----|
| 介面 | SWD |
| AP | 1 |
| Mode | UR (Under Reset) |
| External Loader | `reactor-fw_ExtMemLoader.stldr` |
| Flash 地址 | 0x90000000 (External Flash) |

### External Loader 路徑
```
C:\Users\alice\Downloads\reactor-fw\reactor-fw\ExtMemLoader\Debug\reactor-fw_ExtMemLoader.stldr
```

## 常見問題

### Build 失敗：CubeIDE 找不到
**症狀**：STM32CubeIDE not found

**解決**：確認 STM32CubeIDE 安裝在 `C:\ST\STM32CubeIDE_1.16.1\`

### Build 成功但 Binary 沒更新
**症狀**：Binary unchanged

**可能原因**：
1. 沒有程式碼變更
2. Build 有錯誤但 exit code = 0

**解決**：使用 `-Clean` 參數

### 燒錄失敗：Programmer 找不到
**症狀**：STM32_Programmer_CLI not found

**解決**：確認 STM32CubeIDE 安裝包含 CubeProgrammer plugin

### 燒錄失敗：External Loader 找不到
**症狀**：External loader not found

**解決**：確認 ExtMemLoader 已編譯並放在正確位置

### 燒錄成功但沒重置
**症狀**：Flash completed 但 MCU 沒重開

**解決**：
1. 確認 USB Relay 連接在 COM3
2. 確認 Relay 有供電
3. 手動重置或調整 `-ResetPulseMs`
