# ESP32 Boot Log Pattern

ESP32-S3 (pg-reactor-esp32-wifi-bt) 開機 log pattern。

> **注意**: ESP32 flash 和 serial 共用 COM19，flash 後重啟的瞬間 log 無法完整捕獲。
> 完整 boot log 需要：flash 完成 → 等待啟動 → 手動 reset ESP32 → 從頭抓取。

## 已知的 Boot 輸出 (從 ESP-IDF 標準格式)

ESP-IDF boot log 帶有 ANSI color code，格式：`[顏色碼]TAG (timestamp) message[0m`

### Phase 1: Bootloader
```
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:...
entry ...
```

### Phase 2: Partition & App Load
```
I (XX) boot: ESP-IDF vX.X
I (XX) boot: chip revision: vX.X
I (XX) boot: End of partition table
I (XX) boot: Loaded app from partition at offset 0x10000
```

### Phase 3: Application Start
```
I (XX) wifi: wifi driver task: ...
I (XX) wifi: wifi firmware version: ...
```

### 已觀察到的開機 log (2026-02-25)
```
SPIWP:0xee
I (99) boot: End of partition table
pop_hwcmd_result_from_que fail         ← SPI queue 未就緒
```

## MUST_HAVE (待完善)

目前 ESP32 完整 boot log 尚未捕獲。以下為預期應出現的訊息：

```
boot: ESP-IDF                          ← ESP-IDF 版本
boot: End of partition table            ← Partition 載入完成
wifi driver task                        ← WiFi driver 啟動
BLE init                                ← BLE 初始化
SPI slave init                          ← SPI slave 準備接收 STM32 命令
```

## ERROR_SIGNATURE
```regex
(?i)guru\s*meditation
(?i)core\s*\d+\s*panic
Brownout detector was triggered
(?i)abort\(\)
(?i)backtrace:
(?i)assert failed
```

## `pop_hwcmd_result_from_que fail` 分析

**來源**: ESP32 WiFi/BT 子系統的硬體命令佇列
**情境**: 開機時 SPI 通訊尚未建立，STM32 端的命令佇列查詢失敗
**嚴重性**: 低 — 開機暫態，SPI 通訊建立後消失
**需要注意**: 如果在正常運行時持續出現，則表示 SPI 通訊有問題

## 待辦

- [ ] 獨立捕獲 ESP32 完整 boot log (不經過 flash)
- [ ] 記錄 WiFi provisioning 流程 log
- [ ] 記錄 BLE 配對流程 log
- [ ] 記錄 OTA 更新流程 log
- [ ] 記錄 SPI 通訊建立流程 log
