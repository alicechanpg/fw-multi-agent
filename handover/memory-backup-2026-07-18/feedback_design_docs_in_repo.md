---
name: Design documents must be in repo
description: User requires design documents for every task, stored in docs/ folder of the relevant repo
type: feedback
originSessionId: 96c15cdc-a1a3-4ab9-93a5-dd71363036c3
---
每個任務都要寫 design document，放在 repo 的 `docs/` 資料夾內。

**Why:** 用戶明確要求（2026-04-30），希望所有設計文件都有版本控制。

**How to apply:** 
- STFS-491 design docs 路徑: `D:\mybot\docs\STFS-491-*.md`（mybot workspace）
- 未來任務開始時就規劃 design doc，完成後 commit 進 repo
- 文件名格式: `{JIRA-ID}-{描述}.md`
