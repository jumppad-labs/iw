# Issue #11 - Task Checklist

**Last Updated**: 2025-11-04 20:30
**Status**: Not Started

## Phase 1: Create Branch-Based Git Scripts

- [x] **Task 1.1**: Enhance check_clean.py with branch detection
  - File: `.claude/skills/iw-git-workflow/scripts/check_clean.py`
  - Effort: S
  - Dependencies: None
  - Acceptance: Script returns current_branch and is_implementation_branch fields

- [x] **Task 1.2**: Create create_branch.py script
  - File: `.claude/skills/iw-git-workflow/scripts/create_branch.py` (NEW)
  - Effort: M
  - Dependencies: None
  - Acceptance: Script creates branch, imports get_branch_name.py, returns JSON output

- [x] **Task 1.3**: Create commit_plan_files.py script
  - File: `.claude/skills/iw-git-workflow/scripts/commit_plan_files.py` (NEW)
  - Effort: S
  - Dependencies: None
  - Acceptance: Script commits plan files with proper message format

- [x] **Task 1.4**: Create check_branch.py script
  - File: `.claude/skills/iw-git-workflow/scripts/check_branch.py` (NEW)
  - Effort: S
  - Dependencies: None
  - Acceptance: Script validates current branch matches expected branch from plan

- [x] **Task 1.5**: Create push_and_pr.py script
  - File: `.claude/skills/iw-git-workflow/scripts/push_and_pr.py` (NEW)
  - Effort: M
  - Dependencies: iw-github-pr-creator skill
  - Acceptance: Script pushes branch and optionally creates PR via iw-github-pr-creator

- [x] **Task 1.6**: Make all new scripts executable
  - Files: All new .py files in scripts/
  - Effort: S
  - Dependencies: Tasks 1.2-1.5
  - Acceptance: `chmod +x *.py` applied, scripts run without "permission denied"

### Phase 1 Verification
- [ ] Run: `python3 -m py_compile *.py` in scripts/ directory
- [ ] Run: `python3 create_branch.py --help` shows usage
- [ ] Run: `python3 commit_plan_files.py --help` shows usage
- [ ] Run: `python3 check_branch.py --help` shows usage
- [ ] Run: `python3 push_and_pr.py --help` shows usage
- [ ] Verify: All scripts output valid JSON

---

## Phase 2: Update Skill Documentation

- [ ] **Task 2.1**: Update iw-planner SKILL.md with branch workflow
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: M
  - Dependencies: Phase 1 complete
  - Acceptance: Documentation includes git workflow section after plan file creation

- [x] **Task 2.2**: Rewrite iw-git-workflow SKILL.md completely
  - File: `.claude/skills/iw-git-workflow/SKILL.md`
  - Effort: L
  - Dependencies: Phase 1 complete
  - Acceptance: Complete documentation for branch-based workflow, no worktree references

- [ ] **Task 2.3**: Update iw-executor SKILL.md Step 0 (git setup)
  - File: `.claude/skills/iw-executor/SKILL.md` (lines 43-93)
  - Effort: M
  - Dependencies: Phase 1 complete
  - Acceptance: "Git Branch Validation" section replaces "Git Safety and Worktree Setup"

- [ ] **Task 2.4**: Update iw-executor SKILL.md completion section
  - File: `.claude/skills/iw-executor/SKILL.md` (lines 475-524)
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: "Completion and Cleanup" section uses push_and_pr.py, no worktree removal

### Phase 2 Verification
- [ ] Run: `markdownlint .claude/skills/iw-planner/SKILL.md`
- [ ] Run: `markdownlint .claude/skills/iw-git-workflow/SKILL.md`
- [ ] Run: `markdownlint .claude/skills/iw-executor/SKILL.md`
- [ ] Verify: All script paths in documentation are correct
- [ ] Verify: No broken file references in any SKILL.md

---

## Phase 3: Remove Worktree Code

- [x] **Task 3.1**: Delete create_worktree.py
  - File: `.claude/skills/iw-git-workflow/scripts/create_worktree.py`
  - Effort: S
  - Dependencies: Phase 2 complete
  - Acceptance: File no longer exists

- [x] **Task 3.2**: Delete cleanup_worktree.py
  - File: `.claude/skills/iw-git-workflow/scripts/cleanup_worktree.py`
  - Effort: S
  - Dependencies: Phase 2 complete
  - Acceptance: File no longer exists

- [x] **Task 3.3**: Update create_phase_commit.py docstring
  - File: `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py` (line 8)
  - Effort: S
  - Dependencies: None
  - Acceptance: Docstring no longer mentions "worktree"

- [x] **Task 3.4**: Search for and remove remaining worktree references
  - Files: All skill files in iw-planner/, iw-executor/, iw-git-workflow/
  - Effort: S
  - Dependencies: Tasks 3.1-3.3
  - Acceptance: `grep -r "worktree"` returns no matches except historical docs

### Phase 3 Verification
- [ ] Run: `test ! -f .claude/skills/iw-git-workflow/scripts/create_worktree.py`
- [ ] Run: `test ! -f .claude/skills/iw-git-workflow/scripts/cleanup_worktree.py`
- [ ] Run: `grep -r "worktree" .claude/skills/iw-planner/ .claude/skills/iw-executor/ .claude/skills/iw-git-workflow/ | grep -v "\.md:"` (should return nothing)
- [ ] Verify: Skills load without errors
- [ ] Verify: No broken imports

---

## Final Verification

### Automated Checks:
- [ ] All Python scripts compile: `python3 -m py_compile .claude/skills/iw-git-workflow/scripts/*.py`
- [ ] All documentation is valid markdown
- [ ] Git operations work: `git status`, `git branch`
- [ ] No syntax errors in any new code

### Manual Integration Tests:

**Test 1: Clean Planning Workflow**
- [ ] Start on main branch with clean state
- [ ] Create plan: `/plan 11` or use iw-planner skill
- [ ] Verify: Branch created with name like `issue-11-git-worktree-implementation`
- [ ] Verify: Plan files committed with message "Add implementation plan for issue #11"
- [ ] Verify: `git log -1` shows plan commit
- [ ] Verify: `git branch --show-current` shows implementation branch

**Test 2: Dirty State Prevention**
- [ ] Create uncommitted changes on main
- [ ] Try to create plan
- [ ] Verify: Fails with error about dirty state
- [ ] Verify: Suggests user commit or stash changes
- [ ] Clean up: `git checkout .`

**Test 3: Implementation Branch Prevention**
- [ ] Checkout an implementation branch (issue-* or feature-*)
- [ ] Try to create new plan
- [ ] Verify: Fails with error about being on implementation branch
- [ ] Verify: Suggests returning to main branch
- [ ] Clean up: `git checkout main`

**Test 4: Execution Branch Validation**
- [ ] Checkout main branch
- [ ] Try to run executor on issue #11 plan
- [ ] Verify: Fails with branch mismatch error
- [ ] Verify: Suggests running `git checkout issue-11-*`
- [ ] Checkout correct branch: `git checkout issue-11-*`
- [ ] Verify: Executor starts successfully

**Test 5: Phase Commits**
- [ ] On implementation branch, make changes
- [ ] Run: `python3 .claude/skills/iw-git-workflow/scripts/create_phase_commit.py --phase 1 --plan-path .docs/issues/11`
- [ ] Verify: Commit created with format "Phase 1: ..."
- [ ] Verify: `git log -1` shows phase commit with plan reference
- [ ] Verify: Commit message includes "Issue: #11"

**Test 6: Push Branch**
- [ ] On implementation branch with commits
- [ ] Run: `python3 .claude/skills/iw-git-workflow/scripts/push_and_pr.py --plan-path .docs/issues/11`
- [ ] Verify: Branch pushed to origin
- [ ] Verify: `git branch -r` shows `origin/issue-11-*`

**Test 7: Push and Create PR**
- [ ] On implementation branch with commits
- [ ] Run: `python3 .claude/skills/iw-git-workflow/scripts/push_and_pr.py --plan-path .docs/issues/11 --create-pr`
- [ ] Verify: Branch pushed to origin
- [ ] Verify: PR created via iw-github-pr-creator
- [ ] Verify: `gh pr list` shows new PR
- [ ] Verify: PR body includes plan summary and phases

**Test 8: Permission Propagation (Main Goal)**
- [ ] On implementation branch in main repository
- [ ] Verify: Claude Code does NOT excessively request permissions
- [ ] Verify: Settings from main repo are active
- [ ] Verify: No permission dialogs for every file operation

**Test 9: Multi-Issue Workflow**
- [ ] Complete work on issue #11 branch
- [ ] Push and create PR
- [ ] Return to main: `git checkout main`
- [ ] Create new plan for different issue
- [ ] Verify: New branch created successfully
- [ ] Verify: Can work on multiple issues by switching branches

**Test 10: Cleanup**
- [ ] After PR merged on GitHub
- [ ] Return to main: `git checkout main`
- [ ] Pull updates: `git pull`
- [ ] Delete local branch: `git branch -d issue-11-*`
- [ ] Verify: Branch deleted locally
- [ ] Verify: Remote branch can be deleted via GitHub UI or `git push origin --delete issue-11-*`

### Manual Documentation Checks:
- [ ] Read iw-planner SKILL.md - workflow is clear
- [ ] Read iw-git-workflow SKILL.md - all scripts documented
- [ ] Read iw-executor SKILL.md - integration points clear
- [ ] No worktree terminology except in "what we removed" sections
- [ ] Error handling scenarios are documented
- [ ] Example commands are correct and complete

### Performance Verification:
- [ ] Branch creation is fast (< 1 second)
- [ ] No directory creation/removal overhead
- [ ] File operations work immediately (no permission delays)
- [ ] Git operations feel responsive

## Notes Section

### Implementation Notes:
(Add notes here during implementation)

### Discoveries:
(Document anything found during implementation that differs from plan)

### Issues Encountered:
(Track any problems and their solutions)

### Improvements Made:
(Note any enhancements beyond the plan)
