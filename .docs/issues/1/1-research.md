# Issue #1 - Research & Working Notes

**Research Date**: 2025-11-03
**Researchers**: Claude + nicj

## Initial Understanding

When first reading issue #1, it appeared that the automation scripts (update_task.py, update_context.py, create_phase_commit.py) were either missing or broken. The issue states: "Tasks and context were not automatically updated after the success of a phase and no git commit was created."

Initial hypothesis: The Python scripts don't exist or have bugs.

## Research Process

### Files Examined:

1. **`.claude/skills/iw-executor/SKILL.md`** (lines 1-522)
   - Finding: Complete workflow documentation exists with explicit automation directives
   - Lines 195-207: Task and context update automation spec ("AUTOMATIC - DO IMMEDIATELY")
   - Lines 238-264: Phase commit automation spec ("AUTOMATIC AFTER CONFIRMATION")
   - Relevant code pattern: Automation is specified but with moderate emphasis

2. **`.claude/skills/iw-executor/scripts/update_task.py`** (lines 1-124)
   - Finding: Script exists and appears correctly implemented
   - Lines 23-62: Task update logic using regex pattern matching
   - No bugs found - implementation is clean and working
   - Relevant code pattern: Pattern matching on task checkboxes `- [ ]` and `- [x]`

3. **`.claude/skills/iw-executor/scripts/update_context.py`** (lines 1-152)
   - Finding: Script exists and is well-implemented
   - Lines 53-88: Section finding and content appending logic
   - Automatically adds timestamps
   - Creates sections if missing
   - No bugs found

4. **`.claude/skills/iw-git-workflow/scripts/create_phase_commit.py`** (lines 1-239)
   - Finding: Script exists and handles commit creation properly
   - Lines 91-117: Commit message generation with phase info extraction
   - Lines 120-169: Git commit creation with proper error handling
   - Extracts issue numbers from plan paths automatically
   - No bugs found

5. **`.claude/skills/iw-git-workflow/SKILL.md`** (lines 1-300)
   - Finding: Git workflow skill documentation exists
   - Specifies when phase commits should be created
   - Integration points with executor skill

### Sub-tasks Spawned:

1. **Explore: Find executor implementation files**
   - Result: Found complete set of Python scripts in `.claude/skills/iw-executor/scripts/`
   - Key discovery: Scripts are implemented and working - they just aren't being called consistently

2. **Explore: Find git workflow implementation**
   - Result: Found git workflow scripts in `.claude/skills/iw-git-workflow/scripts/`
   - Key discovery: Phase commit script is fully implemented with proper message formatting

3. **Explore: Search for phase completion patterns**
   - Result: Found automation directives in SKILL.md
   - Key discovery: Documentation says "AUTOMATIC" and "DO IMMEDIATELY" but emphasis could be stronger

4. **iw-learnings: Search past learnings**
   - Result: No learnings directory exists yet (project is new)
   - Key discovery: This is the first plan, so no historical context to learn from

### Questions Asked & Answers:

Initial Question: Are the scripts broken or missing?
Answer (from research): Scripts exist and work correctly when called

Follow-up Question: Why aren't they being called automatically?
Answer (from SKILL.md analysis): Documentation specifies automation but directives may not be prominent enough

## Key Discoveries

### Technical Discoveries:

1. **Scripts are working correctly**: All three automation scripts (update_task.py, update_context.py, create_phase_commit.py) exist and function properly when invoked
   - File: `.claude/skills/iw-executor/scripts/update_task.py:23-62`

2. **Automation is documented**: SKILL.md contains clear directives for automation
   - File: `.claude/skills/iw-executor/SKILL.md:195-207` (task/context updates)
   - File: `.claude/skills/iw-executor/SKILL.md:238-264` (phase commits)

3. **Gap is in enforcement**: The issue is not implementation - it's that the automation directives aren't being followed consistently during execution

4. **Documentation uses "Examples"**: Current SKILL.md uses "Example:" for script invocations, which may imply optional behavior rather than required automation
   - File: `.claude/skills/iw-executor/SKILL.md:198`

5. **No verification checkpoints**: Current workflow doesn't verify that automations actually happened before proceeding to next phase
   - File: `.claude/skills/iw-executor/SKILL.md:209-236`

### Patterns to Follow:

1. **Bash tool for script invocation**: All automation scripts should be called via Bash tool with full paths
   - Pattern: `python3 .claude/skills/iw-executor/scripts/update_task.py <args>`

2. **JSON output for verification**: create_phase_commit.py returns JSON that can be parsed to verify success
   - Pattern seen in: `.claude/skills/iw-git-workflow/scripts/create_phase_commit.py:220-234`

3. **Explicit checkpoints**: Other skills use checkpoint markers (⚠️) to draw attention to critical steps

### Constraints Identified:

1. **Cannot change script implementation**: Scripts work correctly - changing them would be unnecessary and risky

2. **Cannot add new scripts**: Solution must use existing automation infrastructure

3. **Documentation-only solution**: Must strengthen existing directives rather than adding new mechanisms

4. **Backward compatibility**: Changes must not break existing implementations that are following the spec correctly

## Design Decisions

### Decision 1: Strengthen Documentation vs Add New Automation

**Options considered:**
- Option A: Add new hook/trigger system to force automation
  - Pros: Guarantees automation happens
  - Cons: Complex, adds new code, may interfere with skill execution flow

- Option B: Strengthen documentation to make automation requirements unmissable
  - Pros: Simple, no new code, uses existing infrastructure
  - Cons: Relies on documentation being read and followed

**Chosen**: Option B - Strengthen documentation

**Rationale**: The automation infrastructure already exists and works perfectly. The scripts are well-implemented. The issue is that the automation directives in SKILL.md aren't emphatic enough. Making them more prominent and explicit is the right solution because:
- It's simpler (documentation-only change)
- It's safer (no code changes to working scripts)
- It addresses the root cause (directives being overlooked)
- It's maintainable (clearer docs are easier to follow)

### Decision 2: Visual Markers vs Text Emphasis

**Options considered:**
- Option A: Use ONLY text emphasis (bold, caps)
  - Pros: Works in all contexts
  - Cons: Can still be overlooked in long documents

- Option B: Add visual checkpoint markers (⚠️ emoji)
  - Pros: Immediately catches attention, breaks up text flow
  - Cons: May not render in all environments

**Chosen**: Option B - Use visual markers plus text emphasis

**Rationale**: Combining visual markers with text emphasis provides maximum visibility. The markers create "stopping points" in the workflow that are hard to miss.

### Decision 3: Show Examples vs Show Required Steps

**Options considered:**
- Option A: Keep current "Example:" format
  - Pros: Familiar, doesn't sound prescriptive
  - Cons: "Example" implies optional behavior

- Option B: Replace with numbered required steps
  - Pros: Clear that steps must be followed
  - Cons: More prescriptive tone

**Chosen**: Option B - Numbered required steps with Bash tool invocations

**Rationale**: The word "Example" implies the automation is optional. Changing to numbered steps (1. Call the script, 2. Verify success, 3. Continue) makes it clear these are required actions, not suggestions.

### Decision 4: Scope of Changes

**Options considered:**
- Option A: Minimal changes - just strengthen a few directives
  - Pros: Less change risk
  - Cons: May still be insufficient

- Option B: Comprehensive enhancement - checkpoints, summary section, verification steps
  - Pros: Multiple reinforcement points, hard to miss
  - Cons: More extensive changes to review

**Chosen**: Option B - Comprehensive enhancement

**Rationale**: If we're going to fix this, let's fix it properly. Adding:
- Checkpoint markers at automation points
- Verification steps in phase completion
- Automation reminder at phase start
- Summary section in Important Guidelines

This creates multiple touchpoints that reinforce the automation requirements.

## Open Questions (During Research)

- [x] **Are the automation scripts implemented?** - Resolved: Yes, all three scripts exist and work correctly
- [x] **Do the scripts have bugs?** - Resolved: No, scripts are well-implemented with proper error handling
- [x] **Does SKILL.md specify automation?** - Resolved: Yes, but emphasis could be stronger
- [x] **What format should enhanced directives take?** - Resolved: Checkpoint markers + numbered steps + verification
- [x] **Should we modify the scripts?** - Resolved: No, scripts work fine - this is a documentation issue
- [x] **Is this issue about missing features or enforcement?** - Resolved: Enforcement - features exist but aren't being used consistently

**Note**: All questions resolved before finalizing the plan.

## Code Snippets Reference

### Relevant Existing Code:

```python
# From .claude/skills/iw-executor/scripts/update_task.py:23-62
# This shows the task update mechanism works correctly
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

```python
# From .claude/skills/iw-executor/scripts/update_context.py:53-88
# This shows context updates work correctly
def add_to_section(
    content: str,
    section_name: str,
    new_content: str,
    add_timestamp: bool = True
) -> str:
    """Add content to a section in the markdown file."""
    lines = content.split("\n")
    start_line, end_line = find_section(content, section_name)

    # Prepare the content to add
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if add_timestamp:
        content_to_add = f"- [{timestamp}] {new_content}"
    else:
        content_to_add = f"- {new_content}"

    if start_line == -1:
        # Section doesn't exist, create it at the end
        if not content.endswith("\n\n"):
            lines.append("")
        lines.append(f"## {section_name}")
        lines.append("")
        lines.append(content_to_add)
        lines.append("")
    else:
        # Section exists, add to end of section
        insert_position = end_line
        lines.insert(insert_position, content_to_add)

    return "\n".join(lines)
```

```python
# From .claude/skills/iw-git-workflow/scripts/create_phase_commit.py:91-117
# This shows phase commits work correctly
def create_commit_message(
    phase_number: int,
    phase_info: dict,
    plan_path: Path,
    issue_number: int | None
) -> str:
    """Generate commit message for phase."""
    phase_name = phase_info["phase_name"]
    phase_desc = phase_info["phase_description"]

    message_parts = [
        f"Phase {phase_number}: {phase_name}",
        ""
    ]

    if phase_desc:
        message_parts.append(phase_desc)
        message_parts.append("")

    # Add plan reference
    message_parts.append(f"Plan: {plan_path}")

    # Add issue reference if available
    if issue_number:
        message_parts.append(f"Issue: #{issue_number}")

    return "\n".join(message_parts)
```

### Current Automation Directive Format:

```markdown
# From .claude/skills/iw-executor/SKILL.md:195-207
# Current format uses "AUTOMATIC" but could be stronger

d. **Update Progress (AUTOMATIC - DO IMMEDIATELY):**
   - **IMMEDIATELY** after completing task, mark it done
   - Use `scripts/update_task.py` to check off the task in tasks.md
   - Example: `update_task.py tasks.md "Task description" --status done`
   - **DO NOT WAIT** for user to ask - this is automatic
   - This ensures progress is saved incrementally
```

This will be enhanced with:
- Checkpoint markers (⚠️)
- "REQUIRED" emphasis
- Numbered steps instead of "Example:"
- Explicit Bash tool invocation
- Verification step

## Corrections During Planning

None - no user corrections were needed. Research findings matched the issue description: automation isn't happening consistently because the directives aren't emphatic enough.
