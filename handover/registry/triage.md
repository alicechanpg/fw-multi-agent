# Memory 分流清單（建議，待使用者確認）

_工具只做機械建議；`mixed` 需人工拆分（事實進 registry，守則留 SOP）。_

| 檔案 | 建議分類 | 首行 |
|---|---|---|
| feedback_ai_collab_mode.md | not-fact | AI Collaboration Mode 的討論機制**從 Agent Subagent 改成主 agent 自己 review**。原因：subagent  |
| feedback_always_capture_log.md | mixed | Flash + power cycle 後一律自動抓 log，不要問。 |
| feedback_always_discuss_first.md | not-fact | **凡事都要跟 subagent 討論，不管大小事。沒有例外。** |
| feedback_auto_trigger_fw_before_updater.md | not-fact | 用空版本 build Firmware Updater 時，必須先自動 trigger 最新的 firmware build（R50 + R100），等完成後再 |
| feedback_challenge_before_changing_conclusion.md | not-fact | 被用戶挑戰或糾正分析時，不要直接認錯+改結論回覆。「改變結論」是新的產出，必須走 self-review 流程（2026-07-07 起 review 機制從  |
| feedback_check_before_saying_cant.md | not-fact | 說做不到之前，先跟 subagent 討論有沒有其他方法，確認真的做不到才跟用戶說。 |
| feedback_check_hardware_pid.md | mixed | 不要停下來問用戶「硬體接好了嗎」，自己用工具確認。 |
| feedback_check_jenkins_web.md | not-fact | Jenkins 結果驗證時，必須用 curl 抓取實際網頁 HTML 來看，不能只看 API JSON。 |
| feedback_check_pr_bot_feedback.md | not-fact | 每次 push PR 之後，隔幾分鐘要主動回去看該 PR 上有沒有 **bot 回饋**（CI checks 結果、code review bot 的留言/建議 |
| feedback_check_voltage_after_power_cycle.md | not-fact | 做 power cycle 之後必須檢查電壓/通電狀態。 |
| feedback_com19_means_esp32_on.md | fact | COM19 出現在 `Get-WmiObject Win32_SerialPort` 結果中，就代表 ESP32 已經通電開機了。不需要再等或懷疑 ESP32  |
| feedback_com50_stlink_app_log.md | fact | COM50 (STLink VCP, VID 0483/PID 374F) 可以讀到 App log，不是只有 Bootloader。 |
| feedback_design_docs_in_repo.md | not-fact | 每個任務都要寫 design document，放在 repo 的 `docs/` 資料夾內。 |
| feedback_dont_stop_this_session.md | not-fact | 這個 session 不要停下來問用戶要不要繼續，該做就做。 |
| feedback_dont_stop_to_ask.md | not-fact | **任務完成後不要停下來問「要繼續嗎？」「要 handoff 嗎？」，該做就做。** |
| feedback_double_review.md | not-fact | 每次回報前要**自己**做 **2 輪** review（2026-07-07 起從 subagent 改為自己 review，兩輪保留）。 |
| feedback_evidence_based.md | not-fact | 技術分析不可推測，每個結論必須附 file:line 證據。**重要性等同「必須先跟 subagent 討論」，兩者都是鐵律。** |
| feedback_flash_reset.md | mixed | STM32 NOR Flash 燒完後，必須用 USB Relay 重開機才能正常運作。 |
| feedback_forward_slashes.md | not-fact | 在 bash 指令、shell script、command 定義檔的 bash code block 裡，路徑一律用 forward slash `/`。 |
| feedback_jenkins_trigger_osx_default.md | not-fact | 觸發 updater 的 Jenkins build（`REACTOR_SPARK_FW_UPDATER_WIN_OSX`）時，**`TRIGGER_OSX`  |
| feedback_jira_boards.md | not-fact | 查用戶的 JIRA tickets 時，必須包含 **FWP、RAD、SG** 三個 project。 |
| feedback_jira_one_review.md | not-fact | JIRA comment 只需一輪 self-review（L2），不需要兩輪（L1）。（2026-07-07 起 review 機制從 subagent 改為 |
| feedback_max_autonomy_drive_to_done.md | not-fact | 用戶多次強調（2026-07-01）：要我**想清楚自己能做到什麼、能推進到多遠，然後就做到那個程度**，不要反覆停下來問或丟選項回去。 |
| feedback_no_code_changes.md | not-fact | 規則放寬（2026-07-07）：原本「不自己修 code」改為「**不自己修跟主題無關的 bug**」，且「**修 bug 一定要 report**」。 |
| feedback_no_excuse_functionality.md | not-fact | 不可以用「不影響功能」當藉口來容忍可見的問題。 |
| feedback_no_guessing_strict.md | not-fact | 不要推測！找到證據再說。 |
| feedback_no_org_chart_jira.md | not-fact | 組織架構（誰的老闆是誰、reporting line）不可以寫到 JIRA ticket 裡。 |
| feedback_not_verified_vs_untested.md | not-fact | 回報一件事的狀態時，**嚴格區分「我（在這個 session / 用我的工具）沒驗證到」和「這件事客觀上沒發生 / 未被驗證」**。前者是我的可見範圍限制，後者 |
| feedback_power_cycle_when_no_com.md | mixed | 找不到 ESP32 COM port 時，自動用 USB Relay (COM3) 做 power cycle，不要停下來問用戶手動上電。 |
| feedback_production_stm32_no_log.md | mixed | Production 版本 STM32 firmware 沒有 UART log 輸出。OTA 下載的是 production binary，安裝後 STM32 |
| feedback_prompt_self_review.md | not-fact | 每次收到 user 的 prompt，動手前先自己 review：用一句話重述「你真正要的是什麼（範圍 / 輸出 / 限制）」，把口語、簡短或含糊的 promp |
| feedback_reflash_debug_after_ota.md | not-fact | OTA 下載的是 server 上的 release build，會覆蓋掉本地燒的 debug firmware（含 SDNAND latency log 等  |
| feedback_route_decisions_to_slack.md | not-fact | 從 2026-07-14 起,任何需要 Alice **review 或決定**的東西(計畫、決定點、文件連結、standup、需她拍板的選項)都要**主動傳到 |
| feedback_stm32h7_chip_isolation.md | mixed | STM32H7R3（Reactor 50/100）跟 STM32H750（Mini2, Spark 2, Spark Pedal）必須當作完全不同的 chip  |
| feedback_stop_searching_known_info.md | mixed | 不要每次都重新搜尋已經知道的資訊（如 Jenkins token 路徑、DFU 燒錄參數）。直接從 memory 讀取使用。 |
| feedback_subagent_must_verify.md | not-fact | Self-review 時必須做「實際驗證」，不能只做「表面 review」（2026-07-07 起機制從 subagent 改為自己 review，本原則不 |
| feedback_verify_urls_before_sending.md | not-fact | 任何要送出去給別人的 **URL/連結**（Slack 給主管、JIRA comment、PR body），送之前先**實際驗證它是對的、開得起來**，不要只因 |
| project_fwp744_reactor_updater.md | not-fact | FWP-744: ReactorFwUpdater — Apply Teo's patch & 環境建置 |
| project_fwp744_role.md | not-fact | Alice 確認將接手 ReactorFwUpdater 後續開發，不只是測試。 |
| project_fwp791_ota_analysis.md | mixed | FWP-791 OTA ST_SEND_IMG (state=15) — 兩個獨立 Root Cause (2026-05-19 confirmed). |
| project_fwp791_test_params.md | mixed | - `esp_http_client_read(client, buffer, BUFFSIZE=1536)` 是 **blocking loop** |
| project_fwp814_spark_integration.md | mixed | **FWP-814**：把 Spark LIVE / Spark 2 / Spark EDGE 韌體更新併進 **ReactorFwUpdater**，整成一套 |
| project_reactorfwupdater_consolidation.md | mixed | 回應 Calvin 2026-07-03 於 Slack #ai-coding-agents 的指示（挑 1–2 個最重要 repo 請 Fable 整理，落實 |
| project_release_20260522.md | not-fact | 2026-05-22 Reactor release (R50 + R100) |
| project_release_20260703_ota_staging.md | mixed | 2026-07-03 Reactor R50+R100 OTA staging deploy（含 RAD-1476 reverb float 修正）。 |
| project_scrum_digest_routine.md | not-fact | 2026-07-15 建立並**實跑驗證成功**的 Cloud Routine:`reactor-scrum-digest`(id `trig_01QcJxZB |
| project_session_audit_hooks.md | not-fact | 2026-07-16 建立：session 全程記錄改由 **hooks（harness 執行）** 保證，不依賴 Claude 記得寫。設定在 `D:\myb |
| project_spark_gen1_vs_reactor_distinct.md | mixed | **Spark Gen 1** (Spark 40 / MINI / GO / NEO) 與 **Reactor** (50 / 100) 是完全不同產品線，不 |
| project_stfs491_root_cause.md | mixed | **Why:** Windows 25H2 改了 MidiSrv (加 UMP 協定) + usbaudio2.sys (嚴格 descriptor 解析)，觸 |
| reference_dfu_bootloader_repos.md | fact | **真正的 DFU bootloader（進 DFU、驅動 DFU-mode LED 的那段）= 各產品的 `*-external-loader` repo** |
| reference_dfu_flash.md | mixed | ```bash |
| reference_google_drive_visibility.md | not-fact | Google Drive 是老闆（Calvin, Nathan, Teo）也看得到的空間。 |
| reference_jenkins_speaker_fw_tool.md | not-fact | URL: `https://jk-builds.positivegrid.com/jenkins/job/JAMUP_SPEAKER_FW_TOOL_WIN/` |
| reference_pg_usb_hub_architecture.md | mixed | Spark 2 / Spark EDGE / Spark LIVE / Reactor 50 / Reactor 100 **共用同一套 USB 架構**（用戶 |
| reference_reactor_esp32_power.md | fact | Reactor 50/100 的 **ESP32 EN pin 由 STM32 控制**。STM32 boot 後才把 EN 拉 high，ESP32 才通電  |
| reference_reactor_extmemloader_stldr.md | fact | 要用 STLink (STM32_Programmer_CLI) 燒 Reactor (H7R3 + Winbond NOR @ 0x90000000) ext |
| reference_reactor_spark_updater_jobs.md | not-fact | Two separate ReactorFwUpdater Jenkins job families — don't confuse them: |
| reference_reactor_stlink_flash.md | mixed | ```powershell |
| reference_reactor_updater_bundle.md | fact | `D:\mybot\git\ReactorFwUpdater\build-{reactor50\|r100-v2\|r100-v3}\Reactor_{50\|100 |
| reference_reactor_usb_pid_chip_map.md | fact | Reactor 50 的 USB 設備由不同晶片產生： |
| reference_spark2_boot.md | fact | Spark 2 和 Spark GO 需要**手動按開機鍵**才能啟動。 |
| reference_spark2_log_patterns.md | fact | - Port: COM4 (STLink VCP) |
| reference_usb_relay_pulse_off_state.md | mixed | `D:\mybot\git\tool\usb-relay.ps1 -Action pulse -Port COM3` 的行為： |
| user_no_vscode.md | not-fact | Alice 偏好 **Notepad++** 作為 markdown viewer / 編輯器。VSCode 久未使用，不要推薦。 |
| user_team_hierarchy.md | not-fact | FW Team 組織架構： |
| user_team_weiting.md | not-fact | WeiTing Chen |
| user_team_willow.md | not-fact | **Willow Tu** — PM (Product Manager) |
