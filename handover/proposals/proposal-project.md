# Proposal: split 7 project_* memory files into fact-registry candidates vs state/rule

Read-only review. No files under `C:/Users/alice/.claude/projects/D--mybot/memory/` were modified.
Nothing was written to `D:/mybot/handover/registry/facts.jsonl` (it still does not exist).

---

### project_fwp791_ota_analysis.md
**建議:** state-only（不進 registry）

**事實:** 無（0 facts）

**留在原地:** 整份文件是進行中的 bug 分析狀態：Bug A 標明「待驗證」，Bug B 雖「100% 複製」但修法還是 WIP MR（`!318`，branch `bugfix/FWP-791-ota-sdmmc-lockdown`），連 stash 都還在（`stash@{0}`）。每一句可能看起來像「事實」的敘述（`hsd1` 無 mutex、`DEBUG_READBACK_IMAGE_FROM_SDNAND` 硬編碼為 1）其實都是「目前這個 bug 存在」的描述——MR 一 merge 就變假。Next Steps 段落更是純狀態（要不要 re-flash ESP32、要不要 power cycle）。這裡唯一可能長期為真的技術細節（`esp_http_client_read` blocking 行為）已經在姐妹檔 `project_fwp791_test_params.md` 有更完整、可獨立引用的證據，故不在本檔重複造 fact，避免同一 key 兩處各自維護。

**不確定的地方:** 無（判斷為 0 facts 的信心較高——這份文件的性質就是「調查中」，descrption 本身就寫著「Next: apply Bug B fix then retest Bug A」）。

---

### project_fwp791_test_params.md
**建議:** split

**事實:**
```json
{"key": "BEHAVIOR:ESP32_HTTP_CLIENT_READ_BLOCKING", "scope": "Reactor ESP32 firmware (esp-idf esp_http_client)", "fact": "esp_http_client_read() is a blocking loop that only returns once it has filled its 1536-byte buffer or the TLS_TIMEOUT (7000ms) elapses, at which point it returns whatever partial data was read.", "source": "project_fwp791_test_params.md｜esp_http_client.c:1040-1120, app_https_fw_ota.cpp:17,419,460", "owner": "alice", "captured": "2026-05-19", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "只有 server delay > 7s 才能讓 transport_read timeout → return partial data" (line 17), "`config.timeout_ms = TLS_TIMEOUT = 7000`（7 秒）" (line 16)

```json
{"key": "PROC:FWP791_OTA_REPRO_RECIPE", "scope": "Reactor ESP32 firmware OTA test tooling (throttle_server.py)", "fact": "To force esp_http_client_read() into a partial (non-full-buffer) read against Reactor STM32 OTA, the throttle server must use chunk-size=127 (odd, divides neither 512 nor 1536) with burst-size=10 (1270 bytes/burst, under the 1536 buffer) and stall-sec=8 (>7s TLS_TIMEOUT); chunk-size=1536 does not work because 10x1536 exactly fills 10 buffers and produces a clean timeout/error instead of a partial read.", "source": "project_fwp791_test_params.md", "owner": "alice", "captured": "2026-05-19", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "`--chunk-size 127` | 127B | **必須！** 奇數，不整除 512 也不整除 1536。10×127=1270 < BUFFSIZE(1536) → partial read" (line 29); "chunk-size 1536 不行：...第 11 次 ridx=0 → timeout → return error（不是 partial data）" (line 39)

```json
{"key": "BEHAVIOR:ESP32_OTA_PASSTHROUGH_HANG", "scope": "Reactor ESP32 firmware OTA (app_https_fw_ota.cpp)", "fact": "If the ESP32-side test/reference binary (esp32_fw_reactor100.bin) is missing or fails to download, the ESP32 OTA task hangs forever on vTaskDelay(portMAX_DELAY) and the STM32 OTA never starts — a valid binary must always be present for STM32 OTA to be reachable via ESP32 pass-through.", "source": "project_fwp791_test_params.md｜app_https_fw_ota.cpp:274-282", "owner": "alice", "captured": "2026-05-19", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "如果 `esp32_fw_reactor100.bin` 不存在或下載失敗 → ESP32 OTA task 永久掛起（`vTaskDelay(portMAX_DELAY)`） → STM32 OTA 永遠不會開始" (line 59)

**留在原地:** Bug A 的 underflow 數學推導（`img_pkts=2406`、~83% 觸發點、SPI#~2407）綁死在這次測試 image 的具體大小（1,231,368 bytes）——換一顆 firmware image 這些數字全部失效，屬於 test-run state，不進 registry。COM port 資訊（COM4/COM19）也不收：這份文件寫的是 COM19 給 ESP32，但全域 MEMORY.md 的權威表格寫的是 COM7——兩者不一致，正好印證 COM 號碼必須即時 probe、不能當靜態 fact 快取。

**不確定的地方:** `PROC:FWP791_OTA_REPRO_RECIPE` 這條比較像「測試方法/recipe」而非典型的「產品/chip 事實」，schema 的 scope 欄位（設計給 product/chip 用）套在這裡略勉強，但內容本身（buffer 大小與 timeout 的數學關係）在 esp-idf 版本不變的前提下應該長期有效，故仍列入、但請人工複核這條是否真的該進 fact registry 或該留在 debugging runbook 裡。

---

### project_fwp814_spark_integration.md
**建議:** split（狀態遠多於事實——這份是最活躍的進行中專案文件，鐵律規定的「別為了湊數造事實」在這份最重要）

**事實:**
```json
{"key": "ARCH:FW_UPDATE_DETECTION_ANCHOR", "scope": "Spark Gen2 (Spark 2/LIVE/EDGE) + Reactor, ReactorFwUpdater unified", "fact": "Firmware-update device detection anchors on each product's USB Audio PID (not its DFU PID) — the same pattern already used for Reactor's BT Audio PID anchor.", "source": "project_fwp814_spark_integration.md", "owner": "alice", "captured": "2026-07-09", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "裝置偵測用 **USB Audio PID 當錨點**（對應 Reactor 的 BT Audio PID），**不是** DFU PID。" (line 13)

```json
{"key": "USB:PID_MAP", "scope": "Spark LIVE", "fact": "Spark LIVE USB VID:PID is 0x295D:0x0221 (audio) / 0x295D:0x0222 (DFU).", "source": "project_fwp814_spark_integration.md｜Ken Hung sheet 7/6 + source-code verified", "owner": "alice", "captured": "2026-07-06", "ttl": null, "volatile": false, "confidence": "verified"}
```
```json
{"key": "USB:PID_MAP", "scope": "Spark 2", "fact": "Spark 2 USB VID:PID is 0x295D:0x0231 (audio) / 0x295D:0x0232 (DFU).", "source": "project_fwp814_spark_integration.md｜Ken Hung sheet 7/6 + source-code verified", "owner": "alice", "captured": "2026-07-06", "ttl": null, "volatile": false, "confidence": "verified"}
```
```json
{"key": "USB:PID_MAP", "scope": "Spark EDGE", "fact": "Spark EDGE USB VID:PID is 0x295D:0x0251 (audio) / 0x295D:0x0252 (DFU).", "source": "project_fwp814_spark_integration.md｜Ken Hung sheet 7/6 + source-code verified", "owner": "alice", "captured": "2026-07-06", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**VID/PID（Ken Hung sheet 7/6 + 原始碼驗證）**：audio / DFU / VID 全 0x295D — LIVE 0x0221/0x0222、Spark2 0x0231/0x0232、EDGE 0x0251/0x0252。" (line 18)

```json
{"key": "HW:DFU_MODE_LED", "scope": "Spark Gen2 (Spark 2/LIVE/EDGE)", "fact": "Entering DFU/firmware-update mode, the power (BATT) LED breathes white (set_led_breath(LED_COLOR_WHITE)) — it does not blink and is not solid.", "source": "project_fwp814_spark_integration.md｜spark-ii-fw PowerManager.cpp:729, spark-pedal-fw PowerManager.cpp:623/715/1806", "owner": "alice", "captured": "2026-07-12", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**【DFU LED 定論，bootloader 原始碼查證】進 update mode 時 power LED = 呼吸白燈（breathe white），不是閃爍、也不是恆亮**。firmware 用 `set_led_breath(LED_COLOR_WHITE)`：`spark-ii-fw PowerManager.cpp:729`、`spark-pedal-fw :623/715/1806`" (line 59)

```json
{"key": "HW:DFU_MODE_LED", "scope": "Reactor 50/100", "fact": "Entering DFU/firmware-update mode, the WiFi LED breathes white and the BT LED blinks blue (not the power LED, unlike Spark).", "source": "project_fwp814_spark_integration.md｜reactor-fw update_sequence_1() PowerManager.cpp:717-718, commit 09aefe9", "owner": "alice", "captured": "2026-07-12", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**Reactor update-mode LED（bootloader）**：`reactor-fw update_sequence_1() PowerManager.cpp:717-718`＝**WiFi LED 呼吸白 + BT LED 閃藍**。...**全機型定論：白燈都是 breathe（Spark=BATT、Reactor=WiFi），沒有 blink white；只有 BT 閃藍。**" (line 61) — 這條 supersede 了同檔線 59 較早、較簡化的說法（那時還把 reactor-fw 也算進「power LED breathe white」），已用最終定論版本入 fact，避免收錄到後來被自己修正掉的舊結論。

```json
{"key": "HW:POWER_BUTTON_TYPE", "scope": "Spark Gen2 (Spark 2/LIVE/EDGE) vs Reactor", "fact": "Across Gen2 products the DFU-entry combo is power+pair, but the power control differs: Reactor's is a switch, while Spark 2/LIVE/EDGE's is a momentary power button.", "source": "project_fwp814_spark_integration.md", "owner": "alice", "captured": "2026-07-12", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**按鍵**：Gen2 全部是 power+pair；只有 **Reactor 的 power 是 switch，其餘（Spark 2/LIVE/EDGE）是 power button**（走 CDC 自動的 Reactor 不顯示這段手動文字）。" (line 60)

```json
{"key": "HW:SPARK_ESP32_USB_TOPOLOGY", "scope": "Spark Gen2 (Spark 2/LIVE/EDGE)", "fact": "It is assumed (not hardware-verified) that Spark's ESP32 module shares the same USB parent/hub as its USB Audio device, which is the premise the audio-anchored ESP32 detection design depends on.", "source": "project_fwp814_spark_integration.md", "owner": "alice", "captured": "2026-07-10", "ttl": null, "volatile": false, "confidence": "assumed"}
```
> 出處原文: "⚠️ **前提未驗**：Spark ESP32 是否與 USB Audio 同 USB parent——Alice 口頭確認架構如此，但**無實機驗證**（Alice 親口說 Spark 沒實機驗過）。" (line 39)

```json
{"key": "PATH:ESPTOOL_SOURCE_LOCAL", "scope": "alice's dev machine (esp-idf 5.0 py3.11 env)", "fact": "The real esptool source lives at C:\\Users\\alice\\.espressif\\python_env\\idf5.0_py3.11_env\\Lib\\site-packages\\esptool\\ — the esp-idf/components/esptool_py/esptool/esptool.py path is only a launcher stub.", "source": "project_fwp814_spark_integration.md", "owner": "alice", "captured": "2026-07-12", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**esptool 原始碼位置**：`C:\\Users\\alice\\.espressif\\python_env\\idf5.0_py3.11_env\\Lib\\site-packages\\esptool\\`（`esp-idf/components/esptool_py/esptool/esptool.py` 只是 launcher stub）。" (line 66)

```json
{"key": "TOOL:GEMINI_CODE_REVIEW_BOT_STATUS", "scope": "PR review tooling (GitLab/GitHub MRs, Positive Grid)", "fact": "The gemini code-review bot for PR/MR review was sunset on 2026-07-17; /gemini review no longer responds. PR review is now done by running a self-driven subagent holistic review instead.", "source": "project_fwp814_spark_integration.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "**gemini code-review bot 已 sunset**（2026-07-17 停）：`/gemini review` 不再回應。PR review 改自己跑 subagent holistic review。" (line 70)

**留在原地:** 這是全部 7 檔裡狀態密度最高的一份——PR #12/#13 狀態、branch 名稱（`feature/FWP-814-audio-anchor`/`spark-unified`）、Jenkins build 編號（WIN#5~#19、OSX#3~#17）、JIRA 狀態轉換（完成→進行中）、`isSparkFlow()` 判斷邏輯（**文件內自己就修正了一次**：先說「無 CDC=Spark」，後面 2026-07-10 又澄清「無 CDC ≠ Spark」）、updater 版本命名機制改動歷程、build script 路徑——全部是「這個 feature 現在做到哪」的敘述，且部分已經在文件內被自己推翻過，绝不能當固定事實收錄。「仍待辦」「未 merge」「實機未驗」的字樣是最直接的 state 訊號。

**不確定的地方:** `HW:POWER_BUTTON_TYPE` 和 `ARCH:FW_UPDATE_DETECTION_ANCHOR` 這兩條文件裡沒有引用 file:line 原始碼證據（純敘述），信心定為 `reported` 而非 `verified`；若人工複核時發現有更硬的來源，可以升級。`HW:SPARK_ESP32_USB_TOPOLOGY` 明確標成 `assumed`——這條本質上是「還沒驗證的假說」，收錄的價值在於「提醒下次任何人查這件事時，知道它從未被驗證過」，而不是把它當可信結論用。

---

### project_reactorfwupdater_consolidation.md
**建議:** split

**事實:**
```json
{"key": "CHIP:SPARK_GEN2_WIRELESS_MODULE", "scope": "Spark Gen2 (Spark 2/LIVE/EDGE)", "fact": "New-generation Spark's wireless module is Airoha AB1585/1595, not ESP32; there is no separate spark-esp32 GitHub repo for it.", "source": "project_reactorfwupdater_consolidation.md", "owner": "alice", "captured": "2026-07-09", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "spark-esp32 在 GitHub 無獨立 repo（新一代 Spark 無線走 Airoha AB1585/1595 非 ESP32）。" (line 20, under header "不重複做的（已查證）")

```json
{"key": "LIMIT:REACTORFWUPDATER_SUBPROCESS_IO", "scope": "ReactorFwUpdater (Positive-LLC/ReactorFwUpdater)", "fact": "ReactorFwUpdater's shared Subprocess utility has a hardcoded 64KB output buffer and a 120s timeout, which is a common constraint on every shell-out call it makes (esptool, dfu-util, etc.).", "source": "project_reactorfwupdater_consolidation.md", "owner": "alice", "captured": "2026-07-09", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "`Subprocess` 全域 64KB buffer + 120s timeout 是所有 shell-out 共同限制" (line 22, under "Fable 揪出的 repo 問題")

**留在原地:** PR #11 狀態（待 merge）、FWP-819 歸檔 ticket、Google Drive 摘要連結、「下一候選 pg-reactor-esp32」、「不要 block 在 Nathan」等全是治理/流程進度，跟著 Fable 整理案的完成度走，不是可長期查詢的事實。

**不確定的地方:** `LIMIT:REACTORFWUPDATER_SUBPROCESS_IO` 信心定為 `reported` 而非 `verified`——這是 Fable（另一個 agent）的 code review 發現，文件本身沒有寫 file:line，也沒說是 alice 自己重新確認過，屬於「轉述的分析結論」。

---

### project_release_20260703_ota_staging.md
**建議:** state-only（不進 registry），僅 1 條流程性質的 fact 可留意

**事實:**
```json
{"key": "PROC:REACTOR_OTA_STAGING_TO_PRODUCTION", "scope": "Reactor 50/100 OTA release (Jenkins Release_Reactor_FW_FOR_OTA)", "fact": "Promoting a Reactor OTA staging release to production is done by rerunning Release_Reactor_FW_FOR_OTA with the same BUILD_NO/ESP32_BUILD_NO and flipping TO_PRODUCTION=true — it reuses the already-built artifact rather than rebuilding.", "source": "project_release_20260703_ota_staging.md", "owner": "alice", "captured": "2026-07-03", "ttl": null, "volatile": false, "confidence": "reported"}
```
> 出處原文: "**How to apply:** 用戶說「OTA 上 production」時，用**下表同樣的 build number** 跑 `Release_Reactor_FW_FOR_OTA` 改 `TO_PRODUCTION=true`（不要重新 build，用同一批 artifact）。" (line 14)

**留在原地:** 這份文件幾乎整份都是這次特定 release 的狀態——0.1.4.171 是哪個 commit、staging build #85/#86 SUCCESS、RAD-1476 何時 merge、tag 0.1.4.170 打在哪個 commit。這正是 prompt 給的範例本身（「Release 0.1.4.171 正在 staging 等 QA」QA 一過就是假的）。全域 memory 的 `project_release_20260703_ota_staging` 條目已經標「等 QA 過用同 build 跑 TO_PRODUCTION=true」，一旦這批真的上了 production，這份檔案剩下的每一行都會過期，不該進 registry。

**不確定的地方:** `PROC:REACTOR_OTA_STAGING_TO_PRODUCTION` 這條的措辭本質上更接近「行為規則」（用戶說 X 時做 Y）而非單純事實陳述，我已經改寫成描述 Jenkins job 運作方式的中性事實句，但請人工複核這條該進 fact registry 還是該留在 rule/SOP 文件裡——兩種分類都說得通。

---

### project_spark_gen1_vs_reactor_distinct.md
**建議:** fact-only（這份是最接近 prompt 範例的「evergreen 事實」文件，事實密度最高、狀態最少）

**事實:**
```json
{"key": "PROTO:FW_UPDATE_HANDSHAKE", "scope": "Spark Gen 1 (40/MINI/GO/NEO)", "fact": "Spark Gen 1 firmware-update handshake uses MIDI SysEx.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
```json
{"key": "PROTO:FW_UPDATE_HANDSHAKE", "scope": "Reactor 50/100", "fact": "Reactor firmware-update handshake uses CDC (virtual serial), not MIDI.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| Firmware update 握手 | **MIDI SysEx** | **CDC (virtual serial)** |" (line 11); "走 MIDI? | ✅ 走 | ❌ 不走 (2026-04-21 確認)" (line 15)

```json
{"key": "CHIP:MAIN_ARCHITECTURE", "scope": "Reactor 50/100", "fact": "Reactor 50/100's chip combination is STM32 MCU + ESP32 (WiFi/BT).", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| Chip 組合 | 不同 | STM32 MCU + ESP32 (WiFi/BT) |" (line 9)

```json
{"key": "USB:DRIVER_MODE", "scope": "Spark Gen 1", "fact": "Spark Gen 1 firmware update uses the WinUSB driver in ADFU mode.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
```json
{"key": "USB:DRIVER_MODE", "scope": "Reactor 50/100", "fact": "Reactor firmware update uses the WinUSB driver in DFU mode.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| USB Driver path | WinUSB (ADFU mode) | WinUSB (DFU mode) |" (line 12)

```json
{"key": "TOOL:UPDATER_FRAMEWORK", "scope": "Spark Gen 1", "fact": "Spark Gen 1's firmware updater is SparkFwUpgradeLauncher, built on JUCE 7.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
```json
{"key": "TOOL:UPDATER_FRAMEWORK", "scope": "Reactor 50/100", "fact": "Reactor's firmware updater is ReactorFwUpdater, built on JUCE 8.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "| Updater framework | JUCE 7 (SparkFwUpgradeLauncher) | JUCE 8 (ReactorFwUpdater) |" (line 13)

```json
{"key": "PLATFORM:WIN25H2_SHARED_ISSUES", "scope": "Spark Gen 1 + Reactor (shared Windows platform layer)", "fact": "Windows 25H2 platform-level issues (Co-installer deprecation, UAC, driver signing) affect both Spark Gen 1 and Reactor equally, since these are platform-layer problems, not product-specific ones.", "source": "project_spark_gen1_vs_reactor_distinct.md", "owner": "alice", "captured": "2026-04-21", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: "平台層共通問題（Win 25H2 廢 Co-installer、UAC、signing）仍然兩者都適用 — 這層是 platform 不是產品" (line 23)

**留在原地:** "How to apply" 段落（"討論 Reactor updater 時，不要引用 Spark 系列的 MIDI...作為先例"）是行為規則，不是事實——它是「根據上面的事實，該怎麼做」的指示，理當留在原文件當 rule，不重複塞進 registry。

**不確定的地方:** 無。這份文件本身就標榜 "Why: 2026-04-21 Alice 明確糾正" 且每條都有清楚的技術對照表，是 7 份裡信心最高的一份。

---

### project_stfs491_root_cause.md
**建議:** fact-only（歷史性、已修復的 root cause 分析，本質是可長期查詢的技術結論，不是進行中的 state）

**事實:**
```json
{"key": "BUG:STFS491_ROOT_CAUSE_APP_DEADLOCK", "scope": "Spark MINI (SparkFwUpgradeLauncher, Windows 25H2)", "fact": "Windows 25H2 changed MidiSrv behavior (added the UMP protocol), causing 5 independent deadlock paths in SparkFwUpgradeLauncher during Spark MINI firmware update on Windows; all 5 were fixed by dedicated commits (79392d03, e57b2b5b, c7eea3e, fd837a3, and 92e7b4c/598ae04/e9db692/04caf8f). macOS is unaffected because CoreMIDI has no MidiSrv/UMP gateway layer.", "source": "project_stfs491_root_cause.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: table rows P1-P3/P5/P6, B1, P4 (lines 21-25); "**Mac 不受影響原因：** CoreMIDI 沒有 MidiSrv/UMP gateway 層。" (line 27)

```json
{"key": "BUG:STFS491_ROOT_CAUSE_BOOTLOADER_DESCRIPTOR", "scope": "Spark MINI (g1x-bootloader, Windows 25H2)", "fact": "Spark MINI's g1x-bootloader had 4 USB MIDI descriptor non-compliances (wrong wTotalLength=65 instead of 37, no reply to UMP Discovery Request, no bulk-IN data, 3 undeclared endpoints) that Windows 25H2's stricter descriptor parsing turned into hangs/deadlocks; all 4 were fixed (commits 5438843, 1a7b3c9, 9c5bd5d, ffe0819). Older Windows and macOS tolerated the non-compliant descriptor.", "source": "project_stfs491_root_cause.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: table rows 2a-2d (lines 33-36); "**Mac 不受影響原因：** 舊版 Windows 和 Mac 對 descriptor 錯誤寬容，25H2 改為嚴格。" (line 38)

```json
{"key": "BUG:STFS491_ROOT_CAUSE_DMA_STACK_CORRUPTION", "scope": "Spark MINI (bootloader/app, platform-agnostic)", "fact": "In Spark MINI's JUMPTOBOOTLOADER handler, I2S DMA (DMA1_Stream3/SPI2/SPI3) was not stopped before jumping to bootloader; on the STM32 build the static DMA buffer i2s2_adc_buf2 at 0x200057C4 sits only 20 bytes from the bootloader's MSP at 0x200057D8, so DMA writes corrupt the bootloader stack and HardFault. This bug is platform-agnostic (not Windows-25H2-specific); fixed in bootloader SystemInit() by resetting DMA/I2S (commit 4d42bfd).", "source": "project_stfs491_root_cause.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "verified"}
```
> 出處原文: lines 42-46; "**與 Windows 版本無關**，debug 25H2 時附帶發現。" (line 48)

```json
{"key": "HW:BOOTLOADER_MSP_GD32_VS_STM32", "scope": "Spark MINI bootloader (feature/spark-10-develop-gd vs feature/spark-10-develop)", "fact": "The GD32 bootloader build has MSP=0x200057D8 while the STM32 bootloader build has MSP=0x20004720, even though the two branches' source is identical except 2 lines of chip selection in the .ewp project file. The root cause of the MSP difference itself is unverified — it needs a clean-build .map file comparison.", "source": "project_stfs491_root_cause.md", "owner": "alice", "captured": "2026-07-17", "ttl": null, "volatile": false, "confidence": "assumed"}
```
> 出處原文: "GD32 build (feature/spark-10-develop-gd): MSP = 0x200057D8" / "STM32 build (feature/spark-10-develop): MSP = 0x20004720" / "兩個 branch source code 完全相同（git diff 只有 ewp 的 chip selection 2 行）" / "差異原因待驗證：需 clean build 兩個 config 比較 .map file" (lines 62-65)

**留在原地:** header 的 "所有分析必須基於此，不可推測" 是 meta 規則（呼應全域 evidence-based-analysis 規則），不是事實本身，留在文件當提醒。「影響矩陣」表格（Mac/Win25H2前/Win25H2 三欄）是上面 3 個 root cause fact 的重新排版摘要，內容已被涵蓋，不重複造 fact 以免同一資訊有兩個不同 key。

**不確定的地方:** 這份文件本身沒有寫入時間戳（不像其他 6 份都有明確日期），`captured` 一律用 fallback 2026-07-17（今天）；文件系統顯示它是「87 天前」的記憶，實際分析日期可能更早，建議人工核對 STFS-491 JIRA ticket 找出真正的分析日期來替換。`HW:BOOTLOADER_MSP_GD32_VS_STM32` 明確標成 `assumed`，因為文件自己說原因「待驗證」——這條的價值僅止於記錄「這個差異被觀察到、但原因不明」，不能被當成已解釋的結論使用。

---

## 總結

| 檔案 | 判定 | facts 數 |
|---|---|---|
| project_fwp791_ota_analysis.md | state-only | 0 |
| project_fwp791_test_params.md | split | 3 |
| project_fwp814_spark_integration.md | split | 10 |
| project_reactorfwupdater_consolidation.md | split | 2 |
| project_release_20260703_ota_staging.md | state-only（1 條流程性質的邊界 fact） | 1 |
| project_spark_gen1_vs_reactor_distinct.md | fact-only | 8 |
| project_stfs491_root_cause.md | fact-only | 4 |

**Total facts proposed: 28**（2 個檔案判定 state-only / 幾乎無 durable fact：`project_fwp791_ota_analysis.md` 完全 0 條，`project_release_20260703_ota_staging.md` 僅 1 條屬性偏 rule 的邊界案例）。
