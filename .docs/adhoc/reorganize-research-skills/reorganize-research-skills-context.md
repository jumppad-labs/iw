# Reorganize Research Skills - Quick Reference Context

**Last Updated**: 2025-11-03

## Quick Summary

Move three research skills from project root into `.claude/skills/` with `iw-` prefix naming. Update YAML frontmatter, rename commands, and update all documentation to reflect unified naming convention.

## Key Files & Locations

### Files to Move:
- `research-planner/` → `.claude/skills/iw-research-planner/`
- `research-executor/` → `.claude/skills/iw-research-executor/`
- `research-synthesizer/` → `.claude/skills/iw-research-synthesizer/`

### Files to Rename:
- `.claude/commands/research-plan.md` → `iw-research-plan.md`
- `.claude/commands/research-execute.md` → `iw-research-execute.md`
- `.claude/commands/research-synthesize.md` → `iw-research-synthesize.md`

### Files to Edit:
- `.claude/skills/iw-research-planner/SKILL.md` (line 2: name field)
- `.claude/skills/iw-research-executor/SKILL.md` (line 2: name field)
- `.claude/skills/iw-research-synthesizer/SKILL.md` (lines 2, 4: name field + reference)
- `.claude/commands/iw-research-plan.md` (lines 5, 7: skill name, next command)
- `.claude/commands/iw-research-execute.md` (lines 5, 7: skill name, next command)
- `.claude/commands/iw-research-synthesize.md` (line 5: skill name)
- `README.md` (lines 16-48: skills/commands lists, lines 150-203: research workflow)
- `.claude/skills/iw-install/SKILL.md` (lines 88-100: skills list)

### Files to Test:
- `.claude/skills/iw-research-planner/scripts/init_research.py`
- `.claude/skills/iw-research-planner/scripts/add_source.py`
- `.claude/skills/iw-research-executor/scripts/add_finding.py`
- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`

### Files to Preserve (No Changes):
- `.docs/adhoc/research-skills/*` (historical plan documentation)

## Dependencies

### Code Dependencies:
- None - skills are self-contained
- Scripts use standard Python libraries only
- No inter-skill dependencies

### External Dependencies:
- Git - for preserving file history with `git mv`
- Python 3 - for testing scripts

## Key Technical Decisions

**1. Use `git mv` for moves**
- Preserves file history
- Better traceability

**2. Rename commands with `iw-` prefix**
- Consistent with other workflow commands
- Clear association with implementation workflow

**3. Merge skills into single README section**
- Research skills are part of the workflow
- Unified presentation

**4. Update installer to list all 13 skills**
- Research skills should be installed automatically
- Consistent management

## Integration Points

### Skill Name Changes:
- `research-planner` → `iw-research-planner`
- `research-executor` → `iw-research-executor`
- `research-synthesizer` → `iw-research-synthesizer`

### Command Name Changes:
- `/research-plan` → `/iw-research-plan`
- `/research-execute` → `/iw-research-execute`
- `/research-synthesize` → `/iw-research-synthesize`

### Documentation Updates:
- Skills count: 10 → 13
- Command count: stays 7 (renaming, not adding)
- Merge separate sections into unified workflow section

## Environment Requirements

- **Git**: For `git mv` commands
- **Python**: 3.7+ for testing scripts
- **No environment variables** needed
- **No database** changes
- **No external services** affected

## Related Documentation

- Implementation plan: `reorganize-research-skills-plan.md`
- Research notes: `reorganize-research-skills-research.md`
- Task checklist: `reorganize-research-skills-tasks.md`
- Original research skills plan: `.docs/adhoc/research-skills/`
