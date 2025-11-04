# Issue #11 - Context & Dependencies

**Last Updated**: 2025-11-04 20:30

## Quick Summary

Replace git worktree workflow with simpler branch-based workflow to fix permission propagation issues in Claude Code. The planner will create branches and commit plan files, while the executor will implement on the branch without worktree isolation.

## Key Files & Locations

### Files to Modify:

**iw-planner skill:**
- `.claude/skills/iw-planner/SKILL.md:368-390` - Add git workflow section for branch creation
- Need to add branch creation logic after plan files are generated

**iw-git-workflow skill:**
- `.claude/skills/iw-git-workflow/SKILL.md` - Complete rewrite for branch-based workflow
- `.claude/skills/iw-git-workflow/scripts/create_worktree.py` - Delete (replaced by create_branch.py)
- `.claude/skills/iw-git-workflow/scripts/cleanup_worktree.py` - Replace with push_and_pr.py
- `.claude/skills/iw-git-workflow/scripts/check_clean.py` - Keep and enhance with branch detection
- `.claude/skills/iw-git-workflow/scripts/get_branch_name.py` - Keep as-is (reusable)
- `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py` - Keep with minor updates

**iw-executor skill:**
- `.claude/skills/iw-executor/SKILL.md:43-93` - Replace worktree setup with branch validation
- `.claude/skills/iw-executor/SKILL.md:475-524` - Update cleanup workflow (no worktree removal)

### New Files to Create:

- `.claude/skills/iw-git-workflow/scripts/create_branch.py` - Create and switch to new branch
- `.claude/skills/iw-git-workflow/scripts/commit_plan_files.py` - Commit plan files to branch
- `.claude/skills/iw-git-workflow/scripts/push_and_pr.py` - Push branch and optionally create PR
- `.claude/skills/iw-git-workflow/scripts/check_branch.py` - Validate current branch state

### Files to Reference:

- `.claude/skills/iw-git-workflow/scripts/get_branch_name.py:71-96` - Branch naming logic (reuse)
- `.claude/skills/iw-git-workflow/scripts/check_clean.py:35-73` - Git state checking (enhance)
- `.claude/skills/iw-git-workflow/scripts/cleanup_worktree.py:100-142` - PR creation pattern (adapt)
- `.claude/skills/iw-github-pr-creator/scripts/create_pr.py` - PR creation (keep using)

### Test Files:

None required - scripts can be tested manually with git commands

## Dependencies

### Code Dependencies:

- Python 3.6+ (existing requirement)
- `pathlib` - Path manipulation
- `subprocess` - Git command execution
- `json` - Script output formatting
- `argparse` - CLI argument parsing

### External Dependencies:

- Git 2.x - Core git functionality
- GitHub CLI (`gh`) - For PR creation (existing)
- GitHub repository with push access

## Key Technical Decisions

1. **Planner Creates Branch**: Branch is created during planning, plan files committed immediately
2. **Block Multi-Issue**: Prevent planning new issue if already on implementation branch
3. **Auto-Commit Plans**: Plan files automatically committed to branch
4. **Offer PR Creation**: Executor asks user if they want PR created after completion
5. **Replace Worktrees Entirely**: No hybrid approach, clean removal of worktree logic

## Integration Points

**iw-planner → iw-git-workflow:**
- After plan files created, invoke `create_branch.py` with plan path
- Then invoke `commit_plan_files.py` to commit to new branch
- Planner reports branch name to user

**iw-executor → iw-git-workflow:**
- Before execution, invoke `check_branch.py` to validate current branch
- After each phase, invoke `create_phase_commit.py` (existing, works as-is)
- After completion, invoke `push_and_pr.py` to push and optionally create PR

**iw-git-workflow → iw-github-pr-creator:**
- `push_and_pr.py` invokes `create_pr.py` if user requests PR
- Passes branch name, plan path, and base branch
- Returns PR URL to user

## Environment Requirements

- Git version: 2.x or higher
- Python: 3.6+
- GitHub CLI: Installed and authenticated (for PR creation)
- Git repository: Clean state before planning
- Remote: origin configured and accessible

## Related Documentation

- Original ticket: GitHub Issue #11
- Research notes: `.docs/issues/11/11-research.md`
- Implementation plan: `.docs/issues/11/11-plan.md`
- Task checklist: `.docs/issues/11/11-tasks.md`
- Learning from issue #10: Prefer git clone over API requests (simpler is better)
