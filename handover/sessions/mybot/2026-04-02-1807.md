# Session Handover (mybot) — 2026-04-02 17:15

## Done
- **FWP-755 [Reactor 100] bypass signal path 無聲 — 已 Close**
  - 搜尋 reactor-50-100-fw bypass 機制（軟體 bypass，amp 有 root-level protection）
  - 找到 ENABLE_AKM7755_EXTERNAL_CONTROL：commit 588ad40 (Hijay, 2025-08-29)
  - DFU 燒錄 reactor-fw_Appli_DSP_BYPASS.bin 到 PID 0502 成功
  - Binary 由 Lio 在 Slack #tf-reactor-hw-noise 提供，已交給 EE
  - JIRA FWP-755 加 comment + close
- **SG-7 Smart Guitar POC — BLE auto-scan 實作**
  - Guitar #1 (COM27): flash SG-7 mode FW，advertising "SparkX" 成功（PC 可見）
  - AMP #2 (COM29): 原廠 FW 按 btn scan 失敗（status=0x1, BLE controller timing issue）
  - Root cause: SCAN_PARAM_SET_COMPLETE_EVT 裡的 start_scanning 被註解掉
  - 開新 branch `feature/SG-7-auto-scan`，改 ble.c：
    1. SCAN_PARAM_SET_COMPLETE_EVT 加 auto-scan（帶 type guard + status check）
    2. SCAN_STOP_COMPLETE_EVT 加 retry（未連上就重 scan）
  - Build + flash AMP #2 (normal mode, SG7_GUITAR_MODE=off)
  - **Auto-scan 成功！AMP 開機 0.6 秒內自動連上 SparkX**
- **環境 debug**
  - 解決 ESP-IDF MSys/Mingw 限制：PowerShell + Remove-Item Env:MSYSTEM
  - 解決 submodule 缺失：git submodule update --init --recursive
  - 解決 Python env 路徑問題：手動指定 idf5.0_py3.11_env
- **Memory 更新**
  - JIRA 查詢加入 SG board（FWP + RAD + SG）
  - 更新 feedback: migration repo 才不改 code，其他自己做到好
  - 更新 feedback: 凡事都要跟 subagent 討論

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| SG-7 CLI 指令測試 | 未做 | 送 p1/p2/ls 等指令驗證 AMP 執行 |
| SG-7 斷線重連測試 | 未做 | power cycle 一端看另一端是否自動重連 |
| SG-7 長時間穩定性 | 未做 | 30-60 分鐘無異常 |
| SG-7 code commit | 未做 | commit auto-scan 改動到 feature/SG-7-auto-scan |
| Option byte 192K | 未解決 | 確認是哪個產品/repo |

## Environment
- wifi-and-bt-core-on-esp32: `feature/SG-7-auto-scan` (未 commit，working changes)
- Guitar #1 (COM27): SG-7 mode FW (SG7_GUITAR_MODE=y), MAC 74:4d:bd:84:3c:dc
- AMP #2 (COM29): auto-scan FW (normal mode + auto-scan patch), MAC cc:8d:a2:e6:01:da
- COM26/COM28: Spark 2 PG USB (VID:0x295d)
- HOST_DEVICE_NAME: DEV_GENII (Spark 2)
- ESP-IDF: v5.0.4, Python 3.11, GCC xtensa-esp32s3-elf

## Notes for next session
### Build 指令（繞過 MSys 限制）
```powershell
powershell.exe -Command "
    Remove-Item Env:MSYSTEM -ErrorAction SilentlyContinue
    $env:IDF_PYTHON_ENV_PATH = 'C:\Users\alice\.espressif\python_env\idf5.0_py3.11_env'
    $env:IDF_PATH = 'C:\Users\alice\esp\esp-idf'
    $toolsBase = 'C:\Users\alice\.espressif\tools'
    $env:PATH = @(
        \"$toolsBase\xtensa-esp32s3-elf\esp-2022r1-11.2.0\xtensa-esp32s3-elf\bin\",
        \"$toolsBase\cmake\3.24.0\bin\",
        \"$toolsBase\ninja\1.10.2\",
        \"$toolsBase\ccache\4.6.2\ccache-4.6.2-windows-x86_64\",
        'C:\Users\alice\.espressif\python_env\idf5.0_py3.11_env\Scripts',
        'C:\Users\alice\esp\esp-idf\tools',
        $env:PATH
    ) -join ';'
    Set-Location 'D:\mybot\git\wifi-and-bt-core-on-esp32'
    python $env:IDF_PATH\tools\idf.py build
"
```

### Flash 指令
```bash
# Guitar #1 (SG7 mode)
esptool.exe -p COM27 -b 460800 --chip esp32s3 write_flash --flash_mode dio --flash_size 4MB --flash_freq 80m 0x0 build/bootloader/bootloader.bin 0x8000 build/partition_table/partition-table.bin 0xd000 build/ota_data_initial.bin 0x10000 build/wifi_and_bt_core_on_esp32.bin

# AMP #2 (normal mode + auto-scan)
esptool.exe -p COM29 -b 460800 --chip esp32s3 write_flash ...（同上）
```

### 兩台 FW 不同！
- Guitar #1: sdkconfig CONFIG_SG7_GUITAR_MODE=y → BLE_SG7_GUITAR (GATTS only)
- AMP #2: sdkconfig CONFIG_SG7_GUITAR_MODE=off → BLE_GATTS_GATTC (normal mode + auto-scan)
- 切換 build target 要改 sdkconfig 再 fullclean + build
