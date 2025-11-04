---
name: iw-git-workflow
description: Manage git workflow for implementation tasks using simple branches for isolated work. This skill should be used when starting implementation work, creating commits after phases, and completing with push and PR. Provides safety checks, branch management, phase-based commits, and completion operations.
---

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
