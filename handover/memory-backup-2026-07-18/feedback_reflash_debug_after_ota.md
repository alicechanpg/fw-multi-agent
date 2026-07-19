---
name: reflash-debug-after-ota
description: OTA 會覆蓋 debug firmware，測試完要記得燒回 debug 版本
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 24198985-e1cc-4060-b427-b889433b98b6
---

OTA 下載的是 server 上的 release build，會覆蓋掉本地燒的 debug firmware（含 SDNAND latency log 等 debug 功能）。

**Why:** 用戶 2026-05-19 提醒，OTA 覆蓋是正常的，但下次要測試時記得燒回 debug 版本。

**How to apply:** 跑完 OTA 測試後，如果需要繼續用 debug log，要重新 build APP_DEBUG + flash STM32。提醒用戶或自動處理。
