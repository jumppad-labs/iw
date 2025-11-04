# Issue #10 - Context & Dependencies

**Last Updated**: 2025-11-03

## Quick Summary

Replace HTTP-based file downloads in `/iw-install` with a git clone strategy. The current implementation makes 80-100+ GitHub API requests per installation, exceeding the 60 requests/hour unauthenticated limit. The new approach clones the repository once (5-10 seconds) and copies files locally, eliminating rate limiting entirely.

## Key Files & Locations

### Files to Modify:

- `.claude/skills/iw-install/scripts/manage_workflow.py` - Main installation script
  - Add `_clone_repository()` method (after line 85)
  - Add `_copy_files_from_clone()` method (after line 155)
  - Add `_cleanup_clone()` method (after line 225)
  - Replace `install()` method implementation (lines 205-301)
  - Remove obsolete HTTP methods: `_fetch_url()`, `_fetch_json()`, `_list_directory_contents()`, `_download_file()`, `_download_directory()` (lines 86-195)
  - Remove obsolete constants: `GITHUB_API_BASE`, `GITHUB_RAW_BASE` (lines 31-32)

- `.claude/skills/iw-install/SKILL.md` - Documentation
  - Update Requirements section (lines 332-340): Make git required, remove curl
  - Update Installation Process section (lines 124-167): Document git clone approach
  - Update Troubleshooting section (lines 367-388): Git-specific troubleshooting
  - Update Important Notes section (lines 359-365): Add git requirement and rate limit fix notes

### Files to Reference:

- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:120-187` - HTTP error handling pattern
- `.claude/skills/obsidian-local-api/scripts/filesystem_ops.py:70-83` - File operation error handling pattern
- `.docs/knowledge/learnings/installation.md` - User correction documented

### Test Files:

No test files to modify - this uses integration testing via manual execution of the installation script.

## Dependencies

### Code Dependencies:

- **subprocess** (line 20) - Already imported, used for git clone
- **tempfile** - Need to import for temporary directory creation
- **shutil** - Already used in uninstall(), will use for file copying and cleanup
- **Path/pathlib** (line 22) - Already imported

### External Dependencies:

- **git** - Required for cloning repository (check with `git --version`)
- **GitHub** - Repository must be accessible at https://github.com/jumppad-labs/iw
- **Internet connection** - For git clone operation

## Key Technical Decisions

1. **Git Clone Over Token Auth**: Use `git clone` instead of adding GitHub token authentication - simpler and eliminates rate limiting entirely

2. **Shallow Clone**: Use `--depth 1` for faster downloads and less disk space

3. **Temporary Directory**: Clone to temp directory, copy files, then clean up - no caching between installations

4. **Error Handling**: Fail with clear error message if git not installed - no fallback to HTTP method (keep code simple)

5. **Progress Output**: Suppress git output, show simple progress messages - cleaner user experience

6. **No Breaking Changes**: Maintain same command syntax, output format, and directory structure - transparent to users

## Integration Points

- **Installation Flow**: `install()` method used by both fresh installation and updates
- **Update Operation**: `update()` method calls `install()`, so updates automatically get new behavior
- **Verify Operation**: No changes needed, verifies installed files regardless of installation method
- **Uninstall Operation**: No changes needed, doesn't use network
- **List Operation**: No changes needed, lists installed files locally

## Environment Requirements

- **Python version**: 3.7+ (unchanged)
- **Git**: Required (was optional, now required)
- **Internet connection**: Required for git clone
- **Disk space**: ~5-10 MB for temporary clone (automatically cleaned up)
- **Write permissions**: Target directory (.claude/ or ~/.claude/)

## Related Documentation

- **Original Issue**: GitHub Issue #10 - /iw-install getting rate limited by github
- **Research Notes**: `10-research.md` - Detailed research process and findings
- **Implementation Plan**: `10-plan.md` - Phase-by-phase implementation guide
- **Task Checklist**: `10-tasks.md` - Actionable task breakdown
- **Learning Documented**: `.docs/knowledge/learnings/installation.md` - User correction about git clone approach
