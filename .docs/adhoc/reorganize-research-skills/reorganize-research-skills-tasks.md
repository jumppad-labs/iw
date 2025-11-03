# Reorganize Research Skills - Task Checklist

**Last Updated**: 2025-11-03
**Status**: Planning Complete

## Phase 1: Move and Rename Skills

- [ ] **Task 1.1**: Move research-planner directory
  - Command: `git mv research-planner .claude/skills/iw-research-planner`
  - Effort: S
  - Dependencies: None
  - Acceptance: Directory exists at `.claude/skills/iw-research-planner/`

- [ ] **Task 1.2**: Update iw-research-planner SKILL.md name field
  - File: `.claude/skills/iw-research-planner/SKILL.md`
  - Change: Line 2, `name: research-planner` → `name: iw-research-planner`
  - Effort: S
  - Dependencies: Task 1.1
  - Acceptance: YAML frontmatter shows `name: iw-research-planner`

- [ ] **Task 1.3**: Move research-executor directory
  - Command: `git mv research-executor .claude/skills/iw-research-executor`
  - Effort: S
  - Dependencies: None
  - Acceptance: Directory exists at `.claude/skills/iw-research-executor/`

- [ ] **Task 1.4**: Update iw-research-executor SKILL.md name field
  - File: `.claude/skills/iw-research-executor/SKILL.md`
  - Change: Line 2, `name: research-executor` → `name: iw-research-executor`
  - Effort: S
  - Dependencies: Task 1.3
  - Acceptance: YAML frontmatter shows `name: iw-research-executor`

- [ ] **Task 1.5**: Move research-synthesizer directory
  - Command: `git mv research-synthesizer .claude/skills/iw-research-synthesizer`
  - Effort: S
  - Dependencies: None
  - Acceptance: Directory exists at `.claude/skills/iw-research-synthesizer/`

- [ ] **Task 1.6**: Update iw-research-synthesizer SKILL.md
  - File: `.claude/skills/iw-research-synthesizer/SKILL.md`
  - Change: Line 2, `name: research-synthesizer` → `name: iw-research-synthesizer`
  - Change: Line 4, `research-executor` → `iw-research-executor` in description
  - Effort: S
  - Dependencies: Task 1.5
  - Acceptance: YAML frontmatter shows `name: iw-research-synthesizer`, description references `iw-research-executor`

### Phase 1 Verification
- [ ] Run: `ls -la .claude/skills/iw-research-*` (should show 3 directories)
- [ ] Run: `ls research-planner 2>&1 | grep "No such file"` (should confirm deleted)
- [ ] Run: `head -5 .claude/skills/iw-research-*/SKILL.md | grep "name: iw-research-"` (should find 3 matches)
- [ ] Run: `git log --follow --oneline .claude/skills/iw-research-planner/SKILL.md` (should show history)

---

## Phase 2: Update Commands and Documentation

- [ ] **Task 2.1**: Rename research-plan command
  - Command: `git mv .claude/commands/research-plan.md .claude/commands/iw-research-plan.md`
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: File exists at `.claude/commands/iw-research-plan.md`

- [ ] **Task 2.2**: Update iw-research-plan.md content
  - File: `.claude/commands/iw-research-plan.md`
  - Change: Line 5, `research-planner` → `iw-research-planner`
  - Change: Line 7, `/research-execute` → `/iw-research-execute`
  - Effort: S
  - Dependencies: Task 2.1
  - Acceptance: Content references `iw-research-planner` and `/iw-research-execute`

- [ ] **Task 2.3**: Rename research-execute command
  - Command: `git mv .claude/commands/research-execute.md .claude/commands/iw-research-execute.md`
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: File exists at `.claude/commands/iw-research-execute.md`

- [ ] **Task 2.4**: Update iw-research-execute.md content
  - File: `.claude/commands/iw-research-execute.md`
  - Change: Line 5, `research-executor` → `iw-research-executor`
  - Change: Line 7, `/research-synthesize` → `/iw-research-synthesize`
  - Effort: S
  - Dependencies: Task 2.3
  - Acceptance: Content references `iw-research-executor` and `/iw-research-synthesize`

- [ ] **Task 2.5**: Rename research-synthesize command
  - Command: `git mv .claude/commands/research-synthesize.md .claude/commands/iw-research-synthesize.md`
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: File exists at `.claude/commands/iw-research-synthesize.md`

- [ ] **Task 2.6**: Update iw-research-synthesize.md content
  - File: `.claude/commands/iw-research-synthesize.md`
  - Change: Line 5, `research-synthesizer` → `iw-research-synthesizer`
  - Effort: S
  - Dependencies: Task 2.5
  - Acceptance: Content references `iw-research-synthesizer`

- [ ] **Task 2.7**: Update README.md skills section
  - File: `README.md`
  - Change: Lines 16-35, merge "Research Skills" into "Implementation Workflow Skills" with iw- prefix
  - Effort: M
  - Dependencies: None
  - Acceptance: Single unified skills list with all 13 skills using iw- prefix

- [ ] **Task 2.8**: Update README.md commands section
  - File: `README.md`
  - Change: Lines 37-48, merge command lists and update to `/iw-research-*`
  - Effort: S
  - Dependencies: None
  - Acceptance: Unified commands list with `/iw-research-*` names

- [ ] **Task 2.9**: Update README.md research workflow section
  - File: `README.md`
  - Change: Lines 150-203, replace `/research-*` with `/iw-research-*`
  - Effort: M
  - Dependencies: None
  - Acceptance: All command references use `/iw-research-*` pattern

- [ ] **Task 2.10**: Update iw-install/SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md`
  - Change: Lines 88-100, add research skills to list (13 total)
  - Effort: M
  - Dependencies: None
  - Acceptance: Skills list shows "13 total" and includes all three research skills

### Phase 2 Verification
- [ ] Run: `ls .claude/commands/iw-research-*.md | wc -l` (should be 3)
- [ ] Run: `ls .claude/commands/research-*.md 2>&1 | grep "No such file"` (should confirm deleted)
- [ ] Run: `grep -c "iw-research-" README.md` (should find multiple occurrences)
- [ ] Run: `grep "### Research Commands" README.md` (should return nothing - section removed)
- [ ] Run: `grep "Skills (13 total)" README.md .claude/skills/iw-install/SKILL.md` (should find in both files)

---

## Phase 3: Verification and Cleanup

- [ ] **Task 3.1**: Test iw-research-planner skill invocation
  - Test: Invoke `/iw-research-plan` in Claude Code
  - Effort: S
  - Dependencies: Phases 1-2 complete
  - Acceptance: Skill loads without errors, shows correct name

- [ ] **Task 3.2**: Test iw-research-executor skill invocation
  - Test: Invoke `/iw-research-execute` in Claude Code
  - Effort: S
  - Dependencies: Phases 1-2 complete
  - Acceptance: Skill loads without errors, shows correct name

- [ ] **Task 3.3**: Test iw-research-synthesizer skill invocation
  - Test: Invoke `/iw-research-synthesize` in Claude Code
  - Effort: S
  - Dependencies: Phases 1-2 complete
  - Acceptance: Skill loads without errors, shows correct name

- [ ] **Task 3.4**: Test init_research.py script
  - Command: `python3 .claude/skills/iw-research-planner/scripts/init_research.py test-verify`
  - Effort: S
  - Dependencies: Task 1.1-1.2
  - Acceptance: Script executes without errors, creates directory structure

- [ ] **Task 3.5**: Test add_source.py script
  - Command: `python3 .claude/skills/iw-research-planner/scripts/add_source.py test-verify "https://example.com" "paper"`
  - Effort: S
  - Dependencies: Task 1.1-1.2, Task 3.4
  - Acceptance: Script executes without errors, adds source to sources.md

- [ ] **Task 3.6**: Test add_finding.py script
  - Command: `python3 .claude/skills/iw-research-executor/scripts/add_finding.py test-verify "Theme" "Finding" "Source"`
  - Effort: S
  - Dependencies: Task 1.3-1.4, Task 3.4
  - Acceptance: Script executes without errors, adds finding to findings.md

- [ ] **Task 3.7**: Test generate_report.py script
  - Command: `python3 .claude/skills/iw-research-synthesizer/scripts/generate_report.py test-verify`
  - Effort: S
  - Dependencies: Task 1.5-1.6, Task 3.4-3.6
  - Acceptance: Script executes without errors, generates report

- [ ] **Task 3.8**: Clean up test directory
  - Command: `rm -rf .docs/research/test-verify`
  - Effort: S
  - Dependencies: Tasks 3.4-3.7
  - Acceptance: Test directory removed

- [ ] **Task 3.9**: Search for remaining old references
  - Command: `grep -r "research-planner\|research-executor\|research-synthesizer" --exclude-dir=.git --exclude-dir=.docs --include="*.md" --include="*.py" .`
  - Effort: S
  - Dependencies: Phases 1-2 complete
  - Acceptance: No matches outside `.docs/adhoc/research-skills/`

- [ ] **Task 3.10**: Verify git history preservation
  - Command: `git log --follow --oneline .claude/skills/iw-research-*/SKILL.md`
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: History shows commits from before the move for all three skills

- [ ] **Task 3.11**: Verify .docs/adhoc/research-skills/ preserved
  - Command: `ls .docs/adhoc/research-skills/`
  - Effort: S
  - Dependencies: None
  - Acceptance: Historical plan files exist and are unchanged

### Phase 3 Verification
- [ ] All three skills invoke without errors
- [ ] All four Python scripts execute successfully
- [ ] No references to old skill names outside `.docs/adhoc/research-skills/`
- [ ] Git history preserved for all moved files
- [ ] Complete workflow works: `/iw-research-plan` → `/iw-research-execute` → `/iw-research-synthesize`
- [ ] Documentation reads naturally with unified naming
- [ ] Historical plan preserved

---

## Final Verification

### Automated Checks:
- [ ] `ls .claude/skills/iw-research-* | wc -l` returns 3
- [ ] `ls research-* 2>&1 | grep "No such file"` confirms old directories gone
- [ ] `ls .claude/commands/iw-research-*.md | wc -l` returns 3
- [ ] `ls .claude/commands/research-*.md 2>&1 | grep "No such file"` confirms old commands gone
- [ ] `grep "Skills (13 total)" README.md` finds match
- [ ] `grep "Skills (13 total)" .claude/skills/iw-install/SKILL.md` finds match
- [ ] All scripts execute: `python3 .claude/skills/iw-research-*/scripts/*.py --help`

### Manual Checks:
- [ ] Skills load correctly when invoked via commands
- [ ] README.md has unified skills section (no separate "Research Skills")
- [ ] All command references in README use `/iw-research-*`
- [ ] iw-install skill lists all 13 skills
- [ ] Documentation is clear and consistent
- [ ] No broken links or references
- [ ] Historical plan files in `.docs/adhoc/research-skills/` are intact

## Task Estimates Summary

**Phase 1 (Move and Rename Skills):** 6 tasks, ~30 minutes
**Phase 2 (Update Commands and Documentation):** 10 tasks, ~1 hour
**Phase 3 (Verification and Cleanup):** 11 tasks, ~30 minutes

**Total:** 27 tasks, ~2 hours estimated effort

## Notes Section

### Implementation Notes:
[Add notes during implementation]

### Blockers/Issues:
[Track any blockers discovered]

### Deferred Items:
None - this is a complete reorganization with no deferred items.
