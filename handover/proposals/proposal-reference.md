# Proposal: split reference_* memory files into fact-registry entries vs SOP

Read-only review. No source files touched. No writes to `facts.jsonl`.

---

### reference_dfu_flash.md
**建議:** split

**事實:**
```json
{"key": "PID:295D:0504", "scope": "Reactor 50", "fact": "295D:0504 is Reactor 50's DFU-mode PID.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "### Reactor 50 (PID: 0504)"

```json
{"key": "PID:295D:0502", "scope": "Reactor 100", "fact": "295D:0502 is Reactor 100's DFU-mode PID.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "### Reactor 100 (PID: 0502)"

```json
{"key": "PID:295D:0222", "scope": "Spark LIVE", "fact": "295D:0222 is Spark LIVE's DFU-mode PID.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "### Spark LIVE (PID: 0222)"

```json
{"key": "PID:295D:0232", "scope": "Spark 2", "fact": "295D:0232 is Spark 2's DFU-mode PID.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "### Spark 2 (PID: 0232)"

```json
{"key": "PID:295D:0506", "scope": "Reactor 50/100 (shared)", "fact": "295D:0506 is a CDC PID reported by Reactor 50 and Reactor 100 in normal app mode.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "| Reactor 50 | 0504 | 0507, 0506 |" / "| Reactor 100 | 0502 | 0506, 0507 |"

```json
{"key": "PID:295D:0507", "scope": "Reactor 50/100 (shared)", "fact": "295D:0507 is a CDC PID reported by Reactor 50 and Reactor 100 in normal app mode.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: same table as above (0506/0507 listed for both products, order swapped between rows)

```json
{"key": "TOOL_PATH:dfu-util", "scope": "workspace tooling", "fact": "dfu-util.exe lives at D:\\mybot\\git\\tool\\dfu-util-0.11-binaries\\win64\\dfu-util.exe.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "dfu-util: `D:\mybot\git\tool\dfu-util-0.11-binaries\win64\dfu-util.exe`"

```json
{"key": "TOOL_PATH:esptool", "scope": "workspace tooling", "fact": "esptool.exe lives at D:\\mybot\\git\\tool\\esptool-v4.5.1-win64\\esptool.exe.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "esptool: `D:\mybot\git\tool\esptool-v4.5.1-win64\esptool.exe`"

```json
{"key": "JENKINS:URL", "scope": "Reactor/Spark firmware tooling", "fact": "Jenkins base URL is https://jk-builds.positivegrid.com/jenkins/; the older jenkins.positivegrid.com is deprecated and its DNS no longer resolves.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "URL: `https://jk-builds.positivegrid.com/jenkins/` (舊的 `jenkins.positivegrid.com` 已廢棄，DNS 不通)"

```json
{"key": "JENKINS:TOKEN_PATH", "scope": "Reactor/Spark firmware tooling", "fact": "Jenkins API token for user alice.chan@positivegrid.com is stored at D:\\mybot\\git\\tool\\.jenkins-token.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "Token: `D:\mybot\git\tool\.jenkins-token`"

```json
{"key": "JENKINS:JOB:REACTOR_AMP_FW", "scope": "Reactor 50/100 MCU firmware", "fact": "REACTOR_AMP_FW is the Jenkins job that builds Reactor MCU firmware; it is the CopyArtifact source for MCU_BUILD, copying **/*.bin to Images/.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "MCU FW job: `REACTOR_AMP_FW`" / "`MCU_BUILD` → `REACTOR_AMP_FW` (copies `**/*.bin` to `Images/`)"

```json
{"key": "JENKINS:JOB:REACTOR_ESP32_FW", "scope": "Reactor 50/100 ESP32 firmware", "fact": "REACTOR_ESP32_FW is the Jenkins job that builds Reactor ESP32 firmware; it is the CopyArtifact source for ESP_BUILD, copying **/*.bin to Images/ESP32bin/.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "ESP32 FW job: `REACTOR_ESP32_FW`" / "`ESP_BUILD` → `REACTOR_ESP32_FW` (copies `**/*.bin` to `Images/ESP32bin/`)"

```json
{"key": "JENKINS:COPYARTIFACT_PARAM_FORMAT", "scope": "REACTOR_FW_UPDATER_WIN/OSX Jenkins jobs", "fact": "MCU_BUILD and ESP_BUILD are Jenkins BuildSelectorParameter fields; the API trigger must send XML like <SpecificBuildSelector><buildNumber>148</buildNumber></SpecificBuildSelector> — a plain number causes a 500 ArrayIndexOutOfBoundsException.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "純數字會導致 500 ArrayIndexOutOfBoundsException。"

```json
{"key": "DFU:ERASE_TIMEOUT", "scope": "Reactor 50/100 DFU flashing", "fact": "External NOR chip-erase during DFU takes 10-50 seconds; stock dfu-util 0.11 may time out before it completes. Ken Hung built a longer-timeout version, at GitLab desktop/SparkLiveFwUpgradeLauncher/tree/master/Import/dfu-util.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**Erase timeout**: flash chip erase 需 10-50 秒，標準 dfu-util 0.11 可能 timeout。Ken Hung 有 rebuild 過加長 timeout 的版本（在 GitLab: `desktop/SparkLiveFwUpgradeLauncher/tree/master/Import/dfu-util`）"

```json
{"key": "DFU:GET_STATUS_WARNING_NORMAL", "scope": "STM32 DFU flashing (dfu-util 0.11)", "fact": "The get_status error printed by dfu-util after :leave is an expected warning and does not indicate a failed flash.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**Download 完的 get_status error**: `:leave` 時的正常警告，不影響燒錄結果"

```json
{"key": "DFU:SUFFIX_WARNING_NORMAL", "scope": "STM32 DFU flashing (dfu-util 0.11)", "fact": "The dfu-util \"Invalid DFU suffix signature\" warning is expected/normal and does not affect functionality.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**DFU suffix warning**: \"Invalid DFU suffix signature\" 是正常的，不影響功能"

```json
{"key": "MCU:SN_LOCATION", "scope": "Reactor 50/100", "fact": "Device serial number is stored in MCU internal flash at 0x0800FFE0, 32 bytes, ASCII string null-padded.", "source": "reference_dfu_flash.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "序號存在 MCU internal flash `0x0800FFE0`，32 bytes，ASCII 字串（後面補 0x00）。"

**留在 SOP（程序/守則）:** 所有 `dfu-util.exe -s ...` flash 指令（燒錄/讀寫序號)、Jenkins curl 下載範例、DFU 模式進入步驟（BOOT0 拉高+reset）。

**不確定的地方:**
- CDC PID 0506/0507：表格對 R50、R100 各列了同一組值但順序相反，判斷是「這兩個 PID 是 Reactor 系列共用、隨韌體版號在 0506↔0507 間切換」而非各自獨佔一個 — 已用 scope "Reactor 50/100 (shared)" 表示，若人審核認為該分成兩條各自 scope 的 fact 請指正。
- TOOL_PATH / JENKINS 系列 facts：這些更接近「環境設定」而非「硬體事實」，是否該進 fact registry 還是另立 config 清單，留給人審核判斷。
- 已知測試機序號（R50011G165042170、RA012G16504827C）沒有列成 fact —— 這是特定測試機台的盤點資訊，不是晶片/硬體的通用事實，判斷不適合進 registry，故未提案；如需要盤點用途請人另行決定。

---

### reference_pg_usb_hub_architecture.md
**建議:** split

**事實:**
```json
{"key": "USB:HUB_TOPOLOGY", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "These products share one USB architecture: a single PC bus-powered USB hub with 3 endpoints beneath it — MCU (STM32), ESP32, and BT Audio chip.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "Spark 2 / Spark EDGE / Spark LIVE / Reactor 50 / Reactor 100 **共用同一套 USB 架構**（用戶 2026-07-16 確認）" / "機器內有一顆 **USB hub，由 PC 供電**（bus-powered）。hub 底下掛 **3 個 USB 端點/晶片**：**MCU (STM32)**、**ESP32**、**BT Audio chip**。"

```json
{"key": "USB:BT_AUDIO_POWER", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "The BT Audio chip is independently PC(USB bus)-powered and not controlled by the MCU; it stays enumerated through MCU reboot/DFU, making it a reliable persistent detection anchor.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| **BT Audio**（音訊晶片） | **獨立、PC(USB bus) 供電，不受 MCU 控制** | **一直在**，不隨 MCU reboot/DFU 消失 → 可靠的**持續錨點** |"

```json
{"key": "USB:ESP32_POWER_CONTROL", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "ESP32 power/EN is controlled by the MCU; ESP32 only enumerates after MCU boot pulls EN high, and disappears when the MCU loses power.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| **ESP32** | **power/EN 由 MCU 控制**（見 [[reference_reactor_esp32_power]]） | MCU boot 拉 high 後才 enumerate；MCU 斷電它就消失 |"

```json
{"key": "PID:295D:0503", "scope": "Reactor 50", "fact": "295D:0503 is Reactor 50's BT Audio chip (an Actions chip, not the MCU), and serves as its USB audio anchor device.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "BT Audio 的 PID：Reactor = **0503/0501（Actions BT Audio chip，非 MCU）**" + table row "| Reactor 50/100 | `295D:0503` / `295D:0501` | 實機驗證 |"

```json
{"key": "PID:295D:0501", "scope": "Reactor 100", "fact": "295D:0501 is Reactor 100's BT Audio chip (an Actions chip, not the MCU), and serves as its USB audio anchor device.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: same as above; product-order inferred from "Reactor 50/100 | 295D:0503 / 295D:0501" column ordering.

```json
{"key": "USB:AUDIO_ANCHOR:Spark2", "scope": "Spark 2", "fact": "Spark 2's audio anchor device is 295D:0231.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| Spark 2 | **`295D:0231`** | 實機驗證 |"

```json
{"key": "USB:AUDIO_ANCHOR:SparkLIVE", "scope": "Spark LIVE", "fact": "Spark LIVE's audio anchor device is 0D8C:0033, a third-party C-MEDIA chip, not a Positive Grid VID.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| Spark LIVE | **`0D8C:0033`**（C-MEDIA，非 PG VID） | 實機驗證 2026-07-16 |"

```json
{"key": "USB:AUDIO_ANCHOR:SparkLIVE_deprecated", "scope": "Spark LIVE", "fact": "The previously assumed Spark LIVE audio anchor 295D:0221 (extrapolated from Spark 2's 0231, no spec source, git commit ffdd3dc) has been confirmed incorrect; the real anchor is 0D8C:0033.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "舊值 LIVE=`0221`、EDGE=`0251` 是**從 Spark 2 的 0231 推測出來的，沒有 spec 來源**（git commit ffdd3dc）。LIVE 已證實是錯的"

```json
{"key": "USB:AUDIO_ANCHOR:SparkEDGE", "scope": "Spark EDGE", "fact": "Spark EDGE's audio anchor is assumed to be 295D:0251, extrapolated from Spark 2's pattern; not yet verified on real hardware, and the analogous LIVE guess (0221) turned out wrong.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "assumed"}
```
> 出處原文: "| Spark EDGE | `295D:0251` | **未驗證**（從 0231 推測，同 LIVE 的 0221 一樣可能是錯的）|"

```json
{"key": "USB:CMEDIA_GENERIC_ID", "scope": "Spark LIVE / general USB", "fact": "0D8C:0033 is a generic C-MEDIA USB audio chip ID also reported by common third-party USB soundcards/headsets, not exclusive to Spark LIVE hardware.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**`0D8C:0033` 是通用 C-MEDIA 晶片**，一般 USB 音效卡/耳機也會回報同一組 ID"

```json
{"key": "USB:DFU_AUDIO_COEXIST", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "When the MCU enters DFU mode, the BT Audio device does not disappear (it is independently powered); the DFU device appears as a sibling on the same hub alongside audio, not as a replacement of it.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**MCU 進 DFU 時 audio 不會消失**（因 BT Audio 獨立供電）→ DFU 裝置是**跟 audio 並存、同 hub 的 sibling**，不是「audio 走、DFU 頂替同 port」。（我先前誤稱 audio 會消失，已更正）"

```json
{"key": "USB:MCU_ALIVE_SIGNAL", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "ESP32 being visible means the MCU is powered on and booted; BT Audio being visible alone does NOT mean the MCU is alive, since BT Audio power is independent of the MCU.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "ESP32「看得到」代表 MCU 已通電啟動；BT Audio 看得到只代表機器接上 PC 通電，**不代表 MCU 活著**。"

```json
{"key": "USB:PRESENCE_LOGIC", "scope": "Spark 2/EDGE/LIVE, Reactor 50/100", "fact": "Device presence is judged from 3 signals only: audio chip alone means USB cable is connected (audio is always-on, does not imply power-on); ESP32(wireless) or DFU device visible means powered on; only audio with no ESP32/DFU means connected-but-not-powered-on (updater reports \"Cannot detect the device\"); no audio at all means USB not connected.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: 3-case 表格 (lines 49-56), header "判斷 Reactor / Spark 2/EDGE/LIVE 的裝置狀態，只看這三個訊號" + "product owner 2026-07-16 定義"

```json
{"key": "USB:ESP32_VID", "scope": "Reactor 50/100, Spark 2", "fact": "ESP32 module VID is 0x303A (Espressif), verified on real hardware for both Reactor and Spark 2. Spark 2 shows VID_303A&PID_1001 (ESP32-S3 native USB) when powered on, and it disappears when powered off.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**ESP32 VID = `0x303A`（Espressif）已實機驗證：Reactor 與 Spark 2 皆是**；Spark 2 開機後出現 `VID_303A&PID_1001`（ESP32-S3 native USB），關機則消失（2026-07-16 實測）。"

```json
{"key": "USB:PG_VIRTUAL_COM_NOT_CDC", "scope": "Spark 2/EDGE/LIVE", "fact": "Spark 2/EDGE/LIVE have no CDC interface (ProductConfig cdcPid=\"\"); the 0901 serial port they expose is a PG virtual COM, not CDC, and must not be used as a presence-detection signal.", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**PG virtual COM 對偵測沒意義**：Spark 2/EDGE/LIVE **沒有 CDC**（`ProductConfig` cdcPid=""），那個 0901 serial 是 PG virtual COM、不是 CDC，不可當偵測依據。"

```json
{"key": "USB:FW_UPDATE_PATH_SPARK", "scope": "Spark 2/EDGE/LIVE", "fact": "Spark 2/EDGE/LIVE firmware updates go through DFU (STM32 bootloader -> DFU PID), not CDC, because these products have no CDC interface at all; only Reactor has CDC (0506/0507).", "source": "reference_pg_usb_hub_architecture.md", "owner": "alice", "captured": "2026-07-16", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "Spark 2 / EDGE / LIVE 的 firmware update **不經 CDC interface**（它們根本沒 CDC）。更新靠 **DFU**（STM32 進 bootloader → 出 DFU PID）。只有 Reactor 有 CDC（0506/0507）。"

**留在 SOP（程序/守則）:** updater 偵測演算法本身（`getSparkAudioHubId()`+`isOnSameHub()`、`CheckUsbDriverState` 3-case fail-fast、`anyDevicePresent()`/`anyDeviceWithVid()` 的實作位置與呼叫順序、"PG VID 優先，先驗 Reactor 再驗 Spark" 的程式邏輯）——這些是程式行為/程式碼指標，屬於工程師找 code 用的線索，不是獨立的硬體事實。

**不確定的地方:**
- `USB:PRESENCE_LOGIC` 比較接近「判讀規則」而非單純的硬體事實 — 它是 product owner 對訊號的定義，不是量測出來的硬體屬性；已標 confidence=reported（非 verified），但是否該整條留在 SOP 而非進 registry，請人審核判斷。
- PID 0503→Reactor 50、0501→Reactor 100 的對應是根據表格欄位順序（"Reactor 50/100 | 295D:0503 / 295D:0501"）推斷，文件本身沒有逐一標注哪個數字對哪個型號 — 若人審核有其他來源（如 reference_reactor_usb_pid_chip_map.md）可交叉驗證會更保險。

---

### reference_reactor_stlink_flash.md
**建議:** split

**事實:**
```json
{"key": "CHIP:STM32H7R3_DEVICE_ID", "scope": "Reactor 50/100 (STM32H7R3)", "fact": "STM32_Programmer_CLI reports Device ID 0x485 / Revision B for Reactor's STM32H7RSxx (H7R3) MCU.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "Device ID    : 0x485" / "Revision ID  : Rev B" / "Device name  : STM32H7RSxx     ← H7R3 family confirmed"

```json
{"key": "FLASH:H7R3_SWD_AP", "scope": "Reactor 50/100 (STM32H7R3)", "fact": "STM32H7R3 must be accessed via SWD AP 1 (M7 core) for flashing; the default AP 0 does not work for this purpose.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "`port=SWD ap=1` — H7R3 用 AP 1（M7 core），不是 default AP 0"

```json
{"key": "MEMORY:REACTOR_EXT_NOR_BASE", "scope": "Reactor 50/100", "fact": "Reactor 50/100's external XSPI NOR flash base address is 0x90000000.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "`0x90000000` — Reactor external XSPI NOR base address"

```json
{"key": "FLASH:REACTOR_MASS_ERASE_DANGER", "scope": "Reactor 50/100 (STM32H7R3)", "fact": "Passing --mass-erase together with -el <stldr> on Reactor's STM32_Programmer_CLI flash is dangerous: the -el/stldr path already auto-erases external NOR sectors, and adding mass-erase will incorrectly wipe the internal flash bootloader.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**不要帶 `--mass-erase`** — `-el` 配 stldr 已自動 erase external NOR sectors，加 mass-erase 會誤擦 internal flash 上的 bootloader"

```json
{"key": "SERIAL:STLINK_VCP_BAUD", "scope": "Reactor 50/100", "fact": "Reactor's STLink VCP debug serial runs at 921600 baud.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "開 COM4 (STLink VCP) @ 921600 看到："

```json
{"key": "LOG:REACTOR_BOOTLOADER_VERSION", "scope": "Reactor 50/100", "fact": "Observed bootloader prints itself as 'Reactor 50w Bootloader_version: 0.1.0.39' at this point in time.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "Reactor 50w Bootloader_version: 0.1.0.39"

```json
{"key": "LOG:REACTOR_LABEL_QUIRK", "scope": "Reactor 50/100", "fact": "Debug firmware always prints the label 'Reactor 100w fw_version' in its boot log, regardless of whether the actual hardware is R50 or R100 — the '100w' label is a generic/incorrect string, not hardware-specific.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "Reactor 100w fw_version: 0.1.x.x   ← debug build only, label \"100w\" is generic regardless of R50/R100"

```json
{"key": "LOG:RELEASE_BUILD_SILENT", "scope": "Reactor 50/100", "fact": "Release build (RUNNING_MODE_APP) produces no UART output; the serial line going silent after 'Jump to APP code' is expected/normal, not a fault.", "source": "reference_reactor_stlink_flash.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**Release build (RUNNING_MODE_APP) 不輸出 UART**，\"Jump to APP code\" 後 silent 是正常的。"

**留在 SOP（程序/守則）:** 完整 STM32_Programmer_CLI 指令行（含路徑組裝）、"燒完後建議 USB Relay power cycle 再進行 ESP32 燒錄" 的操作建議、`flash-and-reset-stm32.ps1` 路徑寫死問題的處理建議。"ESP32 EN 由 STM32 控制" 這句話在本檔重複出現，但已在 `reference_pg_usb_hub_architecture.md` 提案為 `USB:ESP32_POWER_CONTROL`，此處不重複建議。

**不確定的地方:**
- `LOG:REACTOR_BOOTLOADER_VERSION` (0.1.0.39) 是「當下觀測到的版本號」，版本號會隨韌體發布改變而過期，但檔案本身沒說它是暫時性的 — 沒有把它標成 volatile（因為不是需要 live probe 的東西，probe 語意不合），但也沒加 ttl（不確定何時真的作廢）。是否該給這條加 ttl 或改成「僅供歷史對照」的性質，請人審核判斷。
- `SERIAL:STLINK_VCP_BAUD` 刻意不做成 `COM:COM4`，因為 COM 號碼會隨插拔改變（見 MEMORY.md「Port 號碼會因重插而變」），而 921600 baud + STLink VCP 介面本身是穩定的、與 COM 號脫鉤的事實。

---

### reference_usb_relay_pulse_off_state.md
**建議:** split

**事實:**
```json
{"key": "RELAY:PULSE_BEHAVIOR", "scope": "Alice's flash rig (USB Relay)", "fact": "usb-relay.ps1 -Action pulse turns the relay ON for ~200ms then OFF; the resting state after pulse is OFF (device powered down).", "source": "reference_usb_relay_pulse_off_state.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "`D:\mybot\git\tool\usb-relay.ps1 -Action pulse -Port COM3` 的行為：" / "ON 200ms → OFF" / "最終 state = **OFF (device 斷電)**。"

```json
{"key": "RELAY:BEHIND_RELAY", "scope": "Alice's flash rig", "fact": "On Alice's rig, Reactor CDC and ESP32 USB interfaces are powered through the USB Relay and disappear when the relay is OFF; STLink VCP and the USB Relay's own serial port connect directly to the PC and are not affected by the relay.", "source": "reference_usb_relay_pulse_off_state.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "pulse 後 COM6 (Reactor CDC) + COM19 (ESP32) 全部消失" / "COM4 (STLink VCP) 不受影響（USB 直接接 PC，不過 relay）" / "COM3 (USB Relay 自己) 不受影響"

```json
{"key": "RELAY:WIRING_MODEL", "scope": "Alice's flash rig", "fact": "Relay wiring is inferred (not confirmed by schematic) to be normally-open: ON = relay closed = device powered; OFF = relay open = device unpowered; a pulse (ON then OFF) therefore ends powered-off.", "source": "reference_usb_relay_pulse_off_state.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "assumed"}
```
> 出處原文: "## 推測 wiring" / "Relay 接法是 「ON = device 通電」（normally open）" / "pulse(ON-OFF) = 通電 200ms 後又斷電 = 結果斷電"

```json
{"key": "SCRIPT:FLASH_AND_RESET_END_STATE", "scope": "Alice's flash rig / reactor-fw STM32", "fact": "flash-and-reset-stm32.ps1 ends by calling usb-relay -Action pulse, so after it runs the device is left powered OFF; -Action on must be issued manually before boot-log testing.", "source": "reference_usb_relay_pulse_off_state.md", "owner": "alice", "captured": "2026-04-29", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "`flash-and-reset-stm32.ps1` 結尾是 `usb-relay -Action pulse`，意味著 STLink 燒完後 device 會留斷電 — 跑 boot test 前要記得補 `-Action on`。"

**留在 SOP（程序/守則）:** "要做 reset 後 device 通電：pulse 後再呼一次 -Action on，或直接用 off → sleep → on 兩步驟"、"clean cold boot: off → sleep 800ms → on" 這兩條操作步驟。

**不確定的地方:**
- 檔案內多處提到具體 COM 號碼 (COM3/COM4/COM6/COM19)。依照 MEMORY.md「Port 號碼會因重插而變」的已知教訓，**故意不**把這些號碼做成 `COM:COM6` 之類的 fact（那正是應該 volatile+probe、而非快取的資訊）。改用拓樸關係（"哪些介面走 relay、哪些不走"）當 fact 內容，號碼本身留在原文当例子。若人審核認為 USB Relay 自己的埠 (COM3) 值得存一條 `volatile:true` 的 probe fact（例如靠 VID 比對），可以另外補一條，但目前判斷內容本身（哪些介面受 relay 影響）比號碼更有長期價值，故未提案 COM 開頭的 fact。
- `SCRIPT:FLASH_AND_RESET_END_STATE` 的 confidence 定為 reported 而非 verified — 文件用「意味著」(implies) 描述，屬於讀 script 內容後的推論陳述，不是直接測試出的行為；若人審核讀過該 script 原始碼確認屬實，可以升級為 verified。
