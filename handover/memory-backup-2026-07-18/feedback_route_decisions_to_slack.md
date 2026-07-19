---
name: feedback_route_decisions_to_slack
description: 需要 Alice review 或拍板的東西都主動傳她的私人 Slack DM
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5103f5c6-c8c2-43fd-89b9-2e0d0c162bd0
---

從 2026-07-14 起,任何需要 Alice **review 或決定**的東西(計畫、決定點、文件連結、standup、需她拍板的選項)都要**主動傳到她的私人 Slack DM**,不只在對話裡回報。

- Slack 目標:Alice 自己的 DM,user_id `U04NS4ZFW5R`(self-DM channel `D04NS89Q6BC`)。
- **Why:** 她常在手機 / 遠端 review,Slack 最方便。
- **How to apply:** 產出需決定/審閱的內容時,用 `slack_send_message` 送到她 DM;文件放 Google Drive(繁中)並附連結。
- 注意:背景 headless session 沒有 Slack MCP(實測 NONE)—— 只有登入的互動 session 送得出去。相關 [[reference_google_drive_visibility]]。
- **2026-07-18 Alice 再次明確指示**:「待決定事項」清單(session 結尾整理的 pending decisions)也一律送 Slack DM,不只在終端機顯示。她的回覆管道照舊是 Claude Code 視窗,Slack 只是手機通知。
