# Issue #14 - Research & Working Notes

**Research Date**: 2025-11-04
**Researchers**: Claude + nicj

## Initial Understanding

Issue #14 requests Windows compatibility for the Implementation Workflow installation. The initial problem report identified two critical issues:
1. Bootstrap script (bootstrap.sh) is bash-only
2. Unicode encoding errors in Python scripts on Windows

The report from Windows testing (included in issue description) documented a `UnicodeEncodeError` when running manage_workflow.py on Windows due to cp1252 encoding unable to display Unicode characters like ✓ (U+2713).

## Research Process

### Files Examined:

- `bootstrap.sh` (lines 1-116)
  - Finding: Bash script with platform-specific commands (`read -p`, `$HOME`, `mkdir -p`, `chmod +x`, `curl`)
  - Issue: Won't run natively on Windows, requires WSL/Git Bash
  - Relevant pattern: Uses curl to download initial files from GitHub

- `.claude/skills/iw-install/scripts/manage_workflow.py` (lines 1-587)
  - Finding: Core installation script using git clone approach (lines 85-141)
  - Issue: Unicode characters in print statements (lines 182, 197, 270, 281, 360, 375, 390, etc.)
  - Issue: chmod operations (lines 233-239) use Unix-specific stat flags (S_IXUSR, S_IXGRP, S_IXOTH)
  - Good: Uses pathlib.Path throughout for cross-platform path handling
  - Good: subprocess.run with list arguments (cross-platform compatible)

- `.claude/hooks/load_workflow.sh` (lines 1-16)
  - Finding: Simple echo-based hook, minimal bash usage
  - Issue: Won't execute on Windows

- `.claude/hooks/check_workflow_version.sh` (lines 1-17)
  - Finding: Checks for opt-out marker file, invokes version check skill
  - Issue: Uses bash conditionals and $HOME variable

- `.claude/hooks/list_skills.sh` (lines 1-76)
  - Finding: Most complex hook with git, find, and awk usage
  - Issue: Heavy bash dependencies (arrays, git rev-parse, find, awk)

### Sub-tasks Spawned:

1. **iw-learnings**: Search for past installation learnings
   - Result: Found `.docs/knowledge/learnings/installation.md`
   - Key discovery: Issue #10 decision to use git clone instead of API requests (more robust, avoids rate limiting)

2. **Task/Explore - Find installation files**: Locate all installation-related files
   - Result: Identified 8 key files including bootstrap, manage_workflow.py, hooks, and documentation
   - Key discovery: Hooks are registered in hooks/ directory and invoked by Claude Code at session start

3. **Task/Explore - Unicode usage patterns**: Search for Unicode in Python scripts
   - Result: Found 19 Python files using Unicode characters
   - Key discovery: Unicode usage is widespread (✓, ✗, ✅, ❌, ⚠️, ℹ️, ✨, 🔍, 🚀, →)
   - Impact: All scripts need UTF-8 encoding configuration

4. **Task/Explore - Cross-platform code**: Find existing platform compatibility patterns
   - Result: Good use of pathlib.Path throughout
   - Issue: No platform detection code (no sys.platform checks)
   - Issue: chmod operations don't have Windows fallbacks

5. **Task/Explore - Temp directory handling**: Research cleanup mechanisms
   - Result: Uses tempfile.mkdtemp with shutil.rmtree for cleanup
   - Issue: No retry logic for Windows file locking
   - Pattern: Uses ignore_errors=True in error handlers, try/except in cleanup method

6. **Task/general-purpose - Installation architecture**: Analyze complete flow
   - Result: Comprehensive mapping of entry points, execution flow, and integration points
   - Key discovery: 15 specific Windows compatibility issues identified
   - Bootstrap → iw-install command → manage_workflow.py → git clone → copy files → hooks registered

### Questions Asked & Answers:

1. Q: Which approach should we use for Windows compatibility?
   Options: Pure Python Bootstrap, Dual Bootstrap Scripts, ASCII Fallback
   A: Pure Python Bootstrap
   Follow-up: This provides the most robust cross-platform solution with single codebase

2. Q: Should we make hooks fully cross-platform or keep separate .sh and .ps1 files?
   Options: Pure Python Hooks, Dual Implementation, Minimal Hooks
   A: Pure Python Hooks
   Follow-up: Eliminates platform-specific shell scripts, fully cross-platform

## Key Discoveries

### Technical Discoveries:

1. **Unicode encoding is the primary blocker** (manage_workflow.py:182, 197, 270, etc.)
   - Windows console defaults to cp1252 encoding
   - Python's stdout doesn't auto-detect UTF-8
   - Solution: Configure UTF-8 encoding at script startup with io.TextIOWrapper

2. **Bootstrap script is bash-specific** (bootstrap.sh:1-116)
   - Uses bash-only commands: read -p, case statements, $HOME, chmod
   - Solution: Rewrite as bootstrap.py using cross-platform Python libraries

3. **Hooks won't execute on Windows** (.claude/hooks/*.sh)
   - All hooks are bash scripts with .sh extension
   - Windows needs .py or .ps1 files
   - Solution: Convert to Python scripts (cross-platform)

4. **chmod operations fail silently on Windows** (manage_workflow.py:233-239)
   - Uses stat.S_IXUSR, S_IXGRP, S_IXOTH (Unix-only)
   - Python scripts don't need executable bit on any platform
   - Solution: Make chmod operations platform-aware or skip for Python files

5. **Git clone approach is already cross-platform** (manage_workflow.py:85-141)
   - subprocess.run with list arguments works on all platforms
   - pathlib.Path handles path separators correctly
   - This architecture should be preserved (learned from issue #10)

### Patterns to Follow:

1. **UTF-8 Encoding Configuration** (from Windows bug report)
   ```python
   import sys
   import io

   if sys.platform == 'win32':
       sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
       sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
   ```

2. **Cross-platform path handling** (already used in manage_workflow.py)
   ```python
   from pathlib import Path

   # Good: Uses Path.home() and / operator
   target_dir = Path.home() / ".claude"
   ```

3. **Platform detection for optional operations** (new pattern to add)
   ```python
   import platform

   if platform.system() != 'Windows':
       # Unix-specific operations
       file_path.chmod(0o755)
   ```

### Constraints Identified:

1. **Must preserve git clone architecture** - Learned from issue #10, this approach avoids API rate limiting
2. **Must maintain backward compatibility** - Existing Unix users should see no change in behavior
3. **Must work without bash** - Pure Windows users don't have bash installed
4. **Claude Code hook system** - Hooks must be invokable by Claude Code on all platforms
5. **No external dependencies** - Should work with stdlib Python 3.7+ only

## Design Decisions

### Decision 1: Bootstrap Script Approach

**Options considered:**
- **Option A: Pure Python bootstrap.py**
  - Pros: Fully cross-platform, single codebase, no shell dependencies
  - Cons: Requires Python to be in PATH (already required for workflow)

- **Option B: Dual scripts (bootstrap.sh + bootstrap.ps1)**
  - Pros: Native platform experience
  - Cons: Two codebases to maintain, PowerShell syntax complexity

- **Option C: Keep bash, document WSL requirement**
  - Pros: No code changes
  - Cons: Poor user experience, requires WSL installation

**Chosen**: Option A (Pure Python bootstrap.py)

**Rationale**:
- Python is already required for the workflow to function
- Single codebase reduces maintenance burden
- Provides best cross-platform experience
- Can use rich libraries (urllib, pathlib) for robust implementation

### Decision 2: Hook Implementation Strategy

**Options considered:**
- **Option A: Pure Python hooks**
  - Pros: Fully cross-platform, single codebase, can use Python libraries
  - Cons: Lose bash/awk terseness for text processing

- **Option B: Dual implementation (.sh + .ps1)**
  - Pros: Native platform experience, keeps bash terseness
  - Cons: Two codebases, platform detection needed, PowerShell learning curve

- **Option C: Minimal/optional hooks**
  - Pros: Reduces complexity
  - Cons: Loses useful functionality (skill listing, version checks)

**Chosen**: Option A (Pure Python hooks)

**Rationale**:
- Eliminates platform-specific shell scripts entirely
- Python is already required for workflow
- Can use rich Python libraries for parsing YAML, running git commands
- Single codebase for maintenance
- Better error handling than shell scripts

### Decision 3: Unicode Character Handling

**Options considered:**
- **Option A: Configure UTF-8 encoding at script startup**
  - Pros: Keeps Unicode characters, good UX
  - Cons: Requires configuration code in all scripts

- **Option B: Replace with ASCII alternatives**
  - Pros: No encoding issues
  - Cons: Less visually appealing, loses clarity

- **Option C: Create utility module for output**
  - Pros: Centralized encoding logic
  - Cons: Adds dependency between scripts

**Chosen**: Option A (Configure UTF-8 encoding)

**Rationale**:
- Modern terminals support UTF-8
- Better user experience with visual indicators
- Configuration is simple (5 lines per script)
- Fallback to ASCII via errors='replace' if terminal doesn't support UTF-8

### Decision 4: chmod Operation Handling

**Options considered:**
- **Option A: Platform detection with conditional chmod**
  - Pros: Preserves Unix behavior, safe on Windows
  - Cons: Platform-specific code

- **Option B: Remove chmod entirely**
  - Pros: Simplest solution
  - Cons: Python scripts don't need it, but loses Unix convention

- **Option C: Try/except with silent fail**
  - Pros: Works on both platforms
  - Cons: Already implemented, but doesn't distinguish platforms

**Chosen**: Option A (Platform detection)

**Rationale**:
- Python scripts don't need executable bit on any platform (python3 script.py works everywhere)
- Shell scripts need it on Unix but don't exist on Windows anymore (converting to Python)
- Explicit platform check is clearer than try/except
- Aligns with professional cross-platform Python practices

## Corrections During Planning

*None - user provided clear direction through questions about approach*

## Open Questions (During Research)

- [x] Should we use pure Python or dual implementation? - Resolved: Pure Python for both bootstrap and hooks
- [x] How should we handle Unicode characters? - Resolved: Configure UTF-8 encoding at startup
- [x] Should hooks be converted to Python? - Resolved: Yes, pure Python hooks
- [x] Do we need to preserve bash hooks for backward compatibility? - Resolved: No, Python hooks will replace them

**All questions resolved. Ready to proceed with plan.**

## Code Snippets Reference

### Relevant Existing Code:

```python
# From .claude/skills/iw-install/scripts/manage_workflow.py:233-239
# chmod operation that needs platform awareness
def _make_executable(self, file_path: Path):
    """Make a file executable."""
    try:
        current = file_path.stat().st_mode
        file_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"  Warning: Could not make {file_path} executable: {e}")
```

```python
# From .claude/skills/iw-install/scripts/manage_workflow.py:182
# Unicode characters that cause Windows encoding errors
print(f"  ✓ Copied {file_count} files to {subdir_name}/")
```

```bash
# From bootstrap.sh:31
# Bash-specific read command
read -p "Enter choice [1 or 2]: " choice
```

```bash
# From .claude/hooks/list_skills.sh:49-61
# Complex awk script for parsing YAML frontmatter
description=$(awk '
    /^---$/ { in_fm = !in_fm; next }
    in_fm && /^description:/ {
        sub(/^description: */, "")
        desc = $0
        while (getline > 0 && !/^[a-z].*:/) {
            if (/^---$/) break
            desc = desc " " $0
        }
        print desc
        exit
    }
' "$skill_md")
```

### Similar Patterns Found:

```python
# From .claude/skills/obsidian-local-api/scripts/config_helper.py:96
# Platform-aware file permissions
CONFIG_FILE.chmod(0o600)  # User-only read/write
```

```python
# From .claude/skills/iw-install/scripts/manage_workflow.py:78-83
# Good cross-platform path handling pattern
def _get_target_dir(self) -> Path:
    if self.location == "user":
        return Path.home() / ".claude"
    else:
        return Path.cwd() / ".claude"
```

## Past Learnings Applied

From `.docs/knowledge/learnings/installation.md`:

**2025-11-03 - Clone Repo Instead of Individual API Requests**

Applied to this plan:
- Preserve the git clone architecture (lines 85-141 in manage_workflow.py)
- Don't refactor to use API requests
- This approach is more robust and faster than individual file downloads
- Already cross-platform compatible (subprocess.run with list arguments)
