---
name: Spark Gen 1 與 Reactor 是不同產品線
description: Spark 40/MINI/GO/NEO (Gen 1) 跟 Reactor 50/100 在 chip、架構、通訊協定都不同，不要混用技術討論
type: project
originSessionId: 9a27a1a5-3206-491e-a680-0898219b3850
---
**Spark Gen 1** (Spark 40 / MINI / GO / NEO) 與 **Reactor** (50 / 100) 是完全不同產品線，不可混用技術論述：

| 面向 | Spark Gen 1 | Reactor 50/100 |
|------|------------|---------------|
| Chip 組合 | 不同 | STM32 MCU + ESP32 (WiFi/BT) |
| Updater cmd 傳輸 | **USB-MIDI class (SysEx)** | **CDC virtual serial（載 SysEx）+ DFU 燒錄** |
| USB Driver path | WinUSB (ADFU mode) | WinUSB (DFU mode) |
| Updater framework | JUCE 7 (SparkFwUpgradeLauncher) | JUCE 8 (ReactorFwUpdater) |
| Updater 用 USB-MIDI? | ✅ 用（juce::MidiInput） | ❌ 不用（SysEx over CDC，不經 USB-MIDI class） |
| 裝置有 MIDI 功能? | ✅ | ✅ **有**（UART serial MIDI：`MidiCmdHandler.cpp` MIDI CC 控 FX、`SerialMIDI.cpp` 走 UART1） |

**Why**: 2026-04-21 Alice 明確糾正 — STFS-491 的 JUCE 7 MIDI deadlock patch 屬於 Spark Gen 1，不能當 Reactor updater 架構修法的先例引用。兩者雖然都掛 JUCE，但協定 / chip / 架構都不同。
2026-07-18 Alice 再糾正：之前寫「Reactor 不走 MIDI」過度簡化 — 正確是 **updater cmd 走 CDC + DFU**（`ReactorFwUpdater\Doc\architecture.md:40,120` — CDC 295D:0506/0507 載 SysEx、DFU 燒錄），但 **Reactor 裝置本身有 MIDI**（UART serial MIDI，非 USB-MIDI class）。「不走 MIDI」只對 updater 的 USB 傳輸層成立。

**How to apply**:
- 討論 Reactor updater 時，不要引用 Spark 系列的 MIDI / MidiInput / JUCE 7 相關 patch 作為先例
- STFS-491 (JUCE MIDI deadlock) 對 Reactor 無參考價值
- Spark 系列 Windows driver (INF / Co-installer) 問題跟 Reactor 走不同 path，也不能直接類比
- 平台層共通問題（Win 25H2 廢 Co-installer、UAC、signing）仍然兩者都適用 — 這層是 platform 不是產品
