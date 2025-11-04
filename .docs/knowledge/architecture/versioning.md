# Workflow Versioning

## Overview

The workflow uses semantic versioning to track releases and notify users of available updates. The VERSION file at the repo root is the single source of truth for the workflow version.

## Version File Location

**File:** `VERSION` (at repository root)

**Format:** Semantic version string (e.g., `1.0.0`)

**Example:**
```
1.0.0
```

## Semantic Versioning

The workflow follows [Semantic Versioning 2.0.0](https://semver.org/):

### MAJOR version (X.0.0)

Increment when making **breaking changes**:
- Changes to skill interfaces that break existing usage
- Removal of skills, commands, or hooks
- Changes to workflow behavior that require user action
- Incompatible API changes in scripts or tools

**Example:** Removing a skill or changing required parameters

### MINOR version (x.Y.0)

Increment when adding **new functionality** in a backward-compatible manner:
- New skills added
- New commands added
- New hooks added
- Non-breaking enhancements to existing skills
- New features that don't break existing usage

**Example:** Adding the iw-version-check skill

### PATCH version (x.y.Z)

Increment for **backward-compatible bug fixes**:
- Bug fixes in existing skills
- Documentation updates
- Minor improvements without new features
- Performance optimizations
- Typo corrections

**Example:** Fixing a bug in manage_workflow.py

## Version Update Process

**CRITICAL:** The VERSION file must be updated whenever changes are made to `.claude/` directory contents.

### Step-by-Step Process

1. **Make changes** to skills, commands, or hooks
2. **Determine version type:**
   - Breaking change? → Increment MAJOR
   - New feature? → Increment MINOR
   - Bug fix? → Increment PATCH
3. **Update VERSION file** with new version
4. **Include in commit:**
   - Update VERSION in the same commit as the changes
   - Document the version change in commit message
   - Reference what changed and why version was incremented
5. **After merge:**
   - Users with iw-version-check installed get automatic update notifications
   - Users can run `/iw-install --update` to get latest version

### Commit Message Format

```
<Change description>

Version: <old-version> → <new-version>
Reason: <MAJOR|MINOR|PATCH> - <brief explanation>

<rest of commit message>
```

**Example:**
```
Add iw-version-check skill for automatic update notifications

Version: 0.9.0 → 1.0.0
Reason: MINOR - Added new skill with version checking functionality

- Created iw-version-check skill
- Added startup hook for version checking
- Updated manage_workflow.py to copy VERSION file

Issue: #7
```

## Version Checking System

### Components

1. **VERSION file** - Source of truth for current version
2. **iw-version-check skill** - Compares local vs remote version
3. **check_workflow_version.sh hook** - Runs version check at startup
4. **manage_workflow.py** - Copies VERSION during installation

### How It Works

1. During installation, VERSION file is copied to `.claude/skills/iw-install/VERSION`
2. On session start, the startup hook triggers version check
3. iw-version-check skill:
   - Reads local VERSION from `.claude/skills/iw-install/VERSION`
   - Fetches remote VERSION from GitHub
   - Compares using semantic versioning
   - Notifies user if update available
4. User can choose to update or skip

### User Experience

**When up to date:**
```
✓ Workflow is up to date (v1.0.0)
```

**When update available:**
```
✨ New workflow version available!

Current version: 1.0.0
Latest version:  1.1.0

Would you like to update now?
[Update now] [Skip this time] [Don't ask again]
```

## Common Scenarios

### Adding a New Skill

```bash
# Added iw-research-planner skill
# This is new functionality, not a breaking change
# Increment MINOR version

# Update VERSION file
echo "1.1.0" > VERSION

# Commit with version change
git add .claude/skills/iw-research-planner/ VERSION
git commit -m "Add iw-research-planner skill

Version: 1.0.0 → 1.1.0
Reason: MINOR - Added new research planning skill
"
```

### Fixing a Bug

```bash
# Fixed bug in iw-install script
# No breaking changes, no new features
# Increment PATCH version

# Update VERSION file
echo "1.0.1" > VERSION

# Commit with version change
git add .claude/skills/iw-install/scripts/manage_workflow.py VERSION
git commit -m "Fix error handling in manage_workflow.py

Version: 1.0.0 → 1.0.1
Reason: PATCH - Bug fix for clone timeout handling
"
```

### Breaking Change

```bash
# Changed skill interface parameters (breaking change)
# Increment MAJOR version

# Update VERSION file
echo "2.0.0" > VERSION

# Commit with version change and migration notes
git add .claude/skills/iw-planner/ VERSION
git commit -m "Update iw-planner skill interface

Version: 1.5.0 → 2.0.0
Reason: MAJOR - Breaking change to skill parameters

BREAKING CHANGE: The --mode flag has been replaced with --fast/--detailed
Users must update their invocations accordingly.
"
```

## Consequences of Not Updating VERSION

If VERSION is not updated when changes are made:

1. **Users won't be notified** - No update notification appears
2. **Version mismatch** - Users think they're up to date when they're not
3. **Confusion** - Users may not know which features are available
4. **Support issues** - Harder to debug which version users have installed

**Always update VERSION when changing .claude/ contents.**

## Version History Location

Version history and changelogs should be maintained in:
- Git commit history (primary source)
- GitHub releases (for major/minor versions)
- CHANGELOG.md file (optional, if created)

## Related Files

- `VERSION` - Version file at repo root
- `.claude/skills/iw-version-check/SKILL.md` - Version checking skill
- `.claude/skills/iw-install/scripts/manage_workflow.py` - Installation script
- `.claude/hooks/check_workflow_version.sh` - Startup hook

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- Issue #7 - Workflow versioning implementation
- Plan: `.docs/issues/7/7-plan.md`
