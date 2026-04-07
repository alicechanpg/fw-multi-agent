# Session Handover (mybot) — 2026-04-07 17:40

## Done
- JIRA 查詢：Alice 近期更新的 tickets (FWP-758, SG-7, FWP-739)
- ReactorFwUpdater 全面資訊收集（JIRA FWP-744 + CDP-89、Slack 對話 3/11~4/2、PM Spec、Figma）
- VS2022 BuildTools 安裝完成（winget, MSVC 14.44）
- FW binaries 設定：R50 MCU v0.1.4.123 + ESP32 rev656
- R100 FW binaries 從 Jenkins 下載（REACTOR_AMP_FW #147, REACTOR_ESP32_FW #47）
- Teo's patch apply（tar 解壓 + 手動 apply 文字改動）
- 雙版本 build 成功：Reactor 50 + Reactor 100 Firmware Updater.exe
- Figma 設計稿對照、Release 流程確認（signed exe + zip + S3）
- 實機測試：ESP32 更新成功、CDC 版本查詢成功（MCU 0.1.4.123, ESP 656）、DFU 進入 ack OK
- 發現並修復 3 個 bug + 1 個 flow 改善：
  1. allHavingDriver() 空集合 → 加 found flag
  2. EnterDfuState sleep 1500→3000ms
  3. DfuWrapper retry 4→10
  4. CheckUsbDriverState 加 15s polling
- JIRA 更新：FWP-744 x4 comments, CDP-89 x1 comment

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| DFU driver 安裝 (libwdi) | 改了未驗證 | 跑 updater 看 CheckUsbDriverState log |
| MCU DFU flash | blocked | driver 問題先解決 |
| loading_loop_rim.png | 未補 | 從原始 repo 取 |
| macOS build | 未開始 | 需 Mac |
| Reactor 100 rebuild | 未做 | bug fix 後重 build |
| Code uncommitted | 7 files changed | commit 或讓 Teo review |

## Environment
- Repo: D:\mybot\git\ReactorFwUpdater, branch dev @ 86e3027 + patch + fixes (uncommitted)
- Build: build-reactor50/, build-reactor100/
- Hardware: Reactor 100（FW 枚舉為 Reactor 50 PID 0503/0507）
- USB Relay: COM3 (OFF), Reactor CDC: COM15, Spark 2: COM26+COM28
- VS2022 BuildTools, CMake 4.3.0, JUCE 8.0.7

## Notes for next session
- 核心問題：DFU WinUSB driver 沒裝，libwdi 自動安裝未驗證
- 快速驗證：啟動 updater → Next → 看 log "DFU device found/needs driver"
- 備案：Zadig 手動裝 WinUSB for 295D:0504
- Reactor 100 硬體的 FW USB descriptor 是 R50 PID，用 R50 Updater 測
- ESP32 被刷了多次 R50 FW，之後要用 R100 FW 刷回
- Figma: HBmPjtD9LmvZqCNrCdzabi node 236:10364
- PM Spec: Google Doc 1j4qQUoS_KDNVMMhG_xRGcJXWH8yoWI3Vl8pLdsJ9AdI
