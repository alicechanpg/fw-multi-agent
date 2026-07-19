---
name: Spark 2 firmware log patterns
description: Spark 2 firmware UART log 的關鍵 pattern，用於自動化偵測 boot/power on/power off 等事件
type: reference
originSessionId: 2b1e3496-81ac-4a60-899d-d9f9522807b0
---
## UART 配置

- Port: COM4 (STLink VCP)
- Baud: 921600
- STM32 end: UART5
- 只有 `USER_CONFIG_RUNNING_MODE = RUNNING_MODE_APP_DEBUG` 才有 log（release mode `RUNNING_MODE_APP` 無 log）

## 關鍵 log pattern

### 關機偵測

**`DataManager file operations are completed.`** — **最後一行關機訊息**

用途：判定「firmware 是否有開始/完成關機流程」的執行點。Alice 2026-04-21 指定用這行當關機執行點。

完整關機 sequence 印出順序：
```
[ ***** POWER OFF ***** ]
[POWER] receive button event, mode: 0, state: 1
bt ack : fail
DataManager file operations are completed.   ← 最後一行，之後 MCU reset
```

之後 MCU reset → bootloader reboot → 若 PWR_KEY 還按著會 auto POWER ON（adapter only 時常見）。

### 開機偵測

- `[ ***** POWER ON ***** ]` — 成功觸發開機
- `[POWER] power on check, result: 1, pwr_btn: 0` — power on check 通過（result=1 pass, pwr_btn=0 pressed）
- `[POWER] power on check, result: 0` — fail（pwr_btn 已 released 或其他 check 失敗）

### 開機完整 sequence（APP_DEBUG）

```
RUNNING_MODE : LOADER_DEBUG                    ← bootloader
Jump to APP code (4MB NOR)                     ← bootloader jump APP
RUNNING_MODE : APP_DEBUG                       ← firmware 啟動
fw_version: X.Y.Z.N                            ← version 資訊
SDRAM initialized to 0 using memset, total bytes cleared: 33554432
[tick] HW check: ...
[tick] Charger init complete
[AUTO] result: X, standby: 15, shutdown: 60
[ ***** POWER SUPPLY : Adapter only ***** ]   ← 或 Battery / Adapter+Battery
[tick][POWER] power on check, result: 1, pwr_btn: 0, temp:-99.0, vol: 2880, vbus:20160
[ ***** POWER ON ***** ]
[POWER] receive button event, mode: 1, state: 1
transmit_registers: write X reg done
[Audio] audio chips init are done.
bt version : X.XX_XXXXXXXXXX
bt mac : XX XX XX XX XX XX
```

### 其他事件

- `[ ***** POWER SUPPLY : Adapter only ***** ]` — 純 adapter 供電
- `[ ***** ENABLE CHARGING ***** ]` — 開始充電
- `A illegal app bin length found. sd_nand_fw_info.length = 0` — bootloader check（警告但不影響 jump）

## 注意事項

- **MCU reset 時 UART buffer 會 drop**，短時間內的 log 可能抓不到
- Adapter only 無法真正關機 — POWER OFF 後 MCU reset 會被 latch 重新 boot
- 要 clean shutdown 需接電池或斷 adapter
