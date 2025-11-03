# Issue #6 - Make Research Skills Location-Aware

**Created**: 2025-11-03
**Last Updated**: 2025-11-03
**GitHub Issue**: https://github.com/jumppad-labs/iw/issues/6

## Overview

Enable research skills to work outside of git repositories by making storage locations configurable. Add workspace selection with Obsidian vault auto-detection, final report destination prompts, and automatic cleanup of intermediate files. This allows users to conduct personal research in Obsidian vaults while maintaining backward compatibility with the existing `.docs/research/` workflow.

## Current State Analysis

All three research skills (iw-research-planner, iw-research-executor, iw-research-synthesizer) hardcode `.docs/research/` as the storage location:

### Key Code Locations:

**Hardcoded paths in scripts:**
- `.claude/skills/iw-research-planner/scripts/init_research.py:22` - `base_path: Path = Path(".docs/research")`
- `.claude/skills/iw-research-executor/scripts/add_finding.py:12` - `research_dir = Path(".docs/research") / research_name`
- `.claude/skills/iw-research-executor/scripts/add_source.py:12` - `research_dir = Path(".docs/research") / research_name`
- `.claude/skills/iw-research-synthesizer/scripts/generate_report.py:108` - `research_dir = Path(".docs/research") / research_name`

**No configuration layer:**
- No environment variable support
- No config file reading
- No user prompting for locations
- No Obsidian integration

### Current Implementation Example:

```python
# From .claude/skills/iw-research-planner/scripts/init_research.py:22-29
def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")) -> dict:
    """Create research directory structure."""
    research_dir = base_path / research_name
    created_date = datetime.now().strftime("%Y-%m-%d")

    # Create directories
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "assets").mkdir(exist_ok=True)
```

## Desired End State

Research skills that:
1. **Prompt for workspace location** when creating new research (with Obsidian vault auto-detection)
2. **Prompt for final report location** when synthesis completes
3. **Auto-cleanup intermediate files** after successful synthesis
4. **Support Obsidian vault integration** via obsidian-local-api skill
5. **Maintain backward compatibility** with existing `.docs/research/` workflow
6. **Save preferences** to avoid re-prompting for same research

### Verification:
- Run `/iw-research-plan` and observe workspace location prompt with Obsidian vault option
- Complete research and observe final location prompt during synthesis
- Confirm intermediate files are cleaned up automatically
- Verify existing workflows with `.docs/research/` continue working

## What We're NOT Doing

- ❌ **Not replacing file-based storage with API-only**: Files still written to disk, API is for detection only
- ❌ **Not adding complex multi-level config**: Simple per-research config file only
- ❌ **Not breaking existing research projects**: Backward compatibility maintained
- ❌ **Not implementing database storage**: File-based storage remains
- ❌ **Not adding real-time sync**: Manual file operations, no automatic sync
- ❌ **Not changing iw-planner or iw-executor**: Only research skills affected

## Implementation Approach

**Six-phase implementation:**
1. **Phase 1**: Obsidian detection and workspace selection in iw-research-planner
2. **Phase 2**: Update init_research.py to accept workspace path and save config
3. **Phase 3**: Update executor scripts to read workspace from config
4. **Phase 4**: Add final location prompt and move logic to synthesizer
5. **Phase 5**: Implement auto-cleanup after synthesis
6. **Phase 6**: Update all documentation (README, iw-workflow, SKILL.md files)

**Key design decisions:**
- Two-location pattern: workspace (temporary) + final destination (permanent)
- Split prompting: workspace at start, final at end
- Auto-cleanup: no user prompt, automatic after synthesis
- Simple config: `.research-config.json` per research project

---

## Phase 1: Obsidian Detection & Workspace Selection

### Overview

Add Obsidian vault detection and workspace location prompting to iw-research-planner skill. Check if obsidian-local-api is configured, get vault path via API, and prompt user with detected options plus manual entry.

### Changes Required:

#### 1. Update iw-research-planner SKILL.md - Add Workspace Selection

**File**: `.claude/skills/iw-research-planner/SKILL.md`
**Lines**: After line 34 (after "Extract:" section)
**Changes**: Add new Step 1.5 for workspace selection between current Step 1 and Step 2

**Current structure:**
```markdown
### Step 1: Understand Research Intent
...
### Step 2: Define Research Questions
```

**Proposed changes:**
```markdown
### Step 1: Understand Research Intent
...

### Step 1.5: Select Workspace Location

After understanding intent, determine where to store research files during work.

**Detect Obsidian Vault (if available):**

1. **Check if obsidian-local-api skill is available:**
   ```python
   # Attempt to import or invoke obsidian-local-api skill
   # If successful, proceed with detection
   # If not available, skip Obsidian options
   ```

2. **Test Obsidian API connection:**
   ```bash
   # Use obsidian_client.py to test connection
   python3 .claude/skills/obsidian-local-api/scripts/obsidian_client.py --test
   ```

3. **Get vault information:**
   - If connection successful, get vault path from API
   - Offer vault root as workspace option

**Prompt user for workspace location:**

Present options using AskUserQuestion tool:

```
Where would you like to work on this research?

Options:
1. .docs/research (default) - Standard location in project docs
2. [Obsidian Vault Root] - Your Obsidian vault (if detected)
3. Custom path - Specify a different location

Default: .docs/research
```

**Save choice:**
- Pass selected workspace_path to init_research.py
- Create `.research-config.json` in workspace
- Store: research_name, workspace_path, created_date, obsidian_integration flag

### Step 2: Define Research Questions
(Continue with existing workflow)
```

**Reasoning**: This adds workspace selection as a distinct step in the workflow while maintaining the logical flow of the skill.

#### 2. Add Obsidian Detection Logic to SKILL.md

**File**: `.claude/skills/iw-research-planner/SKILL.md`
**Lines**: After line 183 (in "Resources" section)
**Changes**: Add new subsection explaining Obsidian detection

**Add new section:**
```markdown
### scripts/detect_obsidian.py (New)

Helper script to detect Obsidian vault and test API connection.

**Usage:**
```bash
python3 .claude/skills/iw-research-planner/scripts/detect_obsidian.py
```

**Returns** (JSON):
```json
{
  "available": true,
  "vault_path": "/Users/username/Obsidian/MyVault",
  "vault_name": "MyVault",
  "api_version": "1.5.0"
}
```

**Or if not available:**
```json
{
  "available": false,
  "error": "Obsidian API not configured"
}
```

**Implementation**:
- Attempts to import obsidian_client from obsidian-local-api skill
- Tests API connection
- Queries vault information
- Returns structured result for skill to parse
```

**Reasoning**: Provides clear documentation for the detection mechanism and expected outputs.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test with Obsidian configured:**
   - Configure obsidian-local-api skill
   - Run `/iw-research-plan`
   - Verify vault root appears as option
   - Select vault option
   - Verify research files created in vault

2. **Test without Obsidian:**
   - Disable/unconfigure obsidian-local-api
   - Run `/iw-research-plan`
   - Verify only `.docs/research` and custom path options shown
   - Select `.docs/research`
   - Verify backward compatibility

3. **Test custom path:**
   - Run `/iw-research-plan`
   - Select "Custom path" option
   - Enter custom path (e.g., `~/Documents/Research`)
   - Verify research files created at custom location

### Success Criteria:

#### Automated Verification:
- N/A (skills don't have automated tests yet)

#### Manual Verification:
- [ ] Obsidian vault detected when configured
- [ ] Vault path retrieved correctly from API
- [ ] Workspace prompt shows all relevant options
- [ ] Default to `.docs/research` works (backward compatibility)
- [ ] Custom path entry works
- [ ] Research files created in selected workspace
- [ ] `.research-config.json` created with correct workspace path
- [ ] Graceful fallback when Obsidian not available

---

## Phase 2: Update init_research.py for Configurable Paths

### Overview

Modify init_research.py to accept workspace_path parameter and save configuration. Replace hardcoded `.docs/research` with parameter, create `.research-config.json` to store workspace location.

### Changes Required:

#### 1. Add workspace_path Parameter

**File**: `.claude/skills/iw-research-planner/scripts/init_research.py`
**Lines**: 22-25
**Changes**: Add workspace_path parameter with backward-compatible default

**Current code:**
```python
def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")) -> dict:
    """Create research directory structure."""
    research_dir = base_path / research_name
    created_date = datetime.now().strftime("%Y-%m-%d")
```

**Proposed changes:**
```python
def create_research_structure(
    research_name: str,
    workspace_path: Optional[str] = None,
    obsidian_integration: bool = False
) -> dict:
    """
    Create research directory structure.

    Args:
        research_name: Name of the research project
        workspace_path: Custom workspace location (default: .docs/research)
        obsidian_integration: Whether using Obsidian vault

    Returns:
        Dictionary with research directory info and config
    """
    # Use provided workspace or default to .docs/research
    if workspace_path:
        base_path = Path(workspace_path)
    else:
        base_path = Path(".docs/research")

    research_dir = base_path / research_name
    created_date = datetime.now().strftime("%Y-%m-%d")
```

**Reasoning**: Maintains backward compatibility while adding flexibility. Default behavior unchanged.

#### 2. Create Configuration File

**File**: `.claude/skills/iw-research-planner/scripts/init_research.py`
**Lines**: After line 59 (after creating findings.md)
**Changes**: Add config file creation

**Add new code:**
```python
    # Create configuration file
    config_file = research_dir / ".research-config.json"
    config_data = {
        "research_name": research_name,
        "workspace_path": str(base_path),
        "created_date": created_date,
        "obsidian_integration": obsidian_integration
    }

    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
```

**Reasoning**: Stores workspace location so executor and synthesizer scripts can find files without hardcoding paths.

#### 3. Update Return Value

**File**: `.claude/skills/iw-research-planner/scripts/init_research.py`
**Lines**: 61-65
**Changes**: Include config info in return value

**Current code:**
```python
    return {
        "research_dir": str(research_dir),
        "research_name": research_name,
        "created_date": created_date
    }
```

**Proposed changes:**
```python
    return {
        "research_dir": str(research_dir),
        "research_name": research_name,
        "created_date": created_date,
        "workspace_path": str(base_path),
        "config_file": str(config_file),
        "obsidian_integration": obsidian_integration
    }
```

**Reasoning**: Provides complete information about created structure for logging and verification.

#### 4. Update CLI Argument Parsing

**File**: `.claude/skills/iw-research-planner/scripts/init_research.py`
**Lines**: 68-70
**Changes**: Add workspace_path and obsidian_integration arguments

**Current code:**
```python
def main():
    parser = argparse.ArgumentParser(description="Initialize research project structure")
    parser.add_argument("research_name", help="Name of the research project")
    args = parser.parse_args()
```

**Proposed changes:**
```python
def main():
    parser = argparse.ArgumentParser(description="Initialize research project structure")
    parser.add_argument("research_name", help="Name of the research project")
    parser.add_argument(
        "--workspace",
        help="Workspace path (default: .docs/research)",
        default=None
    )
    parser.add_argument(
        "--obsidian",
        action="store_true",
        help="Enable Obsidian integration"
    )
    args = parser.parse_args()
```

**Reasoning**: Allows command-line specification of workspace for testing and direct script usage.

#### 5. Update Function Call in main()

**File**: `.claude/skills/iw-research-planner/scripts/init_research.py`
**Lines**: 72-78
**Changes**: Pass new parameters to create_research_structure

**Current code:**
```python
    try:
        result = create_research_structure(args.research_name)
        print(f"✅ Research project initialized: {result['research_dir']}")
        # ...
```

**Proposed changes:**
```python
    try:
        result = create_research_structure(
            args.research_name,
            workspace_path=args.workspace,
            obsidian_integration=args.obsidian
        )
        print(f"✅ Research project initialized: {result['research_dir']}")
        print(f"   Workspace: {result['workspace_path']}")
        print(f"   Config: {result['config_file']}")
        if result['obsidian_integration']:
            print(f"   Obsidian integration: enabled")
        # ...
```

**Reasoning**: Passes configuration through and provides informative output about created structure.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test with custom workspace:**
   ```bash
   python3 init_research.py my-research --workspace ~/Documents
   ```
   - Verify files created in `~/Documents/my-research/`
   - Verify `.research-config.json` contains correct workspace_path

2. **Test with Obsidian flag:**
   ```bash
   python3 init_research.py my-research --workspace /path/to/vault --obsidian
   ```
   - Verify config has `obsidian_integration: true`

3. **Test backward compatibility:**
   ```bash
   python3 init_research.py my-research
   ```
   - Verify files created in `.docs/research/my-research/`
   - Verify config has default workspace_path

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] Custom workspace path accepted and used
- [ ] `.research-config.json` created with correct values
- [ ] Default behavior (.docs/research) unchanged
- [ ] Obsidian flag saved to config
- [ ] Return value includes all new fields
- [ ] CLI arguments work correctly
- [ ] Existing invocations (without new args) still work

---

## Phase 3: Update Executor Scripts to Use Config

### Overview

Modify add_finding.py and add_source.py to read workspace path from `.research-config.json` instead of hardcoding `.docs/research`. Add helper function to load config and use it in both scripts.

### Changes Required:

#### 1. Create Config Loading Helper

**File**: `.claude/skills/iw-research-executor/scripts/add_finding.py`
**Lines**: After imports (around line 8)
**Changes**: Add helper function to load research config

**Add new function:**
```python
def load_research_config(research_name: str) -> dict:
    """
    Load research configuration from .research-config.json.

    Tries multiple locations to find the research directory:
    1. .docs/research/<name>/ (default location)
    2. Current directory / <name>/ (for custom workspaces)
    3. Parent directories searching for config

    Args:
        research_name: Name of the research project

    Returns:
        Dictionary with config data or defaults

    Raises:
        FileNotFoundError: If research directory cannot be found
    """
    # Try default location first
    default_path = Path(".docs/research") / research_name
    config_file = default_path / ".research-config.json"

    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)

    # Try current directory
    local_path = Path.cwd() / research_name
    config_file = local_path / ".research-config.json"

    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)

    # Search parent directories (up to 3 levels)
    for parent in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        search_path = parent / research_name
        config_file = search_path / ".research-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

    # Fallback to default if no config found (backward compatibility)
    return {
        "research_name": research_name,
        "workspace_path": ".docs/research",
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "obsidian_integration": False
    }
```

**Reasoning**: Provides flexible config loading with fallback to defaults for backward compatibility. Searches multiple locations to handle various workspace scenarios.

#### 2. Update add_finding Function to Use Config

**File**: `.claude/skills/iw-research-executor/scripts/add_finding.py`
**Lines**: 10-14
**Changes**: Use config helper instead of hardcoded path

**Current code:**
```python
def add_finding(research_name: str, theme: str, finding: str, source_ref: str):
    """Add finding to findings.md under specified theme."""
    research_dir = Path(".docs/research") / research_name
    findings_file = research_dir / "findings.md"
```

**Proposed changes:**
```python
def add_finding(research_name: str, theme: str, finding: str, source_ref: str):
    """Add finding to findings.md under specified theme."""
    # Load research config to get workspace location
    config = load_research_config(research_name)
    workspace_path = Path(config["workspace_path"])

    research_dir = workspace_path / research_name
    findings_file = research_dir / "findings.md"

    # Verify research directory exists
    if not research_dir.exists():
        raise FileNotFoundError(
            f"Research directory not found: {research_dir}\n"
            f"Expected workspace: {workspace_path}\n"
            f"Ensure research was initialized with /iw-research-plan"
        )
```

**Reasoning**: Uses config to find research directory, provides helpful error message if not found.

#### 3. Update add_source.py Similarly

**File**: `.claude/skills/iw-research-executor/scripts/add_source.py`
**Lines**: Add same helper function, update add_source function

**Add helper after imports:**
```python
def load_research_config(research_name: str) -> dict:
    # Same implementation as in add_finding.py
    # (Could be refactored to shared module later)
    ...
```

**Update add_source function:**
```python
def add_source(research_name: str, source_url: str, source_type: str, notes: str = ""):
    """Add source to sources.md file."""
    # Load research config to get workspace location
    config = load_research_config(research_name)
    workspace_path = Path(config["workspace_path"])

    research_dir = workspace_path / research_name
    sources_file = research_dir / "sources.md"

    # Verify research directory exists
    if not research_dir.exists():
        raise FileNotFoundError(
            f"Research directory not found: {research_dir}\n"
            f"Expected workspace: {workspace_path}\n"
            f"Ensure research was initialized with /iw-research-plan"
        )
```

**Reasoning**: Consistent implementation across both scripts for maintainability.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test with .docs/research (default):**
   - Initialize research in `.docs/research/test-research/`
   - Run `add_finding.py test-research "Theme" "Finding" "Source"`
   - Verify finding added to correct location
   - Run `add_source.py test-research "http://example.com" "Paper" "Notes"`
   - Verify source added to correct location

2. **Test with custom workspace:**
   - Initialize research with custom workspace `~/Documents/test-research/`
   - Change to different directory
   - Run add_finding/add_source scripts
   - Verify they find the research directory via config

3. **Test error handling:**
   - Try to add finding to non-existent research
   - Verify helpful error message displayed

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] add_finding.py reads workspace from config
- [ ] add_source.py reads workspace from config
- [ ] Scripts work with default .docs/research location
- [ ] Scripts work with custom workspace paths
- [ ] Scripts work with Obsidian vault paths
- [ ] Helpful error messages when research not found
- [ ] Backward compatibility maintained (fallback to defaults)

---

## Phase 4: Add Final Location Prompt to Synthesizer

### Overview

Add final report destination prompt to iw-research-synthesizer skill. After synthesis completes, ask user where to save the final report (separate from workspace location).

### Changes Required:

#### 1. Update iw-research-synthesizer SKILL.md

**File**: `.claude/skills/iw-research-synthesizer/SKILL.md`
**Lines**: After existing synthesis steps (around line 150)
**Changes**: Add new step for final location prompting

**Add new section before "Resources":**
```markdown
### Step 4: Prompt for Final Report Location

After generating the report framework, ask user where to save the final report.

**Why separate from workspace?**
- Workspace is temporary location for research work
- Final location is permanent home for completed report
- Allows organization (e.g., vault/Research folder vs vault root)
- Enables cleanup of workspace without losing report

**Prompt user for final location:**

Use AskUserQuestion or direct prompt:

```
Research report generated successfully!

Where would you like to save the final report?

Workspace location: {workspace_path}/{research_name}

Options:
1. Same as workspace - Keep report in workspace (no move)
2. Obsidian Research folder - {vault}/Research/{research_name}-report.md
3. Custom path - Specify exact file path

Note: Intermediate files (research-plan.md, sources.md, findings.md, assets/)
will be cleaned up after moving the report.
```

**Validate input:**
- Ensure path is absolute or relative to known location
- Create parent directories if needed
- Verify write permissions

**Save choice:**
- Store final_path in config or pass to move function
- Use for file operations in next phase
```

**Reasoning**: Separates workspace (temporary) from final destination (permanent), gives user control over organization.

#### 2. Add Path Validation Helper

**File**: `.claude/skills/iw-research-synthesizer/SKILL.md`
**Lines**: In "Resources" section
**Changes**: Document new helper for path validation

**Add subsection:**
```markdown
### scripts/validate_path.py (New)

Helper to validate and prepare final report path.

**Usage:**
```bash
python3 validate_path.py "/path/to/report.md"
```

**Returns** (JSON):
```json
{
  "valid": true,
  "absolute_path": "/full/path/to/report.md",
  "directory": "/full/path/to",
  "directory_exists": false,
  "writable": true
}
```

**Implementation:**
- Converts relative paths to absolute
- Checks parent directory existence
- Verifies write permissions
- Creates parent directories if needed
- Returns validation result
```

**Reasoning**: Provides reusable path validation logic to prevent errors during file operations.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test keeping in workspace:**
   - Complete research synthesis
   - Choose "Same as workspace" option
   - Verify report remains in workspace
   - Verify no file move occurs

2. **Test Obsidian folder:**
   - Complete research in Obsidian vault
   - Choose "Obsidian Research folder"
   - Verify report moved to vault/Research/
   - Verify filename correct

3. **Test custom path:**
   - Complete research synthesis
   - Choose "Custom path"
   - Enter path: `~/Documents/Final/my-report.md`
   - Verify parent directories created
   - Verify report moved to specified location

4. **Test validation:**
   - Enter invalid path (no permissions)
   - Verify error message and re-prompt

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] Final location prompt appears after synthesis
- [ ] Prompt shows current workspace location
- [ ] Options are clear and appropriate
- [ ] Path validation works correctly
- [ ] Parent directories created when needed
- [ ] Report not moved when "Same as workspace" chosen
- [ ] Report successfully moved to custom paths
- [ ] Obsidian Research folder option works

---

## Phase 5: Implement Auto-Cleanup After Synthesis

### Overview

Add automatic cleanup of intermediate files after successful report generation and move. Remove research-plan.md, sources.md, findings.md, assets/ directory, and .research-config.json, leaving only the final report at the destination.

### Changes Required:

#### 1. Add Cleanup Function to generate_report.py

**File**: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
**Lines**: After generate_report function (around line 170)
**Changes**: Add new cleanup_workspace function

**Add new function:**
```python
def cleanup_workspace(research_dir: Path, final_report_path: Path, dry_run: bool = False) -> dict:
    """
    Clean up intermediate research files after report is moved.

    Args:
        research_dir: Workspace directory containing intermediate files
        final_report_path: Path where final report was saved
        dry_run: If True, show what would be deleted without deleting

    Returns:
        Dictionary with cleanup results
    """
    files_to_remove = [
        "research-plan.md",
        "sources.md",
        "findings.md",
        ".research-config.json"
    ]

    dirs_to_remove = [
        "assets"
    ]

    removed_files = []
    removed_dirs = []
    errors = []

    # Remove files
    for filename in files_to_remove:
        file_path = research_dir / filename
        if file_path.exists():
            if dry_run:
                print(f"Would remove: {file_path}")
                removed_files.append(str(file_path))
            else:
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                except Exception as e:
                    errors.append(f"Failed to remove {file_path}: {e}")

    # Remove directories
    for dirname in dirs_to_remove:
        dir_path = research_dir / dirname
        if dir_path.exists():
            if dry_run:
                print(f"Would remove: {dir_path}")
                removed_dirs.append(str(dir_path))
            else:
                try:
                    shutil.rmtree(dir_path)
                    removed_dirs.append(str(dir_path))
                except Exception as e:
                    errors.append(f"Failed to remove {dir_path}: {e}")

    # Remove research directory if empty
    if not dry_run:
        try:
            if research_dir.exists() and not any(research_dir.iterdir()):
                research_dir.rmdir()
                removed_dirs.append(str(research_dir))
        except Exception as e:
            # Not empty or can't remove, that's okay
            pass

    return {
        "removed_files": removed_files,
        "removed_dirs": removed_dirs,
        "errors": errors,
        "final_report": str(final_report_path)
    }
```

**Reasoning**: Provides safe cleanup with error handling and optional dry-run for testing.

#### 2. Add Move and Cleanup Logic

**File**: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
**Lines**: In main() function, after report generation
**Changes**: Add report move and cleanup steps

**Add after line 210 (after report is written):**
```python
    # Prompt for final location (if not provided via CLI)
    if not args.final_path:
        print(f"\n📋 Report generated: {report_file}")
        print(f"Workspace: {research_dir}")
        print("\nWhere would you like to save the final report?")
        print("1. Keep in workspace (no move)")
        print("2. Specify custom path")

        choice = input("\nChoice (1-2): ").strip()

        if choice == "2":
            final_path_input = input("Enter final report path: ").strip()
            final_path = Path(final_path_input).expanduser()
        else:
            # Keep in workspace
            final_path = report_file
    else:
        final_path = Path(args.final_path).expanduser()

    # Move report if different location
    moved = False
    if final_path != report_file:
        print(f"\n📦 Moving report to: {final_path}")

        # Create parent directory if needed
        final_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy report to final location
        shutil.copy2(report_file, final_path)

        # Verify copy succeeded
        if final_path.exists():
            print(f"✅ Report saved to: {final_path}")
            moved = True
        else:
            print(f"❌ Failed to move report to: {final_path}")
            print(f"   Report remains in workspace: {report_file}")
            final_path = report_file  # Revert to workspace location

    # Cleanup workspace (only if report was moved successfully)
    if moved:
        print(f"\n🧹 Cleaning up workspace...")
        cleanup_result = cleanup_workspace(research_dir, final_path)

        if cleanup_result["removed_files"]:
            print(f"   Removed {len(cleanup_result['removed_files'])} files")
        if cleanup_result["removed_dirs"]:
            print(f"   Removed {len(cleanup_result['removed_dirs'])} directories")
        if cleanup_result["errors"]:
            print(f"⚠️  Errors during cleanup:")
            for error in cleanup_result["errors"]:
                print(f"   - {error}")
        else:
            print(f"✅ Workspace cleaned successfully")
    else:
        print(f"\n📁 Research files remain in: {research_dir}")
```

**Reasoning**: Provides clear user feedback, safe file operations with verification, and only cleans up after successful move.

#### 3. Add CLI Arguments for Final Path

**File**: `.claude/skills/iw-research-synthesizer/scripts/generate_report.py`
**Lines**: In argument parser (around line 174)
**Changes**: Add final_path and dry_run arguments

**Add arguments:**
```python
    parser.add_argument(
        "--final-path",
        help="Final location for report (prompts if not provided)",
        default=None
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip cleanup of intermediate files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show cleanup actions without executing"
    )
```

**Reasoning**: Allows scripted usage and testing without interactive prompts.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test full workflow with move and cleanup:**
   - Create research, add findings/sources
   - Generate report
   - Choose custom final path
   - Verify report moved
   - Verify workspace files deleted
   - Verify empty workspace directory removed

2. **Test keep in workspace (no cleanup):**
   - Generate report
   - Choose "Keep in workspace"
   - Verify no files deleted
   - Verify all files remain

3. **Test dry-run:**
   ```bash
   python3 generate_report.py my-research --final-path ~/final.md --dry-run
   ```
   - Verify shows what would be deleted
   - Verify nothing actually deleted

4. **Test no-cleanup flag:**
   ```bash
   python3 generate_report.py my-research --final-path ~/final.md --no-cleanup
   ```
   - Verify report moved
   - Verify workspace files NOT deleted

5. **Test error handling:**
   - Set workspace directory read-only
   - Attempt cleanup
   - Verify errors reported but process continues

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] Report successfully moved to final location
- [ ] Intermediate files cleaned up after move
- [ ] Workspace directory removed if empty
- [ ] No cleanup when keeping in workspace
- [ ] Dry-run shows actions without executing
- [ ] --no-cleanup flag prevents deletion
- [ ] Errors during cleanup don't break process
- [ ] Clear confirmation messages shown
- [ ] Final report verified before cleanup

---

## Phase 6: Update Documentation

### Overview

Update README.md, iw-workflow skill, and iw-help to document Obsidian integration and new research workflow with workspace selection and cleanup.

### Changes Required:

#### 1. Update README.md Research Workflow Section

**File**: `README.md`
**Lines**: 145-184 (Research Workflow section)
**Changes**: Add Obsidian integration details

**Current section:**
```markdown
### Research Workflow

For conducting systematic research on technical topics, academic papers, or code implementations:
```

**Enhanced section:**
```markdown
### Research Workflow

For conducting systematic research on technical topics, academic papers, or code implementations. **Now with Obsidian vault integration** for seamless personal knowledge management.

#### Overview

The research workflow supports flexible storage locations:
- **.docs/research/** - Standard project location (default)
- **Obsidian vault** - Auto-detected for personal knowledge base
- **Custom paths** - Any location you specify

Research happens in a temporary workspace, final report saved to your chosen location, and intermediate files are automatically cleaned up.

#### 1. Create Research Plan
```

**Add new subsection after Step 2:**
```markdown
#### Obsidian Integration

If you have the `obsidian-local-api` skill configured:

1. **Automatic vault detection:**
   - Skill detects your Obsidian vault automatically
   - Offers vault root as workspace option
   - Seamless integration with your knowledge base

2. **Live preview during research:**
   - Work in vault root for live Obsidian preview
   - See links and graph view while researching
   - Leverage Obsidian features during work

3. **Organized final storage:**
   - Choose final report location (e.g., Research/ folder)
   - Intermediate files auto-cleaned
   - Only final report remains in vault

**Setup:**
1. Install Obsidian Local REST API plugin
2. Configure via `obsidian-local-api` skill
3. Start research with `/iw-research-plan`
4. Select Obsidian vault when prompted

**Example workflow:**
```bash
/iw-research-plan
# → Choose "Obsidian Vault Root" as workspace
# → Conduct research (files visible in Obsidian)
/iw-research-execute
# → Gather findings and sources
# → Final prompt: "Save report to Research/ folder"
# → Intermediate files auto-cleaned
# → Final report at: vault/Research/my-topic-report.md
```
```

**Reasoning**: Highlights the new Obsidian integration prominently while maintaining existing documentation structure.

#### 2. Update iw-workflow Skill Documentation

**File**: `.claude/skills/iw-workflow/SKILL.md`
**Lines**: After line 167 (in research workflow section)
**Changes**: Add Obsidian research workflow examples

**Add new subsection:**
```markdown
### Research with Obsidian Integration

For personal research stored in Obsidian vault:

**Workflow:**

1. **Start research with workspace selection:**
   ```
   /iw-research-plan
   ```
   - Skill auto-detects Obsidian vault
   - Prompts: ".docs/research", "Obsidian Vault", or "Custom path"
   - Choose Obsidian vault for personal research

2. **Research execution in vault:**
   ```
   /iw-research-execute
   ```
   - Files created in vault root
   - Visible in Obsidian during research
   - Use Obsidian features (links, tags, graph view)
   - Add findings and sources as usual

3. **Final report and cleanup:**
   - Report synthesis completes
   - Prompt for final location (e.g., `Research/topic-name.md`)
   - Report moved to final location
   - Intermediate files auto-cleaned
   - Only final report remains

**Benefits:**
- Live preview while researching
- Obsidian features available during work
- Clean final vault (no clutter)
- Organized knowledge base

**Requirements:**
- Obsidian with Local REST API plugin
- `obsidian-local-api` skill configured
- API key set in config
```

**Reasoning**: Provides concrete examples of the Obsidian workflow for users.

#### 3. Update Research Skill SKILL.md Files

**Files to update:**
- `.claude/skills/iw-research-planner/SKILL.md:145-169` - Update workflow summary
- `.claude/skills/iw-research-executor/SKILL.md` - Note workspace config usage
- `.claude/skills/iw-research-synthesizer/SKILL.md` - Document cleanup behavior

**For iw-research-planner SKILL.md, update Step 6:**
```markdown
### Step 6: Present Plan for Confirmation

Show research plan to user and confirm before proceeding to execution phase.

Present summary:
```
✓ Research Plan Created

Research: [research-name]
Workspace: [workspace-path]
Obsidian integration: [enabled/disabled]

Research Questions:
1. [Question 1]
2. [Question 2]
3. [Question 3]

Scope: [Brief summary of what's included/excluded]

Source Types:
- [List of source types to investigate]

Methodology: [Brief description of organization strategy]

Success Criteria: [How completion will be measured]

The research plan is ready. Next step:
Use /iw-research-execute to gather information and generate report

Note: Final report location will be selected after synthesis completes.
Intermediate files will be cleaned up automatically.

Ready to proceed with research execution?
```
```

**For iw-research-synthesizer SKILL.md, update workflow:**
```markdown
### Step 5: Cleanup Workspace

After moving report to final location, automatically cleanup intermediate files.

**Files removed:**
- `research-plan.md` - Planning document (temporary)
- `sources.md` - Source list (temporary)
- `findings.md` - Findings collection (temporary)
- `assets/` - Supporting files directory
- `.research-config.json` - Workspace config

**Files kept:**
- Final report at chosen destination

**Confirmation message:**
```
✅ Research Complete!

Final report: [final-path]
Workspace cleaned: [workspace-path]

Removed:
- 4 files
- 1 directory

Your research is complete and organized!
```
```

**Reasoning**: Ensures all documentation is updated consistently to reflect new workflow.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Verify README clarity:**
   - Read updated README section
   - Follow Obsidian setup instructions
   - Confirm all steps make sense

2. **Verify iw-workflow examples:**
   - Test example workflow from documentation
   - Confirm all commands work as documented
   - Verify output matches descriptions

3. **Verify skill documentation:**
   - Read through all three SKILL.md files
   - Confirm workflow described correctly
   - Check for consistency across files

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] README clearly explains Obsidian integration
- [ ] Setup instructions are accurate and complete
- [ ] Example workflow in README works correctly
- [ ] iw-workflow skill has clear Obsidian examples
- [ ] All SKILL.md files updated consistently
- [ ] Benefits and requirements clearly stated
- [ ] New workflow steps documented
- [ ] Cleanup behavior explained

---

## Testing Strategy

### Manual Testing Checklist:

**Backward Compatibility:**
- [ ] Existing research in `.docs/research/` works unchanged
- [ ] No config file required for default behavior
- [ ] All scripts work with old research directories

**Workspace Selection:**
- [ ] Obsidian vault detected when configured
- [ ] Custom path entry works
- [ ] Default `.docs/research` works
- [ ] Config file created correctly

**Research Execution:**
- [ ] Findings added to correct workspace
- [ ] Sources added to correct workspace
- [ ] Scripts find research via config

**Final Location & Cleanup:**
- [ ] Final location prompt appears
- [ ] Report moved successfully
- [ ] Intermediate files deleted
- [ ] Workspace directory removed if empty
- [ ] Errors handled gracefully

**Obsidian Integration:**
- [ ] Vault path retrieved from API
- [ ] Files visible in Obsidian during research
- [ ] Final report saved to specified vault location

**Documentation:**
- [ ] README examples work
- [ ] iw-workflow examples work
- [ ] SKILL.md instructions accurate

### Performance Considerations:

- **File operations**: Copy + verify before delete for safety
- **API calls**: Single connection test, not repeated calls
- **Path searching**: Limit to 3 parent directory levels
- **Config reading**: Small JSON files, negligible performance impact

### Migration Notes:

**Existing research projects:**
- Continue working in `.docs/research/`
- No migration required
- Can manually create `.research-config.json` if desired

**New research:**
- Prompted for workspace location
- Config created automatically
- Full feature support

## References

- Original issue: https://github.com/jumppad-labs/iw/issues/6
- Research notes: `.docs/issues/6/6-research.md`
- Context document: `.docs/issues/6/6-context.md`
- Task breakdown: `.docs/issues/6/6-tasks.md`
- Obsidian Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api
- obsidian-local-api skill: `.claude/skills/obsidian-local-api/`
