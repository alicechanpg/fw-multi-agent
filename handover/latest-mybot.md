# Session Handover (mybot) — 2026-04-07 12:30

## Done
- **Phase 3 穩定性測試 — PASS (681/681, 100%)**
  - 60 分鐘連續測試，0 disconnects
  - avg 66.6ms, p50 66.6ms, p95 100.0ms, p99 110.8ms, max 135.2ms
  - 亮點：BLE 連線從 4/2 到 4/7 維持 5 天 connected 狀態
- **Phase 4 F17/F18 結論報告 — 已發佈到 JIRA SG-7**
  - Executive Summary + 測試環境 + Pass Criteria + 結果表 + 已知限制
  - 結論：PASS — BLE 直連架構可行
- **FWP-758 建立並 link to SG-7**
  - assign to Alice, 狀態：進行中
- **JIRA SG-7 補充**
  - Phase 2 壓測指令說明（PM 可讀版）
  - 距離/遮蔽 + exp pedal：待代工廠依照其他產品標準測試

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| 斷線重連測試 | 待硬體恢復 | Guitar #1 (COM27) 目前離線 |
| Phase 4 A-E Dual GATTS | 未開始 | A: ADV 策略 (blocker) 優先 |

## Environment
- Guitar #1 (COM27): **離線**
- AMP #2 (COM29): 在線
- wifi-and-bt-core-on-esp32: feature/SG-7-auto-scan, clean

## Notes for next session
- Guitar #1 需重新接上 USB
- 接上後先做斷線重連測試（3-5 輪）
- 然後開始 Dual GATTS 實驗：A (ADV blocker) → B → C+D → E → F19
