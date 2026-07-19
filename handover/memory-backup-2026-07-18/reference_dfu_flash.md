---
name: DFU Flash 指令參考
description: Reactor 50/100、Spark STM32 DFU 燒錄指令、PID 對照、Jenkins URL、已知問題
type: reference
originSessionId: 9b322bc5-e481-4941-b52c-16c7eb0ccb87
---
## STM32 DFU 燒錄指令

### Reactor 50 (PID: 0504)
```bash
dfu-util.exe -s 0x90000000:leave:mass-erase:force -d ",295d:0504" -D <firmware.bin>
```

### Reactor 100 (PID: 0502)
```bash
dfu-util.exe -s 0x90000000:leave:mass-erase:force -d ",295d:0502" -D <firmware.bin>
```

### Spark LIVE (PID: 0222)
```bash
dfu-util.exe -s 0x90000000:leave:mass-erase:force -d ",295d:0222" -D <firmware.bin>
```

### Spark 2 (PID: 0232)
```bash
dfu-util.exe -s 0x90000000:leave:mass-erase:force -d ",295d:0232" -D <firmware.bin>
```

## CDC PID（正常模式）

| 產品 | DFU PID | CDC PID |
|------|---------|---------|
| Reactor 50 | 0504 | 0507, 0506 |
| Reactor 100 | 0502 | 0506, 0507 |

## 關鍵參數說明

- `-s 0x90000000:leave:mass-erase:force` — 外部 NOR Flash 地址 + 燒完離開 DFU + 強制全片擦除
- `-d ",295d:XXXX"` — 逗號開頭表示指定 DFU mode 的 VID:PID（不加逗號無效）
- `-D <file>` — 要燒的 binary 檔案

## 工具路徑

- dfu-util: `D:\mybot\git\tool\dfu-util-0.11-binaries\win64\dfu-util.exe`
- esptool: `D:\mybot\git\tool\esptool-v4.5.1-win64\esptool.exe`

## Jenkins 下載

- URL: `https://jk-builds.positivegrid.com/jenkins/` (舊的 `jenkins.positivegrid.com` 已廢棄，DNS 不通)
- User: `alice.chan@positivegrid.com`
- Token: `D:\mybot\git\tool\.jenkins-token`
- MCU FW job: `REACTOR_AMP_FW`
- ESP32 FW job: `REACTOR_ESP32_FW`

下載範例：
```bash
curl -u "alice.chan@positivegrid.com:$(cat D:/mybot/git/tool/.jenkins-token)" -o output.bin -fSL "https://jk-builds.positivegrid.com/jenkins/job/REACTOR_AMP_FW/<build#>/artifact/Appli/Debug/<filename>.bin"
```

## Jenkins Updater Build 參數

REACTOR_FW_UPDATER_WIN / OSX 的 `MCU_BUILD` 和 `ESP_BUILD` 是 CopyArtifact 的 `BuildSelectorParameter`，API trigger 時必須用 XML 格式：
```bash
--data-urlencode "MCU_BUILD=<SpecificBuildSelector><buildNumber>148</buildNumber></SpecificBuildSelector>"
--data-urlencode "ESP_BUILD=<SpecificBuildSelector><buildNumber>48</buildNumber></SpecificBuildSelector>"
```
純數字會導致 500 ArrayIndexOutOfBoundsException。

CopyArtifact source jobs:
- `MCU_BUILD` → `REACTOR_AMP_FW` (copies `**/*.bin` to `Images/`)
- `ESP_BUILD` → `REACTOR_ESP32_FW` (copies `**/*.bin` to `Images/ESP32bin/`)

## 已知問題

- **Erase timeout**: flash chip erase 需 10-50 秒，標準 dfu-util 0.11 可能 timeout。Ken Hung 有 rebuild 過加長 timeout 的版本（在 GitLab: `desktop/SparkLiveFwUpgradeLauncher/tree/master/Import/dfu-util`）
- **Download 完的 get_status error**: `:leave` 時的正常警告，不影響燒錄結果
- **DFU suffix warning**: "Invalid DFU suffix signature" 是正常的，不影響功能

## DFU 讀取序號 (SN)

序號存在 MCU internal flash `0x0800FFE0`，32 bytes，ASCII 字串（後面補 0x00）。

### 讀取指令
```bash
# R50 (PID: 0504)
dfu-util.exe -s 0x0800FFE0:32:force -d 295d:0504 -U serial.txt

# R100 (PID: 0502)
dfu-util.exe -s 0x0800FFE0:32:force -d 295d:0502 -U serial.txt
```

### 寫入指令
```bash
# 用 srec_cat 產生 32-byte bin，再 DFU 寫入
dfu-util.exe -s 0x0800FFE0:force -d 295d:0504 -D 32_byte_serial.bin
```

參考腳本: `C:\Users\alice\Downloads\Reactor-USB-DFU-SN\Reactor-USB-DFU-SN\dfu-util-0.11-binaries\write_SN_R50.bat`

### 已知設備序號
| 設備 | 序號 |
|------|------|
| R50 (測試機) | R5011G165042170 |
| R100 (測試機) | RA012G16504827C |

## DFU 模式進入方式

1. BOOT0 拉高 + Reset
2. 或 firmware 內建 jump to bootloader 指令
3. 進入後用 `dfu-util.exe -l` 確認裝置出現
