# Issue #15 - Research & Working Notes

**Research Date**: 2025-11-04
**Researchers**: Claude + nicj

## Initial Understanding

Initially understood the task as: Add a two-pass planning system to iw-planner to improve speed and reduce token consumption. Issue #15 proposes:
1. Fast plan as first pass (minimal research, high-level)
2. User review with option to request detailed plan
3. Detailed plan as second pass (full current quality)
4. Both passes must check CLAUDE.md and guidelines
5. User should be able to request detailed plan directly

## Research Process

### Files Examined:

1. **`.claude/skills/iw-planner/SKILL.md` (lines 1-604)**
   - Finding: Current workflow launches 14-17 parallel research agents
   - Finding: 5-step comprehensive process (Context Gathering → Research & Discovery → Structure Dev → Plan Writing → Validation)
   - Finding: Agent-first strategy with extensive Task tool usage
   - Finding: Always activates language guidelines (go-dev-guidelines for Go projects)
   - Relevant pattern: Skill composition using Skill tool (iw-github-issue-reader, iw-learnings, iw-init)

2. **`.claude/commands/iw-plan.md` (lines 1-9)**
   - Finding: Simple command entry point with {{ARGS}} placeholder
   - Finding: Currently no flag parsing for modes
   - Entry point needs enhancement to communicate new flags

3. **`.claude/skills/iw-planner/scripts/init_plan.py` (lines 1-160)**
   - Finding: Python script creates 4-file structure from templates
   - Finding: Supports --type flag (issue vs adhoc)
   - Finding: No current support for planning modes
   - Pattern: Uses Path, argparse for file generation

4. **`.claude/skills/iw-planner/assets/` templates**
   - plan-template.md: 139 lines - comprehensive with code examples
   - research-template.md: 90 lines - captures discovery process
   - context-template.md: 53 lines - quick reference
   - tasks-template.md: 60 lines - actionable checklist
   - Total: 342 lines of template structure before content expansion

5. **`.docs/knowledge/learnings/installation.md`**
   - Learning: "Clone repo instead of 100 API requests" - preference for simple approaches
   - Impact: Simple approaches preferred over complex multi-step workflows
   - Relevant to: Designing fast mode to be straightforward, not over-engineered

### Sub-tasks Spawned:

1. **iw-github-issue-reader**: Fetch issue #15 details
   - Result: Retrieved complete issue description and requirements
   - Key discovery: User explicitly wants fast plans under 100 lines

2. **iw-learnings**: Search for relevant past learnings
   - Result: Found installation.md learning about simplicity
   - Key discovery: Project culture values simple solutions

3. **Explore Agent - iw-planner implementation**
   - Result: Identified all key files and structure
   - Key discovery: Skill uses markdown-based templates, not code generation

4. **Explore Agent - Template files**
   - Result: Mapped all 4 template files and their structure
   - Key discovery: Templates are well-organized with clear placeholder system

5. **Explore Agent - iw-init skill**
   - Result: Understood .docs directory initialization
   - Key discovery: Skills can invoke other skills for foundational setup

6. **Explore Agent - Skill composition patterns**
   - Result: Found examples of skills invoking other skills
   - Key discovery: Skill tool is used with command name only, no parameters

### Questions Asked & Answers:

1. Q: Which implementation approach - Mode-Based or Progressive Enhancement?
   A: Mode-Based (Option A) with modification: Detailed mode should read fast plan if it exists to preserve user comments
   Follow-up: Confirmed upgrade path is critical - user edits must be preserved

2. Q: What level of research for fast plans?
   A: GitHub issue + past learnings + guidelines check + quick file scan (all 4)
   Follow-up: Confirmed guidelines must always be checked for quality

3. Q: What output format for fast plans?
   A: Single file (not 4-file structure, not just plan+tasks)
   Follow-up: Confirmed single markdown file with combined sections

## Key Discoveries

### Technical Discoveries:
- Current iw-planner uses 14-17 agents:
  - 2 skill invocations (GitHub issue reader, learnings)
  - 5-7 Task agents (Explore and general-purpose subagents)
  - Follow-up agents for deep dive research
- Agent launch is parallel (single message with multiple tool calls)
- Templates use {{PLACEHOLDER}} syntax for programmatic filling
- Skills communicate through files, not through Skill tool parameters
- Language guidelines activation is mandatory in current workflow

### Patterns to Follow:
- **Skill composition**: `.claude/skills/iw-planner/SKILL.md:169-174` - Shows how to invoke iw-learnings
- **Skill composition**: `.claude/skills/iw-planner/SKILL.md:364-374` - Shows how to invoke iw-init
- **Agent launching**: `.claude/skills/iw-planner/SKILL.md:162-195` - Parallel Task tool invocations
- **Template system**: `.claude/skills/iw-planner/scripts/init_plan.py` - Python script with placeholder replacement

### Constraints Identified:
- Must maintain backward compatibility (existing /iw-plan commands must work)
- Detailed mode must remain the default (no breaking changes)
- Both modes must check CLAUDE.md and guidelines (quality requirement)
- Fast plans should be under 100 lines "in many cases" (not a hard limit)
- Upgrade path must preserve user edits (critical user requirement)

## Design Decisions

### Decision 1: Mode Selection Strategy
**Options considered:**
- Option A: Mode-based with flags (--fast, --detailed) - Clear separation, independent workflows
- Option B: Progressive enhancement (always start fast, upgrade if needed) - Single workflow, state management complexity
- Option C: Hybrid (auto-detect complexity, allow override) - Complex logic, unclear user control

**Chosen**: Option A (Mode-Based) with upgrade enhancement
**Rationale**:
- User explicitly chooses the mode (clear control)
- Easier to maintain two distinct workflows
- Detailed mode can read fast plans for upgrade path
- Progressive enhancement adds state management complexity without clear benefit
- Hybrid auto-detection could frustrate users ("why did it choose the wrong mode?")
- User feedback during planning session confirmed preference for explicit choice

### Decision 2: Fast Plan Research Scope
**Options considered:**
- Minimal: GitHub issue only (too minimal, no context)
- Medium: Issue + learnings + guidelines (good but missing file context)
- Extended: Issue + learnings + guidelines + quick file scan (comprehensive enough)
- Full-lite: All above + pattern discovery (approaching detailed complexity)

**Chosen**: Extended (4 agents)
**Rationale**:
- GitHub issue provides requirements
- Learnings prevent repeating mistakes (critical)
- Guidelines maintain quality (non-negotiable per issue requirements)
- Quick file scan provides concrete file context (user needs file references)
- Pattern discovery deferred to detailed mode (not essential for simple tasks)
- User confirmed all 4 components during planning session

### Decision 3: Fast Plan Output Format
**Options considered:**
- Single combined file (all sections in one markdown)
- Minimal 4-file (same structure, less detail)
- Plan + tasks only (skip research and context)

**Chosen**: Single combined file
**Rationale**:
- Simpler for user to review (one file vs four)
- Faster to generate (one write operation)
- Appropriate for simple tasks (doesn't warrant 4-file structure)
- User confirmed single file preference
- Can still include all essential sections (summary, context, steps, testing, criteria, notes)

### Decision 4: Upgrade Path Implementation
**Options considered:**
- No preservation (regenerate from scratch in detailed mode)
- Manual copy-paste (user transfers content manually)
- Automatic detection and extraction (read fast plan, parse user edits)

**Chosen**: Automatic detection and extraction
**Rationale**:
- User explicitly requested preservation of comments
- Manual copy-paste is error-prone and tedious
- Automatic extraction provides seamless upgrade experience
- Can distinguish template text from user additions
- Preserves user questions in research.md "Fast Plan Review" section

### Decision 5: Template Strategy
**Options considered:**
- Reuse existing templates with conditionals (one template, branching logic)
- Separate fast template (new file for fast plans)
- No template (generate programmatically)

**Chosen**: Separate fast template
**Rationale**:
- Clean separation of concerns
- Existing templates are optimized for detailed plans
- Fast template can be much simpler (~50 lines vs 342 lines)
- Follows existing pattern (one template per output style)
- Easier to maintain (no conditionals in templates)

### Decision 6: Script Enhancement Approach
**Options considered:**
- Separate script for fast plans (init_fast_plan.py)
- Add --mode flag to existing script (init_plan.py)
- Create wrapper script that calls appropriate sub-script

**Chosen**: Add --mode flag to existing script
**Rationale**:
- Minimal changes to existing workflow
- Follows existing pattern (--type flag for issue/adhoc)
- Orthogonal flags (--type and --mode are independent)
- Single entry point for all plan initialization
- Easier to discover (users know init_plan.py already)

## Open Questions (During Research)

- [x] Should fast mode be default or detailed? - Resolved: Detailed remains default for backward compatibility
- [x] How to parse flags from command args? - Resolved: {{ARGS}} placeholder in command file passes full arg string to skill
- [x] Can skills read their own command invocation args? - Resolved: Yes, through {{ARGS}} placeholder expansion
- [x] Should fast plans support ad-hoc or only issues? - Resolved: Both issue and ad-hoc (use --type as usual)
- [x] What happens if user runs --fast twice? - Resolved: Detect existing, prompt user (view/regenerate/upgrade)
- [x] Should detailed mode always check for fast plans? - Resolved: Yes, always check and read if exists
- [x] How to distinguish user edits from template text? - Resolved: Look for specific markers (comments, TODO:, ?, specific file paths)
- [x] Should fast plans generate tasks.md? - Resolved: No, single file includes brief tasks in "Implementation Steps" section

All questions resolved before finalizing plan.

## Code Snippets Reference

### Relevant Existing Code:

```markdown
# From .claude/skills/iw-planner/SKILL.md:164-174
**1. GitHub Issue Analysis** (if issue-based plan)
- Invoke `iw-github-issue-reader` skill using Skill tool
- Gathers: title, description, comments, linked PRs, labels, related issues
- Returns: Full context and discussion history

**2. Past Learnings Search** (Skill tool - `iw-learnings`)
- Invoke `iw-learnings` skill using Skill tool with keywords from issue/task
- Searches: `.docs/knowledge/learnings/` directory for relevant corrections and discoveries
- Returns: Relevant learnings, corrections, and decisions from previous work
- Purpose: Avoid repeating past mistakes, inform planning with institutional knowledge
```

```markdown
# From .claude/skills/iw-planner/SKILL.md:364-374
**FIRST: Invoke the `iw-init` skill to ensure base .docs structure exists:**

Use the Skill tool to invoke the `iw-init` skill. This ensures the `.docs/` directory structure is properly set up before creating plan files.

The init skill will:
- Create `.docs/issues/` and `.docs/adhoc/` directories if missing
- Create `.docs/knowledge/` structure if missing
- Create README files for documentation guidelines
- Report what was created

**This is idempotent** - safe to run even if structure already exists.
```

```python
# From .claude/skills/iw-planner/scripts/init_plan.py:120-140 (simplified)
def create_plan_file(plan_dir, name, plan_type):
    """Create main plan file from template"""
    template_path = Path(__file__).parent.parent / 'assets' / 'plan-template.md'
    output_path = plan_dir / f'{name}-plan.md'

    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    content = template.replace('{{TASK_NAME}}', f'Issue #{name}' if plan_type == 'issue' else name)
    content = content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d'))
    # ... more replacements

    with open(output_path, 'w') as f:
        f.write(content)
```

### Similar Patterns Found:

```markdown
# From .claude/commands/iw-plan.md (current simple structure)
---
name: iw-plan
description: Create detailed implementation plan with code snippets and clean separation
paramDescription: Describe what you need planned (e.g., "refactor auth", "add feature X") or provide ticket file path
---

Use the iw-planner skill to create a detailed implementation plan.

{{ARGS}}
```

This pattern shows command files are simple frontmatter + invocation text. We'll enhance with flag documentation.

```python
# From .claude/skills/iw-planner/scripts/init_plan.py:1-30 (pattern for argparse)
parser = argparse.ArgumentParser(description='Initialize implementation plan structure')
parser.add_argument('name', help='Plan name or issue number')
parser.add_argument('--type', choices=['issue', 'adhoc'], required=True)
```

This pattern shows how to add flag arguments. We'll add `--mode` following same pattern.

## Corrections During Planning

None - user provided clear guidance on approach during initial questioning. No corrections needed during research phase.

## Implementation Notes

**Critical Success Factors:**
1. **Preserve User Edits**: The upgrade path MUST accurately extract and preserve user comments/questions from fast plans
2. **Quality Maintenance**: Fast mode MUST check guidelines (cannot sacrifice quality for speed)
3. **Backward Compatibility**: Existing /iw-plan usage MUST work unchanged (detailed by default)
4. **Clear Communication**: Users must understand when to use each mode and how to upgrade

**Implementation Order Rationale:**
- Phase 1 (Infrastructure): Foundation must be solid before workflow changes
- Phase 2 (Fast Workflow): Fast mode can be tested independently
- Phase 3 (Upgrade Path): Requires both fast and detailed modes to exist
- Phase 4 (Testing/Docs): Comprehensive validation after all features exist

**Risk Mitigation:**
- Edge case handling prevents workflow failures
- Documentation includes concrete examples for clarity
- Testing scenarios cover happy path and edge cases
- Performance targets are measurable and specific
