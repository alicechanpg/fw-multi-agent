---
name: feedback_choices_need_recommendation_procons
description: 要 Alice 做選擇時（Slack 或 Claude Code 內）必須附上明確建議 + 各選項 pros/cons
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 530214ed-26de-4bd0-9704-882c8e95dc6f
---

（2026-07-18 用戶指示）**任何時候請 Alice 做選擇——不論在 Slack 訊息還是 Claude Code 對話——都必須：**
1. **給出明確建議**（推薦哪個、一句話為什麼），不能只丟選項；
2. **列出各選項的 pros / cons**（簡短、白話，讓不讀 code 的人能判斷）。

**Why:** Alice 不讀 code，光看選項標籤無法判斷；沒有建議＋利弊的選擇題等於把技術判斷丟回給她（違反 [[feedback_max_autonomy_drive_to_done]] 的精神——她只想按「同意/否決」，而要能否決就必須看得懂代價）。

**How to apply:** AskUserQuestion 的 option description 寫進 pros/cons、推薦項標 (推薦) 放第一個；Slack 選擇訊息用「建議：X，因為…」開頭，選項各附一行利弊。回顧：今天的 A/B hook 問題就沒附 pros/cons——這條就是那次的糾正。

相關：[[feedback_route_decisions_to_slack]]、[[feedback_max_autonomy_drive_to_done]]
