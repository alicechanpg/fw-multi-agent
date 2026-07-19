---
name: feedback-auto-trigger-fw-before-updater
description: "When building firmware updater with empty version, first trigger fresh REACTOR_AMP_FW + REACTOR_ESP32_FW builds for R50+R100"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b7741786-95b1-48f2-afcc-5232fd4db290
---

用空版本 build Firmware Updater 時，必須先自動 trigger 最新的 firmware build（R50 + R100），等完成後再打 updater。

**Why:** 空版本會抓 Jenkins 上最新的 build，但最新的 R50 和 R100 可能版本不同步（例如 R50=0.1.4.132 但 R100=0.1.4.130）。先重新 build 才能確保兩個 product 用的是同一份 source code。

**How to apply:** 
1. 先 trigger 4 個 job（全部用 develop branch）：
   - REACTOR_AMP_FW: Reactor 50 + Reactor 100
   - REACTOR_ESP32_FW: Reactor 50 + Reactor 100
2. 等 4 個都完成
3. 再 trigger `REACTOR_FW_UPDATER_WIN_OSX`（2026-07-01 確認的正確 job 名；舊名 WIN_V4 已不存在。TRIGGER_OSX=true 會自動帶 Mac build）
