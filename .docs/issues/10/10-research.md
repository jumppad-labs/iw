# Issue #10 - Research & Working Notes

**Research Date**: 2025-11-03
**Researchers**: Claude + nicj

## Initial Understanding

**Initial assumption**: The `/iw-install` command was hitting GitHub API rate limits because it wasn't using authentication tokens. Assumed the solution would be to add GitHub token authentication (`GITHUB_TOKEN` or `GH_TOKEN` environment variables) to individual HTTP requests.

**Initial approach proposed**:
- Add token authentication to HTTP requests
- Implement exponential backoff for retries
- Add rate limit detection and handling
- Check multiple token sources (env vars, gh CLI)

## Research Process

### Files Examined:

- `.claude/skills/iw-install/scripts/manage_workflow.py` (all lines)
  - Finding: Script makes 80-100+ GitHub API requests per installation
  - Current approach: Individual HTTP requests for each file
  - No authentication headers present
  - Simple retry logic without backoff

- `.claude/skills/iw-install/SKILL.md` (documentation)
  - Finding: Documents HTTP-based installation process
  - Confirms git is listed as "optional" (will need to change to required)

- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:120-187`
  - Finding: Good error handling pattern for HTTP requests
  - Pattern: Returns `(success, data, error)` tuple
  - Uses requests library with timeouts

- `.claude/skills/obsidian-local-api/scripts/filesystem_ops.py`
  - Finding: Good file operation error handling patterns
  - Pattern: Defensive validation with clear error messages

### Sub-tasks Spawned:

1. **Task: Find GitHub API usage patterns (Explore agent)**
   - Result: Found that codebase uses `gh` CLI for GitHub operations (issue reader, PR creator)
   - Key discovery: No direct GitHub REST API usage elsewhere - all via `gh` CLI
   - The iw-install script is the ONLY place making direct API calls

2. **Task: Find error handling patterns (Explore agent)**
   - Result: Found consistent patterns across Python scripts
   - Key patterns:
     - Tuple return type: `(bool, data, Optional[str])`
     - Specific exception handling
     - Clear, actionable error messages
   - Example: obsidian_client.py has excellent HTTP error handling

3. **Task: Analyze rate limit issue (general-purpose agent)**
   - Result: Detailed breakdown of API request volume
   - Analysis:
     - `_list_directory_contents()` called ~33 times (one per skill subdirectory)
     - `_download_file()` called ~50-70 times (all individual files)
     - Total: 80-100+ requests per installation
     - Rate limit: 60 requests/hour unauthenticated
     - Conclusion: **Cannot complete even 1 installation within rate limit**

4. **Skill: iw-learnings** (search past learnings)
   - Result: No existing learnings about GitHub API or rate limiting
   - This is a new problem area
   - Documented new learning in `.docs/knowledge/learnings/installation.md`

### Questions Asked & Answers:

1. Q: Should we add GitHub token authentication to avoid rate limiting?
   **A: No - better approach is to clone the repo instead of individual API requests**

   User correction: Instead of adding authentication to 100+ API requests, simply clone the repository once with git and copy files from the clone.

   Follow-up research:
   - Verified git is already installed on the system: `git --version` = 2.43.0
   - Verified subprocess is already imported in the script
   - Confirmed git clone approach will work

2. Q: What should happen if git is not installed?
   **A: Fail with clear error message** (from recommended options)

3. Q: Should we cache the clone for future updates?
   **A: No, keep it simple - clone fresh each time and clean up**  (from recommended options)

4. Q: Should we show git output to user?
   **A: No, suppress git output and show simple progress messages** (from recommended options)

## Key Discoveries

### Technical Discoveries:

- **Rate Limit Math**: `.claude/skills/iw-install/scripts/manage_workflow.py:120-195`
  - Each skill installation requires ~7-9 requests minimum
  - 11 skills × 7 requests = 77 requests minimum
  - Plus commands (4) and hooks (2) = 83+ requests total
  - With subdirectories and recursive calls: **80-100+ requests realistic**
  - GitHub limit: 60 requests/hour unauthenticated
  - **Result: Cannot complete 1 installation within limit!**

- **Git Already Available**: System check showed git 2.43.0 installed
  - No need to add git as dependency (already present)
  - Just need to document it as required

- **subprocess Already Imported**: Line 20 of manage_workflow.py
  - Can use subprocess.run() directly for git commands
  - No need to add imports

- **Error Handling Patterns**: Found consistent patterns across codebase
  - File operations use try/except with specific error types
  - HTTP operations return tuple `(success, data, error)`
  - Clear error messages with troubleshooting steps

### Patterns to Follow:

- **Error Handling Pattern** from `obsidian_client.py:120-187`:
  ```python
  try:
      result = subprocess.run(...)
      return True, data, None
  except subprocess.CalledProcessError as e:
      return False, None, f"Error: {e}"
  except FileNotFoundError:
      return False, None, "git command not found. Install with..."
  ```

- **Cleanup Pattern** from filesystem operations:
  ```python
  try:
      shutil.rmtree(temp_dir)
  except Exception as e:
      # Non-fatal, just warn
      print(f"Warning: cleanup failed: {e}")
  ```

### Constraints Identified:

- Must maintain same user-facing interface (command syntax unchanged)
- Must maintain same output format for consistency
- Must handle git not being installed gracefully
- Must clean up temporary clone directory
- Must make hook scripts executable (same as current behavior)
- Must track installed files for reporting (same as current behavior)

## Design Decisions

### Decision 1: Git Clone vs Token Authentication

**Options considered:**
- **Option A**: Add GitHub token authentication to existing HTTP requests
  - Pros: Minimal code changes, maintains existing architecture
  - Cons: Complex (multiple token sources), still makes 100+ requests, slower

- **Option B**: Replace HTTP requests with git clone
  - Pros: Simple, fast (1 operation), no rate limiting, less code
  - Cons: Adds git as hard requirement

**Chosen**: Option B (Git Clone)

**Rationale**: User correction pointed out that git clone is simpler and more robust. Analysis confirmed:
- 1 git operation vs 100+ HTTP operations
- Faster (5-10s vs 30-60s)
- Simpler code (fewer methods, less complexity)
- No rate limiting issues
- Git likely already installed on developer machines

### Decision 2: Shallow Clone vs Full Clone

**Options considered:**
- Full clone: Gets entire git history
- Shallow clone (`--depth 1`): Gets only latest commit

**Chosen**: Shallow clone with `--depth 1`

**Rationale**:
- Only need latest version for installation
- Faster download (less data)
- Less disk space used
- Git standard practice for CI/CD and installation scripts

### Decision 3: Temporary Clone Cleanup

**Options considered:**
- Cache clone for future updates (reuse)
- Always delete after installation

**Chosen**: Always delete after installation

**Rationale**:
- Simpler (no cache management logic)
- No stale cache issues
- Minimal performance impact (clone is fast)
- Less disk space usage
- Follows user's recommended approach: "keep it simple"

### Decision 4: Error Handling for Missing Git

**Options considered:**
- Fail with error and require git
- Fall back to old HTTP method if git not found

**Chosen**: Fail with clear error message

**Rationale**:
- Follows user's recommended approach
- Simpler (no dual-strategy complexity)
- Git is standard tool on developer machines
- Error message provides installation instructions
- Maintains single code path (easier to maintain)

### Decision 5: Progress Output During Clone

**Options considered:**
- Show git clone output (verbose)
- Suppress git output, show simple progress message

**Chosen**: Suppress git output

**Rationale**:
- Follows user's recommended approach
- Cleaner, more professional output
- Consistent with current installation output style
- Git output can be confusing to users
- Use `capture_output=True` in subprocess.run()

## Open Questions (During Research)

- [x] **Should we use token authentication?** - Resolved: No, use git clone instead (user correction)
- [x] **What token sources to check?** - Resolved: N/A, not using tokens
- [x] **Should we add exponential backoff?** - Resolved: N/A, not using HTTP retries
- [x] **How to handle git not installed?** - Resolved: Fail with clear error message
- [x] **Should we cache the clone?** - Resolved: No, delete after use (keep simple)
- [x] **Should we show git output?** - Resolved: No, suppress output (cleaner UX)
- [x] **Is git already installed?** - Resolved: Yes, git 2.43.0 present on system
- [x] **Do we need to add git to dependencies?** - Resolved: Just document as required (not optional)

**Note**: All questions resolved before finalizing the plan.

## Corrections During Planning

### User Correction: Clone Repo Instead of Token Auth

**Date**: 2025-11-03
**Context**: Proposed adding GitHub token authentication to HTTP requests
**Correction**: User pointed out that cloning the repo is a much simpler and more robust solution
**Impact**: Complete redesign of approach - replaced authentication strategy with git clone strategy
**Documented**: `.docs/knowledge/learnings/installation.md`

**Reasoning for correction**:
- Git clone is simpler (1 operation vs managing tokens)
- No need for environment variables or token management
- No need for retry logic or rate limit detection
- Faster (git pack protocol is optimized)
- More reliable (git handles all the complexity)
- Standard practice for installation scripts

This correction fundamentally changed the implementation approach and resulted in a much better solution.

## Code Snippets Reference

### Current HTTP-Based Installation:

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
    result = self._fetch_json(url)
    # Returns list of file/directory info

# From .claude/skills/iw-install/scripts/manage_workflow.py:165-195
def _download_directory(self, repo_path: str, local_dir: Path, recursive: bool = True) -> int:
    """Download entire directory from GitHub."""
    contents = self._list_directory_contents(repo_path)  # API call
    count = 0
    for item in contents:
        if item_type == "file":
            self._download_file(item_path, local_file)  # Raw request
        elif item_type == "dir" and recursive:
            count += self._download_directory(item_path, subdir, recursive=True)  # Recursive!
    return count
```

**Problem**: Recursive directory traversal multiplies API requests exponentially.

### Error Handling Pattern to Follow:

```python
# From .claude/skills/obsidian-local-api/scripts/obsidian_client.py:150-186
try:
    response = self.session.request(method, url, ...)

    if response.status_code >= 400:
        error_msg = self._parse_error(response)
        return False, None, error_msg

    return True, response.json(), None

except requests.exceptions.ConnectionError:
    return False, None, "Connection refused. Ensure service is running..."
except requests.exceptions.Timeout:
    return False, None, "Request timed out. Check network connection."
except requests.exceptions.RequestException as e:
    return False, None, f"Request failed: {str(e)}"
```

**Pattern**: Specific exception types with helpful error messages.

### File Operation Pattern to Follow:

```python
# From .claude/skills/obsidian-local-api/scripts/filesystem_ops.py:70-83
def read_note(self, note_path: str) -> Tuple[bool, str, Optional[str]]:
    try:
        full_path = self._resolve_note_path(note_path)

        if not full_path.exists():
            return False, None, f"Note not found: {note_path}"

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return True, content, None

    except Exception as e:
        return False, None, f"Failed to read note: {str(e)}"
```

**Pattern**: Validate first, then perform operation, catch all exceptions.

## Research Artifacts

### GitHub API Rate Limit Info:
- Unauthenticated: 60 requests/hour per IP
- Authenticated: 5,000 requests/hour per user
- Raw content (raw.githubusercontent.com): Higher limit but still throttles
- Source: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting

### Git Clone Performance:
- Shallow clone (`--depth 1`): Only downloads latest commit
- Typical size: 2-3 MB compressed for this repo
- Typical time: 5-10 seconds on normal connection
- Source: Tested on local system

### System Environment:
```bash
$ git --version
git version 2.43.0

$ python3 --version
Python 3.11.x

$ which git
/usr/bin/git
```

## Summary

**Problem**: Installation makes 80-100+ GitHub API requests, exceeding 60/hour rate limit.

**Root Cause**: Individual HTTP requests for each file instead of bulk operation.

**Solution**: Replace HTTP-based downloads with single git clone operation.

**Key Insight** (from user correction): Git clone is simpler, faster, and more robust than trying to optimize HTTP requests with authentication.

**Implementation**: 3 phases
- Phase 1: Add git clone methods (clone, copy, cleanup)
- Phase 2: Replace install() method to use git clone
- Phase 3: Update documentation

**Result**: Installation becomes faster (5-10s vs 30-60s), more reliable (no rate limiting), and simpler (less code to maintain).
