# Issue #15 - Context & Dependencies

**Last Updated**: 2025-11-04

## Quick Summary

Add two-pass planning system to iw-planner skill: fast mode (minimal research, single file, <100 lines) and detailed mode (full research, 4 files). Fast plans can be upgraded to detailed plans while preserving user comments. Both modes check guidelines and learnings to maintain quality.

## Key Files & Locations

### Files to Modify:

- `.claude/commands/iw-plan.md` - Add --fast and --detailed flag documentation to command description
- `.claude/skills/iw-planner/SKILL.md:46-87` - Add mode detection (step 0) and fast workflow branch
- `.claude/skills/iw-planner/SKILL.md:110-140` - Enhance detailed workflow to detect/read fast plans
- `.claude/skills/iw-planner/SKILL.md:26-44` - Update Quick Start documentation with mode examples
- `.claude/skills/iw-planner/SKILL.md:566+` - Add Edge Cases section before Resources
- `.claude/skills/iw-planner/scripts/init_plan.py:1-160` - Add --mode flag and create_fast_plan_file() function

### Files to Create:

- `.claude/skills/iw-planner/assets/fast-plan-template.md` - New single-file template for fast plans (~50 lines)
- `.docs/issues/15/testing-scenarios.md` - Test scenarios documentation (7 test cases)

### Files to Reference:

- `.claude/skills/iw-planner/SKILL.md:164-174` - Pattern for invoking iw-learnings skill
- `.claude/skills/iw-planner/SKILL.md:364-374` - Pattern for invoking iw-init skill
- `.claude/skills/iw-planner/SKILL.md:162-195` - Pattern for parallel Task agent launching
- `.claude/skills/iw-planner/scripts/init_plan.py:120-140` - Template placeholder replacement pattern
- `.docs/knowledge/learnings/installation.md` - Learning about simple approaches

### Test Files:

- `.docs/issues/15/testing-scenarios.md` - Manual test scenarios (to be created in Phase 4)

## Dependencies

### Code Dependencies:

- **iw-github-issue-reader skill** - Fast and detailed modes both use for issue fetching
- **iw-learnings skill** - Both modes search past learnings
- **iw-init skill** - Both modes ensure .docs structure exists
- **Task tool with Explore subagent** - Fast mode uses "quick" thoroughness for file scanning
- **Read tool** - Detailed mode reads existing fast plans for upgrade path

### External Dependencies:

- Python 3.6+ (for init_plan.py script)
- argparse module (standard library)
- Path from pathlib (standard library)
- datetime module (standard library)

## Key Technical Decisions

1. **Mode-Based Workflow**: Separate --fast and --detailed flags with distinct workflows. Detailed mode reads fast plans for upgrade path. User explicitly chooses mode.

2. **Fast Mode Research**: 4 agents only (GitHub issue + learnings + guidelines + quick file scan). Maintains quality while reducing token consumption by ~70%.

3. **Single File Output for Fast Plans**: One combined markdown file with all sections (vs 4-file structure). Appropriate for simple tasks, faster to generate and review.

4. **Automatic User Edit Preservation**: Detailed mode automatically detects, reads, and extracts user comments/questions from fast plans. Preserved in research.md "Fast Plan Review" section.

5. **Backward Compatibility**: Detailed mode remains default. Existing `/iw-plan` commands work unchanged. New flags are optional.

6. **Template Separation**: New fast-plan-template.md separate from existing templates. Clean separation, easier maintenance, optimized for concise output.

## Integration Points

- **Command Entry** (`.claude/commands/iw-plan.md`): Parses flags, passes {{ARGS}} to skill
- **Skill Workflow** (`.claude/skills/iw-planner/SKILL.md`): Mode detection → branch to fast or detailed workflow
- **Script Layer** (`.claude/skills/iw-planner/scripts/init_plan.py`): Creates appropriate file structure based on --mode flag
- **Template System** (`.claude/skills/iw-planner/assets/`): Fast template for single-file, existing templates for 4-file
- **Upgrade Path**: Detailed workflow reads fast plan → extracts user content → incorporates into research

## Environment Requirements

- No new environment variables needed
- No database migrations needed
- Python 3.6+ (already required)
- No new external packages required

## Related Documentation

- Original ticket: GitHub Issue #15
- Research notes: `.docs/issues/15/15-research.md`
- Implementation plan: `.docs/issues/15/15-plan.md`
- Task checklist: `.docs/issues/15/15-tasks.md`
- Testing scenarios: `.docs/issues/15/testing-scenarios.md` (to be created)
- Past learning: `.docs/knowledge/learnings/installation.md` - Simple approaches preferred
