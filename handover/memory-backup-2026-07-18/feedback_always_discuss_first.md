---
name: Always discuss with subagent BEFORE acting
description: Must consult subagent before ANY action - creating files, debugging, code changes, status reports. No size exception.
type: feedback
---

**凡事都要跟 subagent 討論，不管大小事。沒有例外。**

**Why:** 
- 2026-03-24: 建 /handoff command 先做才討論，subagent 抓到設計問題
- 2026-04-01: pedal build 連試 5 種方法全失敗，先討論就能一次找到根因
- 2026-04-02: debug SG-7 BLE 連線問題時直接 trial-and-error 跑了多輪 monitor 沒結果，用戶提醒「你有跟 subagent 凡事都討論嗎 天啊」
- 用戶原話：跟 subagent 討論會「變超級聰明」

**How to apply:**
- 順序永遠是：想方案 → 跟 subagent 討論 → 根據建議修正 → 才動手
- **Debug 時**：遇到問題先跟 subagent 分析 log 和 code，不要盲目 retry
- **Build/Flash 時**：遇到環境問題先討論再嘗試
- **Code 改動**：改之前先討論影響範圍
- **回報結果**：回報前先讓 subagent review
- 不要因為「很簡單」就跳過，簡單的東西也會有盲點
- 這不是形式，是真的能避免走彎路
