# MyBot Workspace Memory

## 專案狀態

| 專案 | 路徑 | 狀態 |
|------|------|------|
| reactor-fw | `D:\mybot\git\reactor-fw\` | **主要 STM32 repo**（活躍） |
| pg-reactor-esp32-wifi-bt | `D:\mybot\git\pg-reactor-esp32-wifi-bt\` | 活躍 |
| reactor-50-100-fw | `D:\mybot\git\reactor-50-100-fw\` | **已停用**（2026-05-20） |
| ReactorFwUpdater | `D:\mybot\git\ReactorFwUpdater\` | FWP-744 / FWP-814 |

## AI Collaboration Mode（最重要的規則）

- [**【鐵律1】AI Collab 改用自己 review**](feedback_ai_collab_mode.md) — 不管大小事都先自己 review 再回報，無例外
- [**【鐵律2】不推測用證據**](feedback_evidence_based.md) — 每個結論附 file:line；說「應該」之前先用工具驗證
- [**嚴禁推測（加強版）**](feedback_no_guessing_strict.md) — 連假說都不要在回報時提，先驗證再說
- [**「我沒驗證到」≠「沒發生」**](feedback_not_verified_vs_untested.md) — 對外記錄不可把「我這邊沒看到」寫成「未驗證/pending」；狀態先問第一手
- [**對外連結送出前先驗證**](feedback_verify_urls_before_sending.md) — Slack/JIRA/PR 的 URL 先用 `gh api html_url` 核對；懂 private repo 假 404
- [**Self-review 要做兩輪**](feedback_double_review.md) — 第一輪審初稿，第二輪審修正版
- [Review 必須實際驗證](feedback_subagent_must_verify.md) — 查原始資料，不能只重讀自己的字
- [JIRA comment 只需一輪](feedback_jira_one_review.md) — 降為 L2
- [被挑戰時不要直接改結論](feedback_challenge_before_changing_conclusion.md) — 改結論是新產出，要先 review

## Session Audit

- [**Session 全程記錄由 hooks 保證**](project_session_audit_hooks.md) — 不靠 Claude 記得；`latest-mybot.md` 沒寫會 exit 2 叫我補寫（2026-07-16）

## 用戶偏好

- [**技術決定我自己做，不要丟回去問**](feedback_max_autonomy_drive_to_done.md) — 用戶不讀 code；approve 桶只留不可逆/對外的事
- [不要停下來問，該做就做](feedback_dont_stop_to_ask.md) — 完成 milestone 自動 update JIRA / handoff / 下一步
- [每次 prompt 先自我 review](feedback_prompt_self_review.md) — 先重述範圍/輸出/限制；也 review command 本身
- [必須先討論再動手](feedback_always_discuss_first.md) — 建新檔/command/hook 前先討論
- [**要 review/決定的都傳 Slack**](feedback_route_decisions_to_slack.md) — Alice DM `U04NS4ZFW5R`，她常手機看
- [**選擇題必附建議+pros/cons**](feedback_choices_need_recommendation_procons.md) — Slack 或 cmd 都一樣；只丟選項不行（2026-07-18）
- [Design docs 必須在 repo](feedback_design_docs_in_repo.md) — 放 `docs/{JIRA-ID}-*.md`
- [不自己修無關的 bug + 修 bug 一定 report](feedback_no_code_changes.md) — 相關的可修但要回報
- [不可用「不影響功能」當藉口](feedback_no_excuse_functionality.md) — 可見異常要修乾淨，不能標 PASS
- [說做不到前先找替代方案](feedback_check_before_saying_cant.md) — API token / curl / workaround
- [不要反覆搜尋已知資訊](feedback_stop_searching_known_info.md) — Jenkins token / DFU 參數直接讀 memory
- [PR push 後回看 bot 回饋](feedback_check_pr_bot_feedback.md) — 看 CI checks / review bot 留言
- [驗證 Jenkins 要看網頁](feedback_check_jenkins_web.md) — curl 抓 HTML，不能只看 API JSON
- [JIRA 查詢要包含 SG board](feedback_jira_boards.md) — FWP + RAD + SG
- [組織架構不可寫到 JIRA](feedback_no_org_chart_jira.md) — 只存 memory
- [Bash 路徑用 forward slash](feedback_forward_slashes.md)
- [STM32H7R3 vs STM32H750 完全隔離](feedback_stm32h7_chip_isolation.md) — Anti-Hallucination 優先於 DRY
- [用 Notepad++，不用 VSCode](user_no_vscode.md)
- 所有 Agent 模型維持 opus，不降級
- **禁止自動在 RAD board 開 JIRA issue**（2026-03-06）

## 團隊成員

- [FW Team 組織架構](user_team_hierarchy.md) — Teo (leader) → Nathan → Calvin (CEO)
- **Teo Hsieh** — FW Team Leader，Alice 直屬主管｜**Bo Chiu** — iOS｜**Ian Lin** — Android｜**Chiyang** (chiyang.huang) — App Manager
- [WeiTing Chen — Support Team (male)](user_team_weiting.md) — 不是 QA
- [Willow Tu — PM](user_team_willow.md)

## ReactorFwUpdater (FWP-744 / FWP-814)

- [FWP-744 環境建置](project_fwp744_reactor_updater.md) — Build 環境、Jenkins jobs、patch 狀態
- [**FWP-814 Spark 併入 ReactorFwUpdater**](project_fwp814_spark_integration.md) — audio anchor、無 CDC 手動 DFU、unified 架構；PR #12
- [ReactorFwUpdater 已 Fable 治理整理](project_reactorfwupdater_consolidation.md) — 2026-07-09 完成
- [ReactorFwUpdater bundle 結構與 PID](reference_reactor_updater_bundle.md) — Reactor CDC 0506→0507 是 fw 升級正常變化
- [Spark Gen 1 ≠ Reactor](project_spark_gen1_vs_reactor_distinct.md) — chip/架構/協定都不同；Reactor updater cmd 走 CDC+DFU（SysEx over CDC，非 USB-MIDI class）；裝置本身有 UART MIDI
- VS2022 BuildTools 需 admin（`setup_env.ps1` 已備好）；**MSYS2 MinGW64 gcc 壞了**；無 host C++ compiler / 無 qemu / **無 jq**

## USB 架構與 PID（Reactor + Spark）

- [**共用 USB hub 架構 + 3-case 偵測**](reference_pg_usb_hub_architecture.md) — hub 下有 MCU/ESP32/BT Audio；audio=接USB、ESP32 或 DFU=power on；**Spark 無 CDC**；**audio anchor 的 VID 不一定是 295D（LIVE = C-MEDIA `0d8c:0033`）**
- [**PID_0503 是 Actions BT Audio chip，不是 MCU**](reference_reactor_usb_pid_chip_map.md) — 0503 active 不代表 MCU 活著
- [**各產品 DFU bootloader = `*-external-loader` repo**](reference_dfu_bootloader_repos.md) — 非 app fw、非 .stldr；含 DFU-mode LED ground truth
- [Reactor ESP32 EN pin 由 STM32 控制](reference_reactor_esp32_power.md) — cold boot 後才是燒 ESP32 的時序窗

## Jenkins / Flash 工具

- [**Jenkins build 一律 TRIGGER_OSX=true**](feedback_jenkins_trigger_osx_default.md) — 不主動傳 false；交付用 SIGN=true（2026-07-16）
- [**統一版 job = `REACTOR_SPARK_FW_UPDATER_WIN_OSX`**](reference_reactor_spark_updater_jobs.md) — PRODUCT=all；≠ 舊的 reactor-only `REACTOR_FW_UPDATER_WIN_OSX`；版本欄位空白=最新
- [空版本要先 trigger firmware build](feedback_auto_trigger_fw_before_updater.md) — 先 build AMP+ESP32 再打 updater
- [DFU Flash 完整參考](reference_dfu_flash.md) — DFU 指令、Jenkins URL/token、產品 PID 對照表
- [JAMUP_SPEAKER_FW_TOOL_WIN 參數](reference_jenkins_speaker_fw_tool.md) — BUILD_TARGET 預設 Spark_GO！要用 POST body 傳 Spark_MINI
- `BRANCH` 是 **Choice**（清單外的值 Jenkins 一定 400）；要別的 branch 得先改 job config.xml
- Jenkins token `D:\mybot\git\tool\.jenkins-token`；DFU `flash-dfu-stm32.ps1`；ESP32 `flash-esp32.ps1`；binary 暫存 `release-binaries\`

## Reactor Hardware / Flash Rig

- [Reactor STLink flash 完整指令](reference_reactor_stlink_flash.md) — port=SWD ap=1 mode=UR + ext-loader stldr，不要 mass-erase
- [Reactor H7R3 ExtMemLoader stldr](reference_reactor_extmemloader_stldr.md) — `reactor-fw\ExtMemLoader\Debug\*.stldr`
- [Flash 後必須 USB Relay 重開](feedback_flash_reset.md) — NOR Flash 燒完要 power cycle
- [USB Relay pulse 留 OFF state](reference_usb_relay_pulse_off_state.md) — pulse 後要 explicit `-Action on`
- [Power cycle 後要看電壓](feedback_check_voltage_after_power_cycle.md) — 用 Get-PnpDevice 確認裝置出現
- [**Production STM32 沒有 UART log**](feedback_production_stm32_no_log.md) — stress test 必須用 local server + debug fw
- [OTA 後記得燒回 debug 版](feedback_reflash_debug_after_ota.md)
- [Spark 系列需要手動開機](reference_spark2_boot.md) — Spark 2 + GO，flash/power cycle 後要按 power button
- [Spark 2 firmware log patterns](reference_spark2_log_patterns.md) — 關機以 `DataManager file operations are completed.` 為最後一行

## COM Port 配置

| 設備 | Port | Baud | 用途 |
|------|------|------|------|
| STM32 (STLink VCP) | COM4 | 921600 | Debug serial（需 debug build） |
| Reactor CDC | COM6 | - | USB CDC (295D, 0506/0507)，App 正常模式 |
| ESP32 | COM7 | 115200 | Debug serial（與 flash 共用） |
| USB Relay | COM3 | 9600 | **Reactor** MCU reset |

> Port 號碼會因重插而變（COM4↔COM50）｜**COM7 出現 = ESP32 已通電**｜抓 log 時要先停 logger 再 flash
> App debug log 只在 APP_DEBUG mode 輸出 UART；release build 不輸出
> Bootloader 量產版 0.1.0.39（給國光）；0.1.0.0 = local build

## Build 工具

- STM32 build script `D:\mybot\git\tool\build-stm32.ps1`（是 `tool` 不是 `tools`）；原指向已停用的 reactor-50-100-fw，現用 `reactor-fw`
- CubeIDE headless build 可能因 workspace lock 失敗 → 改直接用 make（`/c/ST/STM32CubeIDE_1.16.1/.../make.exe`、`arm-none-eabi-gcc.exe`）
- `capture-boot-log.ps1` — 自動 build/flash/抓開機 log｜`qa-log-patterns` skill（stm32-boot, esp32-boot, error-signatures）

## 進行中的分析 / Release

- [**Reactor SPI5 已是 DMA，Mini2 BDMA fix 不需移植**](project_reactor_spi5_already_dma.md) — 判定 (c)，2026-07-18 已驗證；含下個產品檢查清單

- [**FWP-791 ST_SEND_IMG 分析結論**](project_fwp791_ota_analysis.md) — server 端無法重現；健康設備 SDNAND max=29ms；需問題設備
- [FWP-791 測試參數](project_fwp791_test_params.md) — chunk-size=127 + stall>7s 才觸發 partial read
- [**STFS-491 三個獨立 Root Cause**](project_stfs491_root_cause.md) — App deadlock + Bootloader descriptor + DMA latent bug
- [**Release 2026-07-03 OTA staging**](project_release_20260703_ota_staging.md) — 0.1.4.171 + ESP32 rev686；等 QA 過用**同 build** 跑 TO_PRODUCTION=true
- [Release 2026-05-22](project_release_20260522.md) — R50+R100 → OTA staging → Updater Win+Mac
- [**Scrum digest Cloud Routine 已上線**](project_scrum_digest_routine.md) — 每 5hr 發繁中 digest 到 Alice DM；report-only

## 外部系統 / 其他

- [**Chiyang 的 bot machine / A2A 計畫**](project_chiyang_bot_machine_a2a.md) — reactor-app-bot（#reactor-bot-小天地）強 App 弱 FW；我們的 FW agent 是缺的那塊；Alice 已承諾支援

- [Google Drive 老闆可見](reference_google_drive_visibility.md) — 適合放需主管可見的文件
- [**Drive connector 傳不了大二進位檔**](reference_gdrive_upload_limit.md) — 只收 inline base64；>~140KB 走 Google Doc 轉檔或手動拖
- Team Monitor 用 SQLite `D:\mybot\.claude\db\team-monitor.db`；**環境沒 sqlite3 CLI，要用 Python**；knowledge.db 31 筆
- 2026-02-25: EA Agent → Team Monitor Agent（私人特助 → 團隊監督）
