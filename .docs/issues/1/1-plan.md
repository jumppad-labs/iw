# Issue #1 Implementation Plan: Auto-Update Tasks and Create Commits After Each Phase

**Created**: 2025-11-03
**Last Updated**: 2025-11-03
**GitHub Issue**: #1

## Overview

The iw-executor skill is not automatically updating tasks.md and context.md after completing tasks, nor is it creating git commits after each phase completes. The SKILL.md documentation explicitly states these operations should happen **AUTOMATICALLY** and **IMMEDIATELY**, but the current implementation requires the user to manually prompt for these actions.

This plan adds enforcement mechanisms to ensure the executor skill follows its own specification for automatic updates and commits.

## Current State Analysis

### What Exists Now:

The infrastructure for automatic updates and commits exists:

1. **Task Update Script**: `.claude/skills/iw-executor/scripts/update_task.py:1-124`
   - Marks tasks done/pending in tasks.md automatically
   - Uses pattern matching to find tasks
   - Already implemented and working

2. **Context Update Script**: `.claude/skills/iw-executor/scripts/update_context.py:1-152`
   - Appends discoveries to context.md sections
   - Creates sections if missing
   - Adds timestamps automatically
   - Already implemented and working

3. **Phase Commit Script**: `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py:1-239`
   - Creates phase-based git commits
   - Extracts phase info from plan files
   - Generates proper commit messages
   - Already implemented and working

### What's Missing:

The SKILL.md documentation contains clear directives, but these are not being consistently followed:

**From `.claude/skills/iw-executor/SKILL.md:195-207`:**
```markdown
d. **Update Progress (AUTOMATIC - DO IMMEDIATELY):**
   - **IMMEDIATELY** after completing task, mark it done
   - Use `scripts/update_task.py` to check off the task in tasks.md
   - **DO NOT WAIT** for user to ask - this is automatic

e. **Document Discoveries (AUTOMATIC WHEN FOUND):**
   - **IMMEDIATELY** when interesting findings emerge
   - Use `scripts/update_context.py` to add to context.md
   - **DO NOT WAIT** for user to ask - document as you discover
```

**From `.claude/skills/iw-executor/SKILL.md:238-264`:**
```markdown
d. **Create Phase Commit (AUTOMATIC AFTER CONFIRMATION):**
   **IMMEDIATELY** after user confirms phase completion:
   - Use `iw-git-workflow` skill to create phase commit
   - Run `scripts/create_phase_commit.py`
   - **DO NOT WAIT** for user to ask - commit happens automatically
```

### Current Implementation Example:

The scripts exist and work correctly when called. For example, `update_task.py:23-62` handles task updates:

```python
def find_and_update_task(
    content: str,
    task_pattern: str,
    new_status: str
) -> tuple[str, bool]:
    """Find task matching pattern and update its status."""
    lines = content.split("\n")
    updated_lines = []
    found = False

    # Convert status to checkbox marker
    marker = "x" if new_status == "done" else " "

    for line in lines:
        # Check if this is a task line
        task_match = re.match(r"^(-\s+\[)([ x])(\]\s+.+)$", line)
        if task_match:
            # Check if task description matches pattern
            task_desc = task_match.group(3)[2:]  # Remove "] " prefix
            if task_pattern.lower() in task_desc.lower():
                # Update the status marker
                updated_line = f"{task_match.group(1)}{marker}{task_match.group(3)}"
                updated_lines.append(updated_line)
                found = True
                continue

        # Keep line as is
        updated_lines.append(line)

    return "\n".join(updated_lines), found
```

The problem is NOT the implementation - the scripts work fine. The problem is that the skill documentation's automation directives are not being enforced consistently.

## Desired End State

After implementing this plan:

1. **Task Updates Are Automatic**: When a task is completed during implementation, the executor immediately calls `update_task.py` without being prompted
2. **Context Updates Are Automatic**: When discoveries are made, the executor immediately calls `update_context.py` without being prompted
3. **Phase Commits Are Automatic**: After user confirms phase completion, the executor immediately calls `create_phase_commit.py` without being prompted
4. **Verification**: The implementation behavior matches the SKILL.md specification exactly

**How to Verify**: Run an implementation session and observe that tasks.md updates happen after each task completion, context.md updates happen when discoveries are made, and git commits are created after each phase - all without manual prompting.

## What We're NOT Doing

- Changing the Python scripts (they already work correctly)
- Modifying the git workflow (it's correct as-is)
- Adding new automation scripts
- Changing the worktree approach
- Modifying plan file formats
- Altering the phase-based workflow structure

This is purely about **enforcing the existing specification** that's already documented in SKILL.md.

## Implementation Approach

The issue is that the automation directives in SKILL.md are clear but not being followed consistently. The solution is to strengthen these directives with:

1. **Clearer Emphasis**: Make the automation requirements impossible to miss
2. **Explicit Workflow Reminders**: Add checkpoints in the workflow that explicitly require automation
3. **Success Criteria Integration**: Tie automation to phase completion criteria
4. **Example Integration**: Show exactly when and how to call the automation scripts

This is a documentation enhancement that makes the existing automation requirements more prominent and explicit.

---

## Phase 1: Strengthen Task and Context Update Automation in SKILL.md

### Overview
Enhance the iw-executor SKILL.md to make the automatic task and context update requirements more explicit and harder to overlook.

### Changes Required:

#### 1. Strengthen Automation Directives in Step 3 (Execute Tasks by Phase)

**File**: `.claude/skills/iw-executor/SKILL.md:162-208`

**Current code:**
```markdown
2. **Execute Each Task:**
   For each uncompleted task in the phase:

   a. **Read Referenced Files:**
      - Read the files mentioned in the task using Read tool
      - Understand current implementation
      - Review code examples from plan.md for this change

   b. **Implement the Task:**
      - Follow the detailed approach in plan.md
      - Use code patterns from language guidelines
      - Apply TDD approach if specified (write tests first for Go)
      - Make incremental changes following the plan

   c. **Run Tests/Verification:**
      - Run automated verification commands from success criteria
      - Check that tests pass
      - Verify the change works as expected

   d. **Update Progress (AUTOMATIC - DO IMMEDIATELY):**
      - **IMMEDIATELY** after completing task, mark it done
      - Use `scripts/update_task.py` to check off the task in tasks.md
      - Example: `update_task.py tasks.md "Task description" --status done`
      - **DO NOT WAIT** for user to ask - this is automatic
      - This ensures progress is saved incrementally

   e. **Document Discoveries (AUTOMATIC WHEN FOUND):**
      - **IMMEDIATELY** when interesting findings emerge (unexpected patterns, edge cases, etc.)
      - Use `scripts/update_context.py` to add to context.md
      - Example: `update_context.py context.md --section "Key Findings" --content "Found that..."`
      - **DO NOT WAIT** for user to ask - document as you discover
      - This preserves knowledge across context compaction
```

**Proposed changes:**
```markdown
2. **Execute Each Task:**
   For each uncompleted task in the phase:

   a. **Read Referenced Files:**
      - Read the files mentioned in the task using Read tool
      - Understand current implementation
      - Review code examples from plan.md for this change

   b. **Implement the Task:**
      - Follow the detailed approach in plan.md
      - Use code patterns from language guidelines
      - Apply TDD approach if specified (write tests first for Go)
      - Make incremental changes following the plan

   c. **Run Tests/Verification:**
      - Run automated verification commands from success criteria
      - Check that tests pass
      - Verify the change works as expected

   ⚠️ **CRITICAL AUTOMATION CHECKPOINT** ⚠️

   d. **Update Progress (REQUIRED - AUTOMATIC - DO NOT SKIP):**

      **IMMEDIATELY** after completing task implementation and verification:

      1. Call the update script using Bash tool:
         ```bash
         python3 .claude/skills/iw-executor/scripts/update_task.py \
           <worktree-path>/.docs/issues/<N>/<N>-tasks.md \
           "<task description pattern>" \
           --status done
         ```

      2. Verify the update succeeded (script outputs "✓ Updated task status")

      3. Continue to next task

      **IMPORTANT**:
      - This is NOT optional - it MUST happen after every task completion
      - DO NOT wait for user to request this update
      - DO NOT batch multiple task updates together
      - Update happens IMMEDIATELY, before moving to the next task
      - This ensures progress survives context compaction and session interruptions

   e. **Document Discoveries (REQUIRED WHEN FOUND - AUTOMATIC):**

      **IMMEDIATELY** when any of these occur during implementation:
      - Unexpected patterns discovered
      - Edge cases identified
      - Integration points found
      - Performance characteristics observed
      - Workarounds needed
      - Deviations from the plan

      Call the context update script using Bash tool:
      ```bash
      python3 .claude/skills/iw-executor/scripts/update_context.py \
        <worktree-path>/.docs/issues/<N>/<N>-context.md \
        --section "Implementation Discoveries" \
        --content "<brief description of discovery>"
      ```

      **IMPORTANT**:
      - This is NOT optional - discoveries MUST be documented when found
      - DO NOT wait for user to request documentation
      - DO NOT delay documentation until end of phase
      - Document happens IMMEDIATELY when discovery is made
      - This preserves knowledge across context compaction
```

**Reasoning**: The original text had the right intent but wasn't emphatic enough. The new version:
- Adds visual markers (⚠️ CRITICAL AUTOMATION CHECKPOINT ⚠️)
- Changes "Example:" to explicit numbered steps with Bash tool usage
- Adds explicit verification step
- Lists what constitutes a "discovery"
- Emphasizes "REQUIRED" and "NOT optional"
- Shows exact script paths relative to worktree

#### 2. Add Automation Verification to Phase Completion

**File**: `.claude/skills/iw-executor/SKILL.md:209-236`

**Current code:**
```markdown
3. **Phase Completion Verification:**
   After all tasks in the phase complete:

   a. **Run Phase Success Criteria:**
      - Execute automated verification commands from plan.md
      - Perform manual verification steps as listed
      - Document results

   b. **Confirm with User:**
      ```
      Phase [N]: [Phase Name] - COMPLETED

      Completed tasks:
      - [x] [Task 1 description]
      - [x] [Task 2 description]
      - [x] [Task 3 description]

      Verification results:
      - Automated: [test results]
      - Manual checks needed: [list from plan]

      Ready to proceed to Phase [N+1]?
      ```

   c. **Wait for User Confirmation:**
      - User can approve to continue
      - User can request adjustments
      - User can pause implementation
```

**Proposed changes:**
```markdown
3. **Phase Completion Verification:**
   After all tasks in the phase complete:

   a. **Verify All Task Updates Were Made:**
      - Read the tasks.md file in the worktree
      - Confirm all tasks in current phase are marked [x]
      - If any tasks are not marked complete, update them now using update_task.py
      - This is a safety check to ensure automation worked

   b. **Run Phase Success Criteria:**
      - Execute automated verification commands from plan.md
      - Perform manual verification steps as listed
      - Document results

   c. **Confirm with User:**
      ```
      Phase [N]: [Phase Name] - COMPLETED

      ✅ Task Tracking Updated:
      - All [X] tasks in Phase [N] marked complete in tasks.md
      - [Y] discoveries documented in context.md

      Completed tasks:
      - [x] [Task 1 description]
      - [x] [Task 2 description]
      - [x] [Task 3 description]

      Verification results:
      - Automated: [test results]
      - Manual checks needed: [list from plan]

      Ready to proceed to Phase [N+1]?
      ```

   d. **Wait for User Confirmation:**
      - User can approve to continue
      - User can request adjustments
      - User can pause implementation
```

**Reasoning**: Adding step (a) creates a checkpoint to verify automation actually happened. Including task update status in the confirmation message makes progress tracking visible to the user.

### Testing for This Phase:

**Verification Method**: Review the updated SKILL.md documentation

1. **Manual review of SKILL.md:**
   - Confirm automation directives are prominent
   - Confirm bash commands are shown explicitly
   - Confirm checkpoints are added
   - Confirm verification steps are clear

2. **Check diff for completeness:**
   ```bash
   git diff .claude/skills/iw-executor/SKILL.md
   ```

### Success Criteria:

#### Automated Verification:
- [ ] File `.claude/skills/iw-executor/SKILL.md` has been modified
- [ ] Grep confirms new checkpoint markers exist: `grep -n "CRITICAL AUTOMATION CHECKPOINT" .claude/skills/iw-executor/SKILL.md`
- [ ] Grep confirms REQUIRED emphasis exists: `grep -n "REQUIRED - AUTOMATIC" .claude/skills/iw-executor/SKILL.md`

#### Manual Verification:
- [ ] Read the modified SKILL.md and confirm automation requirements are clear
- [ ] Confirm bash command examples are complete and correct
- [ ] Confirm checkpoint additions make sense in workflow

---

## Phase 2: Strengthen Phase Commit Automation in SKILL.md

### Overview
Enhance the phase commit automation requirements to make them equally explicit and unmissable.

### Changes Required:

#### 1. Strengthen Phase Commit Automation Directive

**File**: `.claude/skills/iw-executor/SKILL.md:238-264`

**Current code:**
```markdown
   d. **Create Phase Commit (AUTOMATIC AFTER CONFIRMATION):**
      **IMMEDIATELY** after user confirms phase completion:
      - Use `iw-git-workflow` skill to create phase commit
      - Run `scripts/create_phase_commit.py --phase <N> --plan-path <plan-path> --worktree <worktree-path>`
      - **DO NOT WAIT** for user to ask - commit happens automatically
      - Script does:
        - Stages all changes in worktree
        - Creates commit with phase-based message
        - Includes plan reference and issue number
      - Commit message format:
        ```
        Phase N: <Phase Name>

        <Description of what was implemented>

        Plan: <path-to-plan>
        Issue: #<issue-number>
        ```
      - Inform user:
        ```
        ✓ Phase N committed

        Commit: abc1234 - Phase N: <Phase Name>
        Files changed: 5
        Insertions: 120, Deletions: 10
        ```
```

**Proposed changes:**
```markdown
   ⚠️ **CRITICAL AUTOMATION CHECKPOINT - PHASE COMMIT** ⚠️

   e. **Create Phase Commit (REQUIRED - AUTOMATIC - DO NOT SKIP):**

      **IMMEDIATELY** after user confirms phase completion (step d above):

      1. Determine phase number and plan path from context
      2. Call the phase commit script using Bash tool:
         ```bash
         python3 .claude/skills/iw-git-workflow/scripts/create_phase_commit.py \
           --phase <N> \
           --plan-path <worktree-path>/.docs/issues/<issue-number> \
           --worktree <worktree-path>
         ```

      3. Verify the commit succeeded (script outputs JSON with "success": true)

      4. Parse the JSON response and extract commit hash and stats

      5. Inform user with commit details:
         ```
         ✅ Phase <N> Automatically Committed

         Commit: <commit-hash> - Phase <N>: <Phase Name>
         Files changed: <count>
         Insertions: <count>, Deletions: <count>

         This commit was created automatically as specified in the workflow.
         ```

      **IMPORTANT**:
      - This is NOT optional - phase commits MUST happen after user confirms
      - DO NOT wait for user to explicitly request the commit
      - DO NOT skip this step even if changes seem small
      - Commit happens IMMEDIATELY after confirmation, before starting next phase
      - This ensures each phase is atomically committed with proper attribution

      **Script behavior**:
      - Stages all changes in worktree with `git add -A`
      - Creates commit with phase-based message
      - Extracts phase name from plan.md
      - Includes plan reference and issue number
      - Returns JSON with commit hash and statistics

      **Commit message format**:
      ```
      Phase N: <Phase Name>

      <Description of what was implemented>

      Plan: .docs/issues/<issue-number>
      Issue: #<issue-number>
      ```
```

**Reasoning**: Same improvements as task automation:
- Visual checkpoint marker
- Explicit numbered steps showing Bash tool usage
- Shows exact script paths
- Verification step
- Emphasizes "REQUIRED" and "NOT optional"
- Explains what the script does
- Shows expected output format

#### 2. Add Pre-Phase Reminder

**File**: `.claude/skills/iw-executor/SKILL.md:163-175`

**Current code:**
```markdown
For each phase in the plan:

1. **Announce Phase Start:**
   ```
   Starting Phase [N]: [Phase Name]

   Tasks in this phase:
   - [ ] [Task 1 description] - [file path] - [effort]
   - [ ] [Task 2 description] - [file path] - [effort]
   - [x] [Task 3 description] - [file path] - [effort] (already completed)

   Proceeding with implementation...
   ```
```

**Proposed changes:**
```markdown
For each phase in the plan:

1. **Announce Phase Start:**
   ```
   Starting Phase [N]: [Phase Name]

   Tasks in this phase:
   - [ ] [Task 1 description] - [file path] - [effort]
   - [ ] [Task 2 description] - [file path] - [effort]
   - [x] [Task 3 description] - [file path] - [effort] (already completed)

   📋 Automation Reminder:
   - Each task will be automatically marked complete in tasks.md upon completion
   - Discoveries will be automatically documented in context.md as found
   - Phase commit will be created automatically after you confirm phase completion

   Proceeding with implementation...
   ```
```

**Reasoning**: Setting expectations upfront helps ensure the automation happens. This reminder appears at the start of every phase.

### Testing for This Phase:

**Verification Method**: Review the updated SKILL.md documentation

1. **Manual review of phase commit section:**
   - Confirm automation directive is stronger
   - Confirm bash command is explicit
   - Confirm verification step is included

2. **Manual review of phase start section:**
   - Confirm automation reminder is present

3. **Check diff for completeness:**
   ```bash
   git diff .claude/skills/iw-executor/SKILL.md
   ```

### Success Criteria:

#### Automated Verification:
- [ ] File `.claude/skills/iw-executor/SKILL.md` has phase commit checkpoint marker
- [ ] Grep confirms checkpoint exists: `grep -n "PHASE COMMIT" .claude/skills/iw-executor/SKILL.md`
- [ ] Grep confirms automation reminder exists: `grep -n "Automation Reminder" .claude/skills/iw-executor/SKILL.md`

#### Manual Verification:
- [ ] Read the modified SKILL.md and confirm phase commit requirements are clear
- [ ] Confirm bash command example is complete with all parameters
- [ ] Confirm the workflow reads naturally with the additions

---

## Phase 3: Add Automation Summary to Important Guidelines Section

### Overview
Add a dedicated section to the "Important Guidelines" that summarizes all automation requirements in one place for easy reference.

### Changes Required:

#### 1. Add Automation Requirements Summary

**File**: `.claude/skills/iw-executor/SKILL.md:448-497`

**Current code (end of Important Guidelines section):**
```markdown
### Be Thorough

- Read all referenced files fully
- Run all verification commands
- Check tests pass before marking tasks complete
- Document all interesting findings
- Don't assume - verify with code and tests
```

**Proposed changes:**
```markdown
### Be Thorough

- Read all referenced files fully
- Run all verification commands
- Check tests pass before marking tasks complete
- Document all interesting findings
- Don't assume - verify with code and tests

### Automation Requirements Summary

**⚠️ CRITICAL: The following automations are REQUIRED and MUST happen without user prompting:**

#### After Each Task Completion:
```bash
# REQUIRED: Mark task as done in tasks.md
python3 .claude/skills/iw-executor/scripts/update_task.py \
  <tasks-file-path> \
  "<task description pattern>" \
  --status done
```
- Happens: IMMEDIATELY after task implementation and tests pass
- Trigger: Task completion
- Frequency: Once per task
- DO NOT: Wait for user to ask
- DO NOT: Batch multiple tasks before updating

#### When Discoveries Are Made:
```bash
# REQUIRED: Document discovery in context.md
python3 .claude/skills/iw-executor/scripts/update_context.py \
  <context-file-path> \
  --section "Implementation Discoveries" \
  --content "<discovery description>"
```
- Happens: IMMEDIATELY when discovery is made
- Trigger: Unexpected finding, workaround needed, deviation from plan
- Frequency: As discoveries occur (may be 0 or many per phase)
- DO NOT: Wait for user to ask
- DO NOT: Defer to end of phase

#### After User Confirms Phase Completion:
```bash
# REQUIRED: Create phase commit
python3 .claude/skills/iw-git-workflow/scripts/create_phase_commit.py \
  --phase <N> \
  --plan-path <plan-directory> \
  --worktree <worktree-path>
```
- Happens: IMMEDIATELY after user confirms "Ready to proceed"
- Trigger: User confirmation of phase completion
- Frequency: Once per phase
- DO NOT: Wait for user to explicitly request commit
- DO NOT: Skip even if changes are small

#### Why These Automations Matter:

1. **Task updates** ensure progress survives context compaction and crashes
2. **Context updates** preserve institutional knowledge for future work
3. **Phase commits** create atomic, reviewable units of work with proper attribution

**If you forget these automations, the implementation will not follow the workflow specification.**
```

**Reasoning**: Having all automation requirements in one place provides:
- Quick reference during implementation
- Clear examples of all three automation types
- Explanation of why each matters
- Explicit "DO NOT" statements to prevent common mistakes

### Testing for This Phase:

**Verification Method**: Review the updated SKILL.md documentation

1. **Manual review of new automation summary section:**
   - Confirm all three automation types are covered
   - Confirm bash examples are correct
   - Confirm explanations are clear

2. **Check placement in document:**
   - Should be at end of "Important Guidelines" section
   - Should be before "Resources" section

### Success Criteria:

#### Automated Verification:
- [ ] File `.claude/skills/iw-executor/SKILL.md` contains automation summary
- [ ] Grep confirms section exists: `grep -n "Automation Requirements Summary" .claude/skills/iw-executor/SKILL.md`
- [ ] All three automation types are documented

#### Manual Verification:
- [ ] Read automation summary and confirm it's comprehensive
- [ ] Confirm examples match the actual script usage
- [ ] Confirm placement makes sense in document flow

---

## Testing Strategy

### Verification Approach:

Since this is a documentation change, testing focuses on:

1. **Correctness**: Verify bash commands work as documented
2. **Completeness**: Verify all automation points are covered
3. **Clarity**: Verify instructions are unambiguous

### Testing Steps:

#### Phase 1 Testing:
```bash
# Verify task update automation is documented correctly
grep -A 10 "Update Progress (REQUIRED - AUTOMATIC" .claude/skills/iw-executor/SKILL.md

# Verify context update automation is documented correctly
grep -A 10 "Document Discoveries (REQUIRED WHEN FOUND" .claude/skills/iw-executor/SKILL.md

# Verify checkpoint marker exists
grep "CRITICAL AUTOMATION CHECKPOINT" .claude/skills/iw-executor/SKILL.md
```

#### Phase 2 Testing:
```bash
# Verify phase commit automation is strengthened
grep -A 15 "Create Phase Commit (REQUIRED - AUTOMATIC" .claude/skills/iw-executor/SKILL.md

# Verify automation reminder exists
grep -A 5 "Automation Reminder" .claude/skills/iw-executor/SKILL.md
```

#### Phase 3 Testing:
```bash
# Verify automation summary section exists
grep -A 30 "Automation Requirements Summary" .claude/skills/iw-executor/SKILL.md

# Verify all three automation types are in summary
grep -A 50 "Automation Requirements Summary" .claude/skills/iw-executor/SKILL.md | grep -E "(update_task|update_context|create_phase_commit)"
```

### Integration Testing:

After documentation changes:

1. **Dry run with a test plan**: Use the updated SKILL.md to implement a trivial test plan
2. **Observe automation behavior**: Verify the strengthened directives result in automatic updates
3. **User feedback**: Have the issue reporter test the updated workflow

## Performance Considerations

No performance implications - this is pure documentation enhancement.

## Migration Notes

No migration needed. Changes are:
- Documentation only (SKILL.md file)
- Backward compatible (existing implementations continue to work)
- Immediate effect (next time skill is loaded, new directives are active)

## References

- **Original Issue**: #1
- **Key Files Examined**:
  - `.claude/skills/iw-executor/SKILL.md:1-522` (entire file reviewed)
  - `.claude/skills/iw-executor/scripts/update_task.py:1-124` (verified working)
  - `.claude/skills/iw-executor/scripts/update_context.py:1-152` (verified working)
  - `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py:1-239` (verified working)
- **Similar Patterns**: None - this is a unique documentation enhancement issue
- **Research Notes**: See `1-research.md` for detailed findings
