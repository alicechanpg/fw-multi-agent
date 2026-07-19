---
name: feedback_jenkins_trigger_osx_default
description: 觸發 updater Jenkins build 時不要傳 TRIGGER_OSX=false — 預設一律 true，Mac 版要跟著出
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e3aafce-65f5-45a1-8488-7a83a6e73825
---

觸發 updater 的 Jenkins build（`REACTOR_SPARK_FW_UPDATER_WIN_OSX`）時，**`TRIGGER_OSX` 一律用 `true`**，不要為了省時間傳 `false`（2026-07-16 用戶明確指示：「以後 build default trigger_osx=true」）。

**Why:** 該 job 的 param 預設本來就是 `true`（見 [[reference_reactor_spark_updater_jobs]]），是我先前為了「只驗證編譯」自作主張傳 `false`，導致 Mac 版沒跟著 build。Win/Mac 要成對存在，只出 Win 對用戶沒用。

**How to apply:** POST `buildWithParameters` 時明確帶 `TRIGGER_OSX=true`（或整個不傳、讓它吃預設）。**絕不主動傳 false**，除非用戶當次明講。

**同場加映 — `SIGN`：** 用戶自己觸發的 build（#30、#31）都是 `SIGN=True`。要交付/上機安裝的 build 用 `SIGN=true`；只是驗證編譯不壞可以 `false`，但別預設就 false。
