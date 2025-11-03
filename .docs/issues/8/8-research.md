# Issue #8 - Research & Working Notes

**Research Date**: 2025-11-03
**Researchers**: Claude + nicj

## Initial Understanding

Issue #8 is about adding filesystem fallback to the Obsidian Local API skill to handle large files that fail via the REST API. This is blocking issue #6 (research skills with Obsidian integration) because large research reports timeout when written through the API.

The Obsidian REST API has a fixed 120-second timeout for all operations, which is insufficient for large markdown files (>1MB). The solution is to add transparent filesystem fallback that maintains backward compatibility while solving the large file problem.

## Research Process

### Files Examined:

1. **`.claude/skills/obsidian-local-api/scripts/obsidian_client.py`** (lines 1-323)
   - Finding: Fixed 120s timeout at line 159
   - Finding: No retry logic or fallback mechanisms
   - Finding: Multi-level config loading pattern (ENV > Project > User) at lines 68-118
   - Relevant code pattern: `_load_config_value()` method for hierarchical config

2. **`.claude/skills/obsidian-local-api/scripts/config_helper.py`** (lines 1-275)
   - Finding: Interactive setup pattern at lines 168-230
   - Finding: Config storage in `~/.obsidian-api/config.json`
   - Finding: Secure permissions (0o600) at line 92
   - Relevant code pattern: User prompting with current value display

3. **`.claude/skills/obsidian-local-api/scripts/create_note.py`** (lines 118-131)
   - Finding: Direct API call via `client.put()` with no fallback
   - Finding: Simple error handling, operation fails if API fails

4. **`.claude/skills/obsidian-local-api/scripts/read_note.py`** (lines 53-90)
   - Finding: Direct API call via `client.get()` with no fallback
   - Finding: JSON format support that needs to be maintained

5. **`.claude/skills/obsidian-local-api/scripts/append_note.py`** (lines 60-91)
   - Finding: Uses POST for append, PATCH for heading insertion
   - Finding: No fallback mechanism

### Sub-tasks Spawned:

1. **Explore Obsidian skill scripts**
   - Result: Found complete implementation details of API operations
   - Key discovery: All operations go through ObsidianClient class methods

2. **Find configuration patterns**
   - Result: Multi-level config precedence well established
   - Key discovery: Can extend existing config schema with vault_path

3. **Analyze error handling patterns**
   - Result: Consistent tuple return pattern (success, data, error)
   - Key discovery: Can wrap existing methods with fallback logic

### Questions Asked & Answers:

1. Q: When should the skill fall back to filesystem operations?
   A: Always try API first, fallback on any error
   Follow-up research: This maintains maximum compatibility with Obsidian features

2. Q: How should we prompt for vault path when needed?
   A: Prompt once, store permanently
   Follow-up research: User config pattern already established in config_helper.py

3. Q: Should we add a file size threshold configuration?
   A: No threshold - only fallback on errors
   Follow-up research: Keep it simple, let API handle what it can

## Key Discoveries

### Technical Discoveries:
- Fixed 120s timeout at obsidian_client.py:159 is the root cause
- No existing retry or fallback logic anywhere in the codebase
- Configuration pattern is well-established and extensible
- ObsidianClient class is perfect place to add fallback logic
- Scripts use simple method calls, easy to swap for fallback versions

### Patterns to Follow:
- Multi-level config loading in `obsidian_client.py:68-118`
- Interactive prompting in `config_helper.py:168-230`
- Tuple return pattern `(success, data, error)` everywhere
- Security-conscious file permissions (0o600) for config files

### Constraints Identified:
- Must maintain backward compatibility (no breaking changes)
- Must preserve API as primary method (try-API-first)
- Must support existing JSON format in read operations
- Must handle path traversal attacks in filesystem operations

## Design Decisions

### Decision 1: Try-API-First Pattern
**Options considered:**
- Option A: Always use filesystem when available
- Option B: Check file size and choose method
- Option C: Try API first, fallback on error (CHOSEN)

**Chosen**: Option C
**Rationale**: Maintains maximum compatibility with Obsidian features (plugins, caching, live updates) while providing fallback when needed. No breaking changes.

### Decision 2: Vault Path Prompting
**Options considered:**
- Option A: Prompt on every operation
- Option B: Require manual configuration
- Option C: Prompt once, save permanently (CHOSEN)

**Chosen**: Option C
**Rationale**: Best user experience - seamless fallback after one-time setup. Follows existing config pattern.

### Decision 3: Implementation Location
**Options considered:**
- Option A: Add to individual scripts
- Option B: Add to ObsidianClient class (CHOSEN)
- Option C: Create separate wrapper

**Chosen**: Option B
**Rationale**: Centralized logic, minimal script changes, maintains single source of truth.

### Decision 4: No File Size Threshold
**Options considered:**
- Option A: Check file size before API call
- Option B: Use configurable threshold
- Option C: No threshold, error-based only (CHOSEN)

**Chosen**: Option C
**Rationale**: Simpler implementation, lets API handle what it can, fallback handles failures naturally.

## Open Questions (During Research)

- [x] How to detect vault path from API? - Resolved: Attempt API call to /vault/, handle gracefully if not available
- [x] How to handle path traversal security? - Resolved: Use Path.resolve().relative_to() validation
- [x] Should we support .md extension auto-addition? - Resolved: Yes, filesystem matches API behavior
- [x] How to preserve JSON format in read operations? - Resolved: Wrap filesystem result in JSON structure when needed

**Note**: All questions were resolved during planning phase.

## Code Snippets Reference

### Relevant Existing Code:

```python
# From obsidian_client.py:68-118
# Multi-level config loading pattern to follow
def _load_config_value(self, key: str, default: Any = None) -> Any:
    # Check environment variables
    env_key = f"OBSIDIAN_{key.upper()}"
    env_value = os.environ.get(env_key)
    if env_value is not None:
        return env_value

    # Check project-level config
    project_config = Path.cwd() / ".obsidian-api.json"
    if project_config.exists():
        try:
            with open(project_config, 'r') as f:
                config = json.load(f)
                if key in config:
                    return config[key]
        except (json.JSONDecodeError, IOError):
            pass

    # Check user-level config
    user_config = Path.home() / ".obsidian-api" / "config.json"
    # ... similar pattern

    return default
```

```python
# From config_helper.py:168-195
# Interactive prompting pattern to follow
def interactive_setup():
    print("Obsidian API Configuration Setup")
    print("=" * 50)

    config = load_config()

    # API Key
    current_key = config.get('api_key', '')
    if current_key:
        masked = current_key[:4] + "*" * 8 + current_key[-4:] if len(current_key) > 8 else "****"
        print(f"Current API key: {masked}")

    api_key = input("\nEnter API key (or press Enter to keep current): ").strip()
    if api_key:
        config['api_key'] = api_key
```

### Similar Patterns Found:

```python
# From create_note.py:118-131
# Current pattern - to be wrapped with fallback
success, data, error = client.put(
    endpoint,
    data=note_content,
    headers={"Content-Type": "text/markdown"}
)

# New pattern with fallback
success, data, error = client.put_with_fallback(path, note_content)
```

## Corrections During Planning

No corrections were needed during planning. User confirmed design decisions through AskUserQuestion tool.

## Learnings

- **2025-11-03** Obsidian REST API has fixed 120s timeout → Filesystem fallback needed for large files - This affects all operations on files >1MB and should be documented as a limitation of the API approach
- **2025-11-03** Try-API-first pattern preferred over filesystem-first → Maintains Obsidian feature compatibility while providing reliability - Future integrations should follow this pattern
- **2025-11-03** Lazy prompting (prompt when needed) better UX than requiring pre-configuration → Users only configure fallback when they actually need it - Should apply to other optional features

## Implementation Notes

Implementation completed in 5 phases as planned:
1. Added vault_path to configuration system
2. Created filesystem_ops.py module with security checks
3. Added fallback methods to ObsidianClient class
4. Updated script files to use fallback methods
5. Updated documentation with fallback behavior

No deviations from plan were necessary.
