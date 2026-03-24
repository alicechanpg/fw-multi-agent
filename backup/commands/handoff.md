# /handoff - Session Handoff

Manual session handoff. Execute ALL steps:

1. Read `D:/mybot/handover\terminal-map.json`, match current working directory to determine terminal ID and JIRA ticket. If no match, default to `mybot` / `FWP-739`.

2. Summarize this session:
   - What was done (list each action)
   - What's pending / in progress
   - Current environment state (branch, hw, etc.)
   - Notes for next session

3. Write handoff log to `D:/mybot/handover\latest-{terminal-id}.md`:
```markdown
# Session Handover ({terminal-id}) — {YYYY-MM-DD HH:mm}

## Done
- [each item]

## Pending
| Item | Status | Next Step |
|------|--------|-----------|

## Environment
- Branch: ...
- Hardware: ...

## Notes for next session
[anything important]
```

4. Archive: copy to `D:/mybot/handover\sessions\{terminal-id}\{YYYY-MM-DD-HHmm}.md`

5. If `D:/mybot/handover\checklist\` has related checklists, update progress.

6. Push to GitHub:
```bash
cd D:/mybot/fw-multi-agent && git pull
cp D:/mybot/handover\latest-*.md handover/
cp D:/mybot/handover\terminal-map.json handover/
cp -r D:/mybot/handover\sessions/ handover/sessions/
git add handover/
git commit -m "session({terminal-id}): {YYYY-MM-DD HHmm} handover"
git push
```

7. Update JIRA (ticket from terminal-map.json) with brief handover comment (for human visibility, not for restore).

8. Also add brief comment to any other JIRA tickets touched during this session.

9. Ask user: "這個 session 完成了嗎？要從 restore 選單移除嗎？"
   - If yes: delete `D:/mybot/handover\latest-{terminal-id}.md` and push deletion to GitHub. Session history preserved in `sessions/{id}/`.
   - If no: keep latest for next restore.

Note: latest-{id}.md is the ONLY source for restore. JIRA comments are notifications for humans only.
