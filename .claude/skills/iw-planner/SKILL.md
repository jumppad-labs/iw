---
name: iw-planner
description: Create implementation plans through an interactive process with research, code snippets, and structured deliverables. Supports two modes - fast (minimal research, single file, ~100 lines for simple tasks) and detailed (comprehensive research, 4 files for complex tasks). Use --fast for simple changes, --detailed for significant features. The skill guides through context gathering, research, design decisions, and generates plans with test strategies and success criteria.
---

# Implementation Planner

## Overview

Create detailed implementation plans through an interactive, iterative process. Be skeptical, thorough, and work collaboratively with the user to produce high-quality technical specifications with proper separation of working notes from deliverables.

**Language-Agnostic Approach:** This skill is language-agnostic and delegates to language-specific guidelines skills (e.g., `go-dev-guidelines` for Go projects) for all coding standards, testing patterns, naming conventions, and architectural decisions. Always detect the project language and activate the appropriate guidelines skill at the start of planning.

**Agent-First Strategy:** This skill uses the Task tool and Skill tool extensively to spawn parallel research agents for maximum efficiency:
- **GitHub Issue Analysis** - Invoke `iw-github-issue-reader` skill immediately when issue number provided
- **Past Learnings Search** - Invoke `iw-learnings` skill to find relevant corrections from previous work
- **Parallel Research** - Launch 5-7 Task agents concurrently (using `Explore` or `general-purpose` subagent types)
- **Verification** - Spawn Task agents to verify user corrections and validate findings
- **Optional Draft Generation** - For complex plans, spawn agent to generate initial structure
- **Optional Validation** - Spawn agent to cross-check plan accuracy before presenting

Task agents handle all information gathering, while the main context handles user interaction and decision-making.

**Note:** Use the built-in agent types (`Explore` for codebase searches, `general-purpose` for complex tasks) via the Task tool. No custom agent definitions needed.

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

**Note:** The `iw-init` skill is invoked automatically to ensure base documentation structure exists.

## Workflow Decision Tree

**🚨 CRITICAL RULE: When the user corrects you, IMMEDIATELY document the correction in research.md and `.docs/knowledge/learnings/` before doing anything else. See "Verify User Corrections" section for details. 🚨**

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
   - If issue number provided → Launch `iw-github-issue-reader` agent immediately (don't wait!)
   - If no issue exists → Prompt user to create one for history tracking
   - If user wants ad-hoc plan → Proceed with ad-hoc workflow

3. **Detect language and activate guidelines:**
   - Identify project language (Go, Python, TypeScript, etc.)
   - Activate appropriate guidelines skill (e.g., go-dev-guidelines)
   - Use throughout planning for coding patterns and architecture

4. **Launch parallel research tasks:**
   - While waiting for user input, launch multiple Skill and Task tool invocations concurrently:
     - Past learnings search (iw-learnings skill)
     - Codebase exploration (Explore subagent)
     - Pattern discovery (Explore subagent)
     - Testing strategy (Explore subagent)
     - Architecture analysis (general-purpose subagent)
     - Guidelines verification (Explore subagent)
   - Agents gather information in parallel for maximum efficiency

5. **Parameters provided** (file path, ticket reference)?
   - YES → Read files immediately after agents return results
   - NO → Request task description and context from user

6. **After gathering context:**
   - Create TodoWrite task list to track planning process
   - Review Task agent findings and read identified files
   - Present comprehensive findings with focused questions

7. **After alignment on approach:**
   - Optionally use Task tool to generate draft for complex plans
   - Create plan structure outline
   - Get feedback on structure
   - Generate the four structured files following language guidelines
   - Optionally use Task tool to validate accuracy before presenting

## Step 1: Context Gathering & Initial Analysis

### Activate Language-Specific Guidelines

**BEFORE STARTING**: Determine the project's primary language and activate the appropriate guidelines skill:

1. **Detect Project Language:**
   - Look at the codebase structure and file extensions
   - Check for language-specific files (go.mod, package.json, requirements.txt, etc.)
   - If unclear, ask the user

2. **Activate Guidelines Skill:**
   - **Go projects** → Use `go-dev-guidelines` skill for all coding standards, testing patterns, and architecture decisions
   - **Other languages** → Use appropriate language-specific guidelines if available
   - These skills provide the coding standards, testing patterns, and architectural patterns to follow

3. **Apply Throughout Planning:**
   - Reference the guidelines skill when making architectural decisions
   - Follow testing patterns from the guidelines (e.g., TDD with testify/require for Go)
   - Use naming conventions and project structure from guidelines
   - Include guidelines-compliant code examples in the plan

### Determine Plan Type and GitHub Issue

**NEXT**: Determine if this is an issue-based or ad-hoc plan:

1. **Check for GitHub Issue Number:**
   - Look for issue number in parameters (e.g., "123", "#123", "issue 123")
   - If found, launch **iw-github-issue-reader agent** immediately to gather comprehensive issue information
   - Plans for issues are stored in `.docs/issues/<issue-number>/`

2. **If No Issue Number Provided:**
   - Ask user: "Is this related to a GitHub issue? If so, please provide the issue number, or I can help you create one for tracking purposes."
   - **If user provides issue number**: Launch iw-github-issue-reader agent
   - **If user wants to create an issue**: Help create it first with `gh issue create`
   - **If user wants ad-hoc plan**: Proceed without issue, store in `.docs/adhoc/<plan-name>/`

3. **GitHub Issue Analysis:**
   - Invoke the `iw-github-issue-reader` skill using Skill tool to gather:
     - Issue title, description, and labels
     - All comments and discussion threads
     - Linked PRs and cross-references
     - Assignees and milestones
     - Related issues and context
   - Skill returns comprehensive analysis to main context
   - Don't wait for user confirmation - start codebase research immediately after skill completes

4. **Benefits of Issue-Based Plans:**
   - Provides history and tracking
   - Links plan to code changes and PRs
   - Enables team visibility and discussion
   - Recommended for all non-trivial features

### Check for Provided Parameters

When the skill is invoked:

- If a file path or ticket reference was provided, skip requesting information
- Immediately read any provided files FULLY using the Read tool
- Begin the research process without delay

### Read All Mentioned Files

**CRITICAL**: Read files completely in the main context:
- Use the Read tool WITHOUT limit/offset parameters
- DO NOT spawn sub-tasks before reading files in main context
- NEVER read files partially - if mentioned, read completely

### Create Task Tracking

Create a TodoWrite task list to track the planning process and ensure nothing is missed.

### Spawn Initial Research Tasks

Before asking the user questions, launch multiple Task tool invocations in parallel. Launch ALL these concurrently in a single message for maximum efficiency:

**1. GitHub Issue Analysis** (if issue-based plan)
- Invoke `iw-github-issue-reader` skill using Skill tool
- Gathers: title, description, comments, linked PRs, labels, related issues
- Returns: Full context and discussion history

**2. Past Learnings Search** (Skill tool - `iw-learnings`)
- Invoke `iw-learnings` skill using Skill tool with keywords from issue/task
- Searches: `.docs/knowledge/learnings/` directory for relevant corrections and discoveries
- Returns: Relevant learnings, corrections, and decisions from previous work
- Purpose: Avoid repeating past mistakes, inform planning with institutional knowledge

**3. Codebase Exploration** (Task tool - `Explore` subagent, medium thoroughness)
- Prompt: "Find all files related to [feature/task]. Identify relevant directories, modules, and entry points. Return file paths with brief descriptions of their purpose."
- Returns: Relevant file paths and structure

**4. Pattern Discovery** (Task tool - `Explore` subagent, medium thoroughness)
- Prompt: "Search for similar implementations to [feature/task] in the codebase. Identify patterns that should be followed, reusable utilities, and existing approaches. Return code examples with file:line references."
- Returns: Code patterns and examples

**5. Testing Strategy Research** (Task tool - `Explore` subagent, medium thoroughness)
- Prompt: "Research existing test patterns in this project. Find test utilities, fixtures, mocks, and integration test setup patterns. Map the testing infrastructure and conventions. Return examples with file:line references."
- Returns: Test patterns and infrastructure

**6. Architecture Analysis** (Task tool - `general-purpose` subagent)
- Prompt: "Analyze the architecture for [feature/task]. Trace data flow, map integration points and dependencies, identify shared interfaces and contracts. Find configuration and deployment patterns. Return detailed explanations with file:line references."
- Returns: Architecture overview and integration points

**7. Guidelines Verification** (Task tool - `Explore` subagent, quick thoroughness)
- Prompt: "Find examples of [language]-specific patterns currently used in the codebase. Identify coding standards, naming conventions, and architectural patterns being followed. Return code examples with file:line references."
- Returns: Existing code patterns

**IMPORTANT:** Launch all Task tool calls in a single message (parallel execution) for maximum efficiency.

### Read Research Results

After research tasks complete:
- Read ALL files identified as relevant
- Read them FULLY into the main context
- Ensure complete understanding before proceeding

### Present Informed Understanding

After research, present findings with specific questions:

```
Based on the ticket and research of the codebase, the task requires [accurate summary].

Found:
- [Current implementation detail with file:line reference]
- [Relevant pattern or constraint discovered]
- [Potential complexity or edge case identified]

Questions that research couldn't answer:
- [Specific technical question requiring human judgment]
- [Business logic clarification]
- [Design preference affecting implementation]
```

Only ask questions that cannot be answered through code investigation.

## Step 2: Research & Discovery

### Verify User Corrections

⚠️ **CRITICAL: DOCUMENT ALL CORRECTIONS IMMEDIATELY** ⚠️

When the user corrects any misunderstanding:

1. **Verify through code** - Don't just accept corrections, spawn Task agents to confirm
2. **Document immediately** - Before continuing, log the correction:
   - Full details in `research.md` ("Corrections During Planning" section)
   - Institutional learning in `.docs/knowledge/learnings/<topic>.md`

**See `.docs/knowledge/learnings/README.md` for complete documentation format.**

**⛔ DO NOT PROCEED WITHOUT DOCUMENTING ⛔**

### Update Task Tracking

Update TodoWrite list to track exploration tasks and Task agent launches.

### Spawn Follow-Up Research Tasks

Based on initial findings and user input, launch additional Task tool invocations in parallel:

**Deep Dive Research** (Task tool - as needed):
- **Dependency Impact** - "Map all affected systems and dependencies for [feature]. Find all integration points and impacted code. Return file:line references."
- **Migration Strategy** - "Research data migration patterns in the codebase. Find examples of previous migrations. Return patterns with file:line references."
- **Performance Analysis** - "Find performance-critical code paths related to [feature]. Identify bottlenecks and optimization patterns. Return file:line references."
- **Security Pattern** - "Identify security patterns currently used for [related feature]. Find authentication, authorization, and validation patterns. Return examples with file:line references."
- **Error Handling** - "Research existing error handling patterns in the codebase. Find how errors are created, wrapped, and handled. Return examples with file:line references."

For each Task agent:
- Use `Explore` subagent for codebase searches (specify thoroughness level)
- Use `general-purpose` subagent for complex analysis
- Each should return specific file:line references and code examples
- Launch all in a single message for parallel execution
- Wait for ALL to complete before proceeding

### Present Findings with Code Examples

```
Based on research, here's what was found:

**Current State:**
- In `<file-path>:<line-range>`, the [component] uses:
  ```<language>
  // existing code pattern
  // show actual code from codebase
  ```
- Pattern to follow: [describe existing pattern with code example]
- Related patterns found in [other files with line numbers]

**Design Options:**
1. [Option A with code sketch following language guidelines] - [pros/cons]
2. [Option B with code sketch following language guidelines] - [pros/cons]

**Open Questions:**
- [Technical uncertainty]
- [Design decision needed]

Which approach aligns best with your vision?
```

**Important:** All code examples must follow the patterns from the language-specific guidelines skill (e.g., go-dev-guidelines for Go projects).

### Using AskUserQuestion for Structured Input

When you need user decisions, use the **AskUserQuestion tool** to present options in the Claude Code UI:

```
Use AskUserQuestion tool with:
- questions: [
    {
      question: "Which approach should we use for authentication?",
      header: "Auth method",
      multiSelect: false,
      options: [
        {
          label: "JWT tokens",
          description: "Stateless authentication with JWT tokens stored in cookies"
        },
        {
          label: "Session-based",
          description: "Server-side sessions with Redis storage"
        },
        {
          label: "OAuth 2.0",
          description: "Third-party authentication via OAuth providers"
        }
      ]
    }
  ]
```

**When to use AskUserQuestion:**
- Choosing between design approaches (architecture decisions)
- Selecting which features to include/exclude
- Picking testing strategies or deployment approaches
- Any decision with 2-4 clear options

**When NOT to use:**
- Open-ended questions requiring detailed explanation
- Questions with more than 4 options (too cluttered)
- Questions where you need code examples in the options
- Technical clarifications better suited to text discussion

**Tips:**
- Set `multiSelect: true` when options aren't mutually exclusive
- Keep labels short (1-5 words) and descriptions clear
- Users can always select "Other" to provide custom input
- You can ask up to 4 questions at once

## Step 3: Plan Structure Development

Once aligned on approach:

1. Create initial plan outline with phases
2. Get feedback on structure before writing details
3. Determine task name for the directory structure

### Optional: Draft Generation Task

For complex plans, consider using Task tool to generate initial draft:
- **Plan Draft Task** (Task tool - `general-purpose` subagent)
  - Prompt: "Based on all research findings about [feature], generate an initial implementation plan structure. Include phases, file references with line numbers, code examples following [language] guidelines, testing strategy, and success criteria. Return a structured plan draft."
  - Uses findings from all previous Task agents
  - Follows language-specific guidelines
  - Creates skeleton with phases, file references, and code examples
  - Returns draft for review and refinement in main context
  - Human reviews and refines the draft before finalizing

**When to use:** Complex multi-phase implementations with extensive research findings.

## Fast Plan Generation (for --fast mode)

After minimal research and user approval of outline in fast planning workflow:

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

## Extracting User Content from Fast Plans (for upgrade path)

When a fast plan exists and user runs detailed mode, distinguish between template content and user additions:

### Template Indicators (ignore these):
- Placeholder text: "[Brief 1-2 sentence summary]", "[Key context]"
- Sections with no content beyond headers
- Exact template phrasing

### User Content Indicators (preserve these):
- Specific file paths, function names, line numbers
- Technical details or code snippets
- Questions marked with "?" or "TODO:"
- Markdown comments: `<!-- user note -->`
- Bold/italic emphasis added by user
- Content that doesn't match template structure
- Additional sections not in template

### Parsing Strategy:

1. **Read entire fast plan** into context
2. **Section-by-section analysis:**
   - Extract Summary section - check if it's not placeholder text
   - Extract Notes section (most likely to have user additions)
   - Extract questions (scan for "?" patterns)
   - Look for markdown comments `<!-- ... -->`

3. **Preserve in detailed plan:**
   - User questions → Research.md "Questions from Fast Plan" section
   - User insights → Context.md "Background from Fast Plan"
   - User concerns → Plan.md relevant phase sections

### Example:

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

## Step 4: Detailed Plan Writing

**⚠️ REMINDER: Verify any user corrections are documented in research.md and `.docs/knowledge/learnings/` before proceeding. ⚠️**

### Ensure Documentation Structure Exists

**FIRST: Invoke the `iw-init` skill to ensure base .docs structure exists:**

Use the Skill tool to invoke the `iw-init` skill. This ensures the `.docs/` directory structure is properly set up before creating plan files.

The init skill will:
- Create `.docs/issues/` and `.docs/adhoc/` directories if missing
- Create `.docs/knowledge/` structure if missing
- Create README files for documentation guidelines
- Report what was created

**This is idempotent** - safe to run even if structure already exists.

### Initialize Plan Structure

After ensuring base structure exists, use the `scripts/init_plan.py` script to create the specific plan directory:

**For issue-based plans:**
```bash
scripts/init_plan.py <issue-number> --type issue
```
This creates `.docs/issues/<issue-number>/` with four template files.

**For ad-hoc plans:**
```bash
scripts/init_plan.py <plan-name> --type adhoc
```
This creates `.docs/adhoc/<plan-name>/` with four template files.

### Customize the Four Files

#### File 1: `[task-name]-plan.md` (The Implementation Plan)

The main deliverable with ALL technical details. Use `assets/plan-template.md` as the base.

**Key sections to complete:**
- Overview: Brief description of what is being implemented and why
- Current State Analysis: What exists now, what's missing, key constraints
- Desired End State: Specification of end state and verification method
- What We're NOT Doing: Explicitly list out-of-scope items
- Implementation Approach: High-level strategy and reasoning

**For each phase:**
- Phase name and overview
- Development approach following language guidelines (e.g., TDD approach for Go: Write failing tests FIRST)
- Changes required with:
  - File paths with line numbers
  - Current code examples
  - Proposed changes with detailed comments (following language-specific patterns)
  - Reasoning for changes
- Testing strategy following language guidelines (e.g., testify/require for Go, separate positive/negative tests)
- Success criteria split into:
  - Automated Verification (commands to run)
  - Manual Verification (human testing steps)

**Include:**
- Testing Strategy: Unit tests, integration tests, manual steps
- Performance Considerations: Implications and metrics
- Migration Notes: How to handle existing data/systems
- References: Original ticket, key files examined, similar patterns

#### File 2: `[task-name]-research.md` (Research & Working Notes)

Captures all research process, questions asked, decisions made. Use `assets/research-template.md` as the base.

**Document:**
- Initial Understanding: What the task seemed to be initially
- Research Process: Files examined, findings, sub-tasks spawned
- Questions Asked & Answers: Q&A with user, follow-up research
- Key Discoveries: Technical discoveries, patterns, constraints
- Design Decisions: Options considered, chosen approach, rationale
- Open Questions: All must be resolved before finalizing plan
- Code Snippets Reference: Relevant existing code and patterns

#### File 3: `[task-name]-context.md` (Quick Reference Context)

Quick reference for key information. Use `assets/context-template.md` as the base.

**Include:**
- Quick Summary: 1-2 sentence summary
- Key Files & Locations: Files to modify, reference, and test
- Dependencies: Code dependencies and external dependencies
- Key Technical Decisions: Brief decisions and rationale
- Integration Points: How systems integrate
- Environment Requirements: Versions, variables, migrations
- Related Documentation: Links to other plan files

#### File 4: `[task-name]-tasks.md` (Task Checklist)

Actionable checklist. Use `assets/tasks-template.md` as the base.

**For each task:**
- Task description in imperative form
- File path where work happens
- Effort estimate (S/M/L)
- Dependencies on other tasks
- Acceptance criteria

**Include:**
- Phase verification steps (automated and manual)
- Final verification checklist
- Notes section for implementation notes

### Important Guidelines

**Follow Language-Specific Guidelines:**
- Use the appropriate language guidelines skill (e.g., go-dev-guidelines for Go)
- Follow testing patterns from the guidelines (e.g., TDD with testify/require for Go)
- Use naming conventions from the guidelines
- Follow project structure conventions from the guidelines
- Apply architectural patterns from the guidelines
- All code examples must be compliant with the language guidelines

**Be Detailed with Code:**
- Include code snippets showing current state
- Include code snippets showing proposed changes
- Add file:line references throughout
- Show concrete examples, not abstract descriptions

**Separate Concerns:**
- Plan file = clean, professional implementation guide
- Research file = working notes, questions, discoveries
- Context file = quick reference
- Tasks file = actionable checklist

**Be Skeptical & Thorough:**
- Question vague requirements
- Identify potential issues early
- Ask "why" and "what about"
- Don't assume - verify with code

**No Open Questions in Final Plan:**
- If open questions arise during planning, STOP
- Research or ask for clarification immediately
- DO NOT write the plan with unresolved questions
- Implementation plan must be complete and actionable
- Every decision must be made before finalizing

**Success Criteria:**
Always separate into two categories:
1. Automated Verification: Commands that can be run by execution agents
2. Manual Verification: UI/UX, performance, edge cases requiring human testing

## Step 5: Validation & Review

### Optional: Plan Validation Task

Before presenting to user, consider using Task tool for validation:
- **Plan Validation Task** (Task tool - `general-purpose` subagent)
  - Prompt: "Review the implementation plan for [feature]. Verify all file paths and line numbers exist and are accurate. Check for conflicts with existing code. Validate that code patterns match the codebase style. Confirm test strategy matches project patterns. Return any issues found."
  - Verifies all file paths and line numbers are accurate
  - Ensures no conflicts with existing code
  - Checks that patterns match existing codebase style
  - Validates test strategy matches project patterns
  - Returns issues found for correction

**When to use:** Complex plans with many file references and integration points.

### Present Plan to User

**✅ FINAL CHECK: Before presenting the plan to the user, verify that:**
- [ ] All user corrections are documented in research.md and `.docs/knowledge/learnings/`
- [ ] All affected plan sections have been updated with the correct information

After creating the plan structure (and optional validation):

**For issue-based plans:**
```
Implementation plan structure created at:
`.docs/issues/<issue-number>/`

Files created:
- `<issue-number>-plan.md` - Detailed implementation plan with code snippets
- `<issue-number>-research.md` - All research notes and working process
- `<issue-number>-context.md` - Quick reference for key information
- `<issue-number>-tasks.md` - Actionable task checklist

GitHub Issue: #<issue-number> - [Issue Title]
```

**For ad-hoc plans:**
```
Implementation plan structure created at:
`.docs/adhoc/<plan-name>/`

Files created:
- `<plan-name>-plan.md` - Detailed implementation plan with code snippets
- `<plan-name>-research.md` - All research notes and working process
- `<plan-name>-context.md` - Quick reference for key information
- `<plan-name>-tasks.md` - Actionable task checklist
```

The plan includes detailed code examples and file:line references throughout.
Research notes are kept separate from implementation details.

Please review:
- Are technical details accurate?
- Are code examples clear and helpful?
- Are phases properly scoped?
- Any missing considerations?

Iterate based on feedback and continue refining until the user is satisfied.

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

## Resources

### scripts/

- `init_plan.py` - Initialize a new implementation plan structure with all template files

### assets/

- `plan-template.md` - Template for the main implementation plan (detailed mode)
- `research-template.md` - Template for research and working notes (detailed mode)
- `fast-plan-template.md` - Template for quick implementation plans (fast mode)
- `context-template.md` - Template for quick reference context
- `tasks-template.md` - Template for actionable task checklist

## File Organization

**Issue-Based Plans:**
```
.docs/
└── issues/
    └── <issue-number>/
        ├── <issue-number>-plan.md      # Main deliverable (detailed, with code)
        ├── <issue-number>-research.md  # Working notes (kept separate)
        ├── <issue-number>-context.md   # Quick reference
        └── <issue-number>-tasks.md     # Actionable checklist
```

**Ad-Hoc Plans:**
```
.docs/
└── adhoc/
    └── <plan-name>/
        ├── <plan-name>-plan.md      # Main deliverable (detailed, with code)
        ├── <plan-name>-research.md  # Working notes (kept separate)
        ├── <plan-name>-context.md   # Quick reference
        └── <plan-name>-tasks.md     # Actionable checklist
```

The plan file should be professional and detailed enough to hand to an implementation agent, while the research file captures all the working process that led to the decisions.
