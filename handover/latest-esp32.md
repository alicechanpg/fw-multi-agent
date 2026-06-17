# Session Handover (esp32) — 2026-06-17 12:10

## Done
- 分析 Round 4 stress test 結果（delay=100ms）：186 cycles, 185 PASS (99.5%), 0 INFRA, 1 FAIL
- Cycle 81 FAIL root cause 分析：BLE L2CAP congestion（非 race condition），FINISH notification 未送達
- 修改 STM32 OTA progress 100% 跳過 BLE notification（減少 FINISH 前 L2CAP congestion）
- 推 PR #51（fix/RAD-1454-ota-coex-round4），close 舊 PR #50
- 記錄 OTA cycle time：avg 7.0 min (422s) with delay=100ms
- 用戶手動調整 Round 5 參數：delay 100ms→50ms, FINISH 後 2000ms, retry delay 也改 50ms
- Rebuild 成功，JIRA RAD-1454 已更新（comment #90259）
- Round 5 測試參數 JIRA comment 待發（subagent review 中）

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| Round 5 stress test | 待 flash + 開始 | flash COM7 後啟動 ble_observer stress test |
| Round 5 JIRA 參數 comment | subagent review 中 | 手動發或下次 session 發 |
| PR #51 merge | 待 Teo review | 等 stress test 結果穩定後 merge |
| FINISH 2s delay 效果 | 待驗證 | 看 Round 5 是否消除 "no FINISH" FAIL |
| delay 50ms OTA 速度 | 待量測 | Round 5 跑完後比較 cycle time vs Round 4 的 7.0 min |

## Environment
- Branch: fix/RAD-1454-ota-coex-round4（PR #51 已推）
- Local uncommitted changes: SIMULATION=1, delay 50ms, FINISH 2s, retry delay 50ms
- Hardware: Reactor 50, ESP32 COM7
- Build: 成功（含用戶手動修改）

## Notes for next session
- PR #51 是 commit 的版本（delay=100ms, FINISH 原本的值），本地有未 commit 的實驗參數
- Round 5 參數：delay=50ms after read, FINISH 後 2000ms, retry delay 50ms, 其餘同 Round 4
- results.csv 需要清空或另存才能區分 Round 4 vs Round 5 數據
- Cycle 81 的 "no FINISH" FAIL：root cause 是 L2CAP congestion，FINISH 2s delay 預期可解決
- App 端需確認不依賴收到 progress=100 才處理 FINISH（低風險但需驗證）
