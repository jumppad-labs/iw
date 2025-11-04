# Issue #11 - Research & Working Notes

**Research Date**: 2025-11-04
**Researchers**: Claude + nicj

## Initial Understanding

Issue #11 describes a problem where Claude creates git worktrees to enable multiple issues to be worked on simultaneously, but this causes excessive permission requests because Claude Code settings don't propagate to worktrees.

The proposed solution is to replace worktree functionality with a simpler git branch approach.

## Research Process

### Files Examined:

**1. iw-git-workflow skill** (`.claude/skills/iw-git-workflow/`)
- `SKILL.md` - Main documentation
- `scripts/check_clean.py` - Verifies git state before worktree creation
- `scripts/create_worktree.py` - Creates isolated worktree in parent directory
- `scripts/get_branch_name.py` - Generates branch names (issue-N-title or feature-name)
- `scripts/create_phase_commit.py` - Creates commits after each phase
- `scripts/cleanup_worktree.py` - Pushes branch, creates PR, removes worktree

**2. iw-planner skill** (`.claude/skills/iw-planner/`)
- `SKILL.md:364-390` - Plan initialization and iw-init invocation
- Currently creates plans but does NOT perform git operations
- Git setup is deferred to executor

**3. iw-executor skill** (`.claude/skills/iw-executor/`)
- `SKILL.md:43-93` - Git safety and worktree setup procedure
- `SKILL.md:206-232` - Integration with iw-git-workflow
- `SKILL.md:289-341` - Phase commit automation
- `SKILL.md:475-524` - Completion and cleanup workflow
- `scripts/update_task.py` - Updates tasks.md with completion status
- `scripts/update_context.py` - Adds discoveries to context.md
- `scripts/parse_plan.py` - Extracts phase structure from plan files

**4. iw-github-pr-creator skill** (`.claude/skills/iw-github-pr-creator/`)
- `scripts/create_pr.py` - Creates PRs via gh CLI
- `scripts/extract_plan_summary.py` - Extracts plan metadata for PR body
- Integrated via cleanup_worktree.py when user requests PR creation

### Sub-tasks Spawned:

1. **iw-github-issue-reader**: Load GitHub issue 11 details
   - Result: Issue #11 by nicholasjackson
   - Label: bug
   - Clear description of worktree problem and proposed solution

2. **iw-learnings**: Search past learnings
   - Result: Found learning about git clone vs API requests (issue #10)
   - Pattern: Prefer simpler git operations over complex solutions

3. **Explore - Find git worktree implementation**
   - Result: Comprehensive mapping of worktree functionality
   - Key discovery: Worktree logic is centralized in iw-git-workflow skill
   - All scripts are well-isolated and modular

4. **Explore - Find git branch patterns**
   - Result: Existing branch management patterns documented
   - Key discovery: `get_branch_name.py` already generates appropriate branch names
   - Can reuse this logic for simple branch approach

5. **Explore - Find PR creation workflow**
   - Result: PR creation is handled by iw-github-pr-creator skill
   - Key discovery: Can still use this skill without worktrees
   - Integration point: cleanup_worktree.py calls create_pr.py

6. **general-purpose - Analyze planner-executor flow**
   - Result: Detailed data flow analysis
   - Key discovery: Plans stored in `.docs/issues/<N>/` are accessible from any branch
   - Worktree isolation unnecessary for plan access

### Questions Asked & Answers:

1. **Q**: Should the planner create the branch immediately, or should the executor create it when implementation starts?
   **A**: Planner creates branch
   **Impact**: Plan files committed to branch immediately, user can review before implementing

2. **Q**: What should happen if the user starts implementing a second issue while already on an implementation branch?
   **A**: Block and warn
   **Impact**: Prevents nested branches and confusion, enforces clean workflow

3. **Q**: Should plan files be committed automatically to the branch?
   **A**: Auto-commit plan files
   **Impact**: Clean history, plan always tracked in git

4. **Q**: After the executor completes implementation and pushes the branch, should it offer to create a PR?
   **A**: Offer to create PR
   **Impact**: Maintains convenient workflow using existing iw-github-pr-creator skill

## Key Discoveries

### Technical Discoveries:

1. **Worktree Creation Location**: `.claude/skills/iw-git-workflow/scripts/create_worktree.py:77-79`
   - Creates worktrees in parent directory: `../repo-name-branch-name`
   - This isolation was designed to avoid permission issues, but it creates them instead

2. **Branch Naming Logic**: `.claude/skills/iw-git-workflow/scripts/get_branch_name.py:71-96`
   - Already generates appropriate branch names
   - Can be reused without modification for simple branch approach

3. **Dirty State Checking**: `.claude/skills/iw-git-workflow/scripts/check_clean.py:35-73`
   - Comprehensive checks for modified, staged, and untracked files
   - Can be reused to validate git state before creating branch

4. **Phase Commits**: `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py`
   - Works in any git directory (not worktree-specific)
   - Can be used as-is with simple branch approach

5. **PR Creation**: Integration via `cleanup_worktree.py:100-142`
   - Calls `iw-github-pr-creator` skill
   - Not worktree-dependent, can be refactored for branch workflow

### Patterns to Follow:

1. **Script Organization**: Each git operation is a separate Python script
   - Makes testing and modification easier
   - Follow same pattern for new branch-based scripts

2. **JSON Output**: All scripts return JSON with success/error info
   - Example: `create_worktree.py:144-151`
   - Maintain this pattern for consistency

3. **Git Command Wrapper**: `run_git_command()` helper function
   - Centralized error handling
   - Consistent across all scripts

4. **Plan Path Detection**: Multiple strategies to find plan directory
   - From path structure (`.docs/issues/<N>/`)
   - From filename patterns (`<N>-plan.md`)
   - Reuse this logic

### Constraints Identified:

1. **Must maintain backward compatibility**: Existing plan files must still work
2. **Settings must propagate**: Working in main repo ensures Claude Code settings apply
3. **User expects PR creation**: Keep existing PR workflow
4. **Phase commits are important**: Maintain granular commit history
5. **No worktree removal needed**: Simpler cleanup process

## Design Decisions

### Decision 1: When to Create Branch

**Options considered:**
- **Option A**: Planner creates branch immediately when plan is created
  - Pros: Plan committed to branch, clear separation, can review before implementing
  - Cons: Branch exists even if never implemented
- **Option B**: Executor creates branch when implementation starts
  - Pros: Branch only created when work begins
  - Cons: Plans would be on main branch initially, potential confusion

**Chosen**: Option A (Planner creates branch)
**Rationale**: User selected this approach. Benefits outweigh the minor downside of unused branches.

### Decision 2: Multi-Issue Workflow

**Options considered:**
- **Option A**: Block and warn if already on implementation branch
  - Pros: Prevents confusion, enforces clean workflow
  - Cons: Requires manual `git checkout main` if user forgets
- **Option B**: Auto-switch to main branch first
  - Pros: More convenient
  - Cons: Potentially surprising, could lose unsaved work
- **Option C**: Allow nested branches
  - Pros: Flexible
  - Cons: Complex, defeats purpose of simplification

**Chosen**: Option A (Block and warn)
**Rationale**: User selected this approach. Explicit is better than implicit, prevents accidents.

### Decision 3: Plan File Commits

**Options considered:**
- **Option A**: Auto-commit plan files when created
  - Pros: Clean history, no manual steps
  - Cons: Less control
- **Option B**: Leave uncommitted
  - Pros: User decides
  - Cons: Plans might not be tracked
- **Option C**: Ask user each time
  - Pros: Balanced control
  - Cons: Extra interaction

**Chosen**: Option A (Auto-commit)
**Rationale**: User selected this approach. Consistency and automation preferred.

### Decision 4: PR Creation

**Options considered:**
- **Option A**: Offer to create PR automatically (use existing skill)
  - Pros: Convenient, maintains current workflow
  - Cons: Requires iw-github-pr-creator integration
- **Option B**: User creates PR manually
  - Pros: Simpler executor, more user control
  - Cons: Less convenient

**Chosen**: Option A (Offer to create PR)
**Rationale**: User selected this approach. Maintains convenience of current workflow.

### Decision 5: Script Organization

**Options considered:**
- **Option A**: Create new branch-based scripts, deprecate worktree scripts
  - Pros: Clean separation, no risk of breaking worktrees during transition
  - Cons: Code duplication during transition
- **Option B**: Modify existing scripts to support both modes
  - Pros: Less code
  - Cons: Complex conditional logic, harder to test
- **Option C**: Replace worktree scripts entirely
  - Pros: Simplest long-term
  - Cons: Breaks anyone using old workflow

**Chosen**: Option C (Replace entirely)
**Rationale**: Issue states worktree functionality should be removed. Clean break preferred.

## Open Questions (During Research)

- [x] **Do we keep worktree scripts as fallback?** - Resolved: No, remove entirely per issue description
- [x] **Can we reuse get_branch_name.py?** - Resolved: Yes, it's not worktree-specific
- [x] **Can we reuse create_phase_commit.py?** - Resolved: Yes, works with any git directory
- [x] **How to handle cleanup without worktree removal?** - Resolved: Just push branch, optionally create PR
- [x] **What if user is on main branch already?** - Resolved: Check current branch, prevent creating branch from main if dirty

## Code Snippets Reference

### Relevant Existing Code:

**Current Worktree Creation:**
```python
# From .claude/skills/iw-git-workflow/scripts/create_worktree.py:87
returncode, stdout, stderr = run_git_command(
    ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
    repo_root
)
```

**Branch Name Generation:**
```python
# From .claude/skills/iw-git-workflow/scripts/get_branch_name.py:71-96
def generate_branch_name(plan_path: Path) -> str:
    issue_number = extract_issue_number(plan_path)

    if issue_number:
        title = extract_plan_title(plan_path)
        if title:
            title_slug = slugify(title)
            if len(title_slug) > 40:
                title_slug = title_slug[:40].rstrip('-')
            return f"issue-{issue_number}-{title_slug}"
        else:
            return f"issue-{issue_number}"
    else:
        plan_name = plan_path.name
        plan_slug = slugify(plan_name)
        return f"feature-{plan_slug}"
```

**Dirty State Check:**
```python
# From .claude/skills/iw-git-workflow/scripts/check_clean.py:35-73
def check_git_status(directory: Path) -> dict:
    # Check for modified files
    returncode, stdout, _ = run_git_command(
        ["git", "diff", "--name-only"],
        directory
    )
    modified = [f.strip() for f in stdout.split("\n") if f.strip()]

    # Check for staged files
    returncode, stdout, _ = run_git_command(
        ["git", "diff", "--cached", "--name-only"],
        directory
    )
    staged = [f.strip() for f in stdout.split("\n") if f.strip()]

    # Check for untracked files
    returncode, stdout, _ = run_git_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        directory
    )
    untracked = [f.strip() for f in stdout.split("\n") if f.strip()]

    is_clean = len(modified) == 0 and len(staged) == 0 and len(untracked) == 0

    return {
        "clean": is_clean,
        "modified": modified,
        "staged": staged,
        "untracked": untracked
    }
```

### Similar Patterns Found:

**Push Branch Pattern:**
```python
# From .claude/skills/iw-git-workflow/scripts/cleanup_worktree.py:66-82
def push_branch(worktree_path: Path, branch_name: str) -> tuple[bool, str]:
    # Push with upstream tracking
    returncode, stdout, stderr = run_git_command(
        ["git", "push", "-u", "origin", branch_name],
        worktree_path
    )

    if returncode != 0:
        return False, f"Failed to push branch: {stderr}"

    return True, ""
```

**PR Creation Integration:**
```python
# From .claude/skills/iw-git-workflow/scripts/cleanup_worktree.py:100-142
def create_pr_with_github_pr_creator(
    worktree_path: Path,
    branch_name: str,
    plan_path: Path | None,
    base_branch: str = "main"
) -> tuple[bool, str, str]:
    script_path = Path(__file__).parent.parent.parent / "iw-github-pr-creator" / "scripts" / "create_pr.py"

    cmd = [
        "python3",
        str(script_path),
        "--branch", branch_name,
        "--base", base_branch,
        "--directory", str(worktree_path)
    ]

    if plan_path:
        cmd.extend(["--plan-path", str(plan_path)])

    returncode, stdout, stderr = run_command(cmd, worktree_path)

    if returncode != 0:
        return False, "", f"Failed to create PR: {stderr}"

    try:
        result = json.loads(stdout)
        pr_url = result.get("url", "")
        return True, pr_url, ""
    except json.JSONDecodeError:
        return False, "", "Failed to parse PR creation result"
```
