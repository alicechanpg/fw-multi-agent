# Session Handover (mybot) — 2026-04-17 14:00

## 重大發現：BLE 連線可能沒斷

120 秒 serial capture 顯示連上後完全靜默 — 沒有 DISCONNECT event、沒有 retry scan。
如果 BLE 真的斷了，應該看到 0x80 → RECONNECT → 第二次 scan。都沒有。

**假設：BLE link 還活著，用戶看到的「斷線」是 Control LED 行為（不是真的 BLE 斷線）。**

## 下次第一件要做的事

1. Flash 目前的 firmware（reactor-fw FWP-664 v2 + ESP32 develop）
2. 開機 → boot RECONNECT → 連上
3. **按 Control 上的腳踏板** → 看 ESP32 log 有沒有收到 pedal data
4. 如果有 → BLE 連線是活的 → 「斷線」是 Control LED 問題，不是 BLE 問題
5. 如果沒有 → BLE 真的斷了 → 需要加 LOGI disconnect log 到 ESP32 看 reason

## Done This Session

1. reactor-fw FWP-664 v2 branch 建立（從 develop，乾淨的 10 行 diff）
2. Sequence diagrams 完成（5 user scenarios + edge cases）
3. Design decisions 確認（always RECONNECT, MAC filter, continuous retry）
4. Make build baseline 修復（clean build 解決 stale objects）
5. 確認 MAC 是 static（不會變）

## Current State

### STM32 (reactor-fw)
- Branch: feature/FWP-664-auto-reconnect-v2
- 3 changes: boot RECONNECT, disconnect handler, scan timeout retry
- Clean build PASS, flashed on hardware

### ESP32 (pg-reactor-esp32-wifi-bt)
- Branch: develop（零改動）
- FWP-664 name filter changes 在 stash 裡
- **注意：develop 的 GATTC_DISCONNECT log 是 ESP_LOGD（看不到）**

### Hardware
- relay COM3, ESP32 COM19
- 2x Control: f6c3 (b.28), e4d4 (b.30)

## Key Files
- `D:\mybot\docs\FWP-664-user-scenario-design.md` — 5 scenarios + design decisions
- `D:\mybot\docs\FWP-664-revised-sequence-diagrams.md` — low level sequence diagrams
- `D:\mybot\docs\FWP-664-ble-sequence-diagrams.md` — develop baseline analysis
