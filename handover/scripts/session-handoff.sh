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

# Build the audit digest from the hook's own trail, and detect a stale latest-*.md.
# This does not depend on Claude having remembered to write anything.
# Exit code 2 from the digest means the handover is stale; it is propagated at the end so
# the asyncRewake hook wakes Claude to write it.
HOOK_INPUT=$(cat)
HOOK_OUT=$(printf '%s' "$HOOK_INPUT" | python "$HANDOVER_DIR/scripts/session-digest.py" 2>/dev/null)
DIGEST_RC=$?

# Copy latest to session archive
if [ -f "$HANDOVER_DIR/latest-${TERMINAL_ID}.md" ]; then
    cp "$HANDOVER_DIR/latest-${TERMINAL_ID}.md" "$HANDOVER_DIR/sessions/$TERMINAL_ID/${DATE_FILE}.md"
fi

# Push to GitHub. Emit the digest's verdict first so a stale handover is still reported
# even if the repo is missing and we bail out early.
emit() { [ -n "$HOOK_OUT" ] && echo "$HOOK_OUT"; exit "$DIGEST_RC"; }

cd "$REPO_DIR" 2>/dev/null || emit
git pull --quiet 2>/dev/null

# Sync files.
# The trailing "/." copies the directory's CONTENTS. Without it, `cp -r src/ dest/`
# copies src INTO dest once dest exists, so every run buried another level:
# handover/scripts/scripts/, handover/audit/audit/, handover/sessions/sessions/.
cp "$HANDOVER_DIR"/latest-*.md handover/ 2>/dev/null
cp "$HANDOVER_DIR"/terminal-map.json handover/ 2>/dev/null
mkdir -p handover/sessions handover/scripts handover/audit
cp -r "$HANDOVER_DIR"/sessions/. handover/sessions/ 2>/dev/null
cp -r "$HANDOVER_DIR"/scripts/. handover/scripts/ 2>/dev/null
cp -r "$HANDOVER_DIR"/audit/. handover/audit/ 2>/dev/null

git add handover/ 2>/dev/null
if git diff --cached --quiet 2>/dev/null; then
    emit
    exit 0
fi
git commit -m "session($TERMINAL_ID): $TIMESTAMP auto-handoff" --quiet 2>/dev/null
git push --quiet 2>/dev/null

emit
