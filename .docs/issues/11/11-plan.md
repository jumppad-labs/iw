# Issue #11 Implementation Plan: Replace Git Worktree with Simple Branch Workflow

**Created**: 2025-11-04 20:30
**Last Updated**: 2025-11-04 20:30
**GitHub Issue**: #11

## Overview

Replace the git worktree-based workflow with a simpler branch-based approach to fix permission propagation issues in Claude Code. Currently, when Claude creates isolated worktrees in a parent directory, Claude Code settings don't propagate to those worktrees, causing excessive permission requests. The new workflow will create branches directly in the main repository, ensuring settings work correctly.

## Current State Analysis

The codebase currently uses a sophisticated worktree-based workflow for implementation isolation:

### Current Workflow:
1. **Planner** creates plan files in `.docs/issues/<N>/` (no git operations)
2. **Executor** invokes `iw-git-workflow` skill to create isolated worktree
3. **Worktree** created in parent directory (e.g., `/code/jumppad-issue-11-fix/`)
4. **Implementation** happens entirely in worktree
5. **Cleanup** pushes branch, optionally creates PR, removes worktree

### Key Code Locations:

**iw-git-workflow skill:**
- `.claude/skills/iw-git-workflow/SKILL.md` - Main documentation
- `.claude/skills/iw-git-workflow/scripts/check_clean.py` - Validates git state
- `.claude/skills/iw-git-workflow/scripts/create_worktree.py:66-94` - Creates worktree
- `.claude/skills/iw-git-workflow/scripts/get_branch_name.py:71-96` - Generates branch names
- `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py` - Phase commits
- `.claude/skills/iw-git-workflow/scripts/cleanup_worktree.py:145-270` - Cleanup and PR

**iw-planner skill:**
- `.claude/skills/iw-planner/SKILL.md:364-390` - Plan initialization
- No current git operations

**iw-executor skill:**
- `.claude/skills/iw-executor/SKILL.md:43-93` - Worktree setup
- `.claude/skills/iw-executor/SKILL.md:475-524` - Cleanup workflow

### Current Implementation Example:

**Worktree Creation:**
```python
# From .claude/skills/iw-git-workflow/scripts/create_worktree.py:66-94
def create_worktree(
    repo_root: Path,
    branch_name: str,
    base_branch: str
) -> tuple[bool, Path, str]:
    """Create worktree in parent directory."""
    repo_name = get_repo_name(repo_root)
    worktree_name = f"{repo_name}-{branch_name}"
    worktree_path = repo_root.parent / worktree_name  # PROBLEM: Parent directory

    if worktree_path.exists():
        return False, worktree_path, f"Worktree directory already exists: {worktree_path}"

    # Creates isolated worktree outside main repo
    returncode, stdout, stderr = run_git_command(
        ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
        repo_root
    )

    if returncode != 0:
        return False, worktree_path, f"Failed to create worktree: {stderr}"

    return True, worktree_path, ""
```

**Problem**: Worktree in parent directory doesn't inherit Claude Code settings from main repo.

## Desired End State

A simpler branch-based workflow where:

1. **Planner** creates branch directly in main repo and commits plan files
2. **Executor** validates branch, implements changes, commits phases
3. **Completion** pushes branch and optionally creates PR
4. **User** manually deletes branch after merging

### Verification:
- Run `/plan <issue-number>` and verify branch is created and plan files committed
- Run implementation and verify work happens on branch without permission issues
- Verify PR creation workflow still functions
- Verify no worktree-related code remains

## What We're NOT Doing

- **NOT** keeping worktree functionality as fallback - complete replacement
- **NOT** supporting both workflows - clean break from worktrees
- **NOT** auto-deleting branches - user responsibility after merge
- **NOT** modifying PR creation logic - reusing existing iw-github-pr-creator
- **NOT** changing branch naming conventions - keeping existing logic
- **NOT** changing phase commit format - keeping existing structure

## Implementation Approach

**Strategy**: Systematic replacement in three phases:

**Phase 1**: Create new branch-based git scripts
- Reuse existing `get_branch_name.py` (works as-is)
- Enhance `check_clean.py` to detect implementation branches
- Create `create_branch.py` for simple branch creation
- Create `commit_plan_files.py` for committing plans
- Create `check_branch.py` for branch validation
- Create `push_and_pr.py` for push and PR workflow

**Phase 2**: Update skill documentation and integration
- Update `iw-planner/SKILL.md` with branch creation workflow
- Rewrite `iw-git-workflow/SKILL.md` for branch-based workflow
- Update `iw-executor/SKILL.md` removing worktree references

**Phase 3**: Remove worktree code
- Delete `create_worktree.py`
- Delete `cleanup_worktree.py`
- Keep `create_phase_commit.py` (works with any git repo)
- Clean up any remaining worktree references

---

## Phase 1: Create Branch-Based Git Scripts

### Overview
Create new Python scripts for branch-based workflow, reusing existing code where possible.

### Changes Required:

#### 1. Enhance check_clean.py with Branch Detection

**File**: `.claude/skills/iw-git-workflow/scripts/check_clean.py`

**Current code:**
```python
# From check_clean.py:35-73
def check_git_status(directory: Path) -> dict:
    # Checks modified, staged, untracked files
    # Returns clean status
    return {
        "clean": is_clean,
        "modified": modified,
        "staged": staged,
        "untracked": untracked
    }
```

**Proposed changes:**
```python
# Enhanced check_clean.py
def check_git_status(directory: Path) -> dict:
    """Check git status including branch information."""
    # Existing checks for modified/staged/untracked files
    modified = check_modified_files()
    staged = check_staged_files()
    untracked = check_untracked_files()

    # NEW: Get current branch name
    returncode, branch_stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        directory
    )
    current_branch = branch_stdout.strip() if returncode == 0 else None

    # NEW: Detect if on implementation branch (issue-* or feature-*)
    is_implementation_branch = False
    if current_branch:
        is_implementation_branch = (
            current_branch.startswith("issue-") or
            current_branch.startswith("feature-")
        )

    is_clean = len(modified) == 0 and len(staged) == 0 and len(untracked) == 0

    return {
        "clean": is_clean,
        "modified": modified,
        "staged": staged,
        "untracked": untracked,
        "current_branch": current_branch,  # NEW
        "is_implementation_branch": is_implementation_branch  # NEW
    }
```

**Reasoning**: Need to know current branch state to prevent nested implementation branches.

#### 2. Create create_branch.py

**File**: `.claude/skills/iw-git-workflow/scripts/create_branch.py` (NEW)

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Create a new git branch for implementation work.

Usage:
    python3 create_branch.py --plan-path .docs/issues/123 [--base-branch main]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def run_git_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root(directory: Path) -> Path | None:
    """Get the git repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())

def get_current_branch(repo_root: Path) -> str | None:
    """Get current branch name."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        repo_root
    )
    if returncode != 0:
        return None
    return stdout.strip()

def check_branch_exists(repo_root: Path, branch_name: str) -> bool:
    """Check if branch already exists."""
    returncode, _, _ = run_git_command(
        ["git", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
        repo_root
    )
    return returncode == 0

def create_branch(
    repo_root: Path,
    branch_name: str,
    base_branch: str
) -> tuple[bool, str]:
    """
    Create new branch from base branch.

    Returns:
        Tuple of (success, error_message)
    """
    # Check if branch already exists
    if check_branch_exists(repo_root, branch_name):
        return False, f"Branch '{branch_name}' already exists"

    # Create and checkout new branch
    returncode, stdout, stderr = run_git_command(
        ["git", "checkout", "-b", branch_name, base_branch],
        repo_root
    )

    if returncode != 0:
        return False, f"Failed to create branch: {stderr}"

    return True, ""

def main():
    parser = argparse.ArgumentParser(description="Create implementation branch")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    parser.add_argument("--base-branch", default="main", help="Base branch to branch from")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "success": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Import get_branch_name helper
    sys.path.insert(0, str(Path(__file__).parent))
    from get_branch_name import generate_branch_name

    # Generate branch name from plan
    branch_name = generate_branch_name(plan_path)

    # Get current branch
    current_branch = get_current_branch(repo_root)

    # Create the branch
    success, error = create_branch(repo_root, branch_name, args.base_branch)

    if success:
        print(json.dumps({
            "success": True,
            "branch_name": branch_name,
            "base_branch": args.base_branch,
            "previous_branch": current_branch,
            "repo_root": str(repo_root)
        }))
        sys.exit(0)
    else:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Reasoning**: Simple branch creation replacing complex worktree logic. Reuses existing `get_branch_name.py`.

#### 3. Create commit_plan_files.py

**File**: `.claude/skills/iw-git-workflow/scripts/commit_plan_files.py` (NEW)

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Commit plan files to the current branch.

Usage:
    python3 commit_plan_files.py --plan-path .docs/issues/123
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def run_git_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root(directory: Path) -> Path | None:
    """Get the git repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())

def commit_plan_files(
    repo_root: Path,
    plan_path: Path
) -> tuple[bool, str, str]:
    """
    Commit all plan files in the plan directory.

    Returns:
        Tuple of (success, commit_hash, error_message)
    """
    # Stage all files in plan directory
    returncode, stdout, stderr = run_git_command(
        ["git", "add", str(plan_path)],
        repo_root
    )

    if returncode != 0:
        return False, "", f"Failed to stage files: {stderr}"

    # Check if there are changes to commit
    returncode, stdout, stderr = run_git_command(
        ["git", "diff", "--cached", "--quiet"],
        repo_root
    )

    if returncode == 0:
        # No changes to commit
        return True, "", "No changes to commit"

    # Extract issue number or plan name for commit message
    plan_name = plan_path.name
    if plan_path.parent.name == "issues":
        commit_message = f"Add implementation plan for issue #{plan_name}"
    else:
        commit_message = f"Add implementation plan: {plan_name}"

    # Create commit
    returncode, stdout, stderr = run_git_command(
        ["git", "commit", "-m", commit_message],
        repo_root
    )

    if returncode != 0:
        return False, "", f"Failed to create commit: {stderr}"

    # Get commit hash
    returncode, commit_hash, _ = run_git_command(
        ["git", "rev-parse", "HEAD"],
        repo_root
    )

    return True, commit_hash.strip(), ""

def main():
    parser = argparse.ArgumentParser(description="Commit plan files")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "success": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Commit plan files
    success, commit_hash, error = commit_plan_files(repo_root, plan_path)

    if success:
        result = {
            "success": True,
            "commit_hash": commit_hash if commit_hash else None,
            "message": "Plan files committed successfully" if commit_hash else "No changes to commit"
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Reasoning**: Automatically commit plan files to new branch for clean git history.

#### 4. Create check_branch.py

**File**: `.claude/skills/iw-git-workflow/scripts/check_branch.py` (NEW)

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Check if current branch is valid for implementation work.

Usage:
    python3 check_branch.py --plan-path .docs/issues/123
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def run_git_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root(directory: Path) -> Path | None:
    """Get the git repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())

def get_current_branch(repo_root: Path) -> str | None:
    """Get current branch name."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        repo_root
    )
    if returncode != 0:
        return None
    return stdout.strip()

def check_branch_for_plan(
    repo_root: Path,
    plan_path: Path
) -> tuple[bool, str, str]:
    """
    Check if we're on the correct branch for this plan.

    Returns:
        Tuple of (is_valid, current_branch, error_message)
    """
    # Get expected branch name
    sys.path.insert(0, str(Path(__file__).parent))
    from get_branch_name import generate_branch_name

    expected_branch = generate_branch_name(plan_path)

    # Get current branch
    current_branch = get_current_branch(repo_root)
    if not current_branch:
        return False, "", "Could not determine current branch"

    # Check if on expected branch
    if current_branch != expected_branch:
        return False, current_branch, f"Expected to be on branch '{expected_branch}', but currently on '{current_branch}'"

    return True, current_branch, ""

def main():
    parser = argparse.ArgumentParser(description="Check branch validity")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "valid": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "valid": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Check branch
    is_valid, current_branch, error = check_branch_for_plan(repo_root, plan_path)

    if is_valid:
        print(json.dumps({
            "valid": True,
            "current_branch": current_branch
        }))
        sys.exit(0)
    else:
        print(json.dumps({
            "valid": False,
            "current_branch": current_branch,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Reasoning**: Validates executor is on correct branch before starting implementation.

#### 5. Create push_and_pr.py

**File**: `.claude/skills/iw-git-workflow/scripts/push_and_pr.py` (NEW)

**Proposed implementation:**
```python
#!/usr/bin/env python3
"""
Push current branch and optionally create pull request.

Usage:
    python3 push_and_pr.py --plan-path .docs/issues/123 [--create-pr] [--base-branch main]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def run_git_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root(directory: Path) -> Path | None:
    """Get the git repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())

def get_current_branch(repo_root: Path) -> str | None:
    """Get current branch name."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        repo_root
    )
    if returncode != 0:
        return None
    return stdout.strip()

def push_branch(repo_root: Path, branch_name: str) -> tuple[bool, str]:
    """Push branch to remote with upstream tracking."""
    returncode, stdout, stderr = run_git_command(
        ["git", "push", "-u", "origin", branch_name],
        repo_root
    )

    if returncode != 0:
        return False, f"Failed to push branch: {stderr}"

    return True, ""

def create_pr(
    repo_root: Path,
    branch_name: str,
    plan_path: Path | None,
    base_branch: str
) -> tuple[bool, str, str]:
    """Create PR using iw-github-pr-creator skill."""
    # Find iw-github-pr-creator script
    script_path = Path(__file__).parent.parent.parent / "iw-github-pr-creator" / "scripts" / "create_pr.py"

    if not script_path.exists():
        return False, "", "iw-github-pr-creator script not found - ensure skill is installed"

    cmd = [
        "python3",
        str(script_path),
        "--branch", branch_name,
        "--base", base_branch,
        "--directory", str(repo_root)
    ]

    if plan_path:
        cmd.extend(["--plan-path", str(plan_path)])

    returncode, stdout, stderr = run_command(cmd, repo_root)

    if returncode != 0:
        return False, "", f"Failed to create PR: {stderr}"

    try:
        result = json.loads(stdout)
        pr_url = result.get("url", "")
        return True, pr_url, ""
    except json.JSONDecodeError:
        return False, "", "Failed to parse PR creation result"

def main():
    parser = argparse.ArgumentParser(description="Push branch and create PR")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    parser.add_argument("--create-pr", action="store_true", help="Create pull request")
    parser.add_argument("--base-branch", default="main", help="Base branch for PR")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "success": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Get current branch
    branch_name = get_current_branch(repo_root)
    if not branch_name:
        print(json.dumps({
            "success": False,
            "error": "Could not determine current branch"
        }))
        sys.exit(1)

    result = {
        "success": True,
        "branch_name": branch_name
    }

    # Push branch
    success, error = push_branch(repo_root, branch_name)
    if not success:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

    result["pushed"] = True

    # Create PR if requested
    if args.create_pr:
        success, pr_url, error = create_pr(repo_root, branch_name, plan_path, args.base_branch)
        if success:
            result["pr_created"] = True
            result["pr_url"] = pr_url
        else:
            # PR creation failure is not fatal
            result["pr_created"] = False
            result["pr_error"] = error

    print(json.dumps(result))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Reasoning**: Replaces `cleanup_worktree.py` but without worktree removal. Reuses PR creation logic.

### Success Criteria:

#### Automated Verification:
- [ ] All new scripts execute without syntax errors: `python3 -m py_compile *.py`
- [ ] Scripts accept expected arguments: `python3 create_branch.py --help`
- [ ] JSON output is valid: `echo $output | python3 -m json.tool`

#### Manual Verification:
- [ ] `create_branch.py` creates branch and switches to it
- [ ] `commit_plan_files.py` commits files with proper message
- [ ] `check_branch.py` validates current branch correctly
- [ ] `push_and_pr.py` pushes branch successfully
- [ ] `push_and_pr.py --create-pr` creates PR via iw-github-pr-creator

---

## Phase 2: Update Skill Documentation

### Overview
Update skill documentation to reflect branch-based workflow, removing all worktree references.

### Changes Required:

#### 1. Update iw-planner Skill Documentation

**File**: `.claude/skills/iw-planner/SKILL.md`

**Current section** (lines 364-390):
```markdown
## Step 4: Detailed Plan Writing

**⚠️ REMINDER: Verify any user corrections are documented in research.md and `.docs/knowledge/learnings/` before proceeding. ⚠️**

### Ensure Documentation Structure Exists

**FIRST: Invoke the `iw-init` skill to ensure base .docs structure exists:**

Use the Skill tool to invoke the `iw-init` skill...
```

**Proposed changes:**
```markdown
## Step 4: Detailed Plan Writing

**⚠️ REMINDER: Verify any user corrections are documented in research.md and `.docs/knowledge/learnings/` before proceeding. ⚠️**

### Ensure Documentation Structure Exists

**FIRST: Invoke the `iw-init` skill to ensure base .docs structure exists:**

Use the Skill tool to invoke the `iw-init` skill...

[Keep existing init instructions]

### Initialize Plan Structure

[Keep existing init_plan.py instructions]

### Create Git Branch and Commit Plan Files

**AFTER creating plan files, set up git branch:**

1. **Check git state** using `check_clean.py`:
   - Verify working directory is clean
   - Check if already on implementation branch
   - If on implementation branch, STOP and warn user to return to main

2. **Create branch** using `create_branch.py`:
   - Generates branch name from plan (issue-N-title or feature-name)
   - Creates branch from main (or specified base)
   - Switches to new branch

3. **Commit plan files** using `commit_plan_files.py`:
   - Stages all files in plan directory
   - Creates commit: "Add implementation plan for issue #N"
   - Reports commit hash

**Example workflow:**
```bash
# Check git state
python3 .claude/skills/iw-git-workflow/scripts/check_clean.py

# If clean, create branch
python3 .claude/skills/iw-git-workflow/scripts/create_branch.py \
  --plan-path .docs/issues/11 \
  --base-branch main

# Commit plan files
python3 .claude/skills/iw-git-workflow/scripts/commit_plan_files.py \
  --plan-path .docs/issues/11
```

4. **Report to user:**
```
✅ Implementation plan created successfully!

Branch: issue-11-git-worktree-implementation
Plan directory: .docs/issues/11/
Commit: abc1234

Files created:
- 11-plan.md - Implementation details
- 11-research.md - Research notes
- 11-context.md - Quick reference
- 11-tasks.md - Task checklist

Ready for implementation with /implement or iw-executor skill.
```

### Customize the Four Files

[Keep existing file customization instructions]
```

**Reasoning**: Adds git workflow to planner after plan files created.

#### 2. Rewrite iw-git-workflow Skill Documentation

**File**: `.claude/skills/iw-git-workflow/SKILL.md`

**Complete rewrite** - new content:

```markdown
# Git Workflow for Implementation

## Overview

Manage git workflow for implementation tasks using simple branches for isolated work. This skill provides safety checks, branch management, phase-based commits, and completion operations.

**Designed to be invoked by iw-planner and iw-executor skills.**

## When to Use This Skill

This skill is automatically invoked by:
- **iw-planner** - After creating plan files, to create branch and commit
- **iw-executor** - Before implementation, to validate branch; after completion, to push

Direct invocation is also supported for manual git operations.

## Workflow Overview

### Planning Phase (invoked by iw-planner):
1. Check git state is clean
2. Verify not on implementation branch
3. Create new branch from main
4. Commit plan files to branch

### Execution Phase (invoked by iw-executor):
1. Validate on correct branch
2. Implement changes
3. Commit after each phase
4. Push branch and optionally create PR

## Scripts

### check_clean.py
**Purpose**: Validate git repository state

**Usage**:
```bash
python3 scripts/check_clean.py
```

**Returns**:
```json
{
  "clean": true,
  "modified": [],
  "staged": [],
  "untracked": [],
  "current_branch": "main",
  "is_implementation_branch": false
}
```

**Use when**: Before creating branch, to ensure clean state

### create_branch.py
**Purpose**: Create new implementation branch

**Usage**:
```bash
python3 scripts/create_branch.py --plan-path .docs/issues/123 [--base-branch main]
```

**Returns**:
```json
{
  "success": true,
  "branch_name": "issue-123-feature-name",
  "base_branch": "main",
  "previous_branch": "main",
  "repo_root": "/path/to/repo"
}
```

**Use when**: After plan files created, to set up implementation branch

### commit_plan_files.py
**Purpose**: Commit plan files to current branch

**Usage**:
```bash
python3 scripts/commit_plan_files.py --plan-path .docs/issues/123
```

**Returns**:
```json
{
  "success": true,
  "commit_hash": "abc1234...",
  "message": "Plan files committed successfully"
}
```

**Use when**: After creating branch, to commit initial plan

### check_branch.py
**Purpose**: Validate on correct branch for implementation

**Usage**:
```bash
python3 scripts/check_branch.py --plan-path .docs/issues/123
```

**Returns**:
```json
{
  "valid": true,
  "current_branch": "issue-123-feature-name"
}
```

**Use when**: Before starting implementation, to ensure correct branch

### create_phase_commit.py
**Purpose**: Commit changes after completing a phase

**Usage**:
```bash
python3 scripts/create_phase_commit.py --phase 1 --plan-path .docs/issues/123
```

**Returns**:
```json
{
  "success": true,
  "commit_hash": "def5678...",
  "commit_message": "Phase 1: Foundation\n\nImplemented...",
  "stats": "3 files changed, 45 insertions(+)"
}
```

**Use when**: After completing each implementation phase

### push_and_pr.py
**Purpose**: Push branch and optionally create PR

**Usage**:
```bash
# Push only
python3 scripts/push_and_pr.py --plan-path .docs/issues/123

# Push and create PR
python3 scripts/push_and_pr.py --plan-path .docs/issues/123 --create-pr --base-branch main
```

**Returns**:
```json
{
  "success": true,
  "branch_name": "issue-123-feature-name",
  "pushed": true,
  "pr_created": true,
  "pr_url": "https://github.com/owner/repo/pull/456"
}
```

**Use when**: After implementation complete, to push and create PR

### get_branch_name.py
**Purpose**: Generate branch name from plan path (helper)

**Usage**: Imported by other scripts, not called directly

**Returns**: `issue-123-feature-name` or `feature-plan-name`

## Integration with Other Skills

### iw-planner Integration

After creating plan files, planner invokes:
1. `check_clean.py` - Ensure clean state
2. `create_branch.py` - Create implementation branch
3. `commit_plan_files.py` - Commit plan to branch

### iw-executor Integration

During implementation, executor invokes:
1. `check_branch.py` - Validate on correct branch before starting
2. `create_phase_commit.py` - After each phase completion
3. `push_and_pr.py` - After all phases complete

### iw-github-pr-creator Integration

`push_and_pr.py` calls `iw-github-pr-creator/scripts/create_pr.py` when `--create-pr` flag provided.

## Branch Naming Conventions

**Issue-based plans**: `issue-<number>-<title-slug>`
- Example: `issue-123-add-rate-limiting`

**Ad-hoc plans**: `feature-<plan-name>`
- Example: `feature-refactor-auth`

## Error Handling

### Git state not clean
```json
{
  "clean": false,
  "modified": ["file1.py", "file2.md"],
  "staged": [],
  "untracked": ["temp.txt"]
}
```
**Action**: Ask user to commit or stash changes

### Already on implementation branch
```json
{
  "current_branch": "issue-100-other-feature",
  "is_implementation_branch": true
}
```
**Action**: Ask user to return to main branch first

### Branch already exists
```json
{
  "success": false,
  "error": "Branch 'issue-123-feature' already exists"
}
```
**Action**: User may have already started, ask if they want to continue on existing branch

## Success Criteria

- Clean state validation prevents dirty commits
- Branch names follow conventions
- Plan files committed with clear messages
- Phase commits include structured info
- PR creation integrates seamlessly
```

**Reasoning**: Complete documentation rewrite for branch-based workflow.

#### 3. Update iw-executor Skill Documentation

**File**: `.claude/skills/iw-executor/SKILL.md`

**Current section** (lines 43-93) - "Git Safety and Worktree Setup":

**Proposed replacement:**
```markdown
## Step 0: Git Branch Validation

Before starting implementation, ensure we're on the correct branch for this plan.

**IMPORTANT**: Work happens on the implementation branch created by iw-planner. All file operations happen in the main repository (no separate worktree).

### Validate Branch

1. **Use `iw-git-workflow` skill to check branch**:
   ```bash
   python3 .claude/skills/iw-git-workflow/scripts/check_branch.py \
     --plan-path <plan-directory>
   ```

2. **Expected output** (success):
   ```json
   {
     "valid": true,
     "current_branch": "issue-123-feature-name"
   }
   ```

3. **If validation fails**:
   ```json
   {
     "valid": false,
     "current_branch": "main",
     "error": "Expected to be on branch 'issue-123-feature', but currently on 'main'"
   }
   ```
   **Action**: Stop and inform user they need to checkout the implementation branch:
   ```
   ❌ Not on correct branch!

   Expected: issue-123-feature-name
   Current: main

   Please run:
   git checkout issue-123-feature-name

   Then restart implementation.
   ```

4. **If valid, proceed** with implementation on current branch.

**Note**: All file operations use the main repository path. No worktree switching needed.
```

**Current section** (lines 475-524) - "Completion and Cleanup":

**Proposed replacement:**
```markdown
## Step N: Completion and Cleanup

After all phases complete, push branch and optionally create PR.

### Push Branch and Create PR

1. **Ask user about PR creation**:
   ```
   ✅ All phases complete!

   Would you like me to:
   1. Push branch and create pull request
   2. Just push branch (create PR manually later)
   3. Leave branch local for review
   ```

2. **Based on user choice**:

   **Option 1: Push and create PR**
   ```bash
   python3 .claude/skills/iw-git-workflow/scripts/push_and_pr.py \
     --plan-path <plan-directory> \
     --create-pr \
     --base-branch main
   ```

   **Option 2: Just push**
   ```bash
   python3 .claude/skills/iw-git-workflow/scripts/push_and_pr.py \
     --plan-path <plan-directory>
   ```

   **Option 3: Do nothing**
   ```
   ✅ Implementation complete!

   Branch: issue-123-feature-name

   To push and create PR later:
   git push -u origin issue-123-feature-name
   gh pr create
   ```

3. **Report results** to user:
   ```
   ✅ Implementation complete and pushed!

   Branch: issue-123-feature-name
   PR: https://github.com/owner/repo/pull/456

   The branch has been pushed but NOT deleted. After the PR is merged, you can delete it with:
   git branch -d issue-123-feature-name
   ```

**Note**: Branch is NOT automatically deleted. User manages branch lifecycle.
```

**Reasoning**: Updates executor to use branch validation instead of worktree creation, and simplified cleanup.

### Success Criteria:

#### Automated Verification:
- [ ] Markdown files are valid: `markdownlint SKILL.md`
- [ ] No broken file references in documentation
- [ ] All script paths are correct

#### Manual Verification:
- [ ] Documentation accurately describes branch workflow
- [ ] No worktree terminology remains (except in "what we're removing" sections)
- [ ] Integration points clearly documented
- [ ] Error handling scenarios covered

---

## Phase 3: Remove Worktree Code

### Overview
Delete worktree-specific scripts and clean up any remaining references.

### Changes Required:

#### 1. Delete create_worktree.py

**File**: `.claude/skills/iw-git-workflow/scripts/create_worktree.py`

**Action**: Delete entire file

**Reasoning**: Replaced by `create_branch.py`

#### 2. Delete cleanup_worktree.py

**File**: `.claude/skills/iw-git-workflow/scripts/cleanup_worktree.py`

**Action**: Delete entire file

**Reasoning**: Replaced by `push_and_pr.py`

#### 3. Keep create_phase_commit.py

**File**: `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py`

**Action**: Keep as-is (works with any git directory)

**Minor update** - change one comment:
```python
# OLD comment line 8:
# """Create a commit for a completed implementation phase in worktree."""

# NEW comment:
# """Create a commit for a completed implementation phase."""
```

**Reasoning**: Script is not worktree-specific, just remove worktree reference in docstring.

#### 4. Keep get_branch_name.py

**File**: `.claude/skills/iw-git-workflow/scripts/get_branch_name.py`

**Action**: Keep as-is (already reusable)

**Reasoning**: Used by both old and new workflows, no changes needed.

#### 5. Search and Remove Remaining References

**Search for** worktree references in all skill files:
```bash
grep -r "worktree" .claude/skills/iw-planner/ .claude/skills/iw-executor/ .claude/skills/iw-git-workflow/
```

**Expected findings**:
- None (all should be updated in Phase 2)

**If found**: Update or remove the references.

### Success Criteria:

#### Automated Verification:
- [ ] `create_worktree.py` does not exist
- [ ] `cleanup_worktree.py` does not exist
- [ ] `grep -r "worktree"` returns no matches (except historical references in docs)
- [ ] All scripts in `scripts/` directory are executable: `ls -la scripts/`

#### Manual Verification:
- [ ] No broken imports or script references
- [ ] Skills load without errors
- [ ] Test planning workflow end-to-end:
  - Create plan with `/plan test-issue`
  - Verify branch created
  - Verify plan files committed
- [ ] Test execution workflow:
  - Check branch validation works
  - Verify phase commits work
  - Verify push and PR creation work

---

## Testing Strategy

### Unit Tests:
Not required for Python scripts (simple git wrappers). Manual testing sufficient.

### Integration Tests:

**Test 1: Planning Workflow**
```bash
# Start fresh
git checkout main
git pull

# Create plan
# (Invoke iw-planner skill)
/plan "Test branch workflow"

# Verify branch created
git branch --show-current  # Should be feature-test-branch-workflow

# Verify commit
git log -1  # Should show "Add implementation plan: test-branch-workflow"
```

**Test 2: Multi-Issue Prevention**
```bash
# While on implementation branch
git checkout issue-100-feature

# Try to create another plan
# (Invoke iw-planner skill)
/plan "Another feature"

# Should fail with error about being on implementation branch
```

**Test 3: Execution Workflow**
```bash
# Checkout implementation branch
git checkout issue-123-feature

# Run executor
# (Invoke iw-executor skill)

# Verify phase commits created
git log --oneline  # Should show "Phase 1: ...", "Phase 2: ..."

# Push and create PR
# (Choose option 1 at completion)

# Verify push
git branch -r  # Should show origin/issue-123-feature

# Verify PR
gh pr list  # Should show new PR
```

### Manual Testing Steps:

1. **Clean Planning:**
   - Start on main with clean state
   - Create plan for new issue
   - Verify branch created with correct name
   - Verify plan files committed

2. **Dirty State Handling:**
   - Make uncommitted changes
   - Try to create plan
   - Should fail with clear error about dirty state

3. **Implementation Branch Prevention:**
   - Checkout implementation branch
   - Try to create new plan
   - Should fail with warning to return to main

4. **Execution Validation:**
   - Checkout wrong branch
   - Try to start executor
   - Should fail with branch mismatch error

5. **Phase Commits:**
   - Execute implementation
   - Verify each phase creates separate commit
   - Verify commit messages formatted correctly

6. **Push and PR:**
   - Complete implementation
   - Choose "push and create PR"
   - Verify branch pushed to remote
   - Verify PR created with correct content

7. **Manual PR Creation:**
   - Complete implementation
   - Choose "just push"
   - Manually create PR with `gh pr create`
   - Verify workflow accommodates manual PR creation

## Performance Considerations

**Branch operations faster than worktrees:**
- `git checkout -b` vs `git worktree add`: Branch ~10ms, worktree ~100ms+
- No directory creation/removal overhead
- No worktree list management
- Simpler git operations overall

**Reduced disk usage:**
- No duplicate working trees
- No parent directory pollution
- Only one `.git` directory

**Improved responsiveness:**
- No permission requests for separate directories
- Settings propagate immediately
- File watchers work correctly

## Migration Notes

**For users with existing worktrees:**

1. **List existing worktrees**:
   ```bash
   git worktree list
   ```

2. **For each worktree**, manually clean up:
   ```bash
   # Get work from worktree
   cd /path/to/worktree
   git push -u origin <branch-name>

   # Return to main repo
   cd /path/to/main/repo

   # Remove worktree
   git worktree remove /path/to/worktree

   # Checkout branch in main repo
   git checkout <branch-name>

   # Continue work or create PR
   ```

3. **After migration**: All new plans use branch workflow automatically.

**For existing plan files:**
- Plans in `.docs/issues/` and `.docs/adhoc/` work identically
- No changes to plan file format
- Branch names generated same way as before

## References

- Original ticket: GitHub Issue #11
- Research notes: `.docs/issues/11/11-research.md`
- Context: `.docs/issues/11/11-context.md`
- Learning from issue #10: Prefer simpler git operations over complex solutions
- Git documentation: https://git-scm.com/docs/git-branch
- GitHub CLI: https://cli.github.com/manual/gh_pr_create
