# Issue #1 - Task Checklist

**Last Updated**: 2025-11-03
**Status**: Not Started

## Phase 1: Strengthen Task and Context Update Automation in SKILL.md

- [x] **Task 1.1**: Strengthen automation directives in Step 3 (Execute Tasks by Phase)
  - File: `.claude/skills/iw-executor/SKILL.md:162-208`
  - Effort: M
  - Dependencies: None
  - Acceptance: Section 2.d and 2.e updated with checkpoint markers, numbered steps, explicit bash commands, and verification steps

- [x] **Task 1.2**: Add automation verification to phase completion section
  - File: `.claude/skills/iw-executor/SKILL.md:209-236`
  - Effort: S
  - Dependencies: None
  - Acceptance: New step (a) added to verify task updates, step (c) updated to show task tracking status

### Phase 1 Verification
- [ ] Run: `grep -n "CRITICAL AUTOMATION CHECKPOINT" .claude/skills/iw-executor/SKILL.md`
- [ ] Run: `grep -n "REQUIRED - AUTOMATIC" .claude/skills/iw-executor/SKILL.md`
- [ ] Verify: Manual review confirms automation directives are clear and prominent

---

## Phase 2: Strengthen Phase Commit Automation in SKILL.md

- [x] **Task 2.1**: Strengthen phase commit automation directive
  - File: `.claude/skills/iw-executor/SKILL.md:238-264`
  - Effort: M
  - Dependencies: Phase 1 complete
  - Acceptance: Section updated with checkpoint marker, numbered steps, verification, and detailed script behavior explanation

- [x] **Task 2.2**: Add pre-phase automation reminder
  - File: `.claude/skills/iw-executor/SKILL.md:163-175`
  - Effort: S
  - Dependencies: None
  - Acceptance: Phase start announcement includes automation reminder box

### Phase 2 Verification
- [ ] Run: `grep -n "PHASE COMMIT" .claude/skills/iw-executor/SKILL.md`
- [ ] Run: `grep -n "Automation Reminder" .claude/skills/iw-executor/SKILL.md`
- [ ] Verify: Manual review confirms phase commit requirements are explicit

---

## Phase 3: Add Automation Summary to Important Guidelines Section

- [x] **Task 3.1**: Add automation requirements summary section
  - File: `.claude/skills/iw-executor/SKILL.md:489-497` (after "Be Thorough" subsection)
  - Effort: M
  - Dependencies: Phases 1 and 2 complete
  - Acceptance: New "Automation Requirements Summary" section added with all three automation types documented, bash examples, and explanations

### Phase 3 Verification
- [ ] Run: `grep -n "Automation Requirements Summary" .claude/skills/iw-executor/SKILL.md`
- [ ] Run: `grep -A 50 "Automation Requirements Summary" .claude/skills/iw-executor/SKILL.md | grep -E "(update_task|update_context|create_phase_commit)"`
- [ ] Verify: Manual review confirms summary is comprehensive and well-placed

---

## Final Verification

### Automated Checks:
- [ ] All grep commands from phase verifications pass
- [ ] Git diff shows changes in expected line ranges
- [ ] No syntax errors in markdown (preview SKILL.md in editor)

### Manual Checks:
- [ ] Read entire modified SKILL.md to ensure flow is natural
- [ ] Verify bash command examples are complete and correct
- [ ] Verify all three automation touchpoints are covered
- [ ] Verify automation summary section has all required content

## Notes Section

[Space for adding notes during implementation]
