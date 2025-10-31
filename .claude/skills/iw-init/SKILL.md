---
name: iw-init
description: Initialize .docs directory structure for plans and knowledge documentation. Can be invoked by users or other skills (like iw-planner) to ensure documentation structure exists.
---

# Documentation Structure Initializer

## Overview

Initialize the `.docs` directory structure for this project. This creates standardized directories for implementation plans and institutional knowledge.

**Designed for both direct invocation and programmatic use by other skills.**

## When to Use This Skill

Invoke this skill when:
1. **Starting a new project** - Set up documentation structure
2. **From iw-planner** - Automatically ensure structure exists before creating plans
3. **Adding knowledge docs** - Ensure knowledge directory structure exists
4. **Project setup** - Initialize documentation alongside code

## What This Skill Creates

### Complete Structure (default):
```
.docs/
├── README.md                      # Documentation overview
├── issues/                        # Issue-based implementation plans
├── adhoc/                         # Ad-hoc implementation plans
└── knowledge/                     # Institutional knowledge
    ├── README.md                  # Knowledge documentation guide
    ├── architecture/              # Architectural decisions
    ├── conventions/               # Project conventions
    ├── learnings/                 # Learnings and corrections
    │   └── README.md              # Learnings format guide
    └── gotchas/                   # Known issues and workarounds
```

## Usage

**Direct invocation:**
```
Skill: iw-init
```

**From another skill (e.g., iw-planner):**
```python
# In skill code:
# Use Skill tool to invoke iw-init skill
```

**With options:**
- No arguments → Create complete structure
- "knowledge-only" → Create only knowledge structure
- "plans-only" → Create only issues/adhoc directories

## Workflow

### Step 1: Check Current State

Use Bash tool to check what exists:
```bash
ls -la .docs 2>/dev/null || echo ".docs does not exist"
```

Document what already exists to avoid duplication.

### Step 2: Create Directory Structure

Based on what's missing, create directories using `mkdir -p`:

**For complete structure:**
```bash
mkdir -p .docs/issues
mkdir -p .docs/adhoc
mkdir -p .docs/knowledge/architecture
mkdir -p .docs/knowledge/conventions
mkdir -p .docs/knowledge/learnings
mkdir -p .docs/knowledge/gotchas
```

**For knowledge-only:**
```bash
mkdir -p .docs/knowledge/architecture
mkdir -p .docs/knowledge/conventions
mkdir -p .docs/knowledge/learnings
mkdir -p .docs/knowledge/gotchas
```

**For plans-only:**
```bash
mkdir -p .docs/issues
mkdir -p .docs/adhoc
```

### Step 3: Create README Files

Create README files only if they don't already exist. Check first with Read tool.

#### .docs/README.md

```markdown
# Project Documentation

This directory contains implementation plans and institutional knowledge.

## Structure

- **issues/** - Implementation plans for GitHub issues
- **adhoc/** - Ad-hoc implementation plans
- **knowledge/** - Institutional knowledge and learnings

## Creating Plans

Use `/plan <description or issue-number>` to create new implementation plans.

The planner will automatically create the appropriate directory structure:
- Issue-based: `.docs/issues/<issue-number>/`
- Ad-hoc: `.docs/adhoc/<plan-name>/`

## Documentation Guidelines

### Implementation Plans
- **Purpose**: Document approach for specific feature/issue
- **Lifecycle**: Temporary, archived after implementation
- **Location**: `issues/` or `adhoc/` subdirectories
- **Files**:
  - `<name>-plan.md` - Implementation phases with code
  - `<name>-tasks.md` - Task breakdown
  - `<name>-context.md` - Background and decisions
  - `<name>-research.md` - Research findings

### Knowledge Documentation
- **Purpose**: Permanent, project-wide patterns and learnings
- **Lifecycle**: Living documentation, updated continuously
- **Location**: `knowledge/` subdirectories
- **Categories**:
  - `architecture/` - System design and patterns
  - `conventions/` - Project-specific conventions
  - `learnings/` - Discoveries and corrections
  - `gotchas/` - Known issues and workarounds

See `knowledge/README.md` for detailed knowledge documentation guidelines.

## Workflow

1. Use `/plan` to create implementation plans
2. Document learnings in `knowledge/learnings/` during work
3. Promote learnings to `architecture/` when formalized
4. Track recurring issues in `gotchas/`

See the `iw-workflow` skill (auto-loaded) for complete process documentation.
```

#### .docs/knowledge/README.md

```markdown
# Project Knowledge

This directory contains project-specific technical knowledge, architectural decisions, and institutional knowledge.

For general development standards, see `/CLAUDE.md`.
For workflow and process information, see the `iw-workflow` skill (auto-loaded).

## Directory Structure

### `/architecture/` - Architectural Decisions and Patterns

Formalized system architecture and design patterns.

### `/conventions/` - Project-Specific Conventions

Project-specific naming, structure, and coding conventions that differ from general standards.

### `/learnings/` - Learnings & Corrections

Discoveries and corrections from planning and implementation. See `learnings/README.md` for documentation format.

### `/gotchas/` - Known Issues and Workarounds

Persistent issues, limitations, and their workarounds.

## When to Add to This Directory

Add to `.docs/knowledge/` when you discover:

- **Project-specific patterns** that differ from general practices
- **System limitations** (like plugin naming requirements)
- **Architectural decisions** that affect multiple features
- **Common gotchas** that future developers should know
- **Integration patterns** specific to this project

**Do NOT add:**
- General development standards → Use `CLAUDE.md`
- Temporary research notes → Use `<name>-research.md` in plan files
- Design decisions for a specific plan → Use `<name>-context.md` in plan files

## How to Document

1. **Create a focused document** in the appropriate subdirectory
2. **Update this README** with a link and brief description
3. **Keep it DRY** - Don't duplicate information
4. **Use examples** - Show concrete code when possible
5. **Explain the "why"** - Document reasoning behind decisions

## Contributing

When you discover new project-specific knowledge during implementation:

1. Check if it belongs in `.docs/knowledge/` (project-specific) vs `CLAUDE.md` (general)
2. Create or update the appropriate document
3. Add entry to this README
4. Keep documents focused and scannable
```

#### .docs/knowledge/learnings/README.md

```markdown
# Learnings & Corrections

This directory captures important learnings and corrections discovered during planning and implementation. These are institutional knowledge items that future work should be aware of.

## Purpose

Document:
- **User corrections** during planning or implementation
- **Mistakes discovered** and how they were caught
- **Important clarifications** that differed from initial assumptions
- **Implementation discoveries** that differed from the plan
- **Things that surprised us** during development
- **Gotchas to avoid** in future work

## Structure

Learnings are organized by topic/area:

```
learnings/
├── README.md (this file)
├── plugin-system.md       # Plugin system learnings
├── resource-providers.md  # Provider pattern learnings
├── testing.md            # Testing-related learnings
└── ...                   # Other topic-based files
```

## When to Add Learnings

### During Planning

Add learnings when:
- User corrects an assumption you made
- Research reveals something unexpected
- You discover a pattern that contradicts your initial understanding
- A limitation or constraint is clarified

### During Implementation

Add learnings when:
- Implementation reveals the plan was incorrect
- You discover an undocumented behavior
- A workaround or solution differs from the plan
- You hit an unexpected obstacle

### After Implementation

Add learnings when:
- Code review reveals issues
- Testing uncovers unexpected behavior
- You identify patterns for future work

## How to Document

### Format

Each learning entry should include:

```markdown
## [Date] - [Brief Title]

**Context:** [What were you working on?]

**Learning:** [What did you discover?]

**Impact:** [How does this affect future work?]

**Related:** [Link to PR, issue, or plan if applicable]
```

### Example

```markdown
## 2025-10-31 - Plugin System Requires Snake_Case Naming

**Context:** Planning ollama API endpoint resources (issue #385)

**Learning:** The plugin system requires resource and provider structs
to use snake_case (e.g., `Ollama_Model`) instead of Go's standard PascalCase
(e.g., `OllamaModel`). This is due to how the plugin system uses reflection
to map HCL resource names to Go structs.

**Impact:** All future resource and provider structs must use snake_case.
This should be documented in plans and acknowledged as a deviation from
standard conventions. Updated architecture docs in `.docs/knowledge/architecture/plugin-system.md`.

**Related:**
- Issue #385
- Plan: `.docs/adhoc/ollama-api-endpoints/`
- Docs: [plugin-system.md](../architecture/plugin-system.md)
```

## Relationship to Other Docs

- **Learnings** → Temporary, evolving knowledge from active development
- **Architecture docs** → Permanent, formalized knowledge about system design
- **Gotchas** → Known issues and workarounds
- **Plan files** → Specific to one implementation, references learnings

### Workflow

1. **Discover learning** during planning/implementation
2. **Document immediately** in appropriate learnings file
3. **Reference in plan** if relevant to that work
4. **Promote to architecture docs** if it becomes formalized knowledge
5. **Move to gotchas** if it's a persistent issue/workaround

## Quick Reference

| Scenario | Action |
|----------|--------|
| User corrects assumption | Add to relevant learnings file immediately |
| Implementation differs from plan | Add to learnings with context |
| Pattern becomes established | Promote from learnings to architecture docs |
| Recurring workaround needed | Move from learnings to gotchas |
| One-time issue | Document in learnings, reference in plan |

## Contributing

1. **Add immediately** - Document learnings when they happen, not later
2. **Be specific** - Include context and impact
3. **Link to work** - Reference the issue/PR/plan
4. **Update architecture docs** - When learnings become formalized
5. **Keep organized** - Use topic-based files, not one giant file
```

### Step 4: Verify Structure

Use Bash to verify the created structure:
```bash
ls -laR .docs
```

### Step 5: Report Results

Provide a summary:
```
✅ Documentation structure initialized successfully!

Created directories:
- .docs/issues/
- .docs/adhoc/
- .docs/knowledge/architecture/
- .docs/knowledge/conventions/
- .docs/knowledge/learnings/
- .docs/knowledge/gotchas/

Created README files:
- .docs/README.md
- .docs/knowledge/README.md
- .docs/knowledge/learnings/README.md

The project is now ready for documentation with /plan and knowledge capture.
```

## Idempotency

This skill is idempotent - safe to run multiple times:
- Existing directories are not modified
- Existing README files are not overwritten
- Only missing structure is created

## Integration with Other Skills

### iw-planner
The planner skill can invoke this skill to ensure structure exists before creating plan files:

```markdown
# In iw-planner workflow:
1. Check if .docs exists
2. If not, invoke iw-init skill using Skill tool
3. Proceed with plan creation
```

### Other Skills
Any skill that needs to create documentation can invoke this skill first to ensure the structure is ready.

## Success Criteria

- [ ] All required directories exist
- [ ] README files created if missing
- [ ] Structure is valid and follows conventions
- [ ] No errors during creation
- [ ] Confirmation message displayed
