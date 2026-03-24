# /restore - Session Restore

Manually trigger session restore. Execute ALL steps:

1. `cd D:\mybot\fw-multi-agent && git pull` (sync latest from GitHub)
2. Read `D:\mybot\handover\terminal-map.json`
3. Scan `D:\mybot\handover\latest-*.md` and `D:\mybot\fw-multi-agent\handover\latest-*.md`
4. Present menu:
```
Available sessions:
1. {id} ({date}) -- {summary}
2. ...
J. 查看最近更新的 JIRA tickets (近 3 天)
M. 查看我的所有 open tickets
0. Start new work
```

5. Based on user selection:

**If user selects a session (1, 2...):**
- Read full `latest-{id}.md`
- Present restore summary: last session done/pending/env/next steps

**If user selects J (recent tickets):**
- Query JIRA: `assignee = currentUser() AND updated >= -3d ORDER BY updated DESC` on FWP + RAD boards
- Show top 10 results with status and last update time
- Ask: "要處理哪一張？輸入 ticket ID，或 0 返回選單"

**If user selects M (my open tickets):**
- Query JIRA: `assignee = currentUser() AND status not in (Done, 完成) ORDER BY priority DESC, updated DESC` on FWP + RAD boards
- Show all results grouped by priority
- Ask: "要處理哪一張？輸入 ticket ID，或 0 返回選單"

**If user selects 0:**
- Start fresh, no restore

Note: Do NOT auto-read JIRA. Only read specific JIRA tickets when user selects J, M, or asks.
