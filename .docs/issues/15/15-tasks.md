# Issue #15 - Task Checklist

**Last Updated**: 2025-11-04
**Status**: Not Started

## Phase 1: Add Fast Plan Mode Infrastructure

- [ ] **Task 1.1**: Update command entry point with flag documentation
  - File: `.claude/commands/iw-plan.md`
  - Effort: S
  - Dependencies: None
  - Acceptance: Command description mentions --fast and --detailed flags, explains when to use each

- [ ] **Task 1.2**: Create fast plan template file
  - File: `.claude/skills/iw-planner/assets/fast-plan-template.md`
  - Effort: S
  - Dependencies: None
  - Acceptance: Template file exists with {{PLACEHOLDER}} syntax, under 50 lines, includes all sections (Summary, Context, Steps, Testing, Criteria, Notes, Upgrade prompt)

- [ ] **Task 1.3**: Add --mode flag to init_plan.py script
  - File: `.claude/skills/iw-planner/scripts/init_plan.py`
  - Effort: M
  - Dependencies: Task 1.2 (template must exist)
  - Acceptance: Script accepts --mode fast/detailed, creates appropriate file structure, displays correct output message with upgrade instructions

- [ ] **Task 1.4**: Implement create_fast_plan_file() function
  - File: `.claude/skills/iw-planner/scripts/init_plan.py`
  - Effort: M
  - Dependencies: Task 1.2 (template must exist)
  - Acceptance: Function reads template, replaces all placeholders, writes single fast-plan file to correct location

### Phase 1 Verification
- [ ] Run: `python3 .claude/skills/iw-planner/scripts/init_plan.py 99 --type issue --mode fast`
- [ ] Verify: Fast plan file created at `.docs/issues/99/99-fast-plan.md`
- [ ] Verify: Template placeholders replaced correctly
- [ ] Verify: Upgrade message displayed in output
- [ ] Run: `grep -q "fast" .claude/commands/iw-plan.md`
- [ ] Verify: Command description mentions fast mode

---

## Phase 2: Implement Fast Planning Workflow

- [ ] **Task 2.1**: Add mode detection (Step 0) to skill workflow
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: S
  - Dependencies: Phase 1 complete
  - Acceptance: Step 0 added before existing workflow, parses flags, branches to appropriate workflow

- [ ] **Task 2.2**: Document Fast Planning Workflow section
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 2.1
  - Acceptance: Complete fast workflow documented with 5 steps: Task tracking, minimal research (4 agents), outline presentation, generation, presentation with upgrade option

- [ ] **Task 2.3**: Document minimal research agent specifications
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: S
  - Dependencies: Task 2.2
  - Acceptance: All 4 agents specified: GitHub issue reader, learnings search, guidelines check, quick file scan with exact prompts

- [ ] **Task 2.4**: Add Fast Plan Generation section with example
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 2.2
  - Acceptance: Section added with guidelines for customizing fast plan, includes concrete example (button color change) demonstrating ~75 lines output

- [ ] **Task 2.5**: Test fast workflow execution manually
  - File: N/A (manual testing)
  - Effort: L
  - Dependencies: All of Phase 2
  - Acceptance: `/iw-plan test --fast` executes fast workflow, launches only 4 agents, generates single file under 100 lines, completes in <2 minutes

### Phase 2 Verification
- [ ] Run: `/iw-plan 999 --fast` (test issue)
- [ ] Verify: Only 4 research agents launch (check logs)
- [ ] Verify: Single fast-plan file generated
- [ ] Verify: File is under 100 lines for simple task
- [ ] Verify: Upgrade prompt included at bottom
- [ ] Verify: Completion time under 2 minutes
- [ ] Verify: Guidelines referenced in output

---

## Phase 3: Implement Upgrade Path (Detailed Mode Enhancement)

- [ ] **Task 3.1**: Add fast plan detection to detailed workflow
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: M
  - Dependencies: Phase 2 complete
  - Acceptance: Step 0 added to detailed workflow, checks for fast plan file, reads if exists, extracts user content

- [ ] **Task 3.2**: Document fast plan detection logic with bash examples
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: S
  - Dependencies: Task 3.1
  - Acceptance: Detection commands documented for issue-based and ad-hoc plans, Read tool usage specified

- [ ] **Task 3.3**: Document user content extraction strategy
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 3.1
  - Acceptance: Section added with template vs user content indicators, parsing strategy with pseudocode, preservation strategy documented

- [ ] **Task 3.4**: Add extraction example with realistic scenario
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: S
  - Dependencies: Task 3.3
  - Acceptance: Example shows user concern in fast plan Notes, extraction logic, and preservation in detailed research.md with resolution plan

- [ ] **Task 3.5**: Document fast plan findings incorporation
  - File: `.claude/skills/iw-planner/SKILL.md`
  - Effort: S
  - Dependencies: Task 3.3
  - Acceptance: Guidelines for using fast plan as context for detailed research, avoiding duplicate research

- [ ] **Task 3.6**: Test upgrade path end-to-end
  - File: N/A (manual testing)
  - Effort: L
  - Dependencies: All of Phase 3
  - Acceptance: Create fast plan, add user comments, run detailed mode, verify comments preserved in research.md, verify no duplicate research

### Phase 3 Verification
- [ ] Run: `/iw-plan 999 --fast` then edit fast plan with user comments
- [ ] Run: `/iw-plan 999 --detailed`
- [ ] Verify: Detailed mode detected existing fast plan
- [ ] Verify: Read tool invoked for fast plan (check logs)
- [ ] Verify: User comments extracted and preserved
- [ ] Verify: Comments appear in research.md "Fast Plan Review" section
- [ ] Verify: Questions from fast plan addressed in detailed plan
- [ ] Verify: No duplicate research between fast/detailed phases

---

## Phase 4: Testing, Documentation, and Refinement

- [ ] **Task 4.1**: Update Quick Start documentation
  - File: `.claude/skills/iw-planner/SKILL.md:26-44`
  - Effort: M
  - Dependencies: Phases 1-3 complete
  - Acceptance: Quick Start section rewritten with Fast Planning, Detailed Planning, and Upgrade Path subsections including examples

- [ ] **Task 4.2**: Add Edge Cases and Error Handling section
  - File: `.claude/skills/iw-planner/SKILL.md` (new section before Resources)
  - Effort: M
  - Dependencies: Phases 1-3 complete
  - Acceptance: Section added covering 6 edge cases: fast plan exists, detailed plan exists, no issue number, conflicting flags, no user edits, corrupted file

- [ ] **Task 4.3**: Create testing scenarios document
  - File: `.docs/issues/15/testing-scenarios.md`
  - Effort: M
  - Dependencies: Phases 1-3 complete
  - Acceptance: Document created with 7 test scenarios: fast plan simple task, upgrade path, detailed from scratch, token measurement, both flags, plan exists, guidelines check

- [ ] **Task 4.4**: Execute Test Scenario 1 (Fast Plan for Simple Task)
  - File: N/A (manual testing)
  - Effort: M
  - Dependencies: Task 4.3
  - Acceptance: Test completes successfully, output matches expectations, document results

- [ ] **Task 4.5**: Execute Test Scenario 2 (Fast Plan Upgrade Path)
  - File: N/A (manual testing)
  - Effort: M
  - Dependencies: Task 4.3
  - Acceptance: Test completes successfully, user edits preserved, document results

- [ ] **Task 4.6**: Execute Test Scenario 3 (Detailed Plan from Scratch)
  - File: N/A (manual testing)
  - Effort: M
  - Dependencies: Task 4.3
  - Acceptance: Test completes successfully, full research workflow executes, document results

- [ ] **Task 4.7**: Execute Test Scenario 4 (Token Consumption Measurement)
  - File: N/A (manual testing)
  - Effort: L
  - Dependencies: Tasks 4.4, 4.6
  - Acceptance: Measurements recorded for fast vs detailed, ≥60% time savings, ≤30% token usage, document results

- [ ] **Task 4.8**: Execute Test Scenario 5 (Edge Case - Both Flags)
  - File: N/A (manual testing)
  - Effort: S
  - Dependencies: Task 4.3
  - Acceptance: Conflict detected, detailed mode used, user notified, document results

- [ ] **Task 4.9**: Execute Test Scenario 6 (Edge Case - Fast Plan Exists)
  - File: N/A (manual testing)
  - Effort: S
  - Dependencies: Task 4.3
  - Acceptance: Existing plan detected, user prompted with options, document results

- [ ] **Task 4.10**: Execute Test Scenario 7 (Guidelines Always Checked)
  - File: N/A (manual testing)
  - Effort: M
  - Dependencies: Task 4.3
  - Acceptance: Both modes reference CLAUDE.md and guidelines, quality maintained, document results

- [ ] **Task 4.11**: Verify no regressions in existing workflow
  - File: N/A (regression testing)
  - Effort: M
  - Dependencies: Phases 1-3 complete
  - Acceptance: Existing `/iw-plan` commands work unchanged, detailed planning quality unchanged, backward compatibility verified

- [ ] **Task 4.12**: Update skill description metadata
  - File: `.claude/skills/iw-planner/SKILL.md:1-4` (frontmatter)
  - Effort: S
  - Dependencies: All testing complete
  - Acceptance: Description mentions two modes (fast/detailed)

### Phase 4 Verification
- [ ] All 7 test scenarios executed successfully
- [ ] Token savings measured and documented (≥60% time, ≤30% tokens for fast mode)
- [ ] Edge cases handled gracefully with clear user messages
- [ ] Documentation examples work as written
- [ ] No regressions in existing detailed planning workflow
- [ ] User experience is smooth for both fast and detailed modes

---

## Final Verification

### Automated Checks:
- [ ] Fast plan initialization works: `python3 .claude/skills/iw-planner/scripts/init_plan.py test --type issue --mode fast`
- [ ] Fast template exists: `test -f .claude/skills/iw-planner/assets/fast-plan-template.md`
- [ ] Command mentions fast mode: `grep -q "fast" .claude/commands/iw-plan.md`
- [ ] Skill documentation updated: `grep -q "Fast Planning Workflow" .claude/skills/iw-planner/SKILL.md`
- [ ] Edge cases documented: `grep -q "Edge Cases and Error Handling" .claude/skills/iw-planner/SKILL.md`

### Manual Checks:
- [ ] Fast plan for simple task completes in <2 minutes with <100 lines
- [ ] Detailed plan preserves all user edits from fast plan
- [ ] Both modes check CLAUDE.md and .docs/knowledge guidelines
- [ ] Upgrade path is seamless (user doesn't repeat information)
- [ ] Documentation is clear and examples are accurate
- [ ] Performance targets met (60% faster, 70% fewer tokens)
- [ ] No quality degradation (fast plans still check guidelines)
- [ ] Edge cases produce helpful error messages

## Implementation Notes

**Progress Tracking:**
- Update task status as work progresses
- Note any blockers or issues in this section
- Record actual vs estimated effort

**Testing Notes:**
- Record test execution dates and results
- Document any deviations from expected behavior
- Note performance measurements for comparison

**User Feedback:**
- If beta tested, record user feedback here
- Note any usability issues discovered
- Document suggested improvements
