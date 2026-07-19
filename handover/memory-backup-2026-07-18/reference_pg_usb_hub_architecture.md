---
name: reference-pg-usb-hub-architecture
description: Spark2/EDGE/LIVE + Reactor50/100 共同 USB hub 架構 — hub 下有 MCU/ESP32/BT Audio；BT Audio 獨立且 PC 供電(不隨 MCU 消失)，ESP32 power 由 MCU 控
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

Spark 2 / Spark EDGE / Spark LIVE / Reactor 50 / Reactor 100 **共用同一套 USB 架構**（用戶 2026-07-16 確認）：

## 架構

- 機器內有一顆 **USB hub，由 PC 供電**（bus-powered）。
- hub 底下掛 **3 個 USB 端點/晶片**：**MCU (STM32)**、**ESP32**、**BT Audio chip**。

## 各晶片供電與可見性（關鍵）

| 晶片 | 供電/控制 | 列舉行為 |
|------|-----------|----------|
| **BT Audio**（音訊晶片） | **獨立、PC(USB bus) 供電，不受 MCU 控制** | **一直在**，不隨 MCU reboot/DFU 消失 → 可靠的**持續錨點** |
| **ESP32** | **power/EN 由 MCU 控制**（見 [[reference_reactor_esp32_power]]） | MCU boot 拉 high 後才 enumerate；MCU 斷電它就消失 |
| **MCU (STM32)** | — | app mode = CDC（Reactor 0506/0507）；bootloader = DFU PID（Spark2=0232, R50=0504, R100=0502） |

BT Audio 的 PID：Reactor = **0503/0501（Actions BT Audio chip，非 MCU）**（見 [[reference_reactor_usb_pid_chip_map]]）。這顆就是 updater `findSparkAudioId`/`findBtAudioPid` 拿來當 anchor 的裝置。

## ⚠️ Audio anchor 的 VID **不一定是 PG（295D）**

**Spark LIVE 的 audio 是第三方 C-MEDIA 晶片 = `0D8C:0033`**（2026-07-16 用戶用 USB Device Tree Viewer 實測；Port Chain 1-1-1-2-1, Full-Speed, 100mA）。`constants.hpp` 註解說 kUsbVid「shared by all Positive Grid devices」**是錯的** —— 只有 PG 自製的 endpoint 才是 295D。

| 產品 | Audio anchor | 來源 |
|------|--------------|------|
| Spark 2 | **`295D:0231`** | 實機驗證 |
| Spark LIVE | **`0D8C:0033`**（C-MEDIA，非 PG VID） | 實機驗證 2026-07-16 |
| Spark EDGE | `295D:0251` | **未驗證**（從 0231 推測，同 LIVE 的 0221 一樣可能是錯的）|
| Reactor 50/100 | `295D:0503` / `295D:0501` | 實機驗證 |

- 舊值 LIVE=`0221`、EDGE=`0251` 是**從 Spark 2 的 0231 推測出來的，沒有 spec 來源**（git commit ffdd3dc）。LIVE 已證實是錯的 → EDGE 的 0251 同樣待驗證。
- **`0D8C:0033` 是通用 C-MEDIA 晶片**，一般 USB 音效卡/耳機也會回報同一組 ID → 不可讓它蓋過真正的 PG 裝置。updater 已改為 **PG VID 優先**，且先驗 Reactor BT Audio 再驗 Spark。
- **（2026-07-17 用戶確認）audio 晶片廠牌不同，LIVE 的 PID/VID 不會再變**：
  - **Spark LIVE audio = C-MEDIA USB audio 晶片** → `0D8C:0033`（第三方，非 PG VID）。
  - **Reactor audio = Actions USB/BT audio 晶片** → `295D:0503 / 0501`。
  - 兩者都是 USB audio 晶片但**不同廠**（C-MEDIA vs Actions）。LIVE 的 `0D8C:0033` 是 C-MEDIA 晶片自己的 ID、**不隨韌體版本改變** → 當**穩定 anchor** 可靠。
  - 但 `0D8C:0033` 仍非 LIVE 專屬（一般 C-MEDIA 音效卡同 ID），偵測仍要 PG VID 優先、避免誤判成 LIVE。

## 重要推論（更正先前錯誤）

- **MCU 進 DFU 時 audio 不會消失**（因 BT Audio 獨立供電）→ DFU 裝置是**跟 audio 並存、同 hub 的 sibling**，不是「audio 走、DFU 頂替同 port」。（我先前誤稱 audio 會消失，已更正）
- **偵測/存在性判斷正解**：以持續在線的 BT/USB Audio 為 anchor，查同 hub siblings 有沒有 MCU(DFU/CDC) 或 ESP32；codebase 的 `getSparkAudioHubId()`+`isOnSameHub()`（`ReactorFwUpdater/Source/wrapper/UsbDriverWrapper_win.cpp`）正是這個設計前提。
- ESP32「看得到」代表 MCU 已通電啟動；BT Audio 看得到只代表機器接上 PC 通電，**不代表 MCU 活著**。

## USB 存在/供電判定（3-case，product owner 2026-07-16 定義）

判斷 Reactor / Spark 2/EDGE/LIVE 的裝置狀態，只看這三個訊號：

| 看到 | 判定 |
|------|------|
| audio chip 在 | **USB 線有接**（audio 是 USB 供電、always-on，**不代表 power on**） |
| **ESP32(wireless) 或 DFU device** 在 | **power on** |
| 只有 audio（無 ESP32、無 DFU） | 有接線但**沒 power on** → updater 回「Cannot detect the device」 |
| 連 audio 都沒有 | USB 沒接 |

- **PG virtual COM 對偵測沒意義**：Spark 2/EDGE/LIVE **沒有 CDC**（`ProductConfig` cdcPid=""），那個 0901 serial 是 PG virtual COM、不是 CDC，不可當偵測依據。
- 偵測 **wireless module → 看 ESP32**；偵測 **DFU → 看 DFU PID**。**ESP32 VID = `0x303A`（Espressif）已實機驗證：Reactor 與 Spark 2 皆是**；Spark 2 開機後出現 `VID_303A&PID_1001`（ESP32-S3 native USB），關機則消失（2026-07-16 實測）。
- 已實作於 `ReactorFwUpdater/Source/state/FwPrepStates.cpp` CheckUsbDriverState（3-case + fail-fast "not detected"）+ `UsbDriverWrapper` 的 `anyDevicePresent()` / `anyDeviceWithVid()`。

## Spark 2/EDGE/LIVE firmware update 不走 CDC interface

Spark 2 / EDGE / LIVE 的 firmware update **不經 CDC interface**（它們根本沒 CDC）。更新靠 **DFU**（STM32 進 bootloader → 出 DFU PID）。只有 Reactor 有 CDC（0506/0507）。故 updater 對 Spark 的偵測/流程不可依賴 CDC。

相關：[[reference_reactor_usb_pid_chip_map]]、[[reference_reactor_esp32_power]]、[[reference_reactor_updater_bundle]]、[[reference_dfu_bootloader_repos]]、[[project_fwp814_spark_integration]]
