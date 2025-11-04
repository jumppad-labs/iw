#!/bin/bash
# Startup hook to check workflow version
# Runs automatically when Claude Code starts

# Check for opt-out marker file
if [ -f "$HOME/.claude/.no-version-check" ] || [ -f ".claude/.no-version-check" ]; then
    # User has opted out of version checks
    exit 0
fi

# Only check if iw-version-check skill exists
if [ -f "$HOME/.claude/skills/iw-version-check/SKILL.md" ] || [ -f ".claude/skills/iw-version-check/SKILL.md" ]; then
    echo "🔄 Checking for workflow updates..."
    # The actual version check logic is handled by Claude invoking the iw-version-check skill
    # This hook just signals that a check should be performed
fi
