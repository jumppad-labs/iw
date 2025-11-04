# Issue #14 Implementation Plan - Windows Compatible Installation

**Created**: 2025-11-04 10:35
**Last Updated**: 2025-11-04 10:35

## Overview

Create a fully cross-platform (Windows, macOS, Linux) installation process for the Implementation Workflow by converting bash-specific scripts to pure Python and adding UTF-8 encoding support for Windows consoles.

Currently, the installation fails on Windows due to:
1. Bash-only bootstrap script (bootstrap.sh) that won't run on Windows
2. Unicode encoding errors in Python scripts (cp1252 can't display ✓, ✗, etc.)
3. Bash-only hook scripts (.sh files) that won't execute on Windows

## Current State Analysis

### Key Code Locations:

**Bootstrap Entry Point:**
- `bootstrap.sh:1-116` - Bash script using `read -p`, `$HOME`, `mkdir -p`, `chmod +x`, `curl`
- Issue: Bash-specific commands don't work on native Windows

**Installation Manager:**
- `.claude/skills/iw-install/scripts/manage_workflow.py:1-587` - Core installation logic
- Line 182, 197, 270, 281, 360, 375, 390, 419, 431, etc. - Unicode characters (✓, ✗)
- Lines 233-239 - chmod with Unix-specific stat flags
- Lines 85-141 - Git clone implementation (already cross-platform compatible)

**Hook Scripts:**
- `.claude/hooks/load_workflow.sh:1-16` - Simple echo-based hook
- `.claude/hooks/check_workflow_version.sh:1-17` - Version check with bash conditionals
- `.claude/hooks/list_skills.sh:1-76` - Complex skill listing with git, find, awk

### Current Bootstrap Implementation:
```bash
# From bootstrap.sh:31
read -p "Enter choice [1 or 2]: " choice

# From bootstrap.sh:55-56
mkdir -p "$INSTALL_DIR/skills/$SKILL_NAME/scripts"
mkdir -p "$INSTALL_DIR/commands"

# From bootstrap.sh:75
chmod +x "$INSTALL_DIR/skills/$SKILL_NAME/scripts/manage_workflow.py" 2>/dev/null || true
```

### Current manage_workflow.py Unicode Usage:
```python
# From manage_workflow.py:182
print(f"  ✓ Copied {file_count} files to {subdir_name}/")

# No UTF-8 configuration at module level
# Windows defaults to cp1252, causing UnicodeEncodeError
```

### Current chmod Implementation:
```python
# From manage_workflow.py:233-239
def _make_executable(self, file_path: Path):
    """Make a file executable."""
    try:
        current = file_path.stat().st_mode
        file_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"  Warning: Could not make {file_path} executable: {e}")
```

## Desired End State

After implementation:
1. **Pure Python bootstrap** that works on Windows, macOS, and Linux without requiring bash
2. **UTF-8 encoding configured** in all Python scripts to display Unicode characters on Windows
3. **Pure Python hooks** that work across all platforms without shell dependencies
4. **Platform-aware chmod** that only applies Unix permissions on Unix systems
5. **No need for backwards compatibility with bash scripts**, if python is not present then the skills will not work anyway

**Verification Method:**
- Run bootstrap.py on Windows, macOS, and Linux
- Verify Unicode characters display correctly on all platforms
- Verify hooks execute successfully on all platforms
- Confirm no regression for existing Unix users

## What We're NOT Doing

- Not changing the git clone architecture (learned from issue #10)
- Not adding external dependencies (Python stdlib only)
- Not creating PowerShell-specific solutions (pure Python is cross-platform)
- Not modifying the overall workflow structure or concepts

## Implementation Approach

Use pure Python to eliminate all platform-specific shell dependencies. Python 3.7+ is already required for the workflow, so this adds no new dependencies. The approach:

1. **Create bootstrap.py** - Cross-platform Python script using urllib and pathlib
2. **Add UTF-8 configuration** - Configure encoding at script startup for Windows
3. **Convert hooks to Python** - Replace bash/awk logic with Python equivalents
4. **Update manage_workflow.py** - Platform-aware chmod and hook handling
5. **Update documentation** - Cross-platform installation instructions

---

## Phase 1: UTF-8 Encoding Support

### Overview
Add UTF-8 encoding configuration to manage_workflow.py to fix Unicode display on Windows. This is the quickest win and unblocks Python script execution.

### Changes Required:

#### 1. manage_workflow.py - UTF-8 Encoding Configuration
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:1-15`
**Changes**: Add UTF-8 encoding configuration at module level

**Current code:**
```python
#!/usr/bin/env python3
"""
Implementation Workflow Installer Script

Manages installation, updates, and removal of the Implementation Workflow
for Claude Code. Uses git clone to fetch files from GitHub.

Usage:
    python3 manage_workflow.py install --location project
    python3 manage_workflow.py update --location user
    python3 manage_workflow.py uninstall --location project
    python3 manage_workflow.py verify --location project
    python3 manage_workflow.py list --location project
"""

import argparse
```

**Proposed changes:**
```python
#!/usr/bin/env python3
"""
Implementation Workflow Installer Script

Manages installation, updates, and removal of the Implementation Workflow
for Claude Code. Uses git clone to fetch files from GitHub.

Usage:
    python3 manage_workflow.py install --location project
    python3 manage_workflow.py update --location user
    python3 manage_workflow.py uninstall --location project
    python3 manage_workflow.py verify --location project
    python3 manage_workflow.py list --location project
"""

# Configure UTF-8 encoding for Windows compatibility
# Windows console defaults to cp1252 which can't display Unicode chars like ✓, ✗
import sys
import io

if sys.platform == 'win32':
    # Wrap stdout and stderr with UTF-8 encoding
    # errors='replace' provides graceful fallback for unsupported chars
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
```

**Reasoning**: This configuration must happen before any Unicode output. Placing it at module level ensures it runs before any functions execute. The `errors='replace'` parameter provides graceful degradation if the terminal truly doesn't support UTF-8.

#### 2. manage_workflow.py - Platform-Aware chmod
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:19,233-239`
**Changes**: Add platform import and make chmod conditional

**Current code:**
```python
import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ... later in file ...

def _make_executable(self, file_path: Path):
    """Make a file executable."""
    try:
        current = file_path.stat().st_mode
        file_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"  Warning: Could not make {file_path} executable: {e}")
```

**Proposed changes:**
```python
import argparse
import json
import os
import platform  # Add platform for OS detection
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ... later in file ...

def _make_executable(self, file_path: Path):
    """
    Make a file executable (Unix only).

    On Windows, Python scripts don't need executable bit.
    On Unix, adds execute permissions for user, group, and other.
    """
    # Python scripts work with 'python3 script.py' on all platforms
    # Only set executable bit on Unix systems for convention
    if platform.system() == 'Windows':
        return  # No-op on Windows

    try:
        current = file_path.stat().st_mode
        file_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as e:
        print(f"  Warning: Could not make {file_path} executable: {e}")
```

**Reasoning**: Python scripts don't require the executable bit on any platform (can always run with `python3 script.py`). Checking platform explicitly is clearer than catching OSError, and prevents confusion about Windows "failures".

### Testing for This Phase:

**Unit Tests**: Not required for this phase (simple configuration changes)

**Manual Testing Steps**:
1. Test on Windows:
   ```powershell
   python3 .claude/skills/iw-install/scripts/manage_workflow.py list --location user
   ```
   - Verify Unicode characters (✓, ✗) display correctly
   - Verify no UnicodeEncodeError
   - Verify no chmod warnings

2. Test on Linux/macOS:
   ```bash
   python3 .claude/skills/iw-install/scripts/manage_workflow.py list --location user
   ```
   - Verify Unicode characters still display
   - Verify chmod still works for Unix scripts
   - Verify no behavior change from before

### Success Criteria:

#### Automated Verification:
- [ ] Script runs without errors: `python3 manage_workflow.py list`
- [ ] No syntax errors: `python3 -m py_compile manage_workflow.py`

#### Manual Verification:
- [ ] Unicode characters display on Windows console
- [ ] No UnicodeEncodeError on Windows
- [ ] No chmod warnings on Windows
- [ ] chmod still works on Unix systems
- [ ] No behavior change for Unix users

---

## Phase 2: Pure Python Bootstrap

### Overview
Create bootstrap.py as a cross-platform replacement for bootstrap.sh. This enables Windows users to install without WSL/Git Bash.

### Changes Required:

#### 1. Create bootstrap.py
**File**: `bootstrap.py` (new file)
**Changes**: Create complete Python bootstrap script

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Implementation Workflow Bootstrap Script

Cross-platform installer for the iw-install skill, which can then
install the full Implementation Workflow.

Supports Windows, macOS, and Linux without requiring bash.

Usage:
    python3 bootstrap.py
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import urllib.request
import urllib.error
from pathlib import Path

# Configuration
REPO_URL = "https://raw.githubusercontent.com/jumppad-labs/iw/main"
SKILL_NAME = "iw-install"


def print_header():
    """Print welcome banner."""
    print("=" * 46)
    print("Implementation Workflow Bootstrap")
    print("=" * 46)
    print()
    print("This script will install the iw-install skill,")
    print("which you can then use to install the full workflow.")
    print()


def get_installation_choice():
    """
    Prompt user for installation location.

    Returns:
        tuple: (install_dir: Path, install_type: str)
    """
    print("Where would you like to install the workflow?")
    print()
    print("1) Project-level (.claude in current directory)")
    print("   - Committed to version control")
    print("   - Shared with team members")
    print("   - Project-specific configuration")
    print()
    print("2) User-level (~/.claude in home directory)")
    print("   - Available in all projects")
    print("   - Personal configuration")
    print("   - Not committed to repos")
    print()

    while True:
        choice = input("Enter choice [1 or 2]: ").strip()

        if choice == "1":
            install_dir = Path.cwd() / ".claude"
            install_type = "project"
            print()
            print(f"Installing to project-level: {install_dir}")
            return install_dir, install_type
        elif choice == "2":
            install_dir = Path.home() / ".claude"
            install_type = "user"
            print()
            print(f"Installing to user-level: {install_dir}")
            return install_dir, install_type
        else:
            print("Invalid choice. Please enter 1 or 2.")


def download_file(url: str, dest_path: Path) -> bool:
    """
    Download a file from URL to destination path.

    Args:
        url: Source URL to download from
        dest_path: Destination file path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()

        # Ensure parent directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        dest_path.write_bytes(content)
        return True

    except urllib.error.URLError as e:
        print(f"  Error: Failed to download {url}")
        print(f"  {e}")
        return False
    except IOError as e:
        print(f"  Error: Failed to write to {dest_path}")
        print(f"  {e}")
        return False


def main():
    """Main bootstrap process."""
    print_header()

    # Get installation location from user
    install_dir, install_type = get_installation_choice()

    print()
    print("Creating directory structure...")

    # Create directory structure
    skill_dir = install_dir / "skills" / SKILL_NAME / "scripts"
    commands_dir = install_dir / "commands"

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        commands_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"  Error: Could not create directories: {e}")
        return 1

    # Download files
    files_to_download = [
        (
            f"{REPO_URL}/.claude/skills/{SKILL_NAME}/SKILL.md",
            install_dir / "skills" / SKILL_NAME / "SKILL.md"
        ),
        (
            f"{REPO_URL}/.claude/skills/{SKILL_NAME}/scripts/manage_workflow.py",
            install_dir / "skills" / SKILL_NAME / "scripts" / "manage_workflow.py"
        ),
        (
            f"{REPO_URL}/.claude/commands/iw-install.md",
            install_dir / "commands" / "iw-install.md"
        ),
    ]

    print("Downloading iw-install skill...")

    for url, dest in files_to_download:
        if not download_file(url, dest):
            print()
            print("=" * 46)
            print("Bootstrap Failed!")
            print("=" * 46)
            print()
            print("Could not download required files. Check:")
            print("  - Internet connection is working")
            print("  - GitHub is accessible")
            print()
            return 1

    print()
    print("=" * 46)
    print("Bootstrap Complete!")
    print("=" * 46)
    print()
    print("The iw-install skill has been installed to:")
    print(f"  {install_dir / 'skills' / SKILL_NAME}")
    print()
    print("Next steps:")
    print()
    print("1. Start or restart Claude Code")
    print()
    print("2. Run the installation command:")
    if install_type == "project":
        print("   /iw-install")
        print()
        print("   This will install the full workflow to your project.")
    else:
        print("   /iw-install --user")
        print()
        print("   This will install the full workflow to ~/.claude/")
    print()
    print("3. Start using the workflow:")
    print("   /iw-help          - Show workflow guidance")
    print("   /iw-plan <task>   - Create implementation plan")
    print()
    print("For more information, see:")
    print("  https://github.com/jumppad-labs/iw")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Reasoning**:
- Uses only Python stdlib (urllib, pathlib) for cross-platform compatibility
- Mirrors bootstrap.sh functionality but in pure Python
- UTF-8 configuration at top for Windows support
- Uses `input()` instead of bash `read -p`
- Uses `Path.home()` and `Path.cwd()` instead of $HOME and $PWD
- Error handling for network and file operations

#### 2. Deprecate bootstrap.sh
**File**: `bootstrap.sh:1`
**Changes**: Add deprecation notice

**Current code:**
```bash
#!/bin/bash
set -e
```

**Proposed changes:**
```bash
#!/bin/bash
set -e

# DEPRECATED: This bash script is deprecated in favor of bootstrap.py
# For Windows compatibility, please use: python3 bootstrap.py
# This script remains for backward compatibility with existing Unix workflows.
#
# See bootstrap.py for the cross-platform Python version.
```

**Reasoning**: Keeps existing script functional for users who have it, but directs new users to Python version.

### Testing for This Phase:

**Manual Testing Steps**:

1. Test on Windows:
   ```powershell
   python3 bootstrap.py
   # Select option 2 (user-level)
   # Verify downloads succeed
   # Verify files created in ~\.claude\
   ```

2. Test on macOS:
   ```bash
   python3 bootstrap.py
   # Select option 1 (project-level)
   # Verify downloads succeed
   # Verify files created in .claude/
   ```

3. Test on Linux:
   ```bash
   python3 bootstrap.py
   # Select option 2 (user-level)
   # Verify downloads succeed
   ```

4. Test network error handling:
   ```bash
   # Disconnect from network
   python3 bootstrap.py
   # Verify graceful error message
   ```

### Success Criteria:

#### Automated Verification:
- [ ] Python syntax valid: `python3 -m py_compile bootstrap.py`
- [ ] No import errors: `python3 -c "import bootstrap"`

#### Manual Verification:
- [ ] Bootstrap runs on Windows without errors
- [ ] Bootstrap runs on macOS without errors
- [ ] Bootstrap runs on Linux without errors
- [ ] Files download successfully
- [ ] Directory structure created correctly
- [ ] Network errors handled gracefully
- [ ] User input validated properly

---

## Phase 3: Pure Python Hooks

### Overview
Convert all three bash hook scripts to pure Python for cross-platform compatibility. Hooks are executed by Claude Code at session start to provide workflow context.

### Changes Required:

#### 1. Create load_workflow.py
**File**: `.claude/hooks/load_workflow.py` (new file)
**Changes**: Create Python version of load_workflow.sh

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Hook script to load the iw-workflow skill at session start.

Provides context about the project workflow and documentation structure.
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    """Print workflow guidance."""
    print("Loading workflow guidance...")
    print()
    print("Documentation Structure:")
    print("- CLAUDE.md: General Go development standards")
    print("- .docs/knowledge/: Jumppad-specific technical knowledge")
    print("- workflow skill: Process and methodology (auto-loaded)")
    print()
    print("Use /iw-plan for complex features, /iw-implement to execute plans.")
    print("See the workflow skill for full details on the planning and implementation process.")
    print()


if __name__ == "__main__":
    main()
```

**Reasoning**: Simple translation of bash echo statements to Python print. UTF-8 configuration ensures output works on Windows.

#### 2. Create check_workflow_version.py
**File**: `.claude/hooks/check_workflow_version.py` (new file)
**Changes**: Create Python version of check_workflow_version.sh

**Proposed implementation:**
```python
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
```

**Reasoning**: Replaces bash conditionals with Path.exists() checks. Uses Path.home() instead of $HOME. Logic is equivalent but more robust (Path handles platform differences).

#### 3. Create list_skills.py
**File**: `.claude/hooks/list_skills.py` (new file)
**Changes**: Create Python version of list_skills.sh

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Hook script to list available skills for Claude Code.

This script is executed at session start to remind Claude of available skills.
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import re
from pathlib import Path


def get_git_root():
    """
    Get git repository root directory.

    Returns:
        Path or None: Root directory if in git repo, None otherwise
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def extract_description(skill_md: Path) -> str:
    """
    Extract description from SKILL.md YAML frontmatter.

    Args:
        skill_md: Path to SKILL.md file

    Returns:
        str: Description or empty string if not found
    """
    try:
        content = skill_md.read_text(encoding='utf-8')
    except (IOError, UnicodeDecodeError):
        return ""

    # Parse YAML frontmatter
    # Format: --- at start, description: value, --- at end
    in_frontmatter = False
    in_description = False
    description_lines = []

    for line in content.split('\n'):
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            if not in_frontmatter and description_lines:
                # End of frontmatter, we have description
                break
            continue

        if not in_frontmatter:
            continue

        # Check if line starts a new field
        if re.match(r'^[a-z].*:', line):
            in_description = line.strip().startswith('description:')
            if in_description:
                # Extract value after "description:"
                value = line.split(':', 1)[1].strip()
                if value:
                    description_lines.append(value)
        elif in_description:
            # Continuation of description (multi-line)
            description_lines.append(line.strip())

    return ' '.join(description_lines)


def main():
    """List all available skills."""
    # Find skill directories
    skill_dirs = []

    # Check project-level skills (if in git repo)
    git_root = get_git_root()
    if git_root:
        project_skills = git_root / ".claude" / "skills"
        if project_skills.is_dir():
            skill_dirs.append(project_skills)

    # Check user-level skills
    user_skills = Path.home() / ".claude" / "skills"
    if user_skills.is_dir():
        skill_dirs.append(user_skills)

    # Exit if no skill directories found
    if not skill_dirs:
        return

    # Count total skills
    skill_count = 0
    for skills_dir in skill_dirs:
        skill_count += sum(1 for _ in skills_dir.iterdir() if _.is_dir())

    if skill_count == 0:
        return

    # Output header
    print(f"Available Skills ({skill_count}):")
    print()

    # List each skill
    for skills_dir in skill_dirs:
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_name = skill_dir.name
            skill_md = skill_dir / "SKILL.md"

            if skill_md.exists():
                description = extract_description(skill_md)
                if description:
                    print(f"- {skill_name}: {description}")
                else:
                    print(f"- {skill_name}")
            else:
                print(f"- {skill_name} (no SKILL.md found)")

    print()


if __name__ == "__main__":
    main()
```

**Reasoning**: Replaces complex bash/awk/find pipeline with Python code. Uses subprocess for git command, pathlib for directory traversal, and regex for YAML parsing. More readable and maintainable than awk script.

#### 4. Deprecate bash hooks
**File**: `.claude/hooks/load_workflow.sh:1`
**Changes**: Add deprecation notices to all bash hooks

**Proposed changes:**
```bash
#!/bin/bash

# DEPRECATED: This bash hook is deprecated in favor of load_workflow.py
# For Windows compatibility, use the Python version: .claude/hooks/load_workflow.py
# This script remains for backward compatibility with existing Unix workflows.
#
# See load_workflow.py for the cross-platform Python version.

# Hook script to load the iw-workflow skill at session start
```

**Reasoning**: Same as bootstrap.sh - maintain backward compatibility while directing users to Python versions.

#### 5. Update manage_workflow.py hook installation
**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:54-58,184-188`
**Changes**: Update HOOKS list and installation logic to include Python hooks

**Current code:**
```python
HOOKS = [
    "load_workflow.sh",
    "list_skills.sh",
    "check_workflow_version.sh",
]

# ... later ...

# Make hook scripts executable
hooks_dir = self.target_dir / "hooks"
if hooks_dir.exists():
    for hook_file in hooks_dir.glob("*.sh"):
        self._make_executable(hook_file)
```

**Proposed changes:**
```python
HOOKS = [
    "load_workflow.sh",        # Deprecated, keep for backward compatibility
    "list_skills.sh",          # Deprecated, keep for backward compatibility
    "check_workflow_version.sh",  # Deprecated, keep for backward compatibility
    "load_workflow.py",        # Cross-platform Python version
    "list_skills.py",          # Cross-platform Python version
    "check_workflow_version.py",  # Cross-platform Python version
]

# ... later ...

# Make hook scripts executable (Unix only, for .sh files)
hooks_dir = self.target_dir / "hooks"
if hooks_dir.exists():
    # Only chmod .sh files on Unix (Python scripts don't need it)
    for hook_file in hooks_dir.glob("*.sh"):
        self._make_executable(hook_file)
```

**Reasoning**: Installs both .sh and .py versions. Claude Code will prefer .py versions on all platforms. The .sh files remain for backward compatibility.

### Testing for This Phase:

**Manual Testing Steps**:

1. Test load_workflow.py:
   ```bash
   python3 .claude/hooks/load_workflow.py
   # Verify output displays correctly
   ```

2. Test check_workflow_version.py:
   ```bash
   python3 .claude/hooks/check_workflow_version.py
   # Verify check runs or skips based on marker files
   ```

3. Test list_skills.py:
   ```bash
   python3 .claude/hooks/list_skills.py
   # Verify all skills listed with descriptions
   ```

4. Test on Windows:
   ```powershell
   python3 .claude\hooks\load_workflow.py
   python3 .claude\hooks\check_workflow_version.py
   python3 .claude\hooks\list_skills.py
   # Verify Unicode displays, no errors
   ```

5. Test YAML parsing:
   - Create test skill with multi-line description
   - Verify list_skills.py parses correctly

### Success Criteria:

#### Automated Verification:
- [ ] Python syntax valid: `python3 -m py_compile .claude/hooks/*.py`
- [ ] All hooks execute without errors

#### Manual Verification:
- [ ] load_workflow.py displays guidance correctly
- [ ] check_workflow_version.py checks opt-out correctly
- [ ] list_skills.py lists all skills with descriptions
- [ ] Hooks work on Windows without bash
- [ ] Hooks work on Unix without regression
- [ ] YAML frontmatter parsing works correctly
- [ ] Git repository detection works correctly

---

## Phase 4: Documentation Updates

### Overview
Update README.md and SKILL.md to document cross-platform installation and Windows support.

### Changes Required:

#### 1. Update README.md Installation Section
**File**: `README.md` (installation section)
**Changes**: Add cross-platform instructions

**Current section** likely shows bash bootstrap only.

**Proposed additions:**
```markdown
## Installation

### Quick Start (All Platforms)

The Implementation Workflow supports Windows, macOS, and Linux.

**Recommended: Python Bootstrap (Cross-Platform)**
```bash
# Download bootstrap script
curl -sSL https://raw.githubusercontent.com/jumppad-labs/iw/main/bootstrap.py -o bootstrap.py

# Run bootstrap
python3 bootstrap.py
```

**Alternative: Bash Bootstrap (Unix Only)**
```bash
# For macOS/Linux users who prefer bash
curl -sSL https://raw.githubusercontent.com/jumppad-labs/iw/main/bootstrap.sh | bash
```

After bootstrap completes, restart Claude Code and run `/iw-install` to complete installation.

### Platform-Specific Notes

**Windows:**
- Requires Python 3.7+ and Git for Windows
- Use `python3 bootstrap.py` (bootstrap.sh won't work without WSL)
- PowerShell, Command Prompt, and Git Bash all supported

**macOS/Linux:**
- Both bootstrap.py and bootstrap.sh work
- Requires Python 3.7+ and git
- Python version recommended for consistency

### Requirements

- **Python 3.7+**: Required for workflow scripts
- **Git**: Required for cloning workflow repository
- **Internet connection**: For downloading files from GitHub
```

**Reasoning**: Documents Python bootstrap as primary method, with bash as alternative for Unix users. Clarifies Windows requirements and support.

#### 2. Update iw-install SKILL.md
**File**: `.claude/skills/iw-install/SKILL.md`
**Changes**: Add Windows compatibility section

**Proposed addition** (insert after Requirements section):
```markdown
## Windows Support

The workflow is fully compatible with Windows 10/11:

- ✅ Python scripts work on Windows natively
- ✅ UTF-8 encoding configured for Unicode output
- ✅ Cross-platform path handling with pathlib
- ✅ Git for Windows supported

**Requirements for Windows:**
- Python 3.7+ (from python.org or Microsoft Store)
- Git for Windows (from git-scm.com)
- Any terminal (PowerShell, Command Prompt, or Git Bash)

**Known Issues:**
- Older Windows terminals may not display Unicode characters (✓, ✗)
- Scripts use ASCII fallback automatically if UTF-8 unavailable
```

**Reasoning**: Explicitly documents Windows support and requirements to give users confidence.

### Testing for This Phase:

**Manual Testing Steps**:

1. Follow README instructions on Windows
   - Verify steps work as written
   - Verify commands are correct

2. Follow README instructions on macOS
   - Verify both Python and bash methods work

3. Verify SKILL.md accuracy
   - Confirm Python version requirements
   - Confirm Git version requirements

### Success Criteria:

#### Automated Verification:
- [ ] Markdown syntax valid: `markdownlint README.md`

#### Manual Verification:
- [ ] Installation instructions clear for all platforms
- [ ] Requirements documented accurately
- [ ] Examples work as written
- [ ] Windows section is comprehensive
- [ ] Links are valid

---

## Testing Strategy

### Integration Testing:

**End-to-end installation test on each platform:**

Windows PowerShell:
```powershell
# Clean environment
Remove-Item -Recurse -Force ~\.claude -ErrorAction SilentlyContinue

# Bootstrap
python3 bootstrap.py
# Select option 2 (user-level)

# Restart Claude Code (simulated)

# Full installation
python3 ~\.claude\skills\iw-install\scripts\manage_workflow.py install --location user

# Verify
python3 ~\.claude\skills\iw-install\scripts\manage_workflow.py verify --location user

# Test hooks
python3 ~\.claude\hooks\load_workflow.py
python3 ~\.claude\hooks\check_workflow_version.py
python3 ~\.claude\hooks\list_skills.py
```

macOS/Linux:
```bash
# Clean environment
rm -rf ~/.claude

# Bootstrap (Python version)
python3 bootstrap.py

# Full installation
python3 ~/.claude/skills/iw-install/scripts/manage_workflow.py install --location user

# Verify
python3 ~/.claude/skills/iw-install/scripts/manage_workflow.py verify --location user

# Test hooks
python3 ~/.claude/hooks/load_workflow.py
python3 ~/.claude/hooks/check_workflow_version.py
python3 ~/.claude/hooks/list_skills.py
```

### Manual Testing Steps:

1. **Unicode Display Test**: Verify ✓, ✗, ✅, ❌ display on:
   - Windows PowerShell
   - Windows Command Prompt
   - Windows Terminal
   - macOS Terminal
   - Linux gnome-terminal

2. **Path Handling Test**: Verify paths with spaces:
   ```bash
   mkdir "test dir with spaces"
   cd "test dir with spaces"
   python3 bootstrap.py
   # Verify installation works
   ```

3. **Network Error Handling Test**:
   - Disconnect network
   - Run bootstrap.py
   - Verify graceful error message

4. **Backward Compatibility Test**:
   - Run bootstrap.sh on Unix
   - Verify still works
   - Verify no warnings or errors

## Performance Considerations

No significant performance impact:
- UTF-8 configuration is one-time at script startup
- Platform detection (`platform.system()`) is cached by Python
- Python hooks may be slightly slower than bash equivalents, but hooks run once at session start (negligible impact)

**Benchmark expectations:**
- Bootstrap: Same speed as bash version (~5-10 seconds for downloads)
- Hook execution: <100ms difference between bash and Python versions
- Installation: No change (git clone is the bottleneck)

## Migration Notes

**For existing Unix users:**
- No action required
- Bash scripts continue to work
- Python scripts installed alongside for future-proofing

**For Windows users:**
- New installations work immediately with bootstrap.py
- Existing WSL-based installations can continue using bash or migrate to Python

**For repository maintainers:**
- Deprecate but don't remove bash scripts
- Update documentation to recommend Python bootstrap
- Consider removing bash scripts in v2.0 (breaking change)

## References

- Original ticket: [GitHub Issue #14](https://github.com/jumppad-labs/iw/issues/14)
- Windows bug report: Included in issue description with UnicodeEncodeError details
- Past learning: `.docs/knowledge/learnings/installation.md` - Git clone architecture decision
- Python stdlib docs: https://docs.python.org/3/library/
- Cross-platform Python: https://docs.python.org/3/library/platform.html
