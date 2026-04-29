# Session Handover (mybot) — 2026-04-09 00:30

## Done (this session continued from 04-07)
- macOS USB parent matching 實作 (CdcWrapper.cpp, ioreg + locationID)
- CMakeLists.txt: 加 IOKit.framework for macOS
- Windows build 確認 OK
- Commit d886a58 pushed, PR #2 updated
- JIRA FWP-764 updated

## Commits on feature/FWP-764-esptool-usb-parent
1. b90d00b: Reactor UI patch + DFU driver fix + USB parent matching (Windows)
2. d886a58: macOS USB parent matching via ioreg locationID

## Pending
| Item | Status | Next Step |
|------|--------|-----------|
| macOS build + test | code 寫好未測 | 借到 Mac 後 cmake + build + 實機測 |
| Driver uninstall 重測 | Windows cache | 換乾淨電腦或 VM |
| MCU DFU flash 結果確認 | 已觸發 | 看 log "File downloaded successfully" |
| loading_loop_rim.png | 未補 | 從原始 repo 取 |
| PR review | WIP PR #2 | 請 Teo review |

## Environment
- Branch: feature/FWP-764-esptool-usb-parent (pushed, 2 commits)
- WIP PR: https://github.com/Positive-LLC/ReactorFwUpdater/pull/2
- Build: build-reactor50/, build-r100-v3/

## Notes
- macOS 用 ioreg + locationID 配對（上 16 bits 是 hub，下 16 bits 是 port）
- Windows 用 PowerShell + DEVPKEY_Device_Parent
- 0901 是 Spark 2 CDC PID，已從 products.json 移除
- PID 對照：R50 DFU=0504 CDC=0507, R100 DFU=0502 CDC=0506
