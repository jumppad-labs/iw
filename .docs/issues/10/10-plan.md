# Issue #10 Implementation Plan: Fix GitHub API Rate Limiting

**Created**: 2025-11-03
**Last Updated**: 2025-11-03
**Issue**: #10 - /iw-install getting rate limited by github

## Overview

Replace the current HTTP-based file download approach in `/iw-install` with a git clone strategy to eliminate GitHub API rate limiting issues. The current implementation makes 80-100+ individual API requests per installation, exhausting the 60 requests/hour unauthenticated limit. The new approach will clone the repository once and copy files locally.

## Current State Analysis

### The Problem

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py`

The installation script currently:
1. Makes ~33 GitHub API requests to list directory contents (lines 120-136)
2. Makes ~50-70 raw content requests to download individual files (lines 138-163)
3. Total: **80-100+ requests per installation**
4. GitHub unauthenticated limit: **60 requests/hour**
5. Result: Rate limit exhausted after 1-2 installation attempts

###Key Code Locations:

- `.claude/skills/iw-install/scripts/manage_workflow.py:86-108` - `_fetch_url()` - Base HTTP request method
- `.claude/skills/iw-install/scripts/manage_workflow.py:110-118` - `_fetch_json()` - GitHub API JSON fetcher
- `.claude/skills/iw-install/scripts/manage_workflow.py:120-136` - `_list_directory_contents()` - Directory listing (API calls)
- `.claude/skills/iw-install/scripts/manage_workflow.py:138-163` - `_download_file()` - Individual file downloads
- `.claude/skills/iw-install/scripts/manage_workflow.py:165-195` - `_download_directory()` - Recursive download
- `.claude/skills/iw-install/scripts/manage_workflow.py:205-301` - `install()` - Main installation method

### Current Implementation Pattern:

```python
# From .claude/skills/iw-install/scripts/manage_workflow.py:86-108
def _fetch_url(self, url: str, retry: int = 3) -> Optional[bytes]:
    """Fetch content from URL with retry logic."""
    for attempt in range(retry):
        try:
            req = Request(url)
            req.add_header("User-Agent", "implementation-workflow-installer")
            with urlopen(req, timeout=10) as response:
                return response.read()
        except (URLError, HTTPError) as e:
            if attempt == retry - 1:
                print(f"  Error fetching {url}: {e}")
                return None
            print(f"  Retry {attempt + 1}/{retry} for {url}...")
    return None

# From .claude/skills/iw-install/scripts/manage_workflow.py:120-136
def _list_directory_contents(self, path: str) -> List[Dict]:
    """List contents of a directory in the GitHub repo."""
    url = f"{GITHUB_API_BASE}/contents/{path}?ref={GITHUB_BRANCH}"
    result = self._fetch_json(url)  # API request!
    # ... returns list of files

# From .claude/skills/iw-install/scripts/manage_workflow.py:138-163
def _download_file(self, repo_path: str, local_path: Path) -> bool:
    """Download a file from GitHub to local path."""
    url = f"{GITHUB_RAW_BASE}/{repo_path}"
    content = self._fetch_url(url)  # Raw content request!
    # ... saves to file
```

**Current Installation Flow:**
```
For each of 11 skills:
  - List scripts/ directory (1 API request)
  - Download SKILL.md (1 raw request)
  - Download each script file (N raw requests)
  - List assets/ directory (1 API request)
  - Download each asset file (N raw requests)
  - List references/ directory (1 API request)
  - Download each reference file (N raw requests)

Total: ~80-100+ requests = Rate limit exceeded
```

## Desired End State

After implementation:
- Installation makes **1 git clone operation** instead of 100+ HTTP requests
- No GitHub API rate limiting issues
- Installation is faster (single network operation)
- Works reliably regardless of number of installations
- Simpler, more maintainable code

**Verification Method:**
1. Run `/iw-install --update` multiple times in succession
2. Should succeed every time without rate limit errors
3. No "403 Forbidden" or rate limit messages in output

## What We're NOT Doing

- NOT adding GitHub token authentication (unnecessary with git clone approach)
- NOT implementing exponential backoff for API requests (eliminating API requests entirely)
- NOT caching partial downloads between requests
- NOT implementing rate limit detection/handling
- NOT modifying the uninstall functionality (no network requests needed)
- NOT changing the installation directory structure or file organization

## Implementation Approach

Replace HTTP-based file fetching with a git-clone-and-copy strategy:

1. **Phase 1**: Add git clone functionality
   - Add method to clone repo to temporary directory
   - Add method to copy `.claude/` contents from clone to target
   - Add cleanup method to remove temporary clone

2. **Phase 2**: Integrate git clone into installation flow
   - Replace `install()` method to use git clone instead of API calls
   - Maintain same progress output and error messages
   - Add git dependency check

3. **Phase 3**: Update documentation
   - Update skill documentation with git requirement
   - Update error messages to mention git dependency

---

## Phase 1: Add Git Clone Functionality

### Overview
Add three new methods to the `WorkflowInstaller` class to handle git cloning, file copying, and cleanup. These methods will replace the existing HTTP-based download methods.

### Changes Required:

#### 1. Add Git Clone Method

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:85` (insert after `_get_target_dir()`)

**Changes**: Add new method `_clone_repository()` to clone repo to temporary directory

**Proposed implementation:**
```python
def _clone_repository(self) -> Optional[Path]:
    """
    Clone the workflow repository to a temporary directory.

    Uses git clone with --depth 1 for a shallow clone (faster, less disk space).

    Returns:
        Path to temporary clone directory, or None on failure
    """
    import tempfile
    import shutil

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="iw-install-"))
    repo_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}.git"

    try:
        # Perform shallow clone (only latest commit)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", GITHUB_BRANCH, repo_url, str(temp_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for clone operation
        )

        # Verify .claude directory exists in clone
        claude_dir = temp_dir / ".claude"
        if not claude_dir.exists():
            print(f"  Error: .claude directory not found in cloned repository")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        return temp_dir

    except subprocess.TimeoutExpired:
        print(f"  Error: Git clone timed out after 60 seconds")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

    except subprocess.CalledProcessError as e:
        print(f"  Error: Git clone failed: {e.stderr}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

    except FileNotFoundError:
        print(f"  Error: git command not found. Please install git:")
        print(f"    Ubuntu/Debian: sudo apt-get install git")
        print(f"    macOS: brew install git")
        print(f"    Windows: https://git-scm.com/download/win")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

    except Exception as e:
        print(f"  Error: Unexpected error during clone: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None
```

**Reasoning**:
- Uses `--depth 1` for shallow clone (faster, less disk space)
- Timeout prevents hanging on slow connections
- Comprehensive error handling for network, git, and filesystem issues
- Validates .claude directory exists before returning
- Auto-cleanup on any failure

#### 2. Add File Copy Method

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:155` (insert after `_clone_repository()`)

**Changes**: Add new method `_copy_files_from_clone()` to copy .claude contents to target

**Proposed implementation:**
```python
def _copy_files_from_clone(self, clone_dir: Path) -> bool:
    """
    Copy .claude directory contents from cloned repo to target location.

    Args:
        clone_dir: Path to temporary clone directory

    Returns:
        True if successful, False otherwise
    """
    import shutil

    source_claude = clone_dir / ".claude"

    if not source_claude.exists():
        print("  Error: .claude directory not found in clone")
        return False

    try:
        # Create target directories if they don't exist
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # Copy each subdirectory (skills, commands, hooks)
        for subdir_name in ["skills", "commands", "hooks"]:
            source_subdir = source_claude / subdir_name

            if not source_subdir.exists():
                print(f"  Warning: {subdir_name}/ not found in clone, skipping")
                continue

            target_subdir = self.target_dir / subdir_name

            # Copy entire subdirectory
            # dirs_exist_ok=True allows overwriting existing files
            shutil.copytree(source_subdir, target_subdir, dirs_exist_ok=True)

            # Count files copied for reporting
            file_count = sum(1 for _ in target_subdir.rglob('*') if _.is_file())
            self.installed_files.extend(target_subdir.rglob('*'))
            print(f"  ✓ Copied {file_count} files to {subdir_name}/")

        # Make hook scripts executable
        hooks_dir = self.target_dir / "hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.sh"):
                self._make_executable(hook_file)

        return True

    except PermissionError as e:
        print(f"  Error: Permission denied when copying files: {e}")
        print(f"  Check that you have write permissions to {self.target_dir}")
        return False

    except OSError as e:
        print(f"  Error: Failed to copy files: {e}")
        return False

    except Exception as e:
        print(f"  Error: Unexpected error during copy: {e}")
        return False
```

**Reasoning**:
- Uses `shutil.copytree()` with `dirs_exist_ok=True` to handle updates
- Counts files for progress reporting
- Handles missing subdirectories gracefully
- Makes hook scripts executable automatically
- Tracks installed files in `self.installed_files` for consistency with old implementation

#### 3. Add Cleanup Method

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:225` (insert after `_copy_files_from_clone()`)

**Changes**: Add new method `_cleanup_clone()` to remove temporary clone

**Proposed implementation:**
```python
def _cleanup_clone(self, clone_dir: Path):
    """
    Remove temporary clone directory.

    Args:
        clone_dir: Path to temporary clone to remove
    """
    import shutil

    try:
        if clone_dir and clone_dir.exists():
            shutil.rmtree(clone_dir)
    except Exception as e:
        # Non-fatal error, just warn
        print(f"  Warning: Failed to clean up temporary directory {clone_dir}: {e}")
        print(f"  You may want to manually remove it later")
```

**Reasoning**:
- Non-fatal error (cleanup failure shouldn't fail installation)
- Informative warning if cleanup fails
- Defensive check for None and existence

### Testing for This Phase:

**Manual Testing** (No unit tests needed for this phase - integration testing in Phase 2):

1. Test `_clone_repository()`:
   ```python
   # In Python REPL or test script:
   installer = WorkflowInstaller(location="project")
   clone_dir = installer._clone_repository()
   assert clone_dir is not None
   assert (clone_dir / ".claude").exists()
   installer._cleanup_clone(clone_dir)
   ```

2. Test `_copy_files_from_clone()`:
   ```python
   # Create test target directory
   installer = WorkflowInstaller(location="project")
   clone_dir = installer._clone_repository()
   success = installer._copy_files_from_clone(clone_dir)
   assert success == True
   assert (installer.target_dir / "skills").exists()
   installer._cleanup_clone(clone_dir)
   ```

3. Test error handling:
   - Test with git not installed (use Docker container without git)
   - Test with invalid repo URL
   - Test with network disconnected
   - Test with read-only target directory

### Success Criteria:

#### Automated Verification:
- [ ] Git clone completes successfully with valid repo
- [ ] Files are copied to correct locations
- [ ] Hook scripts are executable after copy
- [ ] Temporary directory is cleaned up
- [ ] Error handling works for missing git, network issues, permission errors

#### Manual Verification:
- [ ] Clone operation takes < 10 seconds on normal connection
- [ ] All 11 skills are present in target after copy
- [ ] All 4 commands are present in target after copy
- [ ] All 2 hooks are present and executable
- [ ] Temporary directory is removed from `/tmp`

---

## Phase 2: Integrate Git Clone into Installation Flow

### Overview
Replace the existing `install()` method implementation to use git clone instead of HTTP requests. Maintain the same user-facing output and error messages for consistency.

### Changes Required:

#### 1. Simplify install() Method

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:205-301`

**Current code:**
```python
def install(self) -> bool:
    """Install the Implementation Workflow."""
    print(f"Installing Implementation Workflow to: {self.target_dir}")
    print()

    # Create base directories
    print("Creating directory structure...")
    (self.target_dir / "skills").mkdir(parents=True, exist_ok=True)
    (self.target_dir / "commands").mkdir(parents=True, exist_ok=True)
    (self.target_dir / "hooks").mkdir(parents=True, exist_ok=True)
    print("  ✓ Directory structure created")
    print()

    # Install skills (loop with _download_file calls)
    print(f"Installing {len(SKILLS)} skills...")
    for skill in SKILLS:
        # ... complex downloading logic ...

    # Install commands (loop with _download_file calls)
    print(f"Installing {len(COMMANDS)} commands...")
    # ... complex downloading logic ...

    # Install hooks (loop with _download_file calls)
    print(f"Installing {len(HOOKS)} hooks...")
    # ... complex downloading logic ...

    # Summary
    print("=" * 50)
    # ... summary output ...
```

**Proposed changes:**
```python
def install(self) -> bool:
    """
    Install the Implementation Workflow.

    Clones the repository and copies files to target location.

    Returns:
        True if successful
    """
    print(f"Installing Implementation Workflow to: {self.target_dir}")
    print()

    # Step 1: Clone repository
    print("Cloning workflow repository...")
    clone_dir = self._clone_repository()

    if clone_dir is None:
        print()
        print("=" * 50)
        print("Installation Failed!")
        print("=" * 50)
        print()
        print("Could not clone repository. Check:")
        print("  - Git is installed: git --version")
        print("  - Network connection is working")
        print("  - GitHub is accessible: ping github.com")
        print()
        return False

    print(f"  ✓ Repository cloned to temporary directory")
    print()

    # Step 2: Copy files from clone to target
    print(f"Copying workflow files to {self.target_dir}...")
    success = self._copy_files_from_clone(clone_dir)

    # Step 3: Cleanup temporary clone
    print()
    print("Cleaning up temporary files...")
    self._cleanup_clone(clone_dir)
    print("  ✓ Temporary files removed")

    if not success:
        print()
        print("=" * 50)
        print("Installation Failed!")
        print("=" * 50)
        print()
        print("Failed to copy files. Check:")
        print(f"  - Write permissions: ls -ld {self.target_dir}")
        print(f"  - Available disk space: df -h {self.target_dir}")
        print()
        return False

    # Step 4: Display success summary
    print()
    print("=" * 50)
    print("Installation Complete!")
    print("=" * 50)
    print()
    print(f"Location: {self.target_dir}")
    print(f"Installed: {len(SKILLS)} skills, {len(COMMANDS)} commands, {len(HOOKS)} hooks")
    print(f"Files: {len(self.installed_files)}")
    print()
    print("Next steps:")
    print("  1. Restart Claude Code or start new session")
    print("  2. Run /iw-help to see workflow guidance")
    print("  3. Use /iw-plan to create your first plan")
    print()

    return True
```

**Reasoning**:
- Drastically simplified from ~100 lines to ~60 lines
- Same user-facing output format for consistency
- Clear error messages with troubleshooting steps
- Maintains installed file count tracking
- Always cleans up temporary clone (even on failure)

#### 2. Remove Obsolete Methods

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py`

**Changes**: Mark old HTTP methods as deprecated or remove them entirely

**Methods to remove**:
- `_fetch_url()` (lines 86-108) - No longer needed
- `_fetch_json()` (lines 110-118) - No longer needed
- `_list_directory_contents()` (lines 120-136) - No longer needed
- `_download_file()` (lines 138-163) - No longer needed
- `_download_directory()` (lines 165-195) - No longer needed

**Reasoning**:
- Removing dead code improves maintainability
- Reduces file size and complexity
- No need to maintain two parallel download strategies

**Note**: Keep the following methods as they're still used:
- `_get_target_dir()` - Still needed
- `_make_executable()` - Still used for hooks
- `update()` - Still uses `install()` method
- `uninstall()` - Doesn't use HTTP methods
- `verify()` - Doesn't use HTTP methods
- `list_installed()` - Doesn't use HTTP methods

#### 3. Remove Obsolete Constants

**File**: `.claude/skills/iw-install/scripts/manage_workflow.py:27-32`

**Current code:**
```python
# GitHub repository configuration
GITHUB_USER = "jumppad-labs"
GITHUB_REPO = "iw"
GITHUB_BRANCH = "main"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
```

**Proposed changes:**
```python
# GitHub repository configuration
GITHUB_USER = "jumppad-labs"
GITHUB_REPO = "iw"
GITHUB_BRANCH = "main"
# Note: No longer need GITHUB_API_BASE or GITHUB_RAW_BASE (git clone instead)
```

**Reasoning**: Remove unused constants for clarity

### Testing for This Phase:

**Integration Testing:**

1. **Test fresh installation:**
   ```bash
   # Remove existing installation
   rm -rf .claude/skills/iw-*
   rm -rf .claude/commands/iw-*

   # Run installation
   python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location project

   # Verify installation
   python3 .claude/skills/iw-install/scripts/manage_workflow.py verify --location project
   ```

2. **Test multiple installations in rapid succession** (the rate limiting test):
   ```bash
   for i in {1..5}; do
     echo "Installation attempt $i"
     python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location project
   done
   ```
   - Should succeed all 5 times without rate limit errors

3. **Test update operation:**
   ```bash
   python3 .claude/skills/iw-install/scripts/manage_workflow.py update --location project
   ```

4. **Test user-level installation:**
   ```bash
   python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location user
   ```

5. **Test error scenarios:**
   - Network disconnected during clone
   - Target directory read-only
   - Git not installed
   - Insufficient disk space

### Success Criteria:

#### Automated Verification:
- [ ] Fresh installation completes successfully
- [ ] 5 consecutive installations succeed without rate limit errors
- [ ] All verification checks pass: `verify --location project`
- [ ] Update operation works correctly
- [ ] User-level installation works
- [ ] Installation is faster than old HTTP method (< 10 seconds vs 30-60 seconds)

#### Manual Verification:
- [ ] No HTTP 403 or rate limit errors in output
- [ ] Skills load correctly in Claude Code after installation
- [ ] Commands are available: `/iw-help`, `/iw-plan`, etc.
- [ ] Hooks execute correctly (if configured)
- [ ] Installation output is clear and informative
- [ ] Error messages provide helpful troubleshooting steps

---

## Phase 3: Update Documentation

### Overview
Update the skill documentation and command documentation to reflect the git requirement and new installation behavior.

### Changes Required:

#### 1. Update SKILL.md Requirements

**File**: `.claude/skills/iw-install/SKILL.md:332-340`

**Current code:**
```markdown
## Requirements

- **Python 3.7+** - For running the management script
- **curl** - For downloading files from GitHub
- **Internet connection** - To fetch files from GitHub

Optional:
- **git** - For some workflow features
- **gh CLI** - For GitHub integration features
```

**Proposed changes:**
```markdown
## Requirements

- **Python 3.7+** - For running the management script
- **git** - For cloning the workflow repository
- **Internet connection** - To clone from GitHub

Optional:
- **gh CLI** - For GitHub integration features (issue reader, PR creator)
```

**Reasoning**:
- Remove curl (no longer needed)
- Make git required (was optional)
- Clarify what each requirement is used for

#### 2. Update Installation Process Documentation

**File**: `.claude/skills/iw-install/SKILL.md:124-167`

**Current code:**
```markdown
## Installation Process

When you invoke this skill with action `install`:

1. **Determine Target Location**
   - Project: `$CWD/.claude/`
   - User: `~/.claude/`

2. **Create Directory Structure**
   ```
   .claude/
   ├── skills/
   ├── commands/
   └── hooks/
   ```

3. **Fetch Workflow Components from GitHub**
   - Uses GitHub API to list all files
   - Downloads each file directly from main branch
   - Preserves directory structure
```

**Proposed changes:**
```markdown
## Installation Process

When you invoke this skill with action `install`:

1. **Determine Target Location**
   - Project: `$CWD/.claude/`
   - User: `~/.claude/`

2. **Clone Repository**
   - Uses `git clone --depth 1` to shallow clone the repository
   - Clones to temporary directory
   - Fast and avoids GitHub API rate limiting

3. **Copy Files**
   - Copies entire `.claude/` directory from clone to target
   - Preserves directory structure
   - Makes hook scripts executable

4. **Cleanup**
   - Removes temporary clone directory
   - Installation complete
```

**Reasoning**: Update to reflect new git-based approach

#### 3. Update Troubleshooting Section

**File**: `.claude/skills/iw-install/SKILL.md:367-388`

**Current code:**
```markdown
## Troubleshooting

### Installation Fails
1. Check internet connection
2. Verify Python 3.7+ installed: `python3 --version`
3. Check permissions for target directory
4. Try with --force flag

### Files Not Downloading
1. Verify GitHub URL is accessible
2. Check for network proxy issues
3. Try manual download to test connectivity
```

**Proposed changes:**
```markdown
## Troubleshooting

### Installation Fails
1. **Check git is installed**: `git --version`
   - Ubuntu/Debian: `sudo apt-get install git`
   - macOS: `brew install git`
   - Windows: https://git-scm.com/download/win
2. **Check internet connection**: `ping github.com`
3. **Verify Python 3.7+ installed**: `python3 --version`
4. **Check permissions for target directory**: `ls -ld .claude`
5. **Check disk space**: `df -h .`

### Clone Fails
1. **Verify GitHub is accessible**: `git ls-remote https://github.com/jumppad-labs/iw.git`
2. **Check for network proxy**: `echo $https_proxy`
3. **Try manual clone**: `git clone https://github.com/jumppad-labs/iw.git /tmp/test-clone`

### Rate Limiting (No Longer an Issue)
The new git clone approach eliminates rate limiting issues. You can run installations as many times as needed.
```

**Reasoning**: Update troubleshooting for git-based approach and note that rate limiting is solved

#### 4. Update Important Notes Section

**File**: `.claude/skills/iw-install/SKILL.md:359-365`

**Current code:**
```markdown
## Important Notes

1. **Force Overwrite**: Installation always overwrites existing workflow files (force=true by default)
2. **Preserves Custom Content**: Your custom skills, commands, and settings are never removed
3. **Network Required**: All operations fetch from GitHub, no local caching
4. **Self-Updating**: The iw-install skill can update itself
5. **No Config Changes**: Never modifies settings.json or other configuration
```

**Proposed changes:**
```markdown
## Important Notes

1. **Git Required**: Installation requires git to be installed and available in PATH
2. **Force Overwrite**: Installation always overwrites existing workflow files (force=true by default)
3. **Preserves Custom Content**: Your custom skills, commands, and settings are never removed
4. **Network Required**: Clone operation requires internet access to GitHub
5. **No Rate Limiting**: Git clone eliminates GitHub API rate limiting issues
6. **Self-Updating**: The iw-install skill can update itself
7. **No Config Changes**: Never modifies settings.json or other configuration
```

**Reasoning**: Add note about git requirement and rate limiting fix

### Testing for This Phase:

**Documentation Review:**

1. Read through updated documentation for clarity
2. Verify all examples are accurate
3. Check that troubleshooting steps are helpful
4. Confirm requirements section is complete

### Success Criteria:

#### Automated Verification:
- [ ] No broken links in documentation
- [ ] All code examples are syntactically correct

#### Manual Verification:
- [ ] Documentation accurately describes new behavior
- [ ] Troubleshooting steps are clear and actionable
- [ ] Requirements section is accurate
- [ ] New users can understand the installation process
- [ ] Migration from old approach is transparent to users

---

## Testing Strategy

### Integration Tests:

**Test 1: Fresh Installation**
```bash
# Clean slate
rm -rf .claude

# Install
python3 /path/to/manage_workflow.py install --location project

# Verify all components present
ls .claude/skills/iw-planner
ls .claude/commands/iw-plan.md
ls .claude/hooks/load_workflow.sh

# Verify hooks are executable
test -x .claude/hooks/load_workflow.sh && echo "Hook is executable"
```

**Test 2: Rapid Successive Installations (Rate Limit Test)**
```bash
# This is the key test - should all succeed without rate limiting
for i in {1..10}; do
  echo "=== Installation attempt $i ==="
  python3 /path/to/manage_workflow.py install --location project || {
    echo "FAILED on attempt $i"
    exit 1
  }
done
echo "SUCCESS: All 10 installations completed without rate limit errors"
```

**Test 3: Update Existing Installation**
```bash
# Initial install
python3 /path/to/manage_workflow.py install --location project

# Update
python3 /path/to/manage_workflow.py update --location project

# Verify
python3 /path/to/manage_workflow.py verify --location project
```

**Test 4: User-Level Installation**
```bash
python3 /path/to/manage_workflow.py install --location user
ls ~/.claude/skills/iw-planner
```

### Error Handling Tests:

**Test 5: Git Not Installed**
```bash
# In Docker container without git
docker run --rm -it python:3.11-slim bash
# Try installation - should fail with helpful error message
```

**Test 6: Network Disconnected**
```bash
# Disconnect network and try install
# Should fail with clear error about network connectivity
```

**Test 7: Read-Only Target Directory**
```bash
mkdir -p .claude
chmod 555 .claude  # Read + execute only
python3 /path/to/manage_workflow.py install --location project
# Should fail with permission error
chmod 755 .claude  # Restore permissions
```

### Manual Testing Steps:

1. **Verify installation speed**
   - Time the installation: `time python3 /path/to/manage_workflow.py install --location project`
   - Should be < 10 seconds on normal connection (vs 30-60 seconds with old method)

2. **Verify Claude Code integration**
   - Install workflow: `python3 /path/to/manage_workflow.py install --location project`
   - Restart Claude Code
   - Verify skills load: Check that skills appear in skill list
   - Verify commands work: Try `/iw-help`

3. **Verify multiple installations**
   - Run installation 5 times in quick succession
   - All should succeed without errors
   - No rate limit messages should appear

## Performance Considerations

### Performance Improvements:

**Before (HTTP method)**:
- 80-100+ individual HTTP requests
- Each request has network round-trip overhead
- Sequential downloads (one at a time)
- Typical time: 30-60 seconds
- Rate limited to 60 requests/hour (1-2 installations max)

**After (Git clone method)**:
- 1 git clone operation
- Git uses efficient pack protocol
- Compressed transfer
- Shallow clone (only latest commit)
- Typical time: 5-10 seconds
- **No rate limiting** (unlimited installations)

### Disk Space:

- Temporary clone: ~5-10 MB (shallow clone)
- Automatically cleaned up after installation
- Final installation size: Same as before (~3-5 MB)

### Network Usage:

- Before: 80-100+ HTTP requests = ~3-5 MB total transfer
- After: 1 git clone = ~2-3 MB total transfer (compressed)
- Net improvement: Slightly less network usage, much faster

## Migration Notes

### For Users:

**No migration needed!** The installation command remains the same:
```bash
/iw-install
/iw-install --update
```

Users will automatically get the new behavior with improved speed and reliability.

### For Developers:

If you have forked or modified the installation script:
1. The new implementation is in the `install()` method
2. Old HTTP methods can be safely removed
3. New dependency: git must be installed
4. Test your modifications work with git clone approach

### Breaking Changes:

**None!** The interface remains exactly the same:
- Same command syntax
- Same output format
- Same installation locations
- Same file organization

The only difference is the internal implementation (which users don't see).

## References

- **Original Issue**: GitHub Issue #10 - /iw-install getting rate limited
- **Learning Documented**: `.docs/knowledge/learnings/installation.md`
- **Key File Modified**: `.claude/skills/iw-install/scripts/manage_workflow.py`
- **GitHub API Docs**: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
- **Git Shallow Clone Docs**: https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---depthltdepthgt

### Similar Patterns in Codebase:

No similar patterns found - this is a unique installation mechanism. However, error handling patterns follow conventions from:
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:120-187` - HTTP error handling pattern
- `.claude/skills/obsidian-local-api/scripts/filesystem_ops.py` - File operation error handling pattern
