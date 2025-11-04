#!/usr/bin/env python3
"""
Startup hook to check workflow version.

Runs automatically when Claude Code starts. Can be disabled by creating
.no-version-check file in ~/.claude/ or .claude/ directory.
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path


def main():
    """Check if version check should run."""
    # Check for opt-out marker files
    user_opt_out = Path.home() / ".claude" / ".no-version-check"
    project_opt_out = Path(".claude") / ".no-version-check"

    if user_opt_out.exists() or project_opt_out.exists():
        # User has opted out of version checks
        return

    # Check if iw-version-check skill exists
    user_skill = Path.home() / ".claude" / "skills" / "iw-version-check" / "SKILL.md"
    project_skill = Path(".claude") / "skills" / "iw-version-check" / "SKILL.md"

    if user_skill.exists() or project_skill.exists():
        print("🔄 Checking for workflow updates...")
        # The actual version check logic is handled by Claude invoking the iw-version-check skill
        # This hook just signals that a check should be performed


if __name__ == "__main__":
    main()
