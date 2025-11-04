# Issue #14 - Context & Dependencies

**Last Updated**: 2025-11-04 10:35

## Quick Summary

Create Windows-compatible version of Implementation Workflow installation by converting bash-specific bootstrap script and hooks to pure Python, and adding UTF-8 encoding configuration to handle Unicode output on Windows consoles.

## Key Files & Locations

### Files to Create:
- `bootstrap.py` - New cross-platform Python bootstrap script (replaces bootstrap.sh)
- `.claude/hooks/load_workflow.py` - Python version of load_workflow.sh
- `.claude/hooks/check_workflow_version.py` - Python version of check_workflow_version.sh
- `.claude/hooks/list_skills.py` - Python version of list_skills.sh

### Files to Modify:
- `.claude/skills/iw-install/scripts/manage_workflow.py:1-15` - Add UTF-8 encoding configuration
- `.claude/skills/iw-install/scripts/manage_workflow.py:233-239` - Update _make_executable() for platform awareness
- `.claude/skills/iw-install/scripts/manage_workflow.py:184-188` - Update hook installation to handle .py files
- `README.md` - Update installation instructions for cross-platform support
- `.claude/skills/iw-install/SKILL.md` - Update documentation for Windows

### Files to Deprecate (keep for backward compatibility):
- `bootstrap.sh` - Keep but mark deprecated, add note to use bootstrap.py
- `.claude/hooks/load_workflow.sh` - Keep for Unix backward compatibility
- `.claude/hooks/check_workflow_version.sh` - Keep for Unix backward compatibility
- `.claude/hooks/list_skills.sh` - Keep for Unix backward compatibility

### Files to Reference:
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:92` - Example of chmod usage
- `.claude/skills/iw-version-check/scripts/check_version.py:129-135` - Unicode characters needing UTF-8
- `.claude/skills/skill-creator/scripts/init_skill.py:290` - Unicode characters needing UTF-8
- `.docs/knowledge/learnings/installation.md` - Git clone architecture decision

## Dependencies

### Code Dependencies:
- Python 3.7+ - Standard library only (no external packages)
- Git - Required for cloning repository (already a dependency)
- urllib.request - For downloading initial bootstrap files
- pathlib.Path - For cross-platform path handling
- subprocess - For running git commands
- platform - For platform detection

### External Dependencies:
- None (no new external dependencies)

## Key Technical Decisions

1. **Pure Python Approach**: Convert all bash scripts to Python for true cross-platform compatibility
2. **UTF-8 Encoding at Startup**: Configure sys.stdout/stderr encoding on Windows to support Unicode characters
3. **Platform-Aware chmod**: Only apply Unix file permissions on non-Windows platforms
4. **Backward Compatibility**: Keep .sh files to avoid breaking existing Unix installations
5. **Hook File Extension**: Use .py for Python hooks, Claude Code will invoke via python3 interpreter

## Integration Points

- **Claude Code Hook System**: Hooks in `.claude/hooks/` are executed at session start
  - Must be executable Python scripts
  - Output goes to console
  - Exit code signals success/failure

- **GitHub Repository**: Bootstrap downloads initial files from `https://raw.githubusercontent.com/jumppad-labs/iw/main/`
  - Must handle network errors gracefully
  - Uses urllib for HTTP requests (cross-platform)

- **Git Clone**: manage_workflow.py clones repository with `git clone --depth 1`
  - Already cross-platform (subprocess.run with list arguments)
  - Requires git in PATH on all platforms

## Environment Requirements

- **Python version**: 3.7+ (for pathlib, subprocess.run, and f-strings)
- **Git**: Required on all platforms for repository cloning
- **Environment variables**: None required (uses Path.home() to find user directory)
- **File permissions**: Python scripts don't require executable bit on any platform
- **Terminal encoding**: UTF-8 support recommended but fallback handles ASCII-only terminals

## Platform-Specific Considerations

### Windows:
- Console encoding defaults to cp1252 (not UTF-8)
- No executable bit for files
- Uses `\` path separators (handled by pathlib)
- Git Bash often installed with Git for Windows
- PowerShell available on all modern Windows

### macOS/Linux:
- UTF-8 terminal encoding standard
- Executable bit required for shell scripts
- `/` path separators (handled by pathlib)
- Bash standard shell

### Cross-Platform Compatibility:
- Use `pathlib.Path` for all path operations
- Use `subprocess.run()` with list arguments (never shell=True)
- Configure UTF-8 encoding on Windows only
- Platform detection with `platform.system()`
- Use `Path.home()` instead of $HOME environment variable

## Related Documentation

- Original ticket: [GitHub Issue #14](https://github.com/jumppad-labs/iw/issues/14)
- Research notes: `.docs/issues/14/14-research.md`
- Implementation plan: `.docs/issues/14/14-plan.md`
- Past learnings: `.docs/knowledge/learnings/installation.md`
- Windows bug report: Included in issue #14 description
