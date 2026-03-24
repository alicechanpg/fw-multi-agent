#!/bin/bash
# Auto Session Handoff - triggered by Stop hook
# Writes latest session state and pushes to GitHub

HANDOVER_DIR="D:/mybot/handover"
REPO_DIR="D:/mybot/fw-multi-agent"
TERMINAL_ID="mybot"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
DATE_FILE=$(date +"%Y-%m-%d-%H%M")

# Create session log directory
mkdir -p "$HANDOVER_DIR/sessions/$TERMINAL_ID"

# Copy latest to session archive
if [ -f "$HANDOVER_DIR/latest-${TERMINAL_ID}.md" ]; then
    cp "$HANDOVER_DIR/latest-${TERMINAL_ID}.md" "$HANDOVER_DIR/sessions/$TERMINAL_ID/${DATE_FILE}.md"
fi

# Push to GitHub
cd "$REPO_DIR" 2>/dev/null || exit 0
git pull --quiet 2>/dev/null

# Sync files
cp "$HANDOVER_DIR"/latest-*.md handover/ 2>/dev/null
cp "$HANDOVER_DIR"/terminal-map.json handover/ 2>/dev/null
cp -r "$HANDOVER_DIR"/sessions/ handover/sessions/ 2>/dev/null
cp -r "$HANDOVER_DIR"/scripts/ handover/scripts/ 2>/dev/null

git add handover/ 2>/dev/null
if git diff --cached --quiet 2>/dev/null; then
    exit 0
fi
git commit -m "session($TERMINAL_ID): $TIMESTAMP auto-handoff" --quiet 2>/dev/null
git push --quiet 2>/dev/null

echo '{"suppressOutput":true}'
