# Session Handover (mybot) — 2026-04-07 15:15

## Done
- **FWP-755 [Reactor 100] bypass 無聲 — Closed**
  - DFU 燒錄 DSP_BYPASS binary 給 EE (Lio 在 #tf-reactor-hw-noise 提供)
  - ENABLE_AKM7755_EXTERNAL_CONTROL: commit 588ad40 (Hijay, 2025-08-29)
- **SG-7 BLE 直連 POC — Phase 1-4 ALL PASS**
  - Phase 1: 基本連線 6/6, 0.6s 自動連線
  - Phase 2: 1000 次混合 CMD 壓測 100%, avg 67ms
  - Phase 3A: 60min 穩定性 681cmd 100% OK, 0 disconnects
  - Phase 3B: 斷線重連 4/4, avg 4.1s, 1 次即連
  - Phase 4A: ADV 策略 — 雙 UUID 可見 (BLE Explorer 截圖)
  - Phase 4B: Dual GATTS — 0xFFC0 + 0xFFC8 同時註冊
  - Phase 4C: 並行操作 — App + AMP 同時連線 CMD 正常
  - Phase 4D: 資源開銷 — 雙連線僅多用 5.2KB RAM
  - Phase 4E: 雙連線穩定性 — 10min 150cmd 100% OK, 無 memory leak
  - 5 天連線觀察（4/2→4/7）
  - Exp pedal BW 評估：100Hz notify BW 餘量 7-12 倍
- **FWP-758 建立 + link SG-7 + assign Alice**
- **Guitar #1 救磚**：ST-Link 燒 external-loader + DFU 燒 fw 2.7.2.200
- **JIRA 完整上下文 comment**：架構圖、build 指令、config 差異、UUID、已知問題、test script、gap analysis
- **Code pushed**: feature/SG-7-auto-scan (5 commits)
- **Memory 更新**：JIRA 含 SG board、不停下來問該做就做、migration 才不改 code

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| SG-7 ticket | 可 close | 用戶確認 |
| FWP-758 | 進行中 | 跟隨 SG-7 狀態 |

## Environment
- wifi-and-bt-core-on-esp32: feature/SG-7-auto-scan (clean, pushed)
- Guitar #1 (COM27): SG7 dual mode, STM32 fw 2.7.2.200
- AMP #2 (COM29): normal mode + auto-scan
- COM26/28: PG USB, COM50: ST-Link

## Notes for next session
- SG-7 POC 全部完成，Production gap: STM32 整合、exp pedal ADC、距離測試、App 實際連線、Security
- 測試距離 60cm（非 1m），已修正 JIRA
- 兩台同 branch 不同 sdkconfig：Guitar=SG7_DUAL_MODE, AMP=都 off
