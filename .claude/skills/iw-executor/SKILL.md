---
name: iw-executor
description: Execute implementation plans created by iw-planner. This skill should be used when the user wants to implement a planned feature, following the detailed plan files (plan.md, tasks.md, context.md, research.md) with incremental progress tracking and user confirmation at key milestones. Handles both issue-based and ad-hoc plans.
---

# Implementation Executor

## Overview

Execute detailed implementation plans created by the iw-planner skill. Follow the structured plan files, track progress by updating tasks.md as work completes, document discoveries in context.md, and confirm with the user after each phase and when issues arise.

**Language-Agnostic Approach:** This skill automatically detects the project language and activates the appropriate language-specific guidelines skill (e.g., `go-dev-guidelines` for Go projects) to ensure implementation follows established coding standards, testing patterns, and architectural conventions.

**Incremental Progress Tracking:** As tasks complete, mark them as done in tasks.md. When interesting findings emerge during implementation, update context.md. This ensures progress is preserved across context compaction or crashes.

**User Confirmation:** Confirm with the user after completing each phase and whenever implementation deviates from the plan or errors occur. User decides whether to proceed, adjust approach, or update the plan.

**Git Workflow Integration:** Uses the iw-git-workflow skill to ensure safe implementation with isolated worktrees. Verifies git state is clean before starting, creates worktrees for isolated work, commits after each phase, and handles cleanup with optional PR creation.

## Quick Start

**Invoke with plan directory path:**
```
/implement .docs/issues/123/
```
or
```
/implement .docs/adhoc/feature-name/
```

The skill will:
1. Check git state and create isolated worktree
2. Load all four plan files
3. Activate language-specific guidelines
4. Execute tasks phase by phase
5. Create git commits after each phase
6. Update tasks.md and context.md incrementally
7. Confirm after each phase and on issues
8. Push branch and cleanup worktree when complete

## Workflow

### Step 0: Git Safety and Worktree Setup

Before loading the plan, ensure safe git workflow:

1. **Activate iw-git-workflow Skill:**
   - Invoke the `iw-git-workflow` skill to handle git operations
   - This skill provides safety checks and worktree management

2. **Check Git State:**
   - Use `iw-git-workflow` to verify main working directory is clean
   - Run `scripts/check_clean.py` from iw-git-workflow skill
   - If not clean:
     ```
     ⚠️  Git Working Directory Not Clean

     The main working directory has uncommitted changes.
     Implementation requires a clean state to use worktrees safely.

     Issues found:
     - [list of files]

     Please commit or stash these changes before starting implementation.
     ```
   - STOP if directory is not clean
   - User must clean up before proceeding

3. **Create Worktree:**
   - Use `iw-git-workflow` to create isolated worktree
   - Run `scripts/create_worktree.py --plan-path <plan-path> --base-branch main`
   - Script does:
     - Generates branch name (e.g., `issue-123-feature-name`)
     - Creates worktree in parent directory (e.g., `../jumppad-issue-123-feature-name`)
     - Checks out new branch in worktree
   - Returns worktree path

4. **Switch Context to Worktree:**
   - All subsequent file operations happen in the worktree
   - Main working directory remains clean and untouched
   - Inform user:
     ```
     ✓ Created worktree for implementation

     Branch: issue-123-add-rate-limiting
     Worktree: /home/user/code/jumppad-issue-123-add-rate-limiting
     Base: main

     All implementation work will happen in the worktree.
     Main working directory remains clean.
     ```

**IMPORTANT:** All file reads, edits, and writes after this point must use the worktree path, not the original working directory.

### Step 1: Load and Parse Plan

When invoked with a plan directory path:

1. **Verify Plan Directory Structure:**
   - Check for required files: `*-plan.md`, `*-tasks.md`, `*-context.md`, `*-research.md`
   - If missing files, inform user and stop

2. **Load Plan Files:**
   - Read `*-plan.md` fully to understand the implementation approach
   - Read `*-tasks.md` fully to see the task checklist
   - Read `*-context.md` fully for quick reference information
   - Read `*-research.md` as needed for additional context
   - Use the Read tool to load these files into context

3. **Search for Relevant Past Learnings:**
   - Invoke `iw-learnings` skill using Skill tool
   - Extract keywords from plan topic/issue title
   - Skill searches all past plan context.md files for "Learnings & Corrections"
   - Present relevant learnings before starting implementation
   - Keep findings in mind during implementation to avoid repeating mistakes

4. **Parse Plan Structure:**
   - Use `scripts/parse_plan.py` to extract:
     - Phases and their order
     - Tasks within each phase
     - Task status (pending/done)
     - File references and locations
     - Success criteria for each phase
   - Returns structured data about what to implement

5. **Display Plan Summary:**
   ```
   Loaded plan from: [path]

   Phases identified:
   1. [Phase 1 name] - [X tasks, Y completed]
   2. [Phase 2 name] - [X tasks, Y completed]
   3. [Phase 3 name] - [X tasks, Y completed]

   Overall progress: [X/Y tasks completed]

   Ready to begin implementation.
   ```

### Step 2: Activate Language Guidelines

Before starting implementation:

1. **Detect Project Language:**
   - Look at plan files for language indicators
   - Check codebase structure and file extensions
   - Look for language-specific files (go.mod, package.json, etc.)

2. **Activate Guidelines Skill:**
   - **Go projects** → Invoke `go-dev-guidelines` skill
   - **Other languages** → Invoke appropriate language-specific guidelines if available
   - These skills provide coding standards, testing patterns, and architectural patterns to follow

3. **Apply Throughout Implementation:**
   - Follow testing patterns from guidelines (e.g., TDD with testify/require for Go)
   - Use naming conventions from guidelines
   - Follow project structure conventions
   - Apply architectural patterns from guidelines

### Step 3: Execute Tasks by Phase

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
      - This ensures each phase is atomically committed with phase and issue references

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

### Step 4: Handle Issues and Deviations

When issues arise during implementation:

#### A. Implementation Differs from Plan

If the actual implementation needs to differ from what the plan specifies:

1. **Stop Immediately:**
   - Do not continue implementing
   - Do not make assumptions

2. **Present Context to User:**
   ```
   ⚠️  Implementation Deviation Detected

   **Plan Expected:**
   [What the plan says to do]
   [Code example from plan]

   **Actual Situation:**
   [What was found in the codebase]
   [Current code example]

   **Why Different:**
   [Explanation of why the plan approach won't work or needs adjustment]

   **Recommended Approach:**
   [Suggested alternative if applicable]

   The plan needs to be updated before proceeding.
   Please update the plan files and I'll continue from there.
   ```

3. **Wait for Plan Update and Log the Learning:**
   - User updates the plan files (plan.md, tasks.md, etc.)
   - User confirms when ready
   - **AUTOMATICALLY log the correction to context.md:**
     - Use `scripts/update_context.py --section "Learnings & Corrections" --content "[Planned X] → [Actually needed Y] - [Why it matters]"`
     - Include current date in the entry
     - Format: `[YYYY-MM-DD] [Original plan] → [Actual approach] - [Impact/reason]`
   - Reload plan files and continue

#### B. Errors or Failures

If tests fail, code doesn't compile, or other errors occur:

1. **Capture Error Details:**
   - Full error message
   - Stack trace if available
   - Context of what was being attempted

2. **Present to User:**
   ```
   ⚠️  Error Encountered

   **During:** [Phase N - Task description]
   **Error:**
   ```
   [error message]
   ```

   **Context:**
   [What was being done when error occurred]

   **Possible causes:**
   - [Hypothesis 1]
   - [Hypothesis 2]

   How would you like to proceed?
   ```

3. **Wait for User Guidance:**
   - User can suggest fix approach
   - User can update plan
   - User can decide to skip and continue

#### C. Unexpected Discoveries

If something interesting or unexpected is found:

1. **Document in Context:**
   - Use `scripts/update_context.py` to add to context.md
   - For general discoveries: Add to "Key Discoveries" or relevant section
   - For corrections/lessons learned: Add to "Learnings & Corrections" section
     - Format: `[YYYY-MM-DD] [What was assumed] → [What was discovered] - [Why it matters]`
     - Example: `update_context.py context.md --section "Learnings & Corrections" --content "Expected sync API → Discovered async-only API - requires Promise handling throughout"`

2. **Inform User if Significant:**
   - If discovery impacts approach or plan
   - If discovery reveals new requirements
   - If discovery simplifies or complicates implementation

### Step 5: Completion

After all phases complete:

1. **Run Final Verification:**
   - Execute all final verification commands from tasks.md
   - Check overall success criteria from plan.md

2. **Present Summary:**
   ```
   ✅ Implementation Complete

   Plan: [plan path]

   Phases completed:
   - [x] Phase 1: [name]
   - [x] Phase 2: [name]
   - [x] Phase 3: [name]

   Total tasks completed: [X/Y]

   Final verification:
   - [List of automated checks passed]

   Manual verification needed:
   - [List of manual checks from plan]

   Files modified:
   - [List of files changed]

   Next steps:
   - [Any follow-up items from plan]
   ```

3. **Update Plan Files:**
   - Ensure all tasks in tasks.md are marked complete
   - Ensure context.md reflects final state
   - Implementation is complete

4. **Git Cleanup and PR Creation:**
   - Use `iw-git-workflow` skill for final git operations
   - Ask user if they want to create a pull request:
     ```
     ✅ All phases complete!

     Would you like me to:
     1. Push branch and create pull request
     2. Just push branch (create PR manually later)
     3. Keep worktree for manual review
     ```
   - Based on user choice:

   **Option 1: Push and create PR:**
   - Run `scripts/cleanup_worktree.py --worktree-path <path> --create-pr`
   - Script does:
     - Pushes branch to remote
     - Creates PR with summary of phases
     - Removes worktree directory
   - Inform user:
     ```
     ✓ Implementation Complete

     Branch pushed: issue-123-add-rate-limiting
     Pull request: #456 - Add Rate Limiting to API
     Worktree cleaned up

     Main working directory remains clean.
     Review the PR at: [PR URL]
     ```

   **Option 2: Just push:**
   - Run `scripts/cleanup_worktree.py --worktree-path <path>`
   - Pushes branch and removes worktree
   - User creates PR manually later

   **Option 3: Keep worktree:**
   - Don't run cleanup script
   - Push manually if desired
   - User can review in worktree before pushing
   - Remind user to clean up worktree later:
     ```
     Worktree preserved at: [path]

     When ready to push and cleanup:
     cd [worktree-path]
     git push -u origin [branch-name]
     cd [main-dir]
     git worktree remove [worktree-path]
     ```

## Important Guidelines

### Follow the Plan

- The plan is the source of truth
- Follow the detailed approach in plan.md
- Use the code examples and patterns specified
- Execute tasks in the order specified
- Don't skip steps or take shortcuts

### When to Stop and Ask

STOP and prompt the user when:
- Implementation needs to differ from the plan
- Tests fail or errors occur
- Unexpected complexity is discovered
- Requirements seem unclear or conflicting
- After each phase completes (for confirmation)

### Progress Tracking

**Update tasks.md incrementally:**
- Mark tasks as done using `update_task.py` as they complete
- Don't batch updates - update after each task
- This ensures progress survives context compaction

**Update context.md when discoveries made:**
- Use `update_context.py` to add findings
- Document unexpected patterns
- Note edge cases discovered
- Record integration insights

### Language Guidelines

**Always activate language-specific guidelines:**
- Detect project language from plan and codebase
- Invoke appropriate guidelines skill (e.g., go-dev-guidelines)
- Follow coding standards from the guidelines
- Apply testing patterns from the guidelines
- Use architectural patterns from the guidelines

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
3. **Phase commits** create atomic, reviewable units of work with phase and issue references

**If you forget these automations, the implementation will not follow the workflow specification.**

## Resources

### scripts/

This skill includes three Python scripts for managing plan execution:

**`parse_plan.py`** - Extract structure from plan files
```bash
python3 scripts/parse_plan.py <plan-directory>
```
Returns JSON with phases, tasks, file references, and progress status.

**`update_task.py`** - Check off tasks in tasks.md
```bash
python3 scripts/update_task.py <tasks-file> <task-pattern> --status done
```
Marks matching task as completed in the tasks checklist.

**`update_context.py`** - Add discoveries to context.md
```bash
python3 scripts/update_context.py <context-file> --section <section-name> --content <new-content>
```
Appends new content to the specified section in context.md.

These scripts ensure progress tracking is reliable and survives context compaction.
