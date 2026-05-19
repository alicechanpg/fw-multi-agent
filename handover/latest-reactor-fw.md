# Session Handover (reactor-fw) — 2026-05-19 23:55

## 本次完成
- FWP-791 Bug B fix: OTA SDMMC lockdown + activity-based 60s idle timeout (commits 1609ae5, 2c2ee09)
- FWP-791 Bug A reproduction: img_pkts underflow confirmed at SPI#2407/2406 (82.8%)
- MR !318 pushed with both commits: https://git.positivegrid.com:8443/firmware/reactor-fw/merge_requests/318
- FWP-797 opened for Bug A (ESP32 side fix needed)
- FWP-791 JIRA comment updated with full reproduction data
- FWP-796 and FWP-791 both have MR URL

## 未完成 / 進行中
| 項目 | 狀態 | 下一步 |
|------|------|--------|
| MR !318 review | 等待 Teo review | merge to develop |
| FWP-797 Bug A fix | 已開 ticket，unassigned | ESP32 team 修 img_pkts 計算 |
| MR description update | 未更新（glab CLI 有 port 問題） | 可手動更新或用 GitLab web UI |

## 環境狀態
- 當前 branch: `bugfix/FWP-791-ota-sdmmc-lockdown` (2 commits ahead of develop)
- 硬體: Reactor 50 通電運作中，NOR flash 有最新 debug build
- SD-NAND: 有損壞的 OTA image（CRC fail），不影響正常運作（bootloader 自動跳 NOR）
- ESP32: 已恢復 production binary 在 OTA server
- Throttle server: 已停止
- COM port loggers: 已停止
- Git stash@{0}: FWP-791 debug modifications（舊的，可能不需要了）

## 給下個 session 的備註
- Bug B fix 經過完整 107 分鐘 OTA 測試驗證，零 SDMMC contention errors
- Bug A 是 ESP32 端問題，STM32 端不需要改（failsafe reboot 行為正確）
- 如果要再跑 OTA 測試：ESP32 production binary 已恢復，throttle server 需重啟
- STLink flash 正確指令用 `-d` 和 `0x90000000`，不是 `-w` 和 `0x70000000`
