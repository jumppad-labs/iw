# Issue #6 - Context & Dependencies

**Last Updated**: 2025-11-03

## Quick Summary

Make research skills location-aware by adding workspace selection (with Obsidian vault auto-detection), final report destination prompts, and automatic cleanup of intermediate files after synthesis. Enables personal research storage in Obsidian vaults while maintaining backward compatibility with `.docs/research/` workflow.

## Key Files & Locations

### Files to Modify:

**Research Planner Skill:**
- `.claude/skills/iw-research-planner/SKILL.md` - Add workspace location detection and prompting workflow
- `.claude/skills/iw-research-planner/scripts/init_research.py` - Accept workspace_path parameter, save config

**Research Executor Skill:**
- `.claude/skills/iw-research-executor/scripts/add_finding.py:12` - Read workspace path from config instead of hardcoding
- `.claude/skills/iw-research-executor/scripts/add_source.py:12` - Read workspace path from config instead of hardcoding

**Research Synthesizer Skill:**
- `.claude/skills/iw-research-synthesizer/SKILL.md` - Add final location prompt and cleanup workflow
- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py` - Add move and cleanup logic

**Documentation:**
- `README.md:145-184` - Update research workflow section to highlight Obsidian integration
- `.claude/skills/iw-workflow/SKILL.md` - Add Obsidian research workflow examples

### Files to Reference:

**Configuration pattern to follow:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:68-118` - Multi-level config precedence pattern
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:184-225` - User prompting pattern

**Current initialization:**
- `.claude/skills/iw-research-planner/scripts/init_research.py:22` - Current hardcoded path pattern
- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py:108` - Current report generation

### Test Files:

No automated tests currently exist for skills. Manual testing required:
- Test with `.docs/research/` (backward compatibility)
- Test with custom file path
- Test with Obsidian vault detection
- Test cleanup after synthesis
- Test final location prompt

## Dependencies

### Code Dependencies:

**Python Standard Library (already in use):**
- `pathlib.Path` - Path handling and manipulation
- `json` - Config file read/write
- `argparse` - Command-line argument parsing
- `datetime` - Timestamp generation
- `shutil` - File and directory operations for cleanup

**Skill Dependencies:**
- `obsidian-local-api` skill - Optional, for Obsidian vault detection and operations
  - Used to detect if Obsidian is configured
  - Used to get vault path
  - Used to create notes via REST API (future enhancement)

### External Dependencies:

**Optional:**
- Obsidian with Local REST API plugin - For vault integration features
  - Not required for basic functionality
  - Graceful degradation if not available

## Key Technical Decisions

1. **Two-Location Pattern**: Workspace for temporary files + final destination for report. Enables clean workflow and auto-cleanup.

2. **Split Prompting**: Ask for workspace at planning time, final location at synthesis time. Matches natural workflow progression.

3. **Auto-Cleanup**: Automatically remove intermediate files after successful synthesis. User explicitly requested this behavior.

4. **Obsidian Auto-Detection**: Check if obsidian-local-api is configured and offer vault root as convenient option. Graceful degradation if not available.

5. **Simple Configuration**: Store workspace path in `.research-config.json` in research directory. Simpler than multi-level config, sufficient for needs.

6. **Backward Compatibility**: Default to `.docs/research/` if user provides no input. Existing workflows continue to work unchanged.

## Integration Points

**With obsidian-local-api skill:**
- Check if Obsidian is configured: Attempt to connect via API
- Get vault root path: Query API for vault information
- Future: Create notes directly via API instead of file operations

**With existing research workflow:**
- Workspace selection happens in iw-research-planner (Step 1)
- Research execution uses workspace config (Steps 2-N)
- Final location + cleanup happens in iw-research-synthesizer (Final step)

**File operations:**
- Create files: Use provided workspace path
- Read/write findings: Use workspace path from config
- Move report: Copy to final location, verify, then cleanup workspace
- Cleanup: Remove all workspace files except final report

## Environment Requirements

**Python:**
- Version: 3.7+ (already required by skills)
- No new packages needed

**Obsidian (Optional):**
- Obsidian application running
- Local REST API plugin installed and configured
- API key in config (via obsidian-local-api skill setup)

**Claude Code:**
- obsidian-local-api skill available (for Obsidian integration)
- All research skills installed (iw-research-planner, iw-research-executor, iw-research-synthesizer)

## Workflow Changes

### Before (Current):
1. `/iw-research-plan` → Creates `.docs/research/<name>/`
2. Research execution → Adds to `.docs/research/<name>/`
3. Synthesis → Generates report in `.docs/research/<name>/`
4. Done → All files remain in `.docs/research/<name>/`

### After (New):
1. `/iw-research-plan` → **Prompts for workspace** → Creates files in chosen location
2. Research execution → Uses workspace from config
3. Synthesis → **Prompts for final location** → Moves report → **Auto-cleans workspace**
4. Done → Only final report remains in final location

## Configuration File Format

**`.research-config.json`** (created in workspace directory):
```json
{
  "research_name": "llm-tool-calling",
  "workspace_path": "/path/to/obsidian/vault",
  "created_date": "2025-11-03",
  "obsidian_integration": true
}
```

## Related Documentation

- Original ticket: `GitHub Issue #6`
- Research notes: `.docs/issues/6/6-research.md`
- Implementation plan: `.docs/issues/6/6-plan.md`
- Task breakdown: `.docs/issues/6/6-tasks.md`

## Success Criteria

**Functional:**
- [ ] Research can be created in Obsidian vault root
- [ ] Research can be created in custom paths
- [ ] Research defaults to `.docs/research/` if no choice made
- [ ] Final report prompts for destination
- [ ] Intermediate files auto-cleanup after synthesis
- [ ] Obsidian vault auto-detected when configured

**Backward Compatibility:**
- [ ] Existing `.docs/research/` workflow unchanged
- [ ] No breaking changes to existing research projects
- [ ] Graceful degradation without Obsidian

**Documentation:**
- [ ] README updated with Obsidian integration examples
- [ ] iw-workflow skill updated with new workflow
- [ ] All SKILL.md files updated with new prompts
