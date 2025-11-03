---
name: iw-workflow
description: Explains the project workflow, documentation structure, and how to use the planning and implementation skills effectively. This skill provides guidance on when to use /plan vs /implement, how skills compose together, and where to find different types of information in the project.
---

# Workflow Guide

## Overview

This skill explains how to work effectively on this project using the available tools and documentation. It covers the workflow methodology, documentation structure, and how various skills work together.

## Documentation Structure

The project uses three complementary sources of knowledge:

### 1. **CLAUDE.md** - Code Style & Standards
**Location:** `/CLAUDE.md`
**Purpose:** General development standards applicable to any project using this language/framework.

**Contains:**
- Code style and formatting rules
- Testing standards and patterns
- Project structure conventions
- Architectural patterns
- Development standards
- Dependency management

**When to use:** When you need to know general coding conventions, testing patterns, or project structure guidelines.

### 2. **`.docs/knowledge/`** - Project-Specific Technical Knowledge
**Location:** `.docs/knowledge/`
**Purpose:** Project-specific architectural decisions, quirks, and institutional knowledge.

**Contains:**
- Framework/system-specific requirements and limitations
- Project-specific patterns and conventions
- Common gotchas and workarounds
- Integration testing setup
- Architecture decisions
- Domain-specific patterns

**When to use:** When you need to understand project-specific architecture, work with custom systems, or understand project-specific patterns.

**Recommended Structure:**
```
.docs/knowledge/
├── README.md                    # Index of all knowledge documents
├── architecture/                # Architectural decisions and patterns
│   ├── system-design.md        # System architecture
│   └── patterns.md             # Project-specific patterns
├── conventions/                 # Project-specific conventions
│   └── naming-conventions.md   # Naming patterns and requirements
└── gotchas/                    # Known issues and workarounds
    └── common-issues.md        # Frequently encountered problems
```

### 3. **This Workflow Skill** - Process & Methodology
**Location:** `.claude/skills/iw-workflow/`
**Purpose:** How to work on this project using the available tools and skills.

**Contains:**
- Planning workflow (when/how to use `/plan`)
- Implementation workflow (when/how to use `/implement`)
- Git workflow patterns
- PR creation process
- Learning capture process
- Skill composition patterns

## The Planning & Implementation Workflow

### When to Use `/plan`

Create a detailed implementation plan when:

1. **Feature is complex or unclear**
   - Multiple components affected
   - Architectural decisions needed
   - Unclear implementation approach

2. **Significant refactoring**
   - Large-scale code changes
   - Breaking changes possible
   - Multiple phases of work

3. **You need alignment**
   - Want to discuss approach before coding
   - Multiple valid solutions exist
   - Need user input on trade-offs

4. **Issue requires research**
   - Need to explore codebase first
   - Pattern discovery needed
   - Dependencies unclear

**Do NOT plan for:**
- Simple bug fixes with clear solutions
- Trivial changes (typos, formatting)
- Emergency hotfixes
- Changes you fully understand already

### Planning Process

**Command:** `/plan <description or issue number>`

**Example:**
```bash
/plan 385  # Plan based on GitHub issue #385
/plan Add user authentication  # Ad-hoc plan
```

**The planner will:**
1. Load the `iw-github-issue-reader` skill if issue provided
2. Search past plans for relevant learnings
3. Activate language-specific guidelines (e.g., `go-dev-guidelines` for Go)
4. Launch parallel research agents to explore codebase
5. Guide you through context gathering
6. Create structured plan files in `.docs/issues/<number>/` or `.docs/adhoc/<name>/`

**Plan Deliverables:**
- `<name>-plan.md` - Implementation phases with code snippets
- `<name>-tasks.md` - Task breakdown for tracking
- `<name>-context.md` - Background and decisions
- `<name>-research.md` - Research findings and explorations

### When to Use `/implement` (When Available)

Execute a plan that was previously created:

1. **After planning is complete**
   - Plan has been reviewed and approved
   - Ready to start coding

2. **Following structured approach**
   - Want to follow plan phases
   - Need progress tracking
   - Working on complex implementation

**Do NOT use for:**
- Ad-hoc changes without a plan
- Quick fixes
- When you want to deviate significantly from plan

### Implementation Process

**Command:** `/implement <plan-path or issue-number>`

**Example:**
```bash
/implement 385  # Implement based on issue #385 plan
/implement .docs/adhoc/auth-system/  # Implement from ad-hoc plan
```

**The executor will:**
1. Load the plan files
2. Show you the phases and tasks
3. Walk through implementation incrementally
4. Track progress with TodoWrite
5. Confirm at key milestones
6. Create phase-based commits using `iw-git-workflow` skill

## Git Workflow

### Using the `iw-git-workflow` Skill (When Available)

The `iw-git-workflow` skill manages git operations for implementation tasks:

**Key features:**
- Creates isolated worktrees for implementation
- Handles phase-based commits
- Manages cleanup after completion
- Provides safety checks

**When to use:**
- Starting implementation work
- Creating commits after phases
- Cleaning up after completion

**Integration with `/implement`:**
The iw-executor skill automatically uses iw-git-workflow to:
1. Set up worktree at start
2. Create commits after each phase
3. Clean up at end

## PR Creation

### Using the `iw-github-pr-creator` Skill (When Available)

Creates PRs with appropriate templates and summaries:

**Supports:**
- Plan-based PRs (with phase summaries)
- Generic PRs (with commit summaries)
- Different PR templates for change types

**When to use:**
- After implementation is complete
- After tests pass
- When ready for review

**Integration:**
The iw-executor can automatically create PRs when implementation completes.

## Research with Obsidian Integration

For personal research stored in Obsidian vault:

**Workflow:**

1. **Start research with workspace selection:**
   ```
   /iw-research-plan
   ```
   - Skill auto-detects Obsidian vault
   - Prompts: ".docs/research", "Obsidian Vault", or "Custom path"
   - Choose Obsidian vault for personal research

2. **Research execution in vault:**
   ```
   /iw-research-execute
   ```
   - Files created in vault root
   - Visible in Obsidian during research
   - Use Obsidian features (links, tags, graph view)
   - Add findings and sources as usual

3. **Final report and cleanup:**
   - Report synthesis completes
   - Prompt for final location (e.g., `Research/topic-name.md`)
   - Report moved to final location
   - Intermediate files auto-cleaned
   - Only final report remains

**Benefits:**
- Live preview while researching
- Obsidian features available during work
- Clean final vault (no clutter)
- Organized knowledge base

**Requirements:**
- Obsidian with Local REST API plugin
- `obsidian-local-api` skill configured
- API key set in config

## Learning Capture Process

Capture learnings in the right place:

### During Planning

**In `<name>-research.md` (temporary):**
- Research findings
- Pattern discoveries
- Architecture explorations
- Initial investigations

**In `<name>-context.md` (plan-specific):**
- Background information
- Design decisions for this specific plan
- Alternatives considered for this feature
- Rationale for approach chosen

**In `.docs/knowledge/learnings/` (institutional):**
- User corrections during planning
- Mistakes that were caught
- Important clarifications
- Things that differed from initial assumptions
- Discoveries that affect future work

### During Implementation

**In `.docs/knowledge/learnings/` (institutional):**
- Implementation discoveries
- Things that differed from plan
- Corrections needed
- Unexpected challenges
- Workarounds discovered
- Patterns that emerged

### After Implementation

**Organize knowledge in `.docs/knowledge/`:**

1. **`learnings/`** - Evolving discoveries and corrections
   - Add immediately when discovered
   - Organized by topic (plugin-system.md, testing.md, etc.)
   - Include context, impact, and links

2. **`architecture/`** - Formalized architectural knowledge
   - Promote from learnings when patterns are established
   - Comprehensive documentation of systems
   - Long-term reference material

3. **`gotchas/`** - Persistent issues and workarounds
   - Move from learnings when issue recurs
   - Known limitations and solutions
   - Things to watch out for

**Update `CLAUDE.md` when:**
- Code style/standards need clarification
- Testing patterns should be documented
- General development practices need to be specified
- It applies to all development in this language/framework (not just this project)

## Skill Composition

### How Skills Work Together

**Typical workflow for a planned feature:**

1. **Start:** `/plan <issue-number>`
   - `iw-planner` skill activates
   - Loads `iw-github-issue-reader` skill (if issue-based)
   - Loads `iw-learnings` skill
   - Loads language-specific guidelines skill (e.g., `go-dev-guidelines`)
   - Creates plan documents

2. **Implement:** `/implement <issue-number>`
   - `iw-executor` skill activates
   - Loads the plan files
   - Uses `iw-git-workflow` skill for commits
   - Uses language guidelines for code standards
   - Tracks progress with TodoWrite

3. **Create PR:** Automatic or manual
   - `iw-github-pr-creator` skill activates
   - Reads plan phases for description
   - Creates PR with appropriate template

### Common Skills

**Planning & Execution:**
- `iw-planner` - Create detailed plans
- `iw-executor` - Execute plans
- `iw-learnings` - Search past learnings

**Version Control:**
- `iw-git-workflow` - Manage git operations
- `iw-github-pr-creator` - Create pull requests
- `iw-github-issue-reader` - Load issue context

**Language/Framework Guidelines:**
- Language-specific skills (e.g., `go-dev-guidelines`, `python-guidelines`)

**Utilities:**
- `workflow` (this skill) - Workflow guidance
- `skill-creator` - Create new skills

## Quick Reference

### When to use what:

| Task | Tool/Skill | Location |
|------|-----------|----------|
| Plan a feature | `/plan` | Creates `.docs/issues/<num>/` or `.docs/adhoc/<name>/` |
| Implement a plan | `/implement` | Executes from plan files |
| Find code style rules | Read `CLAUDE.md` | Root directory |
| Find project patterns | Read `.docs/knowledge/` | Knowledge docs |
| Understand workflow | This skill (auto-loaded) | `.claude/skills/iw-workflow/` |
| Create a PR | `iw-github-pr-creator` skill | Invoked by iw-executor |
| Search past learnings | `iw-learnings` | Auto-invoked by planner |

### Where to document:

| Type of Information | Location |
|---------------------|----------|
| General language/framework standards | `CLAUDE.md` |
| Project architecture | `.docs/knowledge/architecture/` |
| Learnings & corrections | `.docs/knowledge/learnings/` |
| Known issues & workarounds | `.docs/knowledge/gotchas/` |
| Temporary research (plan) | `<name>-research.md` |
| Design decisions (plan) | `<name>-context.md` |

## Rules & Best Practices

### Planning Rules

1. **Always use `/plan` for complex work** - Don't skip planning for significant features
2. **Search past learnings first** - The planner does this automatically
3. **Document corrections** - Add to learnings-and-corrections immediately when user corrects you
4. **Use language guidelines** - Delegate coding decisions to language-specific guidelines skills
5. **Review before implementing** - Get plan approval before starting implementation

### Implementation Rules

1. **Follow the plan phases** - Stick to the planned approach unless you find issues
2. **Document deviations** - Add to learnings-and-corrections when changing approach
3. **Test as you go** - Write tests for each phase
4. **Commit per phase** - Use iw-git-workflow for clean history
5. **Update learnings** - Capture discoveries for future work

### Documentation Rules

1. **Learnings first** - Document corrections in `.docs/knowledge/learnings/` immediately when discovered
2. **CLAUDE.md** - Only general language/framework practices
3. **`.docs/knowledge/`** - Project-specific knowledge organized by type (learnings, architecture, gotchas)
4. **Plan files** - Only temporary research and plan-specific decisions
5. **Keep it DRY** - Don't duplicate information across locations
6. **Promote knowledge** - Move learnings to architecture docs when formalized
7. **Update promptly** - Document learnings while fresh

## Getting Help

- **Workflow questions**: This skill (auto-loaded)
- **Project patterns**: Read `.docs/knowledge/`
- **Code style**: Read `CLAUDE.md`
- **Skill creation**: Use `skill-creator` skill
- **Past learnings**: Plans in `.docs/issues/` and `.docs/adhoc/`
