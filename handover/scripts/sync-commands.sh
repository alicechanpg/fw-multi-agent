#!/bin/bash
# Sync commands and skills from fw-multi-agent backup to local .claude/
# Usage: bash fw-multi-agent/handover/scripts/sync-commands.sh

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET_COMMANDS="D:/mybot/.claude/commands"
TARGET_SKILLS="D:/mybot/.claude/skills"

mkdir -p "$TARGET_COMMANDS" "$TARGET_SKILLS"

# Copy commands
cp "$REPO_DIR/backup/commands/"*.md "$TARGET_COMMANDS/" 2>/dev/null
echo "Commands synced: $(ls "$REPO_DIR/backup/commands/"*.md 2>/dev/null | wc -l) files"

# Copy skills (preserve directory structure)
cp -r "$REPO_DIR/backup/skills/"* "$TARGET_SKILLS/" 2>/dev/null
echo "Skills synced: $(ls -d "$REPO_DIR/backup/skills/"*/ 2>/dev/null | wc -l) skill packs"

echo "Done. Commands and skills restored to .claude/"
