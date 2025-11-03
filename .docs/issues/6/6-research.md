# Issue #6 - Research & Working Notes

**Research Date**: 2025-11-03
**Researchers**: Claude + nicj

## Initial Understanding

Research skills (iw-research-planner, iw-research-executor, iw-research-synthesizer) hardcode `.docs/research/` as storage location. This works for git repos but doesn't support personal research stored in Obsidian vaults without git repos.

**User wants to:**
- Use Claude Code for research on technical topics
- Store research in personal Obsidian vault (not tied to code projects)
- Leverage Obsidian features (graph view, links, tags)

## Research Process

### Files Examined:

**Research skill scripts (all hardcode `.docs/research/`):**
- `.claude/skills/iw-research-planner/scripts/init_research.py:22`
  - `base_path: Path = Path(".docs/research")` hardcoded as default
  - Creates research directory structure and template files

- `.claude/skills/iw-research-executor/scripts/add_finding.py:12`
  - `research_dir = Path(".docs/research") / research_name`
  - Adds findings to findings.md organized by theme

- `.claude/skills/iw-research-executor/scripts/add_source.py:12`
  - `research_dir = Path(".docs/research") / research_name`
  - Adds sources to sources.md file

- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py:108`
  - `research_dir = Path(".docs/research") / research_name`
  - Generates final research report from findings

**Configuration pattern to follow:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:68-118`
  - Shows multi-level configuration precedence
  - Environment vars → Project config → User config → Defaults
  - Good model for storage path configuration

**Obsidian API integration:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py`
  - Provides REST API client for Obsidian operations
  - Can create/read/update/delete notes in vault
  - Handles authentication and connection management

### Sub-tasks Spawned:

1. **Find research skill files** (Explore agent)
   - Result: Found all 3 research skills and their Python scripts
   - Key discovery: All scripts hardcode `.docs/research` path

2. **Find storage location patterns** (Explore agent)
   - Result: No environment detection or configuration exists
   - Key discovery: Obsidian skill shows good configuration pattern to follow

3. **Find iw-init and directory structure** (Explore agent)
   - Result: iw-init creates `.docs/` structure but doesn't configure paths
   - Key discovery: No dynamic path configuration anywhere

### Questions Asked & Answers:

1. Q: When should skills ask users where to store research?
   A: **Always ask at start** of research creation
   Follow-up: Will prompt every time user runs `/iw-research-plan`

2. Q: What should default storage location be?
   A: **.docs/research (current)** - keep current behavior as default
   Follow-up: If user just hits enter, use existing behavior

3. Q: Should we integrate with obsidian-local-api skill?
   A: **Yes, full integration** - use Obsidian REST API for vault storage
   Follow-up: Will use API to create notes directly in vault

4. Q: How should configuration precedence work?
   A: **Ask first, then save** - prompt user, save choice to config
   Follow-up: Will create `.research-config.json` to save preferences

### Clarifications from User:

**🚨 CRITICAL CLARIFICATION:**

**Initial assumption:** Research files stay where created
**Actual requirement:**
- Research work happens in **workspace** (temporary location)
- Final report goes to **user-specified final location**
- **Intermediate files cleaned up** after synthesis
- Only final `research-report.md` remains

**For Obsidian:**
- Working files in **vault root** during research (for live preview/linking)
- Final report **moves to user-specified location** within vault
- **Cleanup removes** temporary working files (research-plan.md, sources.md, findings.md, assets/)

**Additional clarifications:**

5. Q: Should workspace location offer Obsidian vault root as option?
   A: **Yes, detect vault** - auto-detect via obsidian-local-api and offer as option
   Follow-up: Will check if Obsidian is configured and suggest vault root

6. Q: When should we clean up intermediate files?
   A: **Auto after synthesis** - automatically delete working files when report generated
   Follow-up: No user prompt, automatic cleanup after successful synthesis

7. Q: Should final report location have a default?
   A: **Always ask explicitly** - never default, always require user to specify
   Follow-up: Will prompt for final location every time during synthesis

## Key Discoveries

### Technical Discoveries:

- **No configuration layer exists**: All paths are hardcoded, no env vars or config files
- **Obsidian skill shows pattern**: Environment → Project config → User config → Defaults
- **Two-location pattern needed**: Workspace (temporary) + Final destination (permanent)
- **Cleanup is missing**: No cleanup logic exists in current synthesizer
- **Obsidian API is available**: Full REST API client exists for vault operations

### Patterns to Follow:

**From obsidian_client.py:68-118 - Configuration precedence:**
```python
def _load_config_value(self, key: str, default: Any = None) -> Any:
    # 1. Check environment variables
    env_key = f"OBSIDIAN_{key.upper()}"
    env_value = os.environ.get(env_key)

    # 2. Check project-level config
    project_config = Path.cwd() / ".obsidian-api.json"

    # 3. Check user-level config
    user_config = Path.home() / ".obsidian-api" / "config.json"

    return default
```

**Current init pattern from init_research.py:22:**
```python
def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")):
    research_dir = base_path / research_name
    # Creates: research-plan.md, sources.md, findings.md, assets/
```

**Pattern to implement:**
```python
# 1. Detect Obsidian vault (if configured)
# 2. Prompt user for workspace location
# 3. Save choice to config
# 4. Use choice for all file operations
# 5. At synthesis: prompt for final location
# 6. Move report, cleanup workspace
```

### Constraints Identified:

- **Backward compatibility**: Must work with existing .docs/research usage
- **No breaking changes**: Default behavior should remain the same
- **Obsidian optional**: Should work without Obsidian configured
- **User experience**: Minimize prompts, save preferences
- **Cleanup safety**: Only cleanup after successful synthesis

## Design Decisions

### Decision 1: Two-Location Approach (Workspace + Final)

**Options considered:**
- Option A: Single location, keep all files - Simple but clutters workspace
- Option B: Two locations with auto-cleanup - More complex but cleaner

**Chosen**: Option B (Two locations with auto-cleanup)

**Rationale**:
- User explicitly requested cleanup of intermediate files
- Keeps final vault/storage clean
- Workspace can be vault root for live Obsidian preview
- Final location can be organized folder structure

### Decision 2: When to Prompt for Locations

**Options considered:**
- Option A: Both locations at planning time - Annoying, user doesn't know final location yet
- Option B: Workspace at planning, final at synthesis - Logical workflow progression
- Option C: Never prompt, use config only - Not user-friendly for first use

**Chosen**: Option B (Split prompts)

**Rationale**:
- Workspace needed at start for file creation
- Final location only relevant after research complete
- User can see results before deciding where to store
- Matches natural research workflow

### Decision 3: Obsidian Vault Detection

**Options considered:**
- Option A: Always ask for vault path - Annoying for configured users
- Option B: Auto-detect via API, offer as option - Seamless UX
- Option C: No detection, manual only - Misses automation opportunity

**Chosen**: Option B (Auto-detect and offer)

**Rationale**:
- obsidian-local-api skill provides vault detection via API
- Can check if Obsidian configured and running
- Offer vault root as convenient option
- Still allow manual path entry

### Decision 4: Cleanup Timing

**Options considered:**
- Option A: Ask user before cleanup - Extra prompt, annoying
- Option B: Auto cleanup after synthesis - Clean, automated
- Option C: Manual cleanup command - User forgets, cluttered workspace

**Chosen**: Option B (Auto cleanup)

**Rationale**:
- User explicitly requested auto cleanup
- Only happens after successful synthesis
- Show confirmation of what was cleaned
- Can always add manual command later if needed

### Decision 5: Configuration Storage

**Options considered:**
- Option A: Match Obsidian pattern (env + project + user configs) - Complex, maybe overkill
- Option B: Simple project config only - Easy, sufficient for now
- Option C: Prompt every time, no config - Annoying UX

**Chosen**: Option B (Simple project config)

**Rationale**:
- Store workspace preference in `.research-config.json` in research directory
- Simpler than multi-level config
- Can expand later if needed
- Per-research configuration makes sense (different research, different storage)

## Open Questions (During Research)

- [x] **Where are paths hardcoded?** - Resolved: All 4 Python scripts hardcode `.docs/research`
- [x] **Is there existing configuration?** - Resolved: No, completely hardcoded
- [x] **How does Obsidian integration work?** - Resolved: Via obsidian-local-api skill with REST API
- [x] **What configuration pattern to follow?** - Resolved: Simpler version of Obsidian pattern
- [x] **When to prompt user?** - Resolved: Workspace at planning, final at synthesis
- [x] **When to cleanup?** - Resolved: Auto after synthesis
- [x] **What files to cleanup?** - Resolved: All except final research-report.md

## Code Snippets Reference

### Current Hardcoded Path Pattern:

```python
# From iw-research-planner/scripts/init_research.py:22
def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")) -> dict:
    """Create research directory structure."""
    research_dir = base_path / research_name
    # ...
```

```python
# From iw-research-executor/scripts/add_finding.py:12
def add_finding(research_name: str, theme: str, finding: str, source_ref: str):
    """Add finding to findings.md under specified theme."""
    research_dir = Path(".docs/research") / research_name
    # ...
```

### Obsidian Configuration Pattern to Adapt:

```python
# From obsidian-local-api/scripts/obsidian_client.py:68-118
def _load_config_value(self, key: str, default: Any = None) -> Any:
    """
    Load configuration value from environment or config files.

    Precedence:
    1. Environment variables
    2. Project-level .obsidian-api.json
    3. User-level ~/.obsidian-api/config.json
    4. Default value
    """
    # Environment check
    env_key = f"OBSIDIAN_{key.upper()}"
    env_value = os.environ.get(env_key)
    if env_value is not None:
        return env_value

    # Project config check
    project_config = Path.cwd() / ".obsidian-api.json"
    if project_config.exists():
        with open(project_config, 'r') as f:
            config = json.load(f)
            if key in config:
                return config[key]

    return default
```

### Obsidian API Usage:

```python
# From obsidian-local-api/scripts/obsidian_client.py:35-66
class ObsidianClient:
    def __init__(self, api_key=None, host=None, port=None, use_https=None):
        self.api_key = api_key or self._load_config_value("api_key")
        self.host = host or self._load_config_value("host", "localhost")
        # ...

    def post(self, endpoint, data=None, json_data=None):
        """Send POST request to create/update notes"""
        # ...

    def get(self, endpoint):
        """Send GET request to read notes"""
        # ...
```

## Corrections During Planning

None - user clarifications captured above were not corrections but helpful design input.

## Summary for Implementation

**What needs to change:**
1. Add workspace location prompt to iw-research-planner
2. Add Obsidian vault detection using obsidian-local-api
3. Update all Python scripts to accept workspace path parameter
4. Add final location prompt to iw-research-synthesizer
5. Implement auto-cleanup after synthesis
6. Update all SKILL.md files with new workflow
7. Update README.md and iw-workflow skill documentation

**Key files to modify:**
- `.claude/skills/iw-research-planner/SKILL.md` - Add workspace prompting
- `.claude/skills/iw-research-planner/scripts/init_research.py` - Accept workspace path
- `.claude/skills/iw-research-executor/scripts/add_finding.py` - Use config for paths
- `.claude/skills/iw-research-executor/scripts/add_source.py` - Use config for paths
- `.claude/skills/iw-research-synthesizer/SKILL.md` - Add final location & cleanup
- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py` - Move & cleanup
- `README.md` - Document Obsidian integration
- `.claude/skills/iw-workflow/SKILL.md` - Add Obsidian research workflow

**Implementation approach:**
- 6 phases: Workspace selection, final location prompt, storage abstraction, cleanup, documentation, testing
- Backward compatible with existing `.docs/research/` usage
- Optional Obsidian integration (graceful degradation)
- Auto-cleanup with confirmation messages
