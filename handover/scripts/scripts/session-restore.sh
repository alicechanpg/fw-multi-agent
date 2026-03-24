#!/bin/bash
# Session Restore Script - triggered by SessionStart hook
# Scans for restorable sessions and outputs menu for Claude to present

HANDOVER_DIR="D:/mybot/handover"
REPO_DIR="D:/mybot/fw-multi-agent"

# Step 1: Pull latest from GitHub
cd "$REPO_DIR" 2>/dev/null && git pull --quiet 2>/dev/null

# Step 2: Sync latest files from repo to local handover dir
for f in "$REPO_DIR/handover"/latest-*.md; do
    [ -f "$f" ] && cp "$f" "$HANDOVER_DIR/" 2>/dev/null
done
[ -f "$REPO_DIR/handover/terminal-map.json" ] && cp "$REPO_DIR/handover/terminal-map.json" "$HANDOVER_DIR/" 2>/dev/null

# Step 3: Scan for restorable sessions
SESSIONS=()
while IFS= read -r file; do
    filename=$(basename "$file")
    terminal_id="${filename#latest-}"
    terminal_id="${terminal_id%.md}"
    date_line=$(head -1 "$file" | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}' 2>/dev/null || echo "unknown")
    summary=$(grep -m1 "^- " "$file" 2>/dev/null | head -c 80 || echo "")
    SESSIONS+=("$terminal_id|$date_line|$summary")
done < <(find "$HANDOVER_DIR" -maxdepth 1 -name "latest-*.md" -type f 2>/dev/null | sort)

SESSION_COUNT=${#SESSIONS[@]}

if [ "$SESSION_COUNT" -eq 0 ]; then
    echo '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[SESSION-RESTORE] No restorable sessions. Start fresh.\nRead JIRA FWP-739 comments for session handoff protocol context."}}'
    exit 0
fi

# Build context message
CTX="[SESSION-RESTORE] Found $SESSION_COUNT session(s). Present this menu to user:\n"
idx=1
for s in "${SESSIONS[@]}"; do
    IFS='|' read -r tid tdate tsummary <<< "$s"
    CTX+="  $idx. $tid ($tdate) -- $tsummary\n"
    idx=$((idx + 1))
done
CTX+="  0. Start new work\nAsk user which to restore. Then read the corresponding latest-{id}.md and JIRA ticket.\nALSO: Read JIRA FWP-739 comments for session handoff protocol context and latest status."

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"$CTX\"}}"
