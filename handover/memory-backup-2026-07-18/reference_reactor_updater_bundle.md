---
name: ReactorFwUpdater bundle 結構與 PID 變化
description: Updater 的 Images 資料夾結構、bundled fw 版本來源、Updater 完成後 device PID 變化
type: reference
originSessionId: a24b5d2f-3d02-4ae1-9f2c-89e98777117e
---
## Updater build artefact 結構

`D:\mybot\git\ReactorFwUpdater\build-{reactor50|r100-v2|r100-v3}\Reactor_{50|100}_Firmware_Updater_artefacts\Release\`:

```
Reactor 50 Firmware Updater.exe
dfu-util.exe
esptool.exe
Images/
  mcu-fw.bin                          ← Updater 真正用來燒 STM32 的 bin
  reactor100-fw-0.1.4.123.bin         ← legacy/leftover，build script 留下不影響使用
  version.txt                         ← STM32 版本，例如 "0.1.4.123"
  ESP32bin/
    bootloader.bin
    partition-table.bin
    ota_data_initial.bin
    esp32-fw.bin                      ← Updater 真正用來燒 ESP32 的 bin
    esp32-fw-reactor100-rev656.bin    ← legacy/leftover
    version.txt                       ← ESP32 版本，例如 "656"
```

## R50 build 的 mcu-fw.bin 是 R50 版

**驗證 (2026-04-29)**：build-reactor50 內 `Images/mcu-fw.bin` 跟 `Downloads/reactor50-fw-0.1.4.123.bin` `cmp` 完全相同 → 雖然旁邊有 `reactor100-fw-0.1.4.123.bin`，那是 leftover，**Updater 燒的是 R50 fw**。

## Reactor CDC PID

| PID | 模式 | 對應 fw |
|-----|------|--------|
| `295D:0506` | App mode (CDC) | 舊 fw（FWP-664-rebase debug build 0.1.0.0 還用 0506） |
| `295D:0507` | App mode (CDC) | 新 release fw 0.1.4.123 之後改用 0507 |
| `295D:0504` | DFU mode | 進 DFU 時切換到此 PID |
| `295D:0503` | USB Audio | R50 audio class device，永遠在（不隨 fw 升級變化） |

ReactorFwUpdater 的 `ProductConfig.hpp` `cdcPid` 是 comma-separated 的 hex PID list，0506 跟 0507 都認得。Update 完成後 PID 切換是預期行為。

## Update flow（Updater drive）

1. Updater detect device (CDC PID 0506/0507)
2. SysEx CDC `cmd 0x7F 0x10 0x01` → STM32 進 DFU mode (PID 0504)
3. dfu-util 燒 mcu-fw.bin to external NOR @ 0x90000000
4. STM32 reboot → bootloader 0.1.0.39 → jump to new app
5. STM32 cold boot 後 ESP32 EN 起來
6. esptool 燒 ESP32 (COM19) 到 ota_0 partition @ 0x10000
7. Final reboot → device 帶新 PID enumerate

## Updater log 位置

JUCE app 預設 log 路徑為 `%APPDATA%\PositiveGrid\` 或 working dir，**只在 update 跑過後才會建** — 想用就先跑一次 update。
