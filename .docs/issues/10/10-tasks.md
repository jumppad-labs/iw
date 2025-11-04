# Issue #10 - Task Checklist

**Last Updated**: 2025-11-03
**Status**: Not Started

## Phase 1: Add Git Clone Functionality

- [x] **Task 1.1**: Add `_clone_repository()` method
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:85` (insert after `_get_target_dir()`)
  - Effort: M
  - Dependencies: None
  - Acceptance: Method successfully clones repo to temp directory, handles errors gracefully

- [x] **Task 1.2**: Add `_copy_files_from_clone()` method
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:155` (insert after `_clone_repository()`)
  - Effort: M
  - Dependencies: Task 1.1 complete
  - Acceptance: Method copies all files from clone to target, makes hooks executable

- [x] **Task 1.3**: Add `_cleanup_clone()` method
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:225` (insert after `_copy_files_from_clone()`)
  - Effort: S
  - Dependencies: Task 1.2 complete
  - Acceptance: Method removes temporary directory, non-fatal on failure

### Phase 1 Verification

#### Automated:
- [ ] Git clone completes successfully with valid repo
- [ ] Files are copied to correct locations
- [ ] Hook scripts are executable after copy
- [ ] Temporary directory is cleaned up
- [ ] Error handling works for missing git, network issues, permission errors

#### Manual:
- [ ] Test `_clone_repository()` in Python REPL
- [ ] Test `_copy_files_from_clone()` in Python REPL
- [ ] Verify clone takes < 10 seconds on normal connection
- [ ] Verify all 11 skills present after copy
- [ ] Verify all 4 commands present after copy
- [ ] Verify all 2 hooks present and executable
- [ ] Verify temporary directory removed from /tmp

---

## Phase 2: Integrate Git Clone into Installation Flow

- [x] **Task 2.1**: Replace `install()` method implementation
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:205-301`
  - Effort: L
  - Dependencies: Phase 1 complete
  - Acceptance: New install() uses git clone, maintains same output format and error messages

- [x] **Task 2.2**: Remove obsolete HTTP methods
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:86-195`
  - Effort: S
  - Dependencies: Task 2.1 complete
  - Acceptance: Methods `_fetch_url()`, `_fetch_json()`, `_list_directory_contents()`, `_download_file()`, `_download_directory()` removed

- [x] **Task 2.3**: Remove obsolete constants
  - File: `.claude/skills/iw-install/scripts/manage_workflow.py:31-32`
  - Effort: S
  - Dependencies: Task 2.2 complete
  - Acceptance: `GITHUB_API_BASE` and `GITHUB_RAW_BASE` removed, comment added explaining why

### Phase 2 Verification

#### Automated:
- [ ] Run fresh installation: `python3 manage_workflow.py install --location project`
- [ ] Run 5 consecutive installations without errors
- [ ] Run verification: `python3 manage_workflow.py verify --location project`
- [ ] Run update operation: `python3 manage_workflow.py update --location project`
- [ ] Run user-level installation: `python3 manage_workflow.py install --location user`
- [ ] Installation is faster than old method (< 10 seconds vs 30-60 seconds)

#### Manual:
- [ ] No HTTP 403 or rate limit errors in output
- [ ] Skills load correctly in Claude Code after installation
- [ ] Commands are available: `/iw-help`, `/iw-plan`, etc.
- [ ] Hooks execute correctly (if configured)
- [ ] Installation output is clear and informative
- [ ] Error messages provide helpful troubleshooting steps

#### Error Scenarios:
- [ ] Test with git not installed (Docker container without git)
- [ ] Test with network disconnected during clone
- [ ] Test with target directory read-only
- [ ] Test with insufficient disk space

---

## Phase 3: Update Documentation

- [x] **Task 3.1**: Update Requirements section in SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md:332-340`
  - Effort: S
  - Dependencies: Phase 2 complete
  - Acceptance: Git listed as required, curl removed, clarifications added

- [x] **Task 3.2**: Update Installation Process section in SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md:124-167`
  - Effort: S
  - Dependencies: Task 3.1 complete
  - Acceptance: Documentation reflects git clone approach, step-by-step process updated

- [x] **Task 3.3**: Update Troubleshooting section in SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md:367-388`
  - Effort: M
  - Dependencies: Task 3.2 complete
  - Acceptance: Git-specific troubleshooting added, rate limiting section updated

- [x] **Task 3.4**: Update Important Notes section in SKILL.md
  - File: `.claude/skills/iw-install/SKILL.md:359-365`
  - Effort: S
  - Dependencies: Task 3.3 complete
  - Acceptance: Git requirement noted, rate limit fix mentioned

### Phase 3 Verification

#### Automated:
- [ ] No broken links in documentation
- [ ] All code examples are syntactically correct

#### Manual:
- [ ] Documentation accurately describes new behavior
- [ ] Troubleshooting steps are clear and actionable
- [ ] Requirements section is accurate
- [ ] New users can understand the installation process
- [ ] Migration from old approach is transparent to users

---

## Final Verification

### Automated Checks:

- [ ] **Fresh Installation**: Remove .claude/, install from scratch, verify all components present
- [ ] **Rapid Installations**: Run 10 consecutive installations, all succeed without rate limit errors
- [ ] **Update Operation**: Install, then update, verify no errors
- [ ] **User Installation**: Install to ~/.claude/, verify works correctly
- [ ] **Verification Check**: Run `python3 manage_workflow.py verify`, all checks pass
- [ ] **Performance**: Installation completes in < 10 seconds on normal connection

### Manual Checks:

- [ ] **Claude Code Integration**: Skills load and commands work after installation
- [ ] **Error Messages**: Test error scenarios, verify messages are helpful
- [ ] **Documentation Accuracy**: Read through updated docs, verify all accurate
- [ ] **No Regressions**: Verify uninstall, verify, and list operations still work
- [ ] **Rate Limiting Fixed**: Multiple rapid installations succeed (this was the goal!)

## Notes Section

### Implementation Notes:
<!-- Add notes during implementation here -->

### Testing Notes:
<!-- Add testing findings here -->

### Issues Encountered:
<!-- Document any issues and resolutions here -->
