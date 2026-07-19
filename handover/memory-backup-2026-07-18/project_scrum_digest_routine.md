---
name: project_scrum_digest_routine
description: reactor-scrum-digest 已於 2026-07-17 DISABLED，改由 daily-ai-news routine 取代(每天技術新聞+audit改善建議,report-only 自 DM)
metadata: 
  node_type: memory
  type: project
  originSessionId: 5103f5c6-c8c2-43fd-89b9-2e0d0c162bd0
---

> **⚠️ 2026-07-17 更新：`reactor-scrum-digest` 已 DISABLED（enabled=false）**——使用者認為 JIRA 內容變動不大、digest 意義低。改由**兩個新 routine 取代**（都 report-only、送 Alice DM `U04NS4ZFW5R`、sonnet-5、掛 Slack connector）：

1. **`daily-ai-news`**（id `trig_01MDAj7xDFYejRB1AJPb1dzB`）：**每天 02:00 台北（cron `0 18 * * *` UTC，2026-07-18 另一 session 調整）** 發「技術新聞（韌體/嵌入式/音訊/AI 工具實用的，非消費八卦；來源含 **GitHub trending/releases + coding agents Codex/Claude Code/Cursor/Copilot**）＋ audit 系統改善建議」。repo=FWP-713-fw-agent-dev。**07-18 首跑成功**，其中 `/improve` 引用錯誤（文件漂移）→ 已加 **GROUNDING FOR REPO CLAIMS 護欄**（repo 機制必須 Glob/Read 實查才可引用，文件引用≠存在）＋ Glob/Grep 工具。
2. **`daily-audit-review`**（id `trig_011JFAcb1DL6AkUDj9Ut6Zu5`）：**每天 02:00 台北（cron `0 18 * * *` UTC，同上調整）** 讀 `handover/audit/metrics.jsonl`+session audits，發系統表現 KPI 趨勢＋改善建議。**repo=alicechanpg/fw-multi-agent**（audit 資料的家；⚠️ 首跑待驗證 cloud 能否 clone 此個人 repo）。

改善建議一律**只提案不自動套用**（proposer→自我批評→人審，小而可逆，anti-Goodhart）。design 依據 deep-research（evaluator-optimizer / agentic memory / eval-driven / rollback，**驗證未跑完因撞 session 額度**）＋ PG 內部框架（CEO「5-Level AI Capability Framework」、Gary Hsieh「AI Agent Memory Architecture」）。**完整刪除 scrum-digest 要在 claude.ai/code/routines 手動點（API 只能 disable）。**（時間幾經調整：20:00→1:30→最終 04:00 research、23:00 audit-review。）
>
> 以下為原 reactor-scrum-digest 紀錄（保留供參）：

2026-07-15 建立並**實跑驗證成功**的 Cloud Routine:`reactor-scrum-digest`(id `trig_01QcJxZBUPJQZyUyGdBBiC4Y`,網頁 claude.ai/code/routines)。

- **做什麼**:每 5 小時(cron `0 */5 * * *`,UTC 0/5/10/15/20)查 JIRA(Alice + Teo,project RAD+FWP+DP,statusCategory != Done)→ 產繁中 digest → 發**一封** Slack DM 給 Alice 自己(channel `U04NS4ZFW5R`)。report-only,不改任何東西。
- **模型**:sonnet-5(省 token;非 opus——這隻只做摘要,不做工程)。
- **權限(最小化)**:allowed_tools 只有 Read/Grep/Glob(**無 Bash/Write/Edit**);connector 砍到只剩 Atlassian + Slack(建立時預設會自動塞全部 9 個,要手動 update 移除)。
- **驗證**:2026-07-15 09:35 CST 手動 run 一次,digest 真的送達 DM;回報 19 張(Alice 2 / Teo 17)與手動 JQL 交叉吻合。
- **關鍵教訓**:良性具體的 report-only + 自 DM 任務**不會**被模型拒;之前 connector-test 被拒三次是因為任務「形狀」像 prompt-injection(偵察工具+外送+自稱已授權),不是權限問題。見 [[feedback_route_decisions_to_slack]]。
- **cloudId**:`1b7536bc-1172-46a4-9fbc-546f7d1e62c9`。Alice accountId `712020:0fd1ac2e-0c61-4d07-bbb7-c6ae2e8ad4c6`;Teo `712020:893b0492-85c6-4c92-aeb6-cef6a14b6c52`。DP=Reactor Control(Control X)、RAD=Reactor、FWP=Firmware Updater。
- **待擴充(v2)**:audit/state 寫進 git repo(需在網頁給 routine 對 repo 的 push 權限,或寫 `claude/*` 分支);token-save 自動續跑;每日 standup。教學文件見 Drive doc `14DktAo7vXgL-ilx5lbFwrekrRl1jlqMwWZ2MZYWNJRY`。
