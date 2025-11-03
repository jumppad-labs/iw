# Issue #8 - Context & Dependencies

**Last Updated**: 2025-11-03

## Quick Summary

Add filesystem fallback to Obsidian Local API skill to handle large files that timeout via REST API (120s limit). Try-API-first approach with transparent fallback maintains backward compatibility while enabling large file support for issue #6 (research skills integration).

## Key Files & Locations

### Files Modified:

**Configuration Management:**
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:168-270` - Added vault_path prompting in interactive setup
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:112-124` - Added vault_path display with validation
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:308-335` - Added --set-vault-path CLI argument

**Core Client:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:20` - Added sys import
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:314-371` - Added _get_vault_path() method
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:373-407` - Added _try_filesystem_fallback() method
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:409-428` - Added get_with_fallback() method
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:430-454` - Added put_with_fallback() method
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:456-490` - Added append_with_fallback() method

**Script Updates:**
- `.claude/skills/obsidian-local-api/scripts/create_note.py:118-119` - Changed to use put_with_fallback()
- `.claude/skills/obsidian-local-api/scripts/read_note.py:59-61` - Changed to use get_with_fallback()
- `.claude/skills/obsidian-local-api/scripts/append_note.py:63-64` - Changed to use append_with_fallback()

**Documentation:**
- `.claude/skills/obsidian-local-api/SKILL.md:32-91` - Added Fallback Behavior section

### Files Created:

**New Module:**
- `.claude/skills/obsidian-local-api/scripts/filesystem_ops.py` - Complete filesystem operations module with FilesystemOperations class

### Files to Reference:

**Configuration Patterns:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:68-118` - Multi-level config precedence pattern
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:53-97` - Config storage with secure permissions

**Error Handling:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:188-224` - Error parsing and user-friendly messages

## Dependencies

### Code Dependencies:

**Python Standard Library:**
- `pathlib.Path` - Path handling and validation
- `sys` - stderr output for prompts
- `os` - Environment variable access
- `json` - Config file operations

**External Dependencies:**
- `requests` - HTTP client (already required)

**Skill Dependencies:**
- None - self-contained implementation

### External Dependencies:

**Optional:**
- Obsidian with Local REST API plugin - For API operations
  - Falls back to filesystem if not available
  - Graceful degradation

## Key Technical Decisions

1. **Try-API-First Pattern**: Always attempt API before filesystem. Maintains Obsidian feature compatibility (plugins, caching, live updates) while providing reliability fallback.

2. **Lazy Vault Path Prompting**: Only prompt for vault_path when filesystem fallback is actually needed. Better UX than requiring pre-configuration.

3. **Transparent Fallback**: Scripts work identically whether using API or filesystem. Users see informational messages but no behavior changes.

4. **No File Size Threshold**: Simple error-based fallback only. Lets API handle what it can, filesystem handles failures naturally.

5. **Security-First Filesystem**: Path traversal prevention using Path.resolve().relative_to() validation. All paths restricted to vault directory.

6. **Config Persistence**: Vault path saved permanently after first prompt. Future operations use filesystem fallback automatically without re-prompting.

## Integration Points

**With Obsidian REST API:**
- Primary method for all operations
- Returns structured JSON data when available
- Provides plugin integration and live updates

**With Filesystem:**
- Secondary fallback method
- Direct file I/O when API fails
- Obsidian detects changes via file watcher

**With Configuration System:**
- vault_path added to existing config schema
- Uses same multi-level precedence (ENV > Project > User)
- Saved to `~/.obsidian-api/config.json`

**With Issue #6 (Research Skills):**
- Enables large research report creation
- Solves timeout failures for multi-megabyte markdown files
- Unblocks Obsidian vault integration

## Environment Requirements

**Python:**
- Version: 3.6+ (already required by skill)
- No new packages needed

**Obsidian (Optional):**
- Obsidian application running - For API operations
- Local REST API plugin installed and configured - For API operations
- Not required for filesystem fallback

**Filesystem:**
- Read/write access to vault directory
- Sufficient disk space for note files

## Configuration Schema

**Updated ~/.obsidian-api/config.json:**
```json
{
  "api_key": "your-api-key-here",
  "host": "localhost",
  "port": 27124,
  "https": true,
  "vault_path": "/home/user/Documents/ObsidianVault"
}
```

**New field:**
- `vault_path` (string, optional): Absolute path to Obsidian vault root. Used for filesystem fallback operations.

## Related Documentation

- Original ticket: GitHub Issue #8 - https://github.com/jumppad-labs/iw/issues/8
- Related issue: GitHub Issue #6 - https://github.com/jumppad-labs/iw/issues/6
- Implementation plan: `.docs/issues/8/8-plan.md`
- Research notes: `.docs/issues/8/8-research.md`
- Task breakdown: `.docs/issues/8/8-tasks.md`
- Obsidian Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api

## Success Criteria

**Functional:**
- ✅ Large files (>1MB) successfully created via fallback
- ✅ Large files successfully read via fallback
- ✅ Content successfully appended to large files
- ✅ Small files continue using API when available
- ✅ Vault path prompted only when needed
- ✅ Config saved and reused automatically

**Backward Compatibility:**
- ✅ No breaking changes to existing scripts
- ✅ API remains primary method
- ✅ Existing API-only workflows unchanged
- ✅ vault_path optional, not required

**Security:**
- ✅ Path traversal attacks prevented
- ✅ Operations restricted to vault directory
- ✅ Config file has secure permissions (0o600)

**User Experience:**
- ✅ Clear feedback when fallback used
- ✅ One-time vault path prompt
- ✅ Transparent operation regardless of method
- ✅ Helpful error messages

## Performance Characteristics

**API Operations:**
- Best for small files (<1MB)
- 120s timeout limit
- Provides Obsidian integration features

**Filesystem Operations:**
- Best for large files (>1MB)
- No timeout limitations
- Direct I/O, faster for large files

**Fallback Overhead:**
- Zero overhead when API succeeds
- Single prompt on first filesystem use
- Config loaded once per client instance
