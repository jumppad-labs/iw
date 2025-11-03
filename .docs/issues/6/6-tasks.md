# Issue #6 - Task Checklist

**Last Updated**: 2025-11-03
**Status**: Not Started
**GitHub Issue**: https://github.com/jumppad-labs/iw/issues/6

---

## Phase 1: Obsidian Detection & Workspace Selection

### Documentation Updates

- [ ] **Task 1.1**: Update iw-research-planner SKILL.md - Add Step 1.5
  - File: `.claude/skills/iw-research-planner/SKILL.md`
  - Effort: M
  - Dependencies: None
  - Acceptance: New "Step 1.5: Select Workspace Location" section added after Step 1

- [ ] **Task 1.2**: Add Obsidian detection documentation to SKILL.md
  - File: `.claude/skills/iw-research-planner/SKILL.md`
  - Effort: S
  - Dependencies: None
  - Acceptance: "scripts/detect_obsidian.py" section added to Resources

### Testing (Manual)

- [ ] **Task 1.3**: Test workspace prompt appears in skill
  - File: N/A (skill invocation test)
  - Effort: S
  - Dependencies: Task 1.1 complete
  - Acceptance: Workspace prompt shows during `/iw-research-plan`

- [ ] **Task 1.4**: Test Obsidian vault detection
  - File: N/A (integration test)
  - Effort: M
  - Dependencies: obsidian-local-api configured
  - Acceptance: Vault root appears as workspace option when Obsidian configured

- [ ] **Task 1.5**: Test graceful fallback without Obsidian
  - File: N/A (integration test)
  - Effort: S
  - Dependencies: Task 1.1 complete
  - Acceptance: Only `.docs/research` and custom path options when Obsidian unavailable

### Phase 1 Verification
- [ ] Workspace prompt appears when creating research
- [ ] Obsidian vault detected and offered as option
- [ ] Custom path entry works
- [ ] Default `.docs/research` works
- [ ] Graceful fallback when Obsidian not available

---

## Phase 2: Update init_research.py for Configurable Paths

### Code Changes

- [ ] **Task 2.1**: Add workspace_path parameter to create_research_structure()
  - File: `.claude/skills/iw-research-planner/scripts/init_research.py`
  - Lines: 22-25
  - Effort: S
  - Dependencies: None
  - Acceptance: Function accepts workspace_path with backward-compatible default

- [ ] **Task 2.2**: Add configuration file creation logic
  - File: `.claude/skills/iw-research-planner/scripts/init_research.py`
  - Lines: After line 59
  - Effort: M
  - Dependencies: Task 2.1
  - Acceptance: `.research-config.json` created in research directory with correct values

- [ ] **Task 2.3**: Update function return value
  - File: `.claude/skills/iw-research-planner/scripts/init_research.py`
  - Lines: 61-65
  - Effort: S
  - Dependencies: Task 2.2
  - Acceptance: Returns workspace_path, config_file, obsidian_integration fields

- [ ] **Task 2.4**: Add CLI arguments (--workspace, --obsidian)
  - File: `.claude/skills/iw-research-planner/scripts/init_research.py`
  - Lines: 68-70
  - Effort: S
  - Dependencies: None
  - Acceptance: Arguments parsed and available in args

- [ ] **Task 2.5**: Update main() to pass new parameters
  - File: `.claude/skills/iw-research-planner/scripts/init_research.py`
  - Lines: 72-78
  - Effort: S
  - Dependencies: Tasks 2.1, 2.4
  - Acceptance: Parameters passed to function, output shows workspace and config

### Testing

- [ ] **Task 2.6**: Test with custom workspace path
  - Command: `python3 init_research.py test --workspace ~/Documents`
  - Effort: S
  - Dependencies: Tasks 2.1-2.5
  - Acceptance: Files created in ~/Documents/test/, config correct

- [ ] **Task 2.7**: Test with --obsidian flag
  - Command: `python3 init_research.py test --workspace /vault --obsidian`
  - Effort: S
  - Dependencies: Tasks 2.1-2.5
  - Acceptance: Config has obsidian_integration: true

- [ ] **Task 2.8**: Test backward compatibility (no args)
  - Command: `python3 init_research.py test`
  - Effort: S
  - Dependencies: Tasks 2.1-2.5
  - Acceptance: Files created in .docs/research/test/, works as before

### Phase 2 Verification
- [ ] Custom workspace paths accepted
- [ ] .research-config.json created with correct values
- [ ] Obsidian flag persisted to config
- [ ] Backward compatibility maintained
- [ ] CLI output shows workspace and config info

---

## Phase 3: Update Executor Scripts to Use Config

### Code Changes - add_finding.py

- [ ] **Task 3.1**: Add load_research_config() helper to add_finding.py
  - File: `.claude/skills/iw-research-executor/scripts/add_finding.py`
  - Lines: After imports (around line 8)
  - Effort: M
  - Dependencies: None
  - Acceptance: Helper searches multiple locations, returns config with fallback

- [ ] **Task 3.2**: Update add_finding() to use config
  - File: `.claude/skills/iw-research-executor/scripts/add_finding.py`
  - Lines: 10-14
  - Effort: S
  - Dependencies: Task 3.1
  - Acceptance: Uses workspace_path from config, helpful error on missing research

### Code Changes - add_source.py

- [ ] **Task 3.3**: Add load_research_config() helper to add_source.py
  - File: `.claude/skills/iw-research-executor/scripts/add_source.py`
  - Lines: After imports
  - Effort: M
  - Dependencies: None
  - Acceptance: Same implementation as Task 3.1

- [ ] **Task 3.4**: Update add_source() to use config
  - File: `.claude/skills/iw-research-executor/scripts/add_source.py`
  - Lines: Function body
  - Effort: S
  - Dependencies: Task 3.3
  - Acceptance: Uses workspace_path from config, helpful error handling

### Testing

- [ ] **Task 3.5**: Test add_finding with .docs/research
  - Command: `python3 add_finding.py test "Theme" "Finding" "Source"`
  - Effort: S
  - Dependencies: Tasks 3.1-3.2, Phase 2 complete
  - Acceptance: Finding added to .docs/research/test/findings.md

- [ ] **Task 3.6**: Test add_finding with custom workspace
  - Command: Create research in ~/Documents, run add_finding
  - Effort: S
  - Dependencies: Tasks 3.1-3.2
  - Acceptance: Finding added to custom workspace location

- [ ] **Task 3.7**: Test add_source with custom workspace
  - Command: Run add_source on custom workspace research
  - Effort: S
  - Dependencies: Tasks 3.3-3.4
  - Acceptance: Source added to custom workspace location

- [ ] **Task 3.8**: Test error handling for missing research
  - Command: `python3 add_finding.py nonexistent "Theme" "Finding" "Source"`
  - Effort: S
  - Dependencies: Tasks 3.1-3.2
  - Acceptance: Clear error message with workspace path shown

### Phase 3 Verification
- [ ] Scripts read workspace from config
- [ ] Work with default .docs/research location
- [ ] Work with custom workspace paths
- [ ] Helpful error messages when research not found
- [ ] Backward compatibility with missing config

---

## Phase 4: Add Final Location Prompt to Synthesizer

### Documentation Updates

- [ ] **Task 4.1**: Add Step 4 to iw-research-synthesizer SKILL.md
  - File: `.claude/skills/iw-research-synthesizer/SKILL.md`
  - Lines: After synthesis steps (around line 150)
  - Effort: M
  - Dependencies: None
  - Acceptance: "Step 4: Prompt for Final Report Location" section added

- [ ] **Task 4.2**: Document validate_path.py helper in SKILL.md
  - File: `.claude/skills/iw-research-synthesizer/SKILL.md`
  - Lines: Resources section
  - Effort: S
  - Dependencies: None
  - Acceptance: Helper script documented with usage and returns

### Testing (Manual)

- [ ] **Task 4.3**: Test final location prompt appears
  - File: N/A (skill test)
  - Effort: S
  - Dependencies: Task 4.1
  - Acceptance: Prompt shows after synthesis with workspace location

- [ ] **Task 4.4**: Test keeping in workspace option
  - File: N/A (skill test)
  - Effort: S
  - Dependencies: Task 4.1
  - Acceptance: Report stays in workspace, no move occurs

- [ ] **Task 4.5**: Test custom path option
  - File: N/A (skill test)
  - Effort: M
  - Dependencies: Task 4.1
  - Acceptance: Custom path accepted, parent dirs created if needed

- [ ] **Task 4.6**: Test path validation
  - File: N/A (skill test)
  - Effort: S
  - Dependencies: Task 4.1
  - Acceptance: Invalid paths rejected with clear error

### Phase 4 Verification
- [ ] Final location prompt appears after synthesis
- [ ] Options are clear and appropriate
- [ ] Path validation works
- [ ] Parent directories created when needed
- [ ] Report not moved when "keep in workspace" chosen

---

## Phase 5: Implement Auto-Cleanup After Synthesis

### Code Changes

- [ ] **Task 5.1**: Add cleanup_workspace() function to generate_report.py
  - File: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
  - Lines: After generate_report function (around line 170)
  - Effort: L
  - Dependencies: None
  - Acceptance: Function removes files/dirs safely with error handling

- [ ] **Task 5.2**: Add move and cleanup logic to main()
  - File: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
  - Lines: After report generation (around line 210)
  - Effort: L
  - Dependencies: Task 5.1
  - Acceptance: Report moved if needed, workspace cleaned after successful move

- [ ] **Task 5.3**: Add CLI arguments (--final-path, --no-cleanup, --dry-run)
  - File: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
  - Lines: Argument parser (around line 174)
  - Effort: S
  - Dependencies: None
  - Acceptance: Arguments parsed correctly

- [ ] **Task 5.4**: Add import for shutil module
  - File: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
  - Lines: Top of file with other imports
  - Effort: S
  - Dependencies: None
  - Acceptance: `import shutil` added

### Testing

- [ ] **Task 5.5**: Test full workflow with move and cleanup
  - Command: Create research, synthesize, choose custom path
  - Effort: M
  - Dependencies: All Phase 5 tasks
  - Acceptance: Report moved, workspace cleaned, directory removed if empty

- [ ] **Task 5.6**: Test keep in workspace (no cleanup)
  - Command: Synthesize, choose "keep in workspace"
  - Effort: S
  - Dependencies: Task 5.2
  - Acceptance: No files deleted, all remain in workspace

- [ ] **Task 5.7**: Test --dry-run flag
  - Command: `python3 generate_report.py test --final-path ~/report.md --dry-run`
  - Effort: S
  - Dependencies: Tasks 5.1, 5.3
  - Acceptance: Shows what would be deleted, nothing actually deleted

- [ ] **Task 5.8**: Test --no-cleanup flag
  - Command: `python3 generate_report.py test --final-path ~/report.md --no-cleanup`
  - Effort: S
  - Dependencies: Tasks 5.2, 5.3
  - Acceptance: Report moved, workspace NOT cleaned

- [ ] **Task 5.9**: Test error handling during cleanup
  - Command: Set directory read-only, attempt cleanup
  - Effort: M
  - Dependencies: Task 5.1
  - Acceptance: Errors reported but process continues

### Phase 5 Verification
- [ ] Report moved to final location successfully
- [ ] Intermediate files cleaned up after move
- [ ] Workspace directory removed if empty
- [ ] No cleanup when keeping in workspace
- [ ] Dry-run mode works correctly
- [ ] --no-cleanup flag prevents deletion
- [ ] Errors don't break the process
- [ ] Clear confirmation messages shown

---

## Phase 6: Update Documentation

### README Updates

- [ ] **Task 6.1**: Add Obsidian integration overview to README
  - File: `README.md`
  - Lines: 145-184 (Research Workflow section)
  - Effort: M
  - Dependencies: None
  - Acceptance: Overview explains flexible storage locations

- [ ] **Task 6.2**: Add "Obsidian Integration" subsection to README
  - File: `README.md`
  - Lines: After Step 2 in research workflow
  - Effort: M
  - Dependencies: Task 6.1
  - Acceptance: Setup instructions and example workflow added

### iw-workflow Skill Updates

- [ ] **Task 6.3**: Add Obsidian research workflow to iw-workflow SKILL.md
  - File: `.claude/skills/iw-workflow/SKILL.md`
  - Lines: After line 167
  - Effort: M
  - Dependencies: None
  - Acceptance: "Research with Obsidian Integration" section added with examples

### Research Skill Documentation Updates

- [ ] **Task 6.4**: Update iw-research-planner Step 6 confirmation message
  - File: `.claude/skills/iw-research-planner/SKILL.md`
  - Lines: 145-169
  - Effort: S
  - Dependencies: None
  - Acceptance: Shows workspace, Obsidian integration status, cleanup note

- [ ] **Task 6.5**: Add Step 5 cleanup documentation to iw-research-synthesizer
  - File: `.claude/skills/iw-research-synthesizer/SKILL.md`
  - Lines: After synthesis documentation
  - Effort: M
  - Dependencies: None
  - Acceptance: Cleanup behavior, files removed/kept, confirmation message documented

- [ ] **Task 6.6**: Add workspace config note to iw-research-executor SKILL.md
  - File: `.claude/skills/iw-research-executor/SKILL.md`
  - Lines: Resources or Overview section
  - Effort: S
  - Dependencies: None
  - Acceptance: Notes that scripts use .research-config.json for workspace

### Testing Documentation

- [ ] **Task 6.7**: Verify README examples work
  - File: README.md
  - Effort: M
  - Dependencies: Tasks 6.1-6.2
  - Acceptance: Can follow setup instructions and example workflow successfully

- [ ] **Task 6.8**: Verify iw-workflow examples work
  - File: `.claude/skills/iw-workflow/SKILL.md`
  - Effort: M
  - Dependencies: Task 6.3
  - Acceptance: Example workflow matches actual behavior

- [ ] **Task 6.9**: Check SKILL.md consistency
  - File: All three research SKILL.md files
  - Effort: S
  - Dependencies: Tasks 6.4-6.6
  - Acceptance: All files describe workflow consistently

### Phase 6 Verification
- [ ] README clearly explains Obsidian integration
- [ ] Setup instructions accurate and complete
- [ ] Example workflow works as documented
- [ ] iw-workflow has clear examples
- [ ] All SKILL.md files updated consistently
- [ ] Benefits and requirements clearly stated

---

## Final Verification

### Functional Testing

- [ ] **Full workflow test - Default (.docs/research)**
  - Create research with default location
  - Add findings and sources
  - Synthesize report
  - Keep in workspace
  - Verify: All files in .docs/research/, no cleanup

- [ ] **Full workflow test - Custom path**
  - Create research with custom path ~/Documents/test-research
  - Add findings and sources
  - Synthesize report
  - Move to ~/final.md
  - Verify: Report moved, workspace cleaned

- [ ] **Full workflow test - Obsidian vault**
  - Configure obsidian-local-api
  - Create research in vault root
  - Add findings and sources
  - Synthesize report
  - Move to vault/Research/report.md
  - Verify: Report in vault/Research/, workspace cleaned

### Backward Compatibility Testing

- [ ] **Test existing research without config**
  - Find or create old research in .docs/research/ (no .research-config.json)
  - Run add_finding and add_source scripts
  - Synthesize report
  - Verify: Everything works with fallback to defaults

- [ ] **Test init_research.py without new arguments**
  - Run: `python3 init_research.py test`
  - Verify: Creates in .docs/research/test/, works exactly as before

### Edge Cases

- [ ] **Test with no Obsidian configured**
  - Disable obsidian-local-api
  - Create research
  - Verify: No Obsidian option shown, graceful fallback

- [ ] **Test cleanup with read-only workspace**
  - Create research, make workspace read-only
  - Attempt synthesis with cleanup
  - Verify: Errors reported, process continues

- [ ] **Test with invalid final path**
  - Synthesize report
  - Enter invalid final path (e.g., /root/report.md without permissions)
  - Verify: Error message, re-prompt or fallback

- [ ] **Test with very long research name**
  - Create research with 100+ char name
  - Verify: Handles gracefully (truncates or errors)

### Documentation Verification

- [ ] All code changes have file:line references in plan
- [ ] All SKILL.md updates complete
- [ ] README updated with examples
- [ ] iw-workflow skill updated
- [ ] No broken links in documentation
- [ ] Examples in docs actually work

### Performance & Safety

- [ ] File operations don't hang on large research projects
- [ ] Config file reading is fast (negligible overhead)
- [ ] Cleanup doesn't remove files unexpectedly
- [ ] Report verified before cleanup begins
- [ ] Graceful error handling throughout

---

## Notes

### Implementation Order

Phases should be implemented in order (1-6) as later phases depend on earlier ones.

### Testing Strategy

- Each phase should be tested and verified before moving to next phase
- Manual testing required (no automated tests for skills yet)
- Keep test research projects for regression testing
- Test both happy path and error cases

### Rollback Strategy

If issues discovered:
1. Revert Python script changes (git)
2. Restore SKILL.md documentation
3. Existing research projects unaffected (backward compatible)

### Future Enhancements (Out of Scope)

- ❌ Create notes via Obsidian API instead of files
- ❌ Real-time sync between workspace and Obsidian
- ❌ Automated tests for skills
- ❌ Multi-level config (env vars, project, user)
- ❌ Research templates selection
