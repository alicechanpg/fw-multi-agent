---
name: release-20260703-reactor-ota-staging
description: "2026-07-03 Reactor R50+R100 OTA staging: STM32 0.1.4.171 + ESP32 rev686, TO_PRODUCTION=false, awaiting QA before production"
metadata: 
  node_type: memory
  type: project
  originSessionId: 373f863f-1c26-4ce5-b5e5-6e1b391713c6
---

2026-07-03 Reactor R50+R100 OTA staging deploy（含 RAD-1476 reverb float 修正）。

**Why:** 出 staging 給 QA 驗證；QA 過後再 TO_PRODUCTION=true 上 production。0.1.4.171 = develop(50146c1, 已 merge RAD-1476 float 修正) + 一個 no-op staging-test 註解 commit。

**How to apply:** 用戶說「OTA 上 production」時，用**下表同樣的 build number** 跑 `Release_Reactor_FW_FOR_OTA` 改 `TO_PRODUCTION=true`（不要重新 build，用同一批 artifact）。

## Build number 對應（Jenkins jk-builds.positivegrid.com）
| 產品 | STM32 0.1.4.171 (REACTOR_AMP_FW) | ESP32 rev686 (REACTOR_ESP32_FW) |
|------|----------------------------------|----------------------------------|
| Reactor_100 | #166 | #71 |
| Reactor_50 | #167 | #72 |

## OTA staging job 參數（Release_Reactor_FW_FOR_OTA）
- PRODUCT_NAME: Choice `Reactor_50` / `Reactor_100`（每產品各跑一次）
- PROJ_NAME: `REACTOR_AMP_FW`
- BUILD_NO: MCU 的 REACTOR_AMP_FW build#（String）
- ESP32_BUILD_NO: REACTOR_ESP32_FW build#（String）
- TO_PRODUCTION: false=staging / true=production

## Staging deploy 結果（TO_PRODUCTION=false）
- Reactor_100: `Release_Reactor_FW_FOR_OTA #85` SUCCESS（BUILD_NO=166, ESP32_BUILD_NO=71）
- Reactor_50: `Release_Reactor_FW_FOR_OTA #86` SUCCESS（BUILD_NO=167, ESP32_BUILD_NO=72）

## 相關
- RAD-1476 reverb mode float16 bug fix 已 merge 進 develop（MR !322，commit ba620c8），tag `0.1.4.170` 打在 develop merge commit 50146c1。
- artifact 版本嵌在檔名：`reactorXXX-fw-0.1.4.171.bin`、`esp32-fw-reactorXXX-rev686.bin`。
