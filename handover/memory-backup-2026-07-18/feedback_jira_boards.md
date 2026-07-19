---
name: JIRA 查詢要包含 SG board
description: 查用戶 tickets 時必須搜 FWP + RAD + SG 三個 project，不能只查 FWP 和 RAD
type: feedback
---

查用戶的 JIRA tickets 時，必須包含 **FWP、RAD、SG** 三個 project。

**Why:** 用戶在 SG board 也有進行中的工作（如 SG-7 BLE POC），只查 FWP + RAD 會漏掉。

**How to apply:** 所有 JIRA 查詢（/restore、/status、查我的 tickets）的 JQL 都要用 `project IN (FWP, RAD, SG)`。
