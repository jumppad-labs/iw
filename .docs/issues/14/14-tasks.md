# Issue #14 - Task Checklist

**Last Updated**: 2025-11-04 10:35
**Status**: Not Started

## Phase 1: UTF-8 Encoding Support

- [ ] **Task 1.1**: Add UTF-8 encoding configuration to manage_workflow.py
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:1-15`
  - Effort: S
  - Dependencies: None
  - Acceptance: Add `sys.stdout`/`stderr` UTF-8 wrapper for Windows before imports

- [ ] **Task 1.2**: Add platform import to manage_workflow.py
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:19`
  - Effort: S
  - Dependencies: Task 1.1
  - Acceptance: `import platform` added to imports section

- [ ] **Task 1.3**: Update _make_executable() method for platform awareness
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:233-239`
  - Effort: S
  - Dependencies: Task 1.2
  - Acceptance: Add Windows check, return early if Windows, update docstring

### Phase 1 Verification
- [ ] Run: `python3 -m py_compile .claude/skills/iw-install/scripts/manage_workflow.py`
- [ ] Run: `python3 .claude/skills/iw-install/scripts/manage_workflow.py list --location user`
- [ ] Verify: Unicode characters display on Windows console
- [ ] Verify: No UnicodeEncodeError on Windows
- [ ] Verify: No chmod warnings on Windows
- [ ] Verify: chmod still works on Unix systems

---

## Phase 2: Pure Python Bootstrap

- [ ] **Task 2.1**: Create bootstrap.py script
  - File: `bootstrap.py` (new file, ~475 lines)
  - Effort: L
  - Dependencies: None
  - Acceptance: Complete Python bootstrap with UTF-8 config, user prompts, downloads, error handling

- [ ] **Task 2.2**: Add deprecation notice to bootstrap.sh
  - File: `bootstrap.sh:1-6`
  - Effort: S
  - Dependencies: Task 2.1 completed
  - Acceptance: Add comment block explaining deprecation, pointing to bootstrap.py

### Phase 2 Verification
- [ ] Run: `python3 -m py_compile bootstrap.py`
- [ ] Run: `python3 -c "exec(open('bootstrap.py').read())"` (check for syntax errors)
- [ ] Test on Windows: `python3 bootstrap.py` (select user-level)
- [ ] Test on macOS: `python3 bootstrap.py` (select project-level)
- [ ] Test on Linux: `python3 bootstrap.py` (select user-level)
- [ ] Verify: Files download successfully
- [ ] Verify: Directory structure created correctly
- [ ] Verify: Network errors handled gracefully

---

## Phase 3: Pure Python Hooks

- [ ] **Task 3.1**: Create load_workflow.py hook
  - File: `.claude/hooks/load_workflow.py` (new file, ~25 lines)
  - Effort: S
  - Dependencies: None
  - Acceptance: Python version of load_workflow.sh with UTF-8 config

- [ ] **Task 3.2**: Create check_workflow_version.py hook
  - File: `.claude/hooks/check_workflow_version.py` (new file, ~35 lines)
  - Effort: M
  - Dependencies: None
  - Acceptance: Python version with Path.exists() checks for opt-out and skill

- [ ] **Task 3.3**: Create list_skills.py hook
  - File: `.claude/hooks/list_skills.py` (new file, ~110 lines)
  - Effort: L
  - Dependencies: None
  - Acceptance: Python version with git detection, YAML parsing, skill listing

- [ ] **Task 3.4**: Add deprecation notices to bash hooks
  - File: `.claude/hooks/load_workflow.sh:1-6`
  - File: `.claude/hooks/check_workflow_version.sh:1-6`
  - File: `.claude/hooks/list_skills.sh:1-6`
  - Effort: S
  - Dependencies: Tasks 3.1, 3.2, 3.3 completed
  - Acceptance: Add comment blocks explaining deprecation for all three hooks

- [ ] **Task 3.5**: Update HOOKS list in manage_workflow.py
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:54-58`
  - Effort: S
  - Dependencies: Tasks 3.1, 3.2, 3.3 completed
  - Acceptance: Add three .py hook files to HOOKS list with comments

- [ ] **Task 3.6**: Update hook installation logic in manage_workflow.py
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:184-188`
  - Effort: S
  - Dependencies: Task 3.5
  - Acceptance: Update comment to clarify only .sh files need chmod

### Phase 3 Verification
- [ ] Run: `python3 -m py_compile .claude/hooks/load_workflow.py`
- [ ] Run: `python3 -m py_compile .claude/hooks/check_workflow_version.py`
- [ ] Run: `python3 -m py_compile .claude/hooks/list_skills.py`
- [ ] Test: `python3 .claude/hooks/load_workflow.py` (verify output)
- [ ] Test: `python3 .claude/hooks/check_workflow_version.py` (verify opt-out logic)
- [ ] Test: `python3 .claude/hooks/list_skills.py` (verify skill listing)
- [ ] Test on Windows: All three hooks execute without errors
- [ ] Verify: YAML frontmatter parsing works (multi-line descriptions)
- [ ] Verify: Git repository detection works correctly

---

## Phase 4: Documentation Updates

- [ ] **Task 4.1**: Update README.md installation section
  - File: `README.md` (installation section)
  - Effort: M
  - Dependencies: Phases 1-3 completed
  - Acceptance: Add cross-platform instructions, Python bootstrap recommended, platform notes

- [ ] **Task 4.2**: Add Windows support section to iw-install SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md` (after Requirements section)
  - Effort: S
  - Dependencies: Phases 1-3 completed
  - Acceptance: Document Windows compatibility, requirements, known issues

### Phase 4 Verification
- [ ] Test: Follow README instructions on Windows (verify steps work)
- [ ] Test: Follow README instructions on macOS (both Python and bash)
- [ ] Test: Follow README instructions on Linux (Python bootstrap)
- [ ] Verify: All commands in README are correct
- [ ] Verify: Requirements are accurately documented
- [ ] Verify: Links are valid

---

## Final Verification

### End-to-End Installation Tests:

**Windows PowerShell:**
- [ ] Clean environment: `Remove-Item -Recurse -Force ~\.claude -ErrorAction SilentlyContinue`
- [ ] Bootstrap: `python3 bootstrap.py` (select user-level)
- [ ] Install: `python3 ~\.claude\skills\iw-install\scripts\manage_workflow.py install --location user`
- [ ] Verify: `python3 ~\.claude\skills\iw-install\scripts\manage_workflow.py verify --location user`
- [ ] Test hooks: Run all three Python hooks successfully

**macOS:**
- [ ] Clean environment: `rm -rf ~/.claude`
- [ ] Bootstrap: `python3 bootstrap.py` (select project-level)
- [ ] Install: `python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location project`
- [ ] Verify: `python3 .claude/skills/iw-install/scripts/manage_workflow.py verify --location project`
- [ ] Test hooks: Run all three Python hooks successfully

**Linux:**
- [ ] Clean environment: `rm -rf ~/.claude`
- [ ] Bootstrap: `python3 bootstrap.py` (select user-level)
- [ ] Install: `python3 ~/.claude/skills/iw-install/scripts/manage_workflow.py install --location user`
- [ ] Verify: `python3 ~/.claude/skills/iw-install/scripts/manage_workflow.py verify --location user`
- [ ] Test hooks: Run all three Python hooks successfully

### Unicode Display Tests:
- [ ] Windows PowerShell: Verify ✓, ✗, ✅, ❌ display correctly
- [ ] Windows Command Prompt: Verify Unicode or ASCII fallback
- [ ] Windows Terminal: Verify Unicode displays
- [ ] macOS Terminal: Verify Unicode displays
- [ ] Linux gnome-terminal: Verify Unicode displays

### Edge Case Tests:
- [ ] Path with spaces: Create directory "test dir with spaces", run bootstrap, verify success
- [ ] Network error: Disconnect network, run bootstrap.py, verify graceful error message
- [ ] Invalid user input: Enter "3" at bootstrap prompt, verify validation error and retry
- [ ] Missing git: Rename git executable, run manage_workflow.py, verify error message
- [ ] Opt-out version check: Create .no-version-check file, verify check_workflow_version.py skips

### Backward Compatibility Tests:
- [ ] Unix bash bootstrap: Run `bash bootstrap.sh`, verify still works
- [ ] Unix bash hooks: Verify .sh hooks still execute on Unix
- [ ] No warnings: Verify no deprecation warnings shown to user during normal operation
- [ ] Deprecation notices: Verify notices only visible when reading script source

## File Count Summary

**Files to Create:** 4
- bootstrap.py
- .claude/hooks/load_workflow.py
- .claude/hooks/check_workflow_version.py
- .claude/hooks/list_skills.py

**Files to Modify:** 7
- .claude/skills/iw-install/scripts/manage_workflow.py (3 sections)
- bootstrap.sh (deprecation notice)
- .claude/hooks/load_workflow.sh (deprecation notice)
- .claude/hooks/check_workflow_version.sh (deprecation notice)
- .claude/hooks/list_skills.sh (deprecation notice)
- README.md (installation section)
- .claude/skills/iw-install/SKILL.md (Windows support section)

**Total Tasks:** 18 implementation tasks + verification steps

## Effort Estimates

- **Phase 1**: 3 small tasks = ~30 minutes
- **Phase 2**: 1 large + 1 small = ~2 hours
- **Phase 3**: 3 small + 2 medium + 1 large = ~4 hours
- **Phase 4**: 1 medium + 1 small = ~1 hour
- **Testing**: ~2 hours across all platforms

**Total Estimated Effort**: ~9-10 hours

## Notes Section

*Space for adding notes during implementation*

**Implementation Order:**
1. Phase 1 first - Quick win, unblocks Windows users immediately
2. Phase 2 next - Pure Python bootstrap enables full Windows installation
3. Phase 3 - Hooks complete the cross-platform experience
4. Phase 4 - Documentation makes it discoverable

**Testing Strategy:**
- Test each phase independently before moving to next
- Use multiple Windows terminals (PowerShell, CMD, Windows Terminal)
- Test on clean environments (no existing .claude directory)
- Verify backward compatibility on Unix at each phase
