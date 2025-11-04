# Issue #7 Implementation Plan: Workflow Versioning

**Created**: 2025-11-04
**Issue**: https://github.com/jumppad-labs/iw/issues/7

## Overview

Add semantic versioning to the workflow with automatic version checking via startup hook. Users will be notified if a newer version is available and prompted to update.

## Current State

- No version tracking exists in the workflow
- `iw-install` always clones from main without version awareness
- No mechanism to check if updates are available
- manage_workflow.py:83-139 handles git clone but doesn't track versions

## Desired End State

1. VERSION file at repo root with semantic version (e.g., "1.0.0")
2. New `iw-version-check` skill that compares local vs GitHub versions
3. Startup hook that automatically runs version check
4. User prompted to update if newer version available

## What We're NOT Doing

- Automatic updates (user must approve)
- Version pinning or rollback functionality
- Breaking change detection or migration scripts
- Version history tracking

## Implementation Approach

Use a VERSION file at repo root, leverage GitHub API to fetch latest version, compare using semantic versioning, and notify users via startup hook. Keep it simple and non-intrusive.

---

## Phase 1: Add VERSION File and Version Check Skill

### Changes Required:

#### 1. Create VERSION file
**File**: `VERSION` (new file at repo root)
**Content**:
```
1.0.0
```
**Reasoning**: Simple text file, easy to read and update. Semantic versioning format (MAJOR.MINOR.PATCH).

#### 2. Create iw-version-check skill
**File**: `.claude/skills/iw-version-check/SKILL.md` (new)
**Content**:
```markdown
---
name: iw-version-check
description: Check if workflow update is available and prompt user to update if newer version exists. (project)
---

# Workflow Version Check

Check installed workflow version against latest GitHub release.

## Workflow

1. Read local VERSION file from `.claude/skills/iw-install/VERSION`
2. Fetch latest VERSION from GitHub raw content
3. Compare versions using semantic versioning
4. If newer version available, notify user and ask to update

## Implementation

Use WebFetch to get: https://raw.githubusercontent.com/jumppad-labs/iw/main/VERSION
Compare with local version (stored during installation).
Prompt user with AskUserQuestion if update available.
```

**Script**: `.claude/skills/iw-version-check/scripts/check_version.py` (new)
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
from packaging import version

def check_version():
    """Check if workflow update is available."""
    # Read local version
    local_version_file = Path.home() / ".claude/skills/iw-install/VERSION"
    if not local_version_file.exists():
        local_version_file = Path(".claude/skills/iw-install/VERSION")

    if not local_version_file.exists():
        print("No local VERSION file found. Run /iw-install to install workflow.")
        return False

    local_ver = local_version_file.read_text().strip()
    print(f"Installed version: {local_ver}")

    # Remote version fetched via WebFetch (Claude will do this)
    # This script just handles comparison logic
    return True

if __name__ == "__main__":
    check_version()
```

#### 3. Update manage_workflow.py to copy VERSION
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:141-201`
**Change**: In `_copy_files_from_clone()`, add VERSION file copying

**Add after line 189**:
```python
# Copy VERSION file to track installed version
version_source = clone_dir / "VERSION"
if version_source.exists():
    version_target = self.target_dir / "skills" / "iw-install" / "VERSION"
    version_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(version_source, version_target)
    print(f"  ✓ Installed version: {version_source.read_text().strip()}")
```

#### 4. Create startup hook
**File**: `.claude/hooks/check_workflow_version.sh` (new)
```bash
#!/bin/bash
# Startup hook to check workflow version
# Runs automatically when Claude Code starts

# Only check if iw-version-check skill exists
if [ -f "$HOME/.claude/skills/iw-version-check/SKILL.md" ] || [ -f ".claude/skills/iw-version-check/SKILL.md" ]; then
    echo "🔄 Checking workflow version..."
    # Skill invocation will happen via Claude
fi
```

**Reasoning**: Lightweight hook that triggers skill invocation. Actual version checking logic in skill for testability.

#### 5. Update HOOKS list in manage_workflow.py
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:53-56`
**Change**:
```python
HOOKS = [
    "load_workflow.sh",
    "list_skills.sh",
    "check_workflow_version.sh",  # Add this line
]
```

#### 6. Update SKILLS list in manage_workflow.py
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:32-44`
**Change**:
```python
SKILLS = [
    "iw-planner",
    "iw-executor",
    "iw-workflow",
    "iw-learnings",
    "iw-init",
    "iw-github-issue-reader",
    "iw-github-pr-creator",
    "iw-git-workflow",
    "go-dev-guidelines",
    "skill-creator",
    "iw-install",
    "iw-version-check",  # Add this line
]
```

### Success Criteria

#### Automated Verification:
- [ ] VERSION file exists and contains valid semver
- [ ] manage_workflow.py copies VERSION during install
- [ ] Hook script is executable: `test -x .claude/hooks/check_workflow_version.sh`
- [ ] Skill exists: `test -f .claude/skills/iw-version-check/SKILL.md`

#### Manual Verification:
- [ ] Install workflow, verify VERSION copied to `.claude/skills/iw-install/VERSION`
- [ ] Start new Claude session, verify version check message appears
- [ ] If newer version available, verify user is prompted to update
- [ ] User can choose to update or skip

---

## Testing Strategy

### Manual Testing:
1. Create VERSION file with "1.0.0"
2. Run `python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location project`
3. Verify VERSION copied to `.claude/skills/iw-install/VERSION`
4. Change VERSION to "1.0.1" in repo
5. Restart Claude, verify notification of available update
6. Accept update prompt, verify workflow updates

### Edge Cases:
- No local VERSION file (fresh install) - should not error
- Network failure when checking GitHub - should fail gracefully
- Invalid version format - should show error message
- Same version - should skip notification

## References

- Issue #7: https://github.com/jumppad-labs/iw/issues/7
- manage_workflow.py:83-139 (git clone logic)
- Existing hooks: .claude/hooks/load_workflow.sh, .claude/hooks/list_skills.sh
- Learning: .docs/knowledge/learnings/installation.md (git clone approach)
