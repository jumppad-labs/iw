# Issue #15 Implementation Plan: Two-Pass Planning System

**Created**: 2025-11-04
**Last Updated**: 2025-11-04

## Overview

Implement a two-pass planning approach in the iw-planner skill to improve planning speed and reduce token consumption for simple tasks. The system will support both fast plans (minimal research, single file) and detailed plans (full research, 4 files), with the ability to upgrade from fast to detailed while preserving user comments.

## Current State Analysis

### Current Implementation

The iw-planner skill currently uses a single comprehensive workflow that:
- Launches 14-17 parallel research agents in Step 1
- Reads all identified files completely into context
- Performs deep dive research with follow-up agents
- Generates 4 detailed files with extensive code examples
- Consumes significant tokens regardless of task complexity

**Key Code Locations:**
- `.claude/skills/iw-planner/SKILL.md:1-604` - Main skill workflow and documentation
- `.claude/commands/iw-plan.md:1-9` - Command entry point (simple invocation)
- `.claude/skills/iw-planner/scripts/init_plan.py:1-160` - Plan initialization script
- `.claude/skills/iw-planner/assets/plan-template.md` - Main plan template (139 lines)
- `.claude/skills/iw-planner/assets/research-template.md` - Research template (90 lines)
- `.claude/skills/iw-planner/assets/context-template.md` - Context template (53 lines)
- `.claude/skills/iw-planner/assets/tasks-template.md` - Tasks template (60 lines)

### Current Workflow (from SKILL.md:46-87):
```markdown
1. Check for GitHub Issue
2. Detect language and activate guidelines
3. Launch parallel research tasks (5-7 Task agents)
4. Parameters provided? Read files
5. After gathering context: Create TodoWrite, review findings, present
6. After alignment: Optional draft generation, create structure, generate 4 files
```

### Performance Bottlenecks Identified:
1. **Excessive agent spawning** for simple tasks (14-17 agents even for CSS color changes)
2. **Full file reads** regardless of complexity
3. **4-file generation** with extensive templates when simple guidance would suffice
4. **No early exit** option for straightforward tasks

## Desired End State

After implementation:

1. **Fast Plan Mode** (`/iw-plan <issue> --fast`):
   - Minimal research: GitHub issue + learnings + guidelines + quick file scan only
   - Single combined markdown file output (plan + tasks + minimal context)
   - Under 100 lines for simple tasks
   - Completes in ~30-40% of current time
   - User prompted to upgrade to detailed plan if needed

2. **Detailed Plan Mode** (`/iw-plan <issue> --detailed` or default behavior):
   - Full current workflow maintained
   - **NEW**: Reads existing fast plan first if present
   - Preserves user comments/edits from fast plan
   - Incorporates fast plan findings into detailed research
   - Generates standard 4-file output

3. **Seamless Upgrade Path**:
   - User reviews fast plan, adds comments/questions
   - Runs `/iw-plan <issue> --detailed`
   - System reads fast plan, preserves edits, expands to full plan

**Verification Method**:
- Fast plan for simple task completes in <2 minutes with <100 lines output
- Detailed plan preserves all user edits from fast plan
- Both modes inspect CLAUDE.md and .docs/knowledge for guidelines

## What We're NOT Doing

- NOT replacing the detailed planning workflow (it remains the default)
- NOT creating a third "medium" plan option (only fast/detailed)
- NOT auto-detecting complexity (user explicitly chooses mode)
- NOT modifying the executor or other workflow skills
- NOT changing the 4-file structure for detailed plans
- NOT implementing AI-based complexity detection
- NOT adding configuration files (flags only)

## Implementation Approach

**Strategy**: Mode-based workflow with conditional branching and upgrade path.

**Key Decisions**:
1. **Mode Selection**: Parse `--fast` or `--detailed` flag from command args
2. **Fast Mode**: New workflow branch with minimal research and single-file template
3. **Detailed Mode**: Enhanced existing workflow to read fast plans
4. **Upgrade Path**: Detailed mode detects and reads fast plan, extracts user content
5. **Template Strategy**: New fast-plan-template.md for single-file output
6. **Script Enhancement**: Update init_plan.py to support fast mode flag

**Rationale**: Mode-based approach provides clear separation, easier maintenance, and explicit user control. Progressive enhancement considered but rejected due to state management complexity.

---

## Phase 1: Add Fast Plan Mode Infrastructure

### Overview
Create the infrastructure for fast planning mode including template, script updates, and command parsing. This phase establishes the foundation without modifying the main skill workflow logic.

### Changes Required:

#### 1. Command Entry Point - Add Flag Parsing
**File**: `.claude/commands/iw-plan.md:1-9`

**Current code:**
```markdown
---
name: iw-plan
description: Create detailed implementation plan with code snippets and clean separation
paramDescription: Describe what you need planned (e.g., "refactor auth", "add feature X") or provide ticket file path
---

Use the iw-planner skill to create a detailed implementation plan.

{{ARGS}}
```

**Proposed changes:**
```markdown
---
name: iw-plan
description: Create implementation plan (use --fast for quick plans, --detailed for comprehensive plans)
paramDescription: Describe what you need planned or provide issue number. Optional flags: --fast (quick plan), --detailed (comprehensive plan, default)
---

Use the iw-planner skill to create an implementation plan.

Arguments: {{ARGS}}

Note:
- Use --fast for simple tasks requiring minimal research (~100 lines, single file)
- Use --detailed (or omit) for complex tasks requiring comprehensive research (full 4-file plan)
- If you create a fast plan first, you can upgrade to detailed later by running the same command with --detailed
```

**Reasoning**: Command description needs to communicate the new flags to users. The paramDescription explains when to use each mode. Adding a note helps users understand the upgrade path.

#### 2. Fast Plan Template - Create Single-File Template
**File**: `.claude/skills/iw-planner/assets/fast-plan-template.md` (NEW FILE)

**Proposed content:**
```markdown
# {{TITLE}} - Quick Implementation Plan

**Created**: {{DATE}}
**Issue**: {{ISSUE_URL}}
**Mode**: Fast Plan (upgrade to detailed plan with /iw-plan {{ISSUE_NUMBER}} --detailed)

---

## Summary

{{SUMMARY}}

## Context

{{CONTEXT}}

## Implementation Steps

{{IMPLEMENTATION_STEPS}}

## Testing

{{TESTING}}

## Success Criteria

### Automated:
{{AUTOMATED_VERIFICATION}}

### Manual:
{{MANUAL_VERIFICATION}}

## Notes

{{NOTES}}

---

**Need more detail?** This is a quick plan focusing on the essentials. For comprehensive research, detailed code examples, and full test strategy, run:

```
/iw-plan {{ISSUE_NUMBER}} --detailed
```

Your comments and edits to this plan will be preserved when upgrading.
```

**Reasoning**: Single-file template keeps output concise for fast plans. Placeholder structure allows programmatic filling. Upgrade prompt guides users to detailed mode. Template is under 50 lines (vs 342 lines for 4-file templates combined).

#### 3. Plan Initialization Script - Add Fast Mode Support
**File**: `.claude/skills/iw-planner/scripts/init_plan.py:1-160`

**Current relevant code (lines 1-30, simplified):**
```python
#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Initialize implementation plan structure')
    parser.add_argument('name', help='Plan name or issue number')
    parser.add_argument('--type', choices=['issue', 'adhoc'], required=True)
    args = parser.parse_args()

    # Determine base directory
    if args.type == 'issue':
        plan_dir = Path(f'.docs/issues/{args.name}')
    else:
        plan_dir = Path(f'.docs/adhoc/{args.name}')

    # Create plan directory
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Create 4 template files
    create_plan_file(plan_dir, args.name, args.type)
    create_research_file(plan_dir, args.name, args.type)
    create_context_file(plan_dir, args.name, args.type)
    create_tasks_file(plan_dir, args.name, args.type)
```

**Proposed changes:**
```python
#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Initialize implementation plan structure')
    parser.add_argument('name', help='Plan name or issue number')
    parser.add_argument('--type', choices=['issue', 'adhoc'], required=True)
    parser.add_argument('--mode', choices=['fast', 'detailed'], default='detailed',
                        help='Plan mode: fast (single file) or detailed (4 files)')
    args = parser.parse_args()

    # Determine base directory
    if args.type == 'issue':
        plan_dir = Path(f'.docs/issues/{args.name}')
    else:
        plan_dir = Path(f'.docs/adhoc/{args.name}')

    # Create plan directory
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Create files based on mode
    if args.mode == 'fast':
        create_fast_plan_file(plan_dir, args.name, args.type)
        print(f"✅ Fast plan initialized successfully!")
        print(f"\nPlan file: {plan_dir}/{args.name}-fast-plan.md")
        print(f"\nTo upgrade to detailed plan: /iw-plan {args.name} --detailed")
    else:
        # Create 4 template files (existing logic)
        create_plan_file(plan_dir, args.name, args.type)
        create_research_file(plan_dir, args.name, args.type)
        create_context_file(plan_dir, args.name, args.type)
        create_tasks_file(plan_dir, args.name, args.type)
        print(f"✅ Detailed plan initialized successfully!")

def create_fast_plan_file(plan_dir, name, plan_type):
    """Create single fast plan file from template"""
    template_path = Path(__file__).parent.parent / 'assets' / 'fast-plan-template.md'
    output_path = plan_dir / f'{name}-fast-plan.md'

    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    content = template.replace('{{TITLE}}', f'Issue #{name}' if plan_type == 'issue' else name)
    content = content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d'))
    content = content.replace('{{ISSUE_URL}}', f'https://github.com/jumppad-labs/iw/issues/{name}' if plan_type == 'issue' else 'N/A')
    content = content.replace('{{ISSUE_NUMBER}}', str(name))
    content = content.replace('{{SUMMARY}}', '[Brief 1-2 sentence summary]')
    content = content.replace('{{CONTEXT}}', '[Key context and requirements from issue]')
    content = content.replace('{{IMPLEMENTATION_STEPS}}', '[Step-by-step implementation approach]')
    content = content.replace('{{TESTING}}', '[Test approach and key scenarios]')
    content = content.replace('{{AUTOMATED_VERIFICATION}}', '- [ ] Tests pass: `make test`\n- [ ] Build succeeds: `make build`')
    content = content.replace('{{MANUAL_VERIFICATION}}', '- [ ] [Manual verification step]')
    content = content.replace('{{NOTES}}', '[Additional notes or considerations]')

    with open(output_path, 'w') as f:
        f.write(content)
```

**Reasoning**: Adding `--mode` flag allows script to support both fast and detailed initialization. Fast mode creates single file with fast-plan template. Mode flag is separate from type flag (issue/adhoc) for orthogonal concerns. Script reports appropriate message and upgrade command.

### Testing for This Phase:

**Write tests FIRST** before implementing changes:

1. **Test command parsing** - Verify flags are parsed correctly
2. **Test fast template creation** - Verify init_plan.py creates single file
3. **Test template content** - Verify placeholders are replaced correctly
4. **Test upgrade message** - Verify output includes upgrade instructions

### Success Criteria:

#### Automated Verification:
- [ ] Script creates fast plan file: `python3 .claude/skills/iw-planner/scripts/init_plan.py 99 --type issue --mode fast`
- [ ] Fast template file exists: `test -f .claude/skills/iw-planner/assets/fast-plan-template.md`
- [ ] Command file updated: `grep -q "fast" .claude/commands/iw-plan.md`

#### Manual Verification:
- [ ] Fast plan file is created in correct location (.docs/issues/99/99-fast-plan.md)
- [ ] Template placeholders are properly replaced with test values
- [ ] Upgrade message appears in script output
- [ ] Command description accurately explains fast vs detailed modes

---

## Phase 2: Implement Fast Planning Workflow

### Overview
Add the fast planning workflow to the iw-planner skill. This creates a new conditional branch that executes minimal research and generates a single-file plan for simple tasks.

### Changes Required:

#### 1. Skill Workflow - Add Mode Detection and Fast Path
**File**: `.claude/skills/iw-planner/SKILL.md:46-87`

**Current workflow section:**
```markdown
## Workflow Decision Tree

Start by determining what information is available and launching agents immediately:

1. **Check for GitHub Issue:**
   - If issue number provided → Launch `iw-github-issue-reader` agent immediately (don't wait!)
   - If no issue exists → Prompt user to create one for history tracking
   - If user wants ad-hoc plan → Proceed with ad-hoc workflow

2. **Detect language and activate guidelines:**
   ...
```

**Proposed changes (insert new step 0):**
```markdown
## Workflow Decision Tree

Start by determining planning mode and what information is available:

0. **Detect Planning Mode:**
   - Parse command arguments for `--fast` or `--detailed` flags
   - If `--fast` → Execute Fast Planning Workflow (see below)
   - If `--detailed` or no flag → Execute Detailed Planning Workflow (existing)
   - Default behavior: Detailed mode (maintain backward compatibility)

### Fast Planning Workflow

Execute this workflow when `--fast` flag is provided:

1. **Create Task Tracking:**
   - Create TodoWrite list for fast planning process (4-5 tasks max)

2. **Launch Minimal Research** (4 agents only, run in parallel):
   - **GitHub Issue Reader** (Skill tool - if issue-based): Fetch issue details
   - **Past Learnings Search** (Skill tool): Search for relevant corrections
   - **Guidelines Check** (Read tool): Read CLAUDE.md and activate language guidelines
   - **Quick File Scan** (Task tool - Explore subagent, "quick" thoroughness):
     - Prompt: "Quickly identify the 3-5 most relevant files for [task]. Return file paths only with one-line descriptions. Do not read file contents."

3. **Present Fast Plan Outline:**
   - Summarize findings from 4 agents
   - Present quick outline: Summary, Key Files, Implementation Steps, Testing
   - Ask: "Does this outline look correct, or should I run detailed planning?"
   - If user requests detailed → Switch to detailed workflow
   - If user approves → Continue to generation

4. **Generate Fast Plan:**
   - Invoke iw-init skill to ensure .docs structure
   - Run: `scripts/init_plan.py <issue-number> --type issue --mode fast`
   - Customize the single fast-plan file with research findings
   - Keep output under 100 lines for simple tasks
   - Include upgrade prompt at bottom

5. **Present Fast Plan with Upgrade Option:**
   - Display file location
   - Remind user they can upgrade with `/iw-plan <issue> --detailed`
   - Explain that user edits will be preserved during upgrade

### Detailed Planning Workflow (Enhanced)

Execute this workflow when `--detailed` flag is provided or no flag specified:

1. **Check for Existing Fast Plan:**
   - Look for `<issue-number>-fast-plan.md` or `<name>-fast-plan.md` in plan directory
   - If found, read it completely using Read tool
   - Extract user comments, edits, and questions
   - Document in research.md: "User edits from fast plan: [list]"
   - Use fast plan findings as initial context

2. **Check for GitHub Issue:**
   - If issue number provided → Launch `iw-github-issue-reader` agent immediately
   - (Existing logic continues...)

[Rest of existing detailed workflow remains unchanged: Steps 2-6 from current SKILL.md]
```

**Reasoning**: Adding step 0 creates clear branching point. Fast workflow is self-contained with only 4 agents vs 14-17 in detailed. Detailed workflow enhancement reads fast plans to preserve user input. Both modes maintain quality by requiring CLAUDE.md and guidelines checks.

#### 2. Fast Plan Generation Logic
**File**: `.claude/skills/iw-planner/SKILL.md` (new section after line 358)

**Add new section:**
```markdown
## Fast Plan Generation (Step 4 of Fast Workflow)

After minimal research and user approval of outline:

### Customize Fast Plan File

After running init_plan.py in fast mode, customize the single file:

**File**: `.docs/issues/<issue-number>/<issue-number>-fast-plan.md` or `.docs/adhoc/<name>/<name>-fast-plan.md`

Fill in these sections concisely:

1. **Summary** (2-3 sentences):
   - What is being implemented
   - Why it's needed
   - Expected outcome

2. **Context** (3-5 bullet points):
   - Key information from GitHub issue
   - Relevant past learnings found
   - Main files identified by quick scan
   - Key guidelines from CLAUDE.md

3. **Implementation Steps** (numbered list, 3-8 steps):
   - High-level steps to implement
   - File references with line numbers from quick scan
   - Brief rationale for each step
   - No detailed code examples (defer to detailed plan)

4. **Testing** (brief, 3-5 lines):
   - Key test scenarios to verify
   - Test commands to run
   - No detailed test code (defer to detailed plan)

5. **Success Criteria**:
   - **Automated**: 2-3 verification commands
   - **Manual**: 2-3 manual checks

6. **Notes**:
   - Any open questions for user
   - Caveats or assumptions made
   - Suggestions for detailed planning if complexity increases

**Keep total output under 100 lines for simple tasks.**

Example fast plan for "Change button color from blue to green":

```markdown
# Issue #42 - Quick Implementation Plan

**Created**: 2025-11-04
**Issue**: https://github.com/owner/repo/issues/42
**Mode**: Fast Plan

---

## Summary

Change the primary button color from blue to green across the application. This is a simple CSS update affecting the button component styling.

## Context

- Issue requests green (#28a745) instead of current blue (#007bff)
- Main file: `src/components/Button.css:15-20`
- Past learning: Always check both light and dark theme variables
- Guideline: Follow existing CSS variable naming conventions

## Implementation Steps

1. Update primary button color variable in `src/components/Button.css:15`
   - Change `--btn-primary: #007bff` to `--btn-primary: #28a745`

2. Update hover state color in `src/components/Button.css:18`
   - Change `--btn-primary-hover: #0056b3` to `--btn-primary-hover: #218838`

3. Check dark theme variables in `src/styles/dark-theme.css:45`
   - Verify primary button color is consistent

4. Verify contrast ratios meet accessibility guidelines
   - Use browser DevTools accessibility checker

## Testing

- Visual check: Verify buttons appear green in light and dark themes
- Run: `npm run test-visual-regression`
- Manual: Test hover states, focus states, disabled states

## Success Criteria

### Automated:
- [ ] Visual regression tests pass: `npm run test-visual-regression`
- [ ] Build succeeds: `npm run build`

### Manual:
- [ ] Buttons appear green in both themes
- [ ] Hover/focus states work correctly
- [ ] Contrast ratios are acceptable (WCAG AA)

## Notes

This is a straightforward change. If additional button variants need color updates, consider running detailed planning to map all affected components.

---

**Need more detail?** Run: `/iw-plan 42 --detailed`
```

This example is ~75 lines - appropriate for simple task. Complex tasks would naturally be longer but still under 100 lines in most cases.
```

**Reasoning**: Concrete guidelines for fast plan generation prevent scope creep. Example demonstrates appropriate level of detail for simple tasks. Emphasizes conciseness while maintaining essential quality checks (guidelines, learnings, testing).

### Testing for This Phase:

1. **Write tests for mode detection** - Verify --fast flag triggers fast workflow
2. **Test minimal research execution** - Verify only 4 agents launch in fast mode
3. **Test fast plan generation** - Verify single file is created with <100 lines for simple task
4. **Test upgrade prompt** - Verify prompt is included in output

### Success Criteria:

#### Automated Verification:
- [ ] Fast workflow executes with --fast flag
- [ ] Exactly 4 research tasks launch (verify in logs)
- [ ] Single fast-plan file generated
- [ ] File size under 100 lines for simple test case: `wc -l .docs/issues/test/test-fast-plan.md`

#### Manual Verification:
- [ ] Fast plan completes in under 2 minutes for simple task
- [ ] Output is concise and focused on essentials
- [ ] Upgrade prompt is clear and actionable
- [ ] Guidelines and learnings are checked even in fast mode
- [ ] Quality is maintained (not just faster, but appropriate)

---

## Phase 3: Implement Upgrade Path (Detailed Mode Enhancement)

### Overview
Enhance the detailed planning workflow to detect and read existing fast plans. This allows users to start with a fast plan, add comments/questions, then upgrade to a detailed plan while preserving their input.

### Changes Required:

#### 1. Fast Plan Detection and Reading
**File**: `.claude/skills/iw-planner/SKILL.md` (enhance detailed workflow section, around line 110)

**Insert before "Check for GitHub Issue Number" in detailed workflow:**

```markdown
### Detailed Planning Workflow (Enhanced)

**Step 0: Check for Existing Fast Plan**

Before starting detailed research, check if a fast plan exists:

1. **Detect Fast Plan File:**
```bash
# For issue-based plans:
test -f .docs/issues/<issue-number>/<issue-number>-fast-plan.md

# For ad-hoc plans:
test -f .docs/adhoc/<plan-name>/<plan-name>-fast-plan.md
```

2. **Read Fast Plan if Exists:**
   - Use Read tool to read complete fast plan file
   - Parse sections: Summary, Context, Implementation Steps, Notes
   - Extract user-added content:
     - User comments (look for markdown comments <!-- ... --> or inline notes)
     - User edits (compare to template structure, identify additions)
     - User questions (look for "?" or "TODO:" markers)
     - Highlighted concerns (look for bold, italics, or emphasis)

3. **Document Fast Plan Findings:**
   - Create TodoWrite item: "Incorporate fast plan findings into detailed plan"
   - In research.md, add section: "Fast Plan Review"
     ```markdown
     ## Fast Plan Review

     User created fast plan on [date]. Key points from fast plan:

     ### User Edits and Comments:
     - [List user additions not in template]
     - [List user questions or concerns]

     ### Fast Plan Findings to Preserve:
     - [Key context from fast plan]
     - [Implementation insights from fast plan]

     ### Questions from Fast Plan to Address:
     - [x] Question 1 - Resolved: [answer in detailed plan]
     - [x] Question 2 - Resolved: [answer in detailed plan]
     ```

4. **Use Fast Plan as Initial Context:**
   - When launching research agents, include fast plan summary in prompts
   - Example: "Previous fast plan identified files X, Y, Z. Expand this research to find..."
   - Avoid re-researching what fast plan already covered well
   - Focus detailed research on areas fast plan lacked depth

**Step 1: Check for GitHub Issue Number**

[Existing detailed workflow continues from here...]
```

**Reasoning**: Reading fast plans first ensures user input is captured before detailed research begins. Parsing for user edits (not just template content) preserves their contribution. Documenting in research.md maintains separation of concerns. Using fast plan as context makes detailed research more efficient (build on existing findings, don't duplicate).

#### 2. Fast Plan Content Extraction Logic
**File**: `.claude/skills/iw-planner/SKILL.md` (add new subsection)

**Add after fast plan detection section:**

```markdown
### Extracting User Content from Fast Plans

When a fast plan exists, distinguish between template content and user additions:

**Template Indicators** (ignore these):
- Placeholder text: "[Brief 1-2 sentence summary]", "[Key context]"
- Sections with no content beyond headers
- Exact template phrasing

**User Content Indicators** (preserve these):
- Specific file paths, function names, line numbers
- Technical details or code snippets
- Questions marked with "?" or "TODO:"
- Markdown comments: `<!-- user note -->`
- Bold/italic emphasis added by user
- Content that doesn't match template structure
- Additional sections not in template

**Parsing Strategy:**

1. **Read entire fast plan** into context
2. **Section-by-section analysis:**
   ```python
   # Pseudocode for parsing logic
   fast_plan_content = read_file(fast_plan_path)

   # Extract Summary section
   summary = extract_section(fast_plan_content, "## Summary")
   if not is_placeholder(summary):
       user_summary = summary

   # Extract Notes section (most likely to have user additions)
   notes = extract_section(fast_plan_content, "## Notes")
   user_notes = parse_user_additions(notes)

   # Extract questions (scan for "?" patterns)
   questions = find_questions(fast_plan_content)
   ```

3. **Preserve in detailed plan:**
   - User questions → Research.md "Questions from Fast Plan" section
   - User insights → Context.md "Background from Fast Plan"
   - User concerns → Plan.md relevant phase sections

**Example:**

Fast plan Notes section:
```markdown
## Notes

<!-- User is concerned about database migration -->
Need to verify this won't break existing API consumers. The /api/users endpoint currently returns field names in snake_case, but if we change to camelCase, existing clients might break.

TODO: Check if we have versioning strategy for API changes.
```

Extracted user content:
- Concern: API breaking change (snake_case → camelCase)
- Question: Versioning strategy for API changes
- Context: /api/users endpoint affected

Preserved in detailed plan research.md:
```markdown
## Fast Plan Review

### User Concerns from Fast Plan:
- User identified potential breaking change: /api/users endpoint field name format
- Concern about existing API consumers expecting snake_case
- Question raised: Do we have API versioning strategy?

### Resolution:
Detailed research will investigate:
1. Current API versioning approach (search codebase for API version patterns)
2. Impact analysis on /api/users consumers
3. Migration strategy options (versioned endpoint vs feature flag)
```

**Reasoning**: Clear criteria for distinguishing template vs user content prevents losing valuable input. Preservation strategy ensures user contributions appear in appropriate sections of detailed plan. Example demonstrates realistic scenario where fast plan user identifies a concern that detailed planning must address.

### Testing for This Phase:

1. **Test fast plan detection** - Verify detailed mode detects existing fast plan
2. **Test content extraction** - Create fast plan with user comments, verify they're extracted
3. **Test preservation in detailed plan** - Verify user content appears in appropriate sections
4. **Test upgrade workflow** - Full end-to-end: fast plan → user edits → detailed plan

### Success Criteria:

#### Automated Verification:
- [ ] Fast plan detected: Run detailed mode after fast mode, verify detection
- [ ] Read tool called for fast plan: Check logs for Read invocation
- [ ] Research.md contains "Fast Plan Review" section

#### Manual Verification:
- [ ] User comments from fast plan appear in detailed plan research.md
- [ ] User questions from fast plan are addressed in detailed plan
- [ ] Fast plan findings influence detailed research scope
- [ ] No duplicate research between fast and detailed phases
- [ ] Upgrade path feels seamless (user doesn't repeat themselves)

---

## Phase 4: Testing, Documentation, and Refinement

### Overview
Comprehensive testing of both fast and detailed modes, edge case handling, documentation updates, and measurement of token savings to verify the feature achieves its goals.

### Changes Required:

#### 1. Update Skill Documentation - User Guide Section
**File**: `.claude/skills/iw-planner/SKILL.md:26-44`

**Current Quick Start section:**
```markdown
## Quick Start

The planner automatically ensures the `.docs/` structure exists by invoking the `iw-init` skill, then creates the specific plan directory.

**For GitHub issue-based plans (recommended):**
```bash
scripts/init_plan.py <issue-number> --type issue
```
Example: `scripts/init_plan.py 123 --type issue`

**For ad-hoc plans:**
```bash
scripts/init_plan.py <plan-name> --type adhoc
```
Example: `scripts/init_plan.py refactor-auth --type adhoc`
```

**Updated Quick Start section:**
```markdown
## Quick Start

The planner supports two modes: **fast** (quick plans for simple tasks) and **detailed** (comprehensive plans for complex tasks).

### Fast Planning (New!)

Use for simple tasks requiring minimal research:

```bash
/iw-plan <issue-number> --fast
```

**When to use:**
- CSS/styling changes
- Simple configuration updates
- Straightforward bug fixes
- Clear, well-defined tasks
- Tasks you estimate at < 2 hours

**Output:**
- Single combined markdown file (~50-100 lines)
- Minimal research (4 agents: issue + learnings + guidelines + quick file scan)
- Completes in ~30-40% of detailed planning time
- Includes upgrade prompt if more detail needed

**Example:**
```bash
/iw-plan 42 --fast  # Create fast plan for issue #42
# Review plan, add comments/questions
/iw-plan 42 --detailed  # Upgrade to detailed plan (preserves your edits)
```

### Detailed Planning (Default)

Use for complex tasks requiring comprehensive research:

```bash
/iw-plan <issue-number> --detailed
# or simply:
/iw-plan <issue-number>  # --detailed is default
```

**When to use:**
- Multi-phase features
- Architectural changes
- Complex integrations
- Tasks requiring extensive research
- Tasks with unclear requirements

**Output:**
- Four separate files: plan.md, research.md, context.md, tasks.md
- Comprehensive research (14-17 agents for thorough codebase analysis)
- Detailed code examples and test strategies
- If fast plan exists, reads it first and preserves user edits

### Upgrade Path

1. **Start fast:** `/iw-plan 123 --fast`
2. **Review and edit:** Add comments, questions, concerns to fast plan
3. **Upgrade:** `/iw-plan 123 --detailed`
4. **Result:** Detailed plan incorporates your fast plan edits

Your comments and questions from the fast plan will appear in the detailed plan's research.md file and inform the comprehensive research.

### Direct Initialization (Advanced)

For script-based workflows, use init_plan.py directly:

**Fast plan:**
```bash
scripts/init_plan.py <issue-number> --type issue --mode fast
```

**Detailed plan:**
```bash
scripts/init_plan.py <issue-number> --type issue --mode detailed
```
```

**Reasoning**: Updated documentation explains when to use each mode, provides clear examples, and documents the upgrade workflow. Examples show realistic usage patterns. Guidelines help users choose appropriate mode for their task.

#### 2. Add Edge Case Handling
**File**: `.claude/skills/iw-planner/SKILL.md` (add new section)

**Add new section before "Resources":**

```markdown
## Edge Cases and Error Handling

### Fast Plan Already Exists

If user runs `/iw-plan <issue> --fast` but fast plan already exists:

1. **Detect existing fast plan** (check file exists)
2. **Ask user:**
   ```
   A fast plan already exists for this issue:
   .docs/issues/<issue>/<issue>-fast-plan.md

   Options:
   1. View existing fast plan
   2. Regenerate fast plan (overwrites current)
   3. Upgrade to detailed plan

   What would you like to do?
   ```
3. **Handle response:**
   - View: Read and display existing plan
   - Regenerate: Warn about overwriting, confirm, then regenerate
   - Upgrade: Switch to detailed mode workflow

### Detailed Plan Already Exists

If user runs `/iw-plan <issue> --detailed` but detailed plan (4 files) already exists:

1. **Detect existing detailed plan** (check if all 4 files exist)
2. **Ask user:**
   ```
   A detailed plan already exists for this issue:
   .docs/issues/<issue>/

   Options:
   1. View existing plan
   2. Update existing plan (re-research and merge)
   3. Start fresh (archive current plan)

   What would you like to do?
   ```
3. **Handle response based on user choice**

### No Issue Number Provided

If user runs `/iw-plan --fast` without issue number or description:

1. **Prompt for information:**
   ```
   Please provide either:
   - An issue number: /iw-plan 123 --fast
   - A task description: /iw-plan "add user authentication" --fast
   ```

### Conflicting Flags

If user runs `/iw-plan <issue> --fast --detailed`:

1. **Detect conflict**
2. **Prefer detailed mode** (more comprehensive is safer)
3. **Notify user:**
   ```
   Both --fast and --detailed flags provided. Using --detailed mode (comprehensive planning).
   ```

### Fast Plan Upgrade with No User Edits

If fast plan exists but user made no edits (still all placeholder text):

1. **Detect during detailed mode** (check if content matches template exactly)
2. **Notify user:**
   ```
   Fast plan exists but appears unchanged. Proceeding with detailed planning.
   This will generate the full 4-file plan structure.
   ```
3. **Continue with detailed planning** (no special preservation needed)

### Empty or Corrupted Fast Plan

If fast plan file exists but is empty or malformed:

1. **Attempt to read file**
2. **If read fails or file is empty:**
   ```
   Warning: Existing fast plan file is empty or unreadable.
   Proceeding with fresh detailed planning.
   ```
3. **Log warning in research.md:**
   ```markdown
   ## Issues During Planning

   - Fast plan file existed but was empty/corrupted, ignored
   ```

**Reasoning**: Edge case handling prevents workflow failures and provides clear user guidance. Preferring detailed mode when flags conflict is safer. Detecting unchanged fast plans avoids unnecessary "preservation" logic. Error handling for corrupted files prevents crashes.

#### 3. Testing Scenarios
**File**: Create `.docs/issues/15/testing-scenarios.md` (NEW FILE)

**Content:**
```markdown
# Issue #15 Testing Scenarios

## Test Scenario 1: Fast Plan for Simple Task

**Task**: Change button color (CSS update)

**Steps:**
1. Run: `/iw-plan 999 --fast` (using test issue)
2. Verify:
   - Only 4 agents launch (issue reader + learnings + guidelines + quick file scan)
   - Single file created: `.docs/issues/999/999-fast-plan.md`
   - File is under 100 lines
   - Upgrade prompt is included
   - Completes in under 2 minutes

**Expected Output:**
- Fast plan with sections: Summary, Context, Implementation Steps, Testing, Success Criteria, Notes
- Concise content focused on essentials
- File references from quick scan
- No detailed code examples

---

## Test Scenario 2: Fast Plan Upgrade Path

**Task**: Create fast plan, add user comments, upgrade to detailed

**Steps:**
1. Run: `/iw-plan 999 --fast`
2. Edit fast plan file, add:
   ```markdown
   ## Notes

   <!-- Concerned about backwards compatibility -->
   Will this break the mobile app? Check API contract.

   TODO: Verify deployment process for CSS changes.
   ```
3. Run: `/iw-plan 999 --detailed`
4. Verify:
   - Detailed mode detects existing fast plan
   - User comments extracted
   - Comments appear in research.md "Fast Plan Review" section
   - Questions addressed in detailed plan
   - 4-file structure created

**Expected Output:**
- Detailed plan preserves user concerns
- Research.md contains: "User identified concern about mobile app API contract"
- Plan addresses backwards compatibility question

---

## Test Scenario 3: Detailed Plan from Scratch

**Task**: Complex feature requiring architectural decisions

**Steps:**
1. Run: `/iw-plan 888 --detailed` (no fast plan exists)
2. Verify:
   - Full research workflow executes (14-17 agents)
   - No fast plan detection attempted
   - 4-file structure created with comprehensive detail
   - Takes appropriate time for complexity

**Expected Output:**
- Detailed plan with all sections filled comprehensively
- Code examples with file:line references
- Multiple design options presented
- Test strategy detailed

---

## Test Scenario 4: Token Consumption Measurement

**Task**: Compare fast vs detailed token usage

**Measurement Points:**
1. Run fast plan for simple task (CSS change):
   - Record: agent count, file reads, token count (if available), duration
2. Run detailed plan for same task:
   - Record: agent count, file reads, token count (if available), duration
3. Calculate savings:
   - Agent reduction: (detailed_agents - fast_agents) / detailed_agents * 100%
   - Time savings: (detailed_time - fast_time) / detailed_time * 100%

**Expected Results:**
- Fast plan: ~70% fewer agents (4 vs 14-17)
- Fast plan: ~60% time reduction
- Fast plan output: ~85% fewer lines (100 vs 342 template lines + expansion)

---

## Test Scenario 5: Edge Case - Both Flags Provided

**Task**: Test conflict resolution

**Steps:**
1. Run: `/iw-plan 777 --fast --detailed`
2. Verify:
   - System detects conflict
   - Defaults to detailed mode
   - User is notified of choice

**Expected Output:**
```
Both --fast and --detailed flags provided. Using --detailed mode (comprehensive planning).
```

---

## Test Scenario 6: Edge Case - Fast Plan Already Exists

**Task**: Re-run fast planning

**Steps:**
1. Run: `/iw-plan 666 --fast` (creates plan)
2. Run: `/iw-plan 666 --fast` again (plan exists)
3. Verify:
   - System detects existing plan
   - User prompted with options (view, regenerate, upgrade)
   - User choice is respected

**Expected Output:**
```
A fast plan already exists for this issue.

Options:
1. View existing fast plan
2. Regenerate fast plan (overwrites current)
3. Upgrade to detailed plan

What would you like to do?
```

---

## Test Scenario 7: Guidelines Always Checked

**Task**: Verify both modes check CLAUDE.md and guidelines

**Steps:**
1. Create test project with CLAUDE.md containing specific conventions
2. Run fast plan: `/iw-plan test --fast`
3. Verify fast plan mentions conventions from CLAUDE.md
4. Run detailed plan: `/iw-plan test --detailed`
5. Verify detailed plan follows same conventions

**Expected Outcome:**
- Both modes reference CLAUDE.md
- Both modes activate appropriate language guidelines
- Quality maintained in both modes (not just speed difference)
```

**Reasoning**: Concrete test scenarios ensure all features work as designed. Scenarios cover happy path, upgrade path, edge cases, and quality verification. Token measurement validates the performance goals. Edge case tests prevent regressions.

### Testing for This Phase:

1. **Execute all 7 test scenarios** documented above
2. **Measure and document token savings** (fast vs detailed)
3. **Verify documentation accuracy** (examples work as written)
4. **Edge case validation** (all edge cases handled gracefully)

### Success Criteria:

#### Automated Verification:
- [ ] All test scenarios execute successfully
- [ ] Fast mode saves ≥60% time vs detailed for simple tasks
- [ ] Fast mode uses ≤30% tokens of detailed for simple tasks
- [ ] No regressions in existing detailed planning workflow
- [ ] Both modes check CLAUDE.md and guidelines

#### Manual Verification:
- [ ] Fast plans are appropriately concise (<100 lines for simple tasks)
- [ ] Detailed plans maintain current quality level
- [ ] Upgrade path preserves user edits accurately
- [ ] Documentation is clear and examples work
- [ ] Edge cases are handled gracefully with helpful messages
- [ ] User experience is smooth for both workflows

---

## Testing Strategy

### Unit Tests:
No traditional unit tests needed (skill-based workflow, not code library). Testing is scenario-based and manual.

### Integration Tests:
Execute all scenarios in testing-scenarios.md document sequentially:

```bash
# Test 1: Fast planning
/iw-plan 999 --fast

# Test 2: Upgrade path
# (edit fast plan manually)
/iw-plan 999 --detailed

# Test 3: Detailed from scratch
/iw-plan 888 --detailed

# Test 4: Token measurement
# (manual tracking during tests 1-3)

# Test 5: Conflict resolution
/iw-plan 777 --fast --detailed

# Test 6: Re-run detection
/iw-plan 666 --fast
/iw-plan 666 --fast  # second run

# Test 7: Guidelines check
# (verify CLAUDE.md referenced in both modes)
```

### Manual Testing Steps:
1. Create test issues in GitHub (or use test mode with fake issue numbers)
2. Execute each scenario from testing-scenarios.md
3. Verify outputs match expected results
4. Measure time and token consumption
5. Test upgrade workflow end-to-end with real user edits
6. Verify quality of fast plans (concise but complete)
7. Verify quality of detailed plans (comprehensive and thorough)

## Performance Considerations

### Fast Mode Performance Targets:
- **Agent count**: 4 agents (vs 14-17 in detailed)
- **Completion time**: <2 minutes for simple tasks (vs 5-8 minutes detailed)
- **Output size**: <100 lines for simple tasks (vs 300-500 lines detailed)
- **Token consumption**: ~30% of detailed mode for equivalent task

### Detailed Mode Performance:
- **No degradation**: Detailed mode performance should remain unchanged
- **Benefit from fast plans**: When upgrading, detailed mode skips redundant research
- **Preservation overhead**: Minimal (one additional Read operation for fast plan)

### Optimization Opportunities:
- Fast mode "quick" file scan uses haiku model for speed
- Fast mode skips Task agents for deep dive research
- Single file write vs 4-file write (minor I/O savings)
- Upgrade path reuses fast plan research (avoid duplication)

## Migration Notes

Not applicable - this is a new feature addition, not a migration.

**Backward Compatibility:**
- Existing `/iw-plan` commands work unchanged (default to detailed mode)
- Existing detailed plans unaffected
- No breaking changes to skill interface
- Optional flags enable new behavior only when requested

## References

- Original ticket: GitHub Issue #15
- Key files examined:
  - `.claude/skills/iw-planner/SKILL.md:1-604` - Main skill workflow
  - `.claude/commands/iw-plan.md:1-9` - Command entry point
  - `.claude/skills/iw-planner/scripts/init_plan.py:1-160` - Initialization script
  - `.claude/skills/iw-planner/assets/plan-template.md` - Detailed plan template
- Similar patterns found: N/A (new feature, no direct precedent)
- Past learnings: `.docs/knowledge/learnings/installation.md` - Preference for simple approaches
