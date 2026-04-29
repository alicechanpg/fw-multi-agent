# Session Handover (mybot) — 2026-04-02 15:45

## Done
- **FWP-755 [Reactor 100] bypass signal path 無聲 — 已 Close**
  - 搜尋 reactor-50-100-fw bypass 機制：軟體 bypass，非硬體 relay
  - Amp 模組有 root-level protection，bypass 時 DSP 仍強制處理
  - 找到 `ENABLE_AKM7755_EXTERNAL_CONTROL` 首次出現：commit 588ad40 (Hijay, 2025-08-29)
  - DFU 燒錄 `reactor-fw_Appli_DSP_BYPASS.bin` 到裝置 (PID: 0502) 成功
  - Binary 由 Lio 在 Slack #tf-reactor-hw-noise channel 提供
  - 已提供給 EE (Ian Wu) 測試
  - JIRA FWP-755 加 comment + 切到完成
- **Option byte 192K 查詢**
  - 用戶詢問 option byte 改為 192K 的第一個 Jenkins 版本
  - 在 reactor-50-100-fw git history 中未找到明確的 option byte 192K 變更
  - STM32H7R3 內部 flash 只有 64KB，192K 可能是其他產品（spark-pedal-fw / H750）
  - 未解決，用戶未進一步追問

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| Option byte 192K 查詢 | 未解決 | 確認是哪個產品/repo 再查 |

## Environment
- Working dir: D:\mybot
- DFU 裝置: PID 0502, serial 3360396C3034
- reactor-50-100-fw: develop branch

## Notes for next session
- PID 0502 裝置已燒 DSP_BYPASS binary，如需恢復正式版需重新燒錄
- Option byte 192K 問題可能需要問 Lio 或查 spark-pedal-fw repo
- FWP-755 已 close，如 EE 反饋有問題可能需 reopen
