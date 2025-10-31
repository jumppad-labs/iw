---
name: iw-git-workflow
description: Manage git workflow for implementation tasks using worktrees for isolation. This skill should be used when starting implementation work, creating commits after phases, and cleaning up after completion. Provides safety checks, worktree management, phase-based commits, and cleanup operations.
---

# Git Workflow

## Overview

Manage safe git workflows for implementation tasks using worktrees for complete isolation from the main working directory. Ensure clean git state before starting, create isolated worktrees, commit after each phase, and handle cleanup.

**Worktree-Based Approach:** Always use git worktrees to isolate implementation work. This keeps the main working directory clean, allows parallel implementations, and provides easy rollback if needed.

**Safety First:** Verify git state is clean before starting any work. Stop immediately if there are uncommitted changes in the main working directory.

**Phase Commits:** Create meaningful commits after each implementation phase with descriptive messages that reference the plan and phase number.

## Quick Start

**Before starting implementation:**
```bash
# Check if git state is clean
python3 scripts/check_clean.py

# Create worktree for implementation
python3 scripts/create_worktree.py --plan-path .docs/issues/123/ --base-branch main
```

**After completing a phase:**
```bash
# Create phase commit
python3 scripts/create_phase_commit.py --phase 1 --plan-path .docs/issues/123/
```

**After implementation complete:**
```bash
# Push, create PR, cleanup
python3 scripts/cleanup_worktree.py --worktree-path /path/to/worktree --create-pr
```

## Workflow

### Step 1: Safety Check

Before starting any implementation work:

1. **Check Git State:**
   - Use `scripts/check_clean.py` to verify main working directory is clean
   - Script checks for:
     - Uncommitted changes
     - Untracked files (except ignored files)
     - Staged but uncommitted changes
   - Returns status and list of issues if any

2. **If Not Clean:**
   - STOP immediately
   - Present issues to user:
     ```
     ⚠️  Git Working Directory Not Clean

     The main working directory has uncommitted changes.
     Implementation requires a clean state to use worktrees safely.

     Issues found:
     - [list of uncommitted files]
     - [list of staged files]
     - [list of untracked files]

     Please commit or stash these changes before starting implementation.
     ```
   - Do not proceed until user has cleaned up

3. **If Clean:**
   - Proceed to create worktree
   - Main working directory remains untouched

### Step 2: Create Worktree

When starting implementation:

1. **Determine Branch Name:**
   - Use `scripts/get_branch_name.py` to generate branch name
   - For issue-based plans: `issue-<number>-<short-description>`
     - Example: `issue-123-add-rate-limiting`
   - For ad-hoc plans: `feature-<plan-name>`
     - Example: `feature-refactor-auth`
   - Script parses plan files to extract info

2. **Create Worktree:**
   - Use `scripts/create_worktree.py` to create isolated worktree
   - Script does:
     - Creates new branch from base branch (usually main)
     - Creates worktree directory (usually `../jumppad-<branch-name>`)
     - Checks out the new branch in worktree
     - Returns worktree path for use

3. **Inform User:**
   ```
   ✓ Created worktree for implementation

   Branch: issue-123-add-rate-limiting
   Worktree: /home/user/code/jumppad-issue-123-add-rate-limiting
   Base: main

   All implementation work will happen in the worktree.
   Main working directory remains clean and untouched.
   ```

4. **Important:**
   - All subsequent file operations happen in the worktree
   - Main working directory is never modified
   - User can continue other work in main directory if needed

### Step 3: Phase Commits

After each phase completes:

1. **Verify Phase Completion:**
   - All tasks in phase are done
   - Tests pass
   - User confirmed phase completion

2. **Create Phase Commit:**
   - Use `scripts/create_phase_commit.py` to commit changes
   - Script does:
     - Stages all changes in worktree
     - Creates commit with phase-based message
     - Includes plan reference
     - Adds co-authored-by if configured

3. **Commit Message Format:**
   ```
   Phase N: <Phase Name>

   <Brief description of what was implemented in this phase>

   Plan: <path-to-plan>
   Issue: #<issue-number> (if applicable)
   ```

4. **Example:**
   ```
   Phase 1: Add Rate Limiting Middleware

   Implemented token bucket rate limiter with configurable limits.
   Added middleware to API endpoints for request throttling.

   Plan: .docs/issues/123/123-plan.md
   Issue: #123
   ```

5. **Inform User:**
   ```
   ✓ Phase 1 committed

   Commit: abc1234 - Phase 1: Add Rate Limiting Middleware
   Files changed: 5
   Insertions: 120, Deletions: 10
   ```

### Step 4: Completion & Cleanup

After all phases complete and implementation is done:

1. **Final Verification:**
   - All tasks complete
   - All tests pass
   - User confirmed ready to finish

2. **Push Branch:**
   - Use `scripts/cleanup_worktree.py` for final operations
   - Script does:
     - Pushes branch from worktree to remote
     - Optionally creates pull request using `gh pr create`
     - Removes worktree directory
     - Returns to main working directory

3. **Pull Request Creation (Optional):**
   - If `--create-pr` flag used:
     - Delegates to **iw-github-pr-creator skill** for PR creation
     - Automatically detects plan path in worktree
     - iw-github-pr-creator handles:
       - Extracting plan summary and phases
       - Generating PR title and body
       - Linking to plan files and issues
       - Creating PR with gh CLI
   - See iw-github-pr-creator skill for PR format details

4. **Cleanup:**
   - Remove worktree directory
   - Branch remains on remote for PR review
   - Main working directory still clean

5. **Inform User:**
   ```
   ✓ Implementation Complete

   Branch pushed: issue-123-add-rate-limiting
   Pull request: #456 - Add Rate Limiting to API
   Worktree cleaned up: /path/to/worktree

   Main working directory remains clean.
   You can now review the PR or continue other work.
   ```

## Integration with iw-executor

The iw-executor skill uses iw-git-workflow at key points:

**At Start:**
1. Activate iw-git-workflow skill
2. Check if git is clean (stop if not)
3. Create worktree for implementation
4. Switch context to worktree for all file operations

**After Each Phase:**
1. Invoke iw-git-workflow to create phase commit
2. Commit captures all changes from that phase
3. Continue to next phase

**At Completion:**
1. Invoke iw-git-workflow for cleanup
2. Push branch, optionally create PR
3. Remove worktree
4. Return to main directory

This integration ensures:
- Main directory always stays clean
- Each phase has its own commit for easy review
- Easy rollback if something goes wrong
- Clean separation between implementations

## Important Guidelines

### Worktree Best Practices

**Always use worktrees for implementation:**
- Never work directly in main working directory
- Keeps main directory available for other tasks
- Easy to abandon if plan changes
- Allows parallel implementations

**Worktree location:**
- Create worktrees in parent directory: `../jumppad-<branch-name>`
- Keeps worktrees organized and easy to find
- Doesn't clutter main repository directory

**Cleanup promptly:**
- Remove worktrees after PR created
- Don't leave orphaned worktrees around
- Use cleanup script to ensure proper removal

### Commit Messages

**Phase-based commits:**
- One commit per phase
- Clear reference to phase number and name
- Include plan file path
- Link to issue if applicable

**Meaningful descriptions:**
- Explain what was implemented, not just file changes
- Focus on business logic and features
- Help reviewers understand changes

### Safety

**Stop if directory not clean:**
- Never proceed with dirty state
- User must clean up first
- Prevents accidental loss of work

**Verify before cleanup:**
- Ensure all work is committed
- Verify tests pass
- Confirm with user before removing worktree

## Resources

### scripts/

This skill includes five Python scripts for git workflow management:

**`check_clean.py`** - Verify git state is clean
```bash
python3 scripts/check_clean.py [--directory <path>]
```
Returns exit code 0 if clean, non-zero if dirty. Outputs list of issues.

**`get_branch_name.py`** - Generate branch name from plan
```bash
python3 scripts/get_branch_name.py --plan-path <plan-directory>
```
Outputs branch name like `issue-123-feature-name` or `feature-plan-name`.

**`create_worktree.py`** - Create worktree with branch
```bash
python3 scripts/create_worktree.py --plan-path <plan-directory> --base-branch <branch>
```
Creates worktree, checks out new branch, returns worktree path.

**`create_phase_commit.py`** - Create phase commit
```bash
python3 scripts/create_phase_commit.py --phase <number> --plan-path <plan-directory> [--worktree <path>]
```
Commits changes in worktree with phase-based message.

**`cleanup_worktree.py`** - Push, PR, cleanup
```bash
python3 scripts/cleanup_worktree.py --worktree-path <path> [--create-pr] [--no-push] [--plan-path <path>]
```
Pushes branch, optionally creates PR (using iw-github-pr-creator skill), removes worktree.

**Dependencies:**
- **iw-github-pr-creator skill** - Required for `--create-pr` flag. The skill must be installed for PR creation to work.

These scripts provide deterministic git operations that survive context compaction.
