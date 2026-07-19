---
name: release-20260522-reactor
description: "2026-05-22 Reactor R50+R100 release — build FW, OTA staging (TO_PRODUCTION=false), then Updater Win+Mac"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b26a649-6ac4-49d5-8d14-003107877db9
---

2026-05-22 Reactor release (R50 + R100)

**Why:** 用戶要出 release，先 staging 給 QA 驗證，QA 過後再 TO_PRODUCTION=true。

**How to apply:** 下次 session 如果用戶說「OTA 可以上 production 了」，就 trigger Release_Reactor_FW_FOR_OTA 把 TO_PRODUCTION 改 true。

## Phase 1: Build FW（已 trigger）
| # | Job | Device | Build # | Status |
|---|-----|--------|---------|--------|
| 1 | REACTOR_AMP_FW | Reactor 50 | #156 | building |
| 2 | REACTOR_AMP_FW | Reactor 100 | #157 | queued |
| 3 | REACTOR_ESP32_FW | Reactor 50 | #58 | queued |
| 4 | REACTOR_ESP32_FW | Reactor 100 | #59 | queued |

## Phase 2: OTA Staging
- TO_PRODUCTION=false
- 等 Phase 1 完成後 trigger
- QA 驗證通過後再跑 TO_PRODUCTION=true

## Phase 3: Firmware Updater
- REACTOR_FW_UPDATER_WIN_OSX (TRIGGER_OSX=true)
- 等 Phase 1 完成後 trigger
