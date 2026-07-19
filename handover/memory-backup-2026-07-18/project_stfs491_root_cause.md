---
name: STFS-491 Root Cause (Source of Truth)
description: Spark MINI Windows 25H2 firmware update 失敗的 3 個獨立 root cause，每個都有 file:line 證據。所有分析必須基於此，不可推測。
type: project
originSessionId: 96c15cdc-a1a3-4ab9-93a5-dd71363036c3
---
## STFS-491: Spark MINI Win 25H2 FW Update 失敗

**Why:** Windows 25H2 改了 MidiSrv (加 UMP 協定) + usbaudio2.sys (嚴格 descriptor 解析)，觸發 Desktop App deadlock + Bootloader enumerate 失敗。同時發現一個 platform-agnostic 的 DMA latent bug。

**How to apply:** 討論 STFS-491 時，必須區分 3 個獨立 root cause，不可混為一談。每個結論都要對照下方證據欄位。

---

### Root Cause #1: Desktop App deadlock（Windows 25H2 specific）

Win 25H2 MidiSrv 行為改變 → 5 條 deadlock 路徑：

| ID | Deadlock 路徑 | 證據 (repo: SparkFwUpgradeLauncher) | Fix commit |
|----|--------------|-------------------------------------|------------|
| P1 | midiInClose retry 不夠（25H2 release 從 ~30ms→~600ms） | JUCE `juce_win32_Midi.cpp` | `79392d03` |
| P2 | sendMessageNow MHDR_DONE 不被 set → 永久 hang | JUCE `juce_win32_Midi.cpp` | `e57b2b5b` |
| B1 | MIDI callback 內 stop() → self-join deadlock | `PGUsbMidiDeviceFinder.cpp:77-78` | `c7eea3e` |
| P4 | callFunctionOnMessageThread + MidiSrv LPC stall → mutual deadlock | `PGUsbMidiDeviceFinder.cpp` 6 處 | `fd837a3` |
| P3/P5/P6 | message thread 做 blocking MIDI I/O → GUI freeze | `ConnectedAppState.cpp:48`, `PGDeviceManager.cpp:30` | `92e7b4c`, `598ae04`, `e9db692`, `04caf8f` |

**Mac 不受影響原因：** CoreMIDI 沒有 MidiSrv/UMP gateway 層。

### Root Cause #2: Bootloader USB descriptor 不合規（Windows 25H2 specific）

| ID | 問題 | 證據 (repo: g1x-bootloader) | Fix commit |
|----|------|----------------------------|------------|
| 2a | wTotalLength=65（應為 37），25H2 嚴格解析 → midiInGetNumDevs() hang | `usbd_midi_core.c:481` | `5438843` |
| 2b | 不回覆 UMP Discovery Request → MidiSrv deadlock | `usbd_midi_core.c:1001-1055` | `1a7b3c9` |
| 2c | 沒有 bulk IN 資料 → 25H2 midiInOpen() block | `usbd_midi_core.c:718-723` | `9c5bd5d` |
| 2d | 開了 3 個未宣告的 endpoint → EP table 錯亂 | `usbd_midi_core.c:691-705` | `ffe0819` |

**Mac 不受影響原因：** 舊版 Windows 和 Mac 對 descriptor 錯誤寬容，25H2 改為嚴格。

### Root Cause #3: DMA/stack corruption（platform-agnostic latent bug）

- APP JUMPTOBOOTLOADER handler 沒停 I2S DMA — `jamup_hwcontroller.cpp:1769-1796`
- 只停了 TIM5 + USB，沒停 DMA1_Stream3 / SPI2 / SPI3
- v1.11.2.75 的 DMA buffer `i2s2_adc_buf2` (static in `dma_dsp.c:79`) 落在 `0x200057C4`
- Bootloader MSP = `0x200057D8`，距離僅 20 bytes → DMA 寫壞 stack → HardFault
- B9 fix: bootloader SystemInit() reset DMA/I2S — `system_stm32f4xx.c:230-244`, commit `4d42bfd`

**與 Windows 版本無關**，debug 25H2 時附帶發現。

---

### 影響矩陣

| Root Cause | Mac | Win 25H2 前 | Win 25H2 |
|------------|-----|-------------|----------|
| #1 Desktop App deadlock | 不影響 | 不影響 | **crash** |
| #2 Bootloader descriptor | 不影響 | 不影響 | **crash** |
| #3 DMA stack corruption | 潛在風險 | 潛在風險 | 潛在風險 |

### GD32 vs STM32 MSP 差異

- GD32 build (feature/spark-10-develop-gd): MSP = 0x200057D8
- STM32 build (feature/spark-10-develop): MSP = 0x20004720
- 兩個 branch source code 完全相同（git diff 只有 ewp 的 chip selection 2 行）
- 差異原因待驗證：需 clean build 兩個 config 比較 .map file
- ICF file 相同：`stm32f417xG_bootloader.icf`, CSTACK=0x2000, RAM 0x20000000-0x2001FFFF
