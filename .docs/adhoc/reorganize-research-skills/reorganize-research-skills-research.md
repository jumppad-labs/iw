# Reorganize Research Skills - Research & Working Notes

**Research Date**: 2025-11-03
**Task**: Reorganize research skills into .claude/skills with iw- prefix

## Initial Understanding

User requested: "Let's move the research- skills into the .claude/skills directory and name them with the iw prefix. We should ensure that all the help install and other docs are up to date with this info"

**Initial interpretation**: This is a straightforward reorganization task to:
1. Move three research skills from project root to `.claude/skills/`
2. Rename them with `iw-` prefix for consistency
3. Update all documentation and commands
4. Update the installer to include them

## Research Process

### Files Examined:

**Current Research Skills Structure:**
- Examined `research-planner/`, `research-executor/`, `research-synthesizer/` at project root
- Found 10 total files across the three skills (SKILL.md, scripts, assets, references)
- Skills are fully functional at current location

**Existing iw-* Skills:**
- Examined `.claude/skills/` structure
- Found 10 existing iw-* skills (iw-planner, iw-executor, etc.)
- Confirmed standard structure pattern

**Commands:**
- Found 3 research commands: `research-plan.md`, `research-execute.md`, `research-synthesize.md`
- All in `.claude/commands/` directory

**Documentation:**
- `README.md` - Lists research skills separately (lines 27-30, 45-47, 150-203)
- `.claude/skills/iw-install/SKILL.md` - Lists 10 skills, doesn't include research (lines 88-100)
- `.claude/commands/iw-help.md` - References iw-workflow skill for command listing

### Questions Asked & Answers:

**Q1: Where should the research skills be moved?**
**A**: Into `.claude/skills/` with `iw-` prefix naming

**Q2: Should we update the install skill?**
**A**: Yes, the installer should list all 13 skills (10 existing + 3 research)

**Q3: What about historical plan files in `.docs/adhoc/research-skills/`?**
**A**: Leave them as-is - they're historical documentation

## Key Discoveries

### Discovery 1: Skills Count Inconsistency
**Found**: README.md shows "13 total" but iw-install/SKILL.md shows "10 total"
**Impact**: Need to update iw-install to list all 13 skills including research
**Source**: README.md lines 16, iw-install/SKILL.md line 90

### Discovery 2: Separate Documentation Sections
**Found**: README.md separates "Implementation Workflow Skills" and "Research Skills"
**Impact**: Should merge into one section with consistent `iw-` prefix naming
**Source**: README.md lines 17-34

### Discovery 3: Command Reference Chains
**Found**: Commands reference each other (plan → execute → synthesize)
**Impact**: Need to update all command name references in descriptions
**Source**: `.claude/commands/research-*.md` files

### Discovery 4: SKILL.md Internal References
**Found**: `research-synthesizer/SKILL.md` line 4 references "research-executor"
**Impact**: Need to update to "iw-research-executor"
**Source**: research-synthesizer/SKILL.md line 4

## Design Decisions

### Decision 1: Use git mv for Moves
**Options considered:**
- A: Use `mv` command (loses git history)
- B: Use `git mv` command (preserves git history)

**Chosen**: Option B - `git mv`

**Rationale**: Preserve file history for better traceability. Git history is valuable for understanding why skills were created and how they evolved.

### Decision 2: Rename Commands with iw- Prefix
**Options considered:**
- A: Keep command names as `/research-*`
- B: Rename to `/iw-research-*` for consistency

**Chosen**: Option B - `/iw-research-*`

**Rationale**: Consistent naming convention. All other workflow commands use `/iw-*` pattern. Makes it clear these are part of the implementation workflow suite.

### Decision 3: Merge README Sections
**Options considered:**
- A: Keep separate "Research Skills" section
- B: Merge research skills into "Implementation Workflow Skills"

**Chosen**: Option B - Merge sections

**Rationale**: Research skills are part of the implementation workflow. Separating them was temporary during development. Now they should be unified.

### Decision 4: Update Installer
**Options considered:**
- A: Don't update installer (let users install manually)
- B: Update installer to include research skills

**Chosen**: Option B - Update installer

**Rationale**: Research skills should be installed automatically with the workflow. No reason to exclude them from the standard installation.

## Open Questions

**No open questions** - This is a straightforward reorganization task with clear requirements.

## Code Snippets Reference

### YAML Frontmatter Pattern
```yaml
---
name: iw-research-planner
description: Define research scope and create structured research plan...
---
```

### Command File Pattern
```markdown
---
description: Create a new research plan
---

Invoke the iw-research-planner skill to create a structured research plan...
```

### README Skills List Pattern
```markdown
### Skills (13 total)

#### Implementation Workflow Skills
- **iw-planner** - Create detailed implementation plans
- **iw-executor** - Execute implementation plans
...
- **iw-research-planner** - Define research scope...
```

## Corrections During Planning

**No corrections needed** - User request was clear and straightforward.

## Related Documentation

- User request: In conversation (move research skills to .claude/skills with iw- prefix)
- Existing pattern: `.claude/skills/iw-*/` structure
- Historical plan: `.docs/adhoc/research-skills/` (to be preserved as documentation)
