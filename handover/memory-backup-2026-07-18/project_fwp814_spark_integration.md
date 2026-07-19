---
name: project_fwp814_spark_integration
description: FWP-814 把 Spark LIVE/2/EDGE 併進 ReactorFwUpdater 的整合方向與決策
metadata: 
  node_type: memory
  type: project
  originSessionId: 5478b7d1-f3c9-4d30-ba24-bf7bb13251a4
---

**FWP-814**：把 Spark LIVE / Spark 2 / Spark EDGE 韌體更新併進 **ReactorFwUpdater**，整成一套 unified updater，淘汰常出 bug 的舊 `SparkLiveFwUpgradeLauncher`。相關 [[project_reactorfwupdater_consolidation]]。

**Alice 拍板的方向（2026-07-09）**：
- 裝置偵測用 **USB Audio PID 當錨點**（對應 Reactor 的 BT Audio PID），**不是** DFU PID。
- 分流 `isSparkFlow()`＝**偵測到產品 config 的 `cdcPid` 是否為空**，不是即時偵測 CDC。目前 spark config `cdcPid=""` → 手動（提示同時按 power+pair 到 LED 閃）；Reactor 有 CDC 才自動進 DFU。**（2026-07-10 Alice 澄清）「無 CDC」≠「就是 Spark」：新 Spark 系列硬體其實有 CDC；Reactor MCU 變磚時 CDC 也不列舉（故障，非產品判斷）。**
- 架構走 ReactorFwUpdater（unified，runtime 分流 `isSparkFlow()=cdcPid.empty()`），不照 SparkLive 手動 per-product 做法。
- 先做 Spark 2，Live/Edge 之後。

**VID/PID（Ken Hung sheet 7/6 + 原始碼驗證）**：audio / DFU / VID 全 0x295D — LIVE 0x0221/0x0222、Spark2 0x0231/0x0232、EDGE 0x0251/0x0252。最新版本：Spark2 2.7.2.200/rev490、LIVE 2.9.4.209/rev498、EDGE 2.10.1.86/rev498。

**Canonical branch = `feature/FWP-814-spark-unified`**（最新 +1547 行）。已做 products.json spark 條目、ProductConfig、findSparkPid、EspWrapper port-optional、ManualDfuState、15 張 assets。**但它偵測用 DFU PID，要改成 audio-anchor**；且手動 DFU 提示文字錯（現寫「PAIR+插 USB-C」，要改回 SparkLive 產品專屬「hold power+pair until LED blinks」）。其他分支（spark-products #ifdef 版等）建議收斂淘汰。

**計畫文件**：`docs/FWP-814-spark-integration-plan.md`，已進 **PR #12**（base main，assign Alice，待她 merge）。舊的 per-product design doc 在 `D:\mybot\docs\FWP-814-spark-products-in-reactor-updater.md`（已被 unified+audio-anchor 方向取代）。

**Jenkins（重要更新 2026-07-10）**：Alice 要**分開的新 job**（reactor+spark 統一，不動已 release 的 `REACTOR_FW_UPDATER_WIN_OSX`）。已建 **`REACTOR_SPARK_FW_UPDATER_WIN_OSX`**（copy 自 reactor job）。**build #1 = SUCCESS**（跑 `feature/FWP-814-audio-anchor`、`PRODUCT=reactor`、TRIGGER_OSX=false、SIGN=false）→ 證明 audio-anchor code 能編譯、不破壞 reactor build，產出 Win normal+skip 兩個 artifact。
- Jenkins 認證：`curl -u alice.chan@positivegrid.com:$(cat tool/.jenkins-token)`；POST 要 CSRF crumb（`/crumbIssuer/api/json`）+ cookie jar。**copy 出來的 job 會卡 buildable=false**，解法：刪掉、改用 `createItem?name=X` 帶 config.xml body 建立。curl 帶 `[]` 的 URL 要加 `-g`。
- **✅ 統一 build + 4 outputs 完成（2026-07-10，已驗證）**：branch 加 `PRODUCT=all` commit（一顆 exe 打包 Reactor R50/R100 + Spark 2/LIVE/EDGE 全韌體，用 SPARK_II/LIVE/EDGE_FW + SPARK_ESP32_FW 下載進 `Images/<product>/`）。建了 mac companion **`REACTOR_SPARK_FW_UPDATER_OSX`**；WIN+OSX 兩 job 的 build step 都加了 skip_esp32 第二 pass。**4 個 output 全綠**：WIN #5=win normal+skip、OSX #3=mac normal+skip。build 描述列各產品 MCU×ESP 版本。JIRA comment #91852。
- Jenkins config.xml 編輯教訓：POST 前**先本地 XML 驗證**；python 字串路徑別用 `\b`/`\f`（被當跳脫→控制字元），改 `/` 再 `.replace('/',chr(92))`，或用 ElementTree（勿手塞 `&amp;`）。
- **仍尚待**：Spark 三型號 + Reactor 實機驗證、signed release、PR #13 merge。
- Code：PR #13（audio-anchor，format-check 綠，未實機驗）、PR #12（plan+Jenkinsfile 草稿）。FWP-814 ticket 標「完成」但實際還在收尾。

**Branch topology（2026-07-10 Alice 講明）**：主要 code 分支 = `feature/FWP-814-audio-anchor`（base = `feature/FWP-814-spark-unified`），Jenkins `REACTOR_SPARK_FW_UPDATER_WIN_OSX/_OSX` build 這條，PR **#13 = audio-anchor → spark-unified**（code PR）。文件 PR：**#12** `docs/FWP-814-spark-integration-plan`、**#11** `docs/agentic-governance-claude-md`（與 build 無關）。subagent 在獨立 worktree 動 audio-anchor（含讓單一 exe 裝全產品的 CMake）。

**audio-anchor 已實作（原 spark-unified 的 TODO 已完成）**：`findSparkPid` 改掃 USB Audio PID `{0221,0231,0251}`、`detectBySparkPid` 吃 audio PID、products.json 加 `audioPid`、手動 DFU 文字改成正確的 `Hold the power button and pair button of [product] until the power LED starts blinking.`。state machine 不變。

**PR #12 bot feedback（gemini）已處理（2026-07-10）**：3 findings 中 2 個是 bot 對 `main` 誤判（getProductConfig 已 runtime 動態、EspWrapper 已 port-optional，都在 spark-unified/audio-anchor 成立），1 個（燒錄順序）是真 doc 錯字已修。已回 3 threads。

**技術流程文件**：`docs/FWP-814-update-flow.md`（PR #12，給 PM/RD lead，mermaid + file:line 證據）+ Claude Artifact 渲染版；PR #13 有指向它的 comment。**PM 已確認**：燒錄順序 ESP32 先/MCU 後、手動文字、audio-PID 錨點；精簡版（`SKIP_ESP32` MCU-only）= 所有產品、PM/support 保險需求。**已記錄的 code 缺口（未做）**：① 全產品改用 esptool 原生自動偵測（免 --port）；② ESP32 失敗/無 CDC 時仍能救 MCU（現在只 Retry、到不了 DFU，"CDC fail→skip-esp32" 不成立）——待 audio-anchor code 側跟進。

**統一偵測設計方向（2026-07-10 Alice 定稿）**：所有機型都「以 audio 裝置的 USB parent 為 anchor，ESP32（及有 CDC 機型的 CDC）挑同 parent 的」。Reactor **已成立**（`getBtAudioHubId`→`setAnchorHubId`→`pickByAnchorHub`/`isOnSameHub`→`getEspPort` 比對 parent/grandparent）。**Spark 待做**：新增取 Spark USB Audio parent 的函式（比照 getBtAudioHubId 用 audioPid）、ESP32 改錨在 audio parent（取代 esptool 全域偵測）、win+mac 都要改、Spark 無 CDC 沒關係。⚠️ **前提未驗**：Spark ESP32 是否與 USB Audio 同 USB parent——Alice 口頭確認架構如此，但**無實機驗證**（Alice 親口說 Spark 沒實機驗過）。

**JIRA FWP-814（2026-07-10）**：狀態改 **完成→進行中**（transition id 31 / status 10070）；assignee 本來就是 Alice；已加 comment 附 update-flow.md 連結。

**Jenkins 兩個 job 的 BRANCH choices（2026-07-10 實查）**：`REACTOR_SPARK_FW_UPDATER_WIN_OSX` **含** `feature/FWP-814-audio-anchor`（audio-anchor 要 build 用這個）；`REACTOR_FW_UPDATER_WIN_OSX`（released）**不含**（只有 dev/main/feature/skip-esp32-update/feature/mcu-version-gate）——在後者 build audio-anchor 需先改該 job config.xml 加 branch，屬動到 released job，未經明確同意不做。**（Alice 後來確認：用 `REACTOR_SPARK_FW_UPDATER_WIN_OSX` build 即可，該 job ready。）**

**Spark ESP32 audio-parent 偵測已實作 + build 綠（2026-07-10，PR #13）**：commits `d021ae7` + `449c6f6`（fix）on `feature/FWP-814-audio-anchor`。新增 `usb::getSparkAudioHubId`（掃 Spark USB Audio PID 取 USB parent）+ `cdc::getSparkEspPort`（挑同 hub 的 ESP32，`isOnSameHub`）；CoreStates Spark 分支改傳此 port（nullopt 時 EspWrapper 仍 auto-detect，向後相容）。**Windows 完整實作；macOS 缺 primitive（`getBtAudioHubId`/`isOnSameHub` 在 mac 是 stub）→ Spark 走單一 port/auto-detect**。agent review = compile-clean。Build `REACTOR_SPARK_FW_UPDATER_WIN_OSX`：**WIN #7 + OSX #5 = SUCCESS**（SIGN=false）。⚠️ Spark ESP32↔USB Audio 同 parent 拓樸**未 HW 驗**（Alice 口頭確認架構，週一實機驗）。
- **firmware-versions.txt manifest**：`cmake/WriteFwManifest.cmake` + PostBuild，記 updater 版本(PROJECT_VERSION=1.0.0 hardcode) + 各產品 MCU/ESP 版本。
- **mac codesign 教訓**：POST_BUILD 產生的檔案**不可放 `$<TARGET_FILE_DIR>`（mac .app 上 = Contents/MacOS）**，codesign 會拒（"code object is not signed at all"）。要放 Images output dir 的 parent（Win=exe 旁 / mac=Contents/Resources）。build-loop 第一輪(OSX #4)就是踩這個。
- **仍待辦**：Spark 實機驗證。

**Updater 版本控管 + 打包韌體 README 完成（2026-07-12，PR #13）**：commits `2bf399c` + `ebcf7fc` on `feature/FWP-814-audio-anchor`。
- **輸出檔名帶 updater 版本**：版本命名邏輯在 **repo 的 `Tools/build_windows.bat` + `Tools/build_macos.sh`**（Jenkins job 只呼叫它們 + 加 `_win`/`_mac`，config 不用改）。單一 Reactor build 維持 `v<mcu>_esp_<esp>`；**unified（`PRODUCT=all`）改用 updater 版本 `v<updater>`**（來源 `CMakeLists.txt` `project(VERSION 1.0.0)`；CMake 產生 `updater-version.txt` 給 script 讀）。修掉原本 unified 誤用 reactor-50 fw 版本。實測輸出 `Reactor Spark Firmware Updater v1_0_0_{win,mac}.zip`(+`_skip-esp`)。
- **`firmware-versions.txt` = 打包韌體 README**：README 風格、友善產品名、列 updater 版本 + 各產品 MCU/ESP（同 Jenkins 描述）。`cmake/WriteFwManifest.cmake` 也寫 `updater-version.txt`。README.md 已記兩種命名。
- **PR #13 review = gemini-code-assist bot（沒有真人 Robert；Alice 口中的「Robert」= 這個 review bot）**。唯一 HIGH：手動 DFU 文字 `starts blinking` → `lights up in white`（bot 引官方文件；原字來自淘汰的 SparkLive launcher）。已修 `ebcf7fc`。⚠️ **與 Alice 先前確認的「blinking」相反**——已在 PR/JIRA 標明，若實機是閃爍要改回。
- Build 全綠：WIN #7/OSX #5（偵測+manifest）、WIN #8/OSX #6（updater 版本命名）、WIN #9/OSX #7（Text 修正）。build-loop 自主跑到綠（第一輪踩 mac codesign）。
- **version.txt 慣例（build script 讀）**：Win=`%BUILD_DIR%\...`（exe 旁）、mac=`.app/Contents/Resources/`；updater-version.txt 同處。

**燒錄進度百分比 + DFU LED 文字更正（2026-07-12，PR #13，commit `5e03e4a`，build 綠 WIN#10/OSX#8）**：
- **燒錄 %**：`Subprocess` 加 optional `OutputCallback` 串流工具輸出 + `parseLastPercent()`；`esp/dfu::updateFirmware` 加 `onProgress(int)`（解析 esptool/dfu-util `%`）；`UpdateCoreState`/`UpdateFwState` 經 `MessageManager::callAsync`（**capture `MainComponent*` by value，不可 capture task-local reference**）→ `MainComponent::setUpdateProgress` → UpdateView subtitle 顯示 `NN%`。未帶 callback 行為不變。附帶修掉 64KB buffer 1-byte overflow（read 改 `size-pos-1`）。
- **【DFU LED 定論，bootloader 原始碼查證】進 update mode 時 power LED = 呼吸白燈（breathe white），不是閃爍、也不是恆亮**。firmware 用 `set_led_breath(LED_COLOR_WHITE)`：`spark-ii-fw PowerManager.cpp:729`、`spark-pedal-fw :623/715/1806`、`reactor-fw :624`；觸發＝`EVENT_BUTTON_BT_PRESET_COMBINATION_HOLD`→"BT UPGRADE MODE"。updater 文字定為 **"until the power LED breathes white"**（先前「blinking」來自淘汰 SparkLive、gemini 建議的「lights up in white」皆不準）。**這覆蓋先前 memory 說 Alice 確認 blinking——正解是 breathe white。**
- **按鍵**：Gen2 全部是 power+pair；只有 **Reactor 的 power 是 switch，其餘（Spark 2/LIVE/EDGE）是 power button**（走 CDC 自動的 Reactor 不顯示這段手動文字）。updater 文字「power button and pair button」對 Spark 正確；Reactor 手動文字＝「power on while holding pair button」（Alice 確認）。
- **Reactor update-mode LED（bootloader）**：`reactor-fw update_sequence_1() PowerManager.cpp:717-718`＝**WiFi LED 呼吸白 + BT LED 閃藍**。**（2026-07-12 已修 commit `09aefe9`）** Reactor 手動文字改成「until the Wi-Fi LED breathes white」。**全機型定論：白燈都是 breathe（Spark=BATT、Reactor=WiFi），沒有 blink white；只有 BT 閃藍。** Spark 文字「power LED breathes white」本來就對。

**工具錯誤引導 + per-device 測試案例（2026-07-12，PR #13）**：
- **測試案例** `docs/FWP-814-test-cases.md`（commit `0d2f25e`）：Reactor + Spark 2/LIVE/EDGE，涵蓋偵測錨點/自動vs手動DFU/LED/燒錄順序/%/檔名/manifest/skip-esp32 + 工具錯誤引導（E-BUSY/NODEV/BOOT/FATAL/UNKNOWN）。
- **工具錯誤引導**（commit `7510a37`）：`Source/wrapper/ToolError.hpp classifyToolError()`（header-only inline）比對 esptool 4.7.0（`esp-idf/.../esptool/loader.py`）+ dfu-util 字串 → 失敗畫面在 `Exxx` code 之上顯示可操作引導；無法辨識則退回通用。`esp/dfu::updateFirmware` 加 `std::string* outErrorHint`；`TaskFinished` 帶 hint → `FailureState`(加 optional hint，thread 過 copy/move ctor) 顯示。原始輸出仍只進 log。
- **esptool 原始碼位置**：`C:\Users\alice\.espressif\python_env\idf5.0_py3.11_env\Lib\site-packages\esptool\`（`esp-idf/components/esptool_py/esptool/esptool.py` 只是 launcher stub）。
- **Build 累積**：WIN #7/OSX#5(偵測+manifest)、#8/#6(版本命名)、#9/#7(LED breathe white)、#10/#8(flash %)、#12/#10(錯誤引導)、#13/#11(Reactor LED text)、#14/#12(引導文字加步驟)、#15/#13(review fixes)。**Jenkins OSX 偶發 transient**：mac agent SSH 抓 `fmt` submodule 失敗 → 直接 retry 整個 WIN_OSX job 即可（#9 踩過）。
- **工具錯誤引導文字**：cause-matched、cheapest-fix-first、restart PC 只當 escalation（commit `54d9311`）。
- **Review fixes（commit `826d916`）**：① flash progress callback 改用 `juce::Component::SafePointer`（message thread 建、callAsync 內檢查）修掉關窗中途燒錄的 use-after-free；② `Subprocess.cpp` 加 final drain read（收尾補抓 keyword/error line）。
- **gemini code-review bot 已 sunset**（2026-07-17 停）：`/gemini review` 不再回應。PR review 改自己跑 subagent holistic review。
- **已知待辦（deferred，非阻塞）**：`parseLastPercent` chunk-split 進度偶爾閃動（cosmetic；monotonic 修法會壞 esptool per-image reset）。
- **✅ 單一來源 Spark audio PID（commit `3638436`，build #16/#14 綠）**：新增 `product::getSparkAudioPids()`（從 3 個 spark config 的 `audioPid` 欄位 derive）；`findSparkPid`(win/mac)、`getSparkAudioHubId`(win)、`detectBySparkPid` 都改讀它，不再硬寫 0x0221/0x0231/0x0251。behavior-preserving；改 products.json `audioPid` 現在真的生效。`UsbDriverWrapper_{win,mac}.cpp` 改 include `ProductConfig.hpp`（PRODUCT_* macro 是 target-wide，OK）。
- **✅ Updater 版本改 git-commit-count（commit `d18e0fb`，build #17/#15 綠）**：之前 `project(VERSION 1.0.0)` 寫死→每個 build 都 v1_0_0。改成 **mirror reactor-fw**：`CMakeLists.txt` configure 時 `git rev-list --count HEAD`，version = `MAJOR.MINOR.(count/256).(count%256)`（MAJOR.MINOR 手動）。非 git checkout fallback `.0.0`。4-part PROJECT_VERSION 帶動 updater-version.txt/manifest/檔名；macOS `CFBundle*Version` 保持 3-part（Apple 上限）。實測檔名 `v1_0_0_78`（count=78），每 commit 遞增、可溯源。
- **Jenkins build 描述加 updater 版本（2026-07-13，改 job config，非 repo）**：`REACTOR_SPARK_FW_UPDATER_WIN_OSX`（batch `extract_versions`）+ `REACTOR_SPARK_FW_UPDATER_OSX`（bash `emit_desc`）都在描述最上面（Reactor50 行之前）加一行 `Firmware Updater: 1.0.<count/256>.<count%256>`，用 `git rev-list --count HEAD` 現算（跟 CMake/檔名同值）。實測 WIN #19/OSX #17 描述顯示 `Firmware Updater: 1.0.0.79`。**改 config.xml 方法**：fetch → ElementTree 改 `<command>`.text（batch 別在 python 字串放 `\`，會 unicodeescape 爆；bash 用 `/` 免煩惱）→ `tree.write` → POST `config.xml`（帶 crumb + cookie，Content-Type application/xml）→ fetch back 驗證。原始 config 備份在 scratchpad。
- **reactor-fw 版本機制（參考）**：`Appli/Source/Applications/version.h` 放 MAJOR/MINOR + `GIT_COMMIT_COUNT 0`(佔位)；`REACTOR_AMP_FW` Jenkins build step 用 `git rev-list %GIT_COMMIT% --count` 改寫 version.h 的 GIT_COMMIT_COUNT；版本字串 = `MAJOR.MINOR.(count/256).(count%256)`（例 0.1.4.171 = commit 1195）。
