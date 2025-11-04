---
name: iw-version-check
description: Check if workflow update is available and prompt user to update if newer version exists. (project)
---

# Workflow Version Check

Check installed workflow version against latest GitHub release and notify users of available updates.

## Overview

This skill compares the locally installed workflow version with the latest version on GitHub. If a newer version is available, it prompts the user to update. Designed to run automatically via startup hook.

## When to Use This Skill

This skill is typically invoked automatically:
- **Startup hook** - Runs when Claude Code session starts
- **Manual check** - User can invoke to check version on demand
- **After installation** - Verify installed version

## How It Works

1. Read local VERSION file from `.claude/skills/iw-install/VERSION`
2. Fetch latest VERSION from GitHub using WebFetch
3. Compare versions using semantic versioning
4. If newer version available, prompt user to update via AskUserQuestion
5. If user accepts, invoke iw-install skill to update

## Workflow

### Step 1: Check if VERSION File Exists

Before checking for updates, verify local installation:

```bash
# Check user-level installation
test -f "$HOME/.claude/skills/iw-install/VERSION"

# Check project-level installation
test -f ".claude/skills/iw-install/VERSION"
```

**If no VERSION file found:**
- This is a fresh installation or pre-versioning install
- Display message: "Workflow version tracking not available. Run /iw-install --update to get latest version."
- Exit gracefully without error

**If VERSION file found:**
- Read local version
- Proceed to check for updates

### Step 2: Read Local Version

Read the VERSION file:

```python
from pathlib import Path

# Try user-level first, then project-level
version_file = Path.home() / ".claude/skills/iw-install/VERSION"
if not version_file.exists():
    version_file = Path(".claude/skills/iw-install/VERSION")

if version_file.exists():
    local_version = version_file.read_text().strip()
else:
    # No local version available
    return
```

### Step 3: Fetch Remote Version

Use WebFetch tool to get latest version from GitHub:

```
URL: https://raw.githubusercontent.com/jumppad-labs/iw/main/VERSION
Prompt: "Extract the version number from this file. Return only the version string (e.g., '1.0.0')."
```

**Handle errors gracefully:**
- Network failures - Skip check, don't block user
- Invalid version format - Log warning, continue
- GitHub unavailable - Skip check silently

### Step 4: Compare Versions

Use semantic versioning to compare:

```python
from packaging import version

def is_newer_version(remote: str, local: str) -> bool:
    """Check if remote version is newer than local."""
    try:
        return version.parse(remote) > version.parse(local)
    except Exception:
        return False
```

**Comparison logic:**
- `1.0.1 > 1.0.0` → Update available
- `1.1.0 > 1.0.0` → Update available
- `2.0.0 > 1.9.9` → Update available
- `1.0.0 == 1.0.0` → No update needed
- `1.0.0 > 1.0.1` → User has newer (development version)

### Step 5: Notify User if Update Available

If newer version found, use AskUserQuestion to prompt:

```
Question: "A new workflow version is available. Would you like to update now?"

Options:
1. "Update now" - Run /iw-install --update
2. "Skip this time" - Continue without updating
3. "Don't ask again" - Create .no-version-check marker file

Display:
- Current version: {local_version}
- Latest version: {remote_version}
- What's new: [Link to GitHub releases or changelog]
```

### Step 6: Handle User Response

Based on user selection:

**"Update now":**
```bash
# Invoke iw-install skill to perform update
Skill tool → iw-install with update action
```

**"Skip this time":**
- Continue session normally
- Will check again next session

**"Don't ask again":**
- Create marker file to disable checks
- User can re-enable by deleting marker

```bash
# Create marker file
touch "$HOME/.claude/.no-version-check"
# or
touch ".claude/.no-version-check"
```

### Step 7: Version Check Silencing

Allow users to opt out of version checks:

**Check for marker file before running:**
```python
marker_file = Path.home() / ".claude/.no-version-check"
if marker_file.exists():
    # Silently skip version check
    return

# Otherwise proceed with check
```

**To re-enable version checks:**
```bash
rm ~/.claude/.no-version-check
# or
rm .claude/.no-version-check
```

## Integration with Startup Hook

The startup hook `.claude/hooks/check_workflow_version.sh` invokes this skill:

```bash
#!/bin/bash
# Check for version check marker (opt-out)
if [ -f "$HOME/.claude/.no-version-check" ] || [ -f ".claude/.no-version-check" ]; then
    exit 0
fi

# Only check if skill exists
if [ -f "$HOME/.claude/skills/iw-version-check/SKILL.md" ] || [ -f ".claude/skills/iw-version-check/SKILL.md" ]; then
    # Skill invocation happens via Claude
    echo "🔄 Checking for workflow updates..."
fi
```

## Error Handling

**Network failures:**
- Don't block user workflow
- Skip check silently or show brief message
- User can manually check later

**Invalid version formats:**
- Log warning
- Treat as "unable to determine"
- Continue without update prompt

**VERSION file missing:**
- Assume pre-versioning installation
- Suggest running update to get versioning

**GitHub rate limiting:**
- WebFetch handles this automatically
- Skip check if rate limited

## Success Criteria

A successful version check should:
- Complete quickly (< 2 seconds)
- Not block user workflow if it fails
- Provide clear update instructions
- Respect user preferences (opt-out)
- Handle all error cases gracefully

## Resources

### scripts/

**check_version.py** - Python script for version comparison logic

Can be executed standalone for testing:
```bash
python3 scripts/check_version.py
```

Returns:
- Exit code 0: No update needed
- Exit code 1: Update available
- Exit code 2: Unable to determine

## Example Output

**When update available:**
```
🔄 Checking for workflow updates...

✨ New workflow version available!

Current version: 1.0.0
Latest version:  1.1.0

Would you like to update now?
```

**When up to date:**
```
✓ Workflow is up to date (v1.0.0)
```

**When version check fails:**
```
⚠️  Unable to check for updates (network error)
Continuing with current version...
```
