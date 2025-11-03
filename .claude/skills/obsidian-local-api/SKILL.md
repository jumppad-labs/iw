---
name: obsidian-local-api
description: Interact with Obsidian notes through the Local REST API. This skill should be used when users request operations on their Obsidian vault such as creating/reading/updating notes, searching the vault, managing daily/periodic notes, or automating note-taking workflows. Requires the Obsidian Local REST API plugin to be installed and running.
---

# Obsidian Local REST API

## Overview

This skill enables Claude to interact with a local Obsidian vault through the secure REST API provided by the Obsidian Local REST API plugin. Use this skill to automate note creation, content management, search operations, and workflow automation within Obsidian.

## When to Use This Skill

Invoke this skill when users request:
- Creating, reading, updating, or deleting Obsidian notes
- Searching their Obsidian vault
- Managing daily, weekly, or periodic notes
- Automating note-taking workflows
- Batch operations on multiple notes
- Integration with external tools through Obsidian
- Executing Obsidian commands programmatically

## Prerequisites Check

Before performing operations, verify:
1. **Obsidian is running** with the Local REST API plugin enabled
2. **API key is configured** (user can find in plugin settings)
3. **Connectivity** to localhost:27124 (default HTTPS port)

Use `scripts/config_helper.py` for first-time configuration setup.

## Fallback Behavior

The skill uses a **try-API-first with filesystem fallback** approach for reliability:

### Primary Method: REST API
- All operations attempt REST API first
- Faster for small files
- Provides Obsidian features (caching, plugins, live updates)
- Requires Obsidian running

### Fallback Method: Filesystem
- Activates automatically on API failure
- Handles large files (>1MB) that timeout via API
- Works when Obsidian closed or API unavailable
- Requires vault path configuration

### When Fallback Activates

Filesystem fallback automatically activates when:
- API request times out (>120 seconds)
- API returns error (connection refused, authentication failed, etc.)
- File size causes API processing failure
- Obsidian is not running

### Vault Path Configuration

**First-time setup**: When fallback is first needed, you'll be prompted:
```
⚠️  Filesystem Fallback Required
The Obsidian API operation failed or timed out.
To continue, please provide your Obsidian vault path.

Enter vault path (or press Enter to cancel): /Users/name/Documents/ObsidianVault
✅ Vault path validated
✅ Configuration saved. Future operations will use filesystem fallback automatically.
```

**Manual configuration**:
```bash
python3 scripts/config_helper.py --set-vault-path "/path/to/vault"
```

**View current configuration**:
```bash
python3 scripts/config_helper.py --show
```

### Transparency

Fallback is transparent - scripts work identically whether using API or filesystem:
- Same commands
- Same parameters
- Same output format
- Same error handling

You'll see informational messages when fallback is used:
```
ℹ️  API write failed (Request timed out), trying filesystem fallback...
✅ Note created: Research/large-report.md
```

## Workflow Decision Tree

### User Request: "Create a note"

1. Ask for note path if not provided (e.g., "Daily/2025-01-03.md")
2. Ask for initial content if not provided
3. Check if frontmatter is needed (tags, metadata)
4. Use `scripts/create_note.py` to create the note
5. Confirm success and show note path

**Example**:
```bash
cd /path/to/skill
python3 scripts/create_note.py "Daily/2025-01-03.md" \
  --content "# Today's Notes\n\n## Tasks\n- [ ]"
```

### User Request: "Read a note"

1. Identify note path from user request
2. Determine if JSON format (with metadata) or raw markdown needed
3. Use `scripts/read_note.py` to retrieve content
4. Display content in readable format

**Example**:
```bash
# Read as markdown
python3 scripts/read_note.py "Daily/2025-01-03.md"

# Read with metadata
python3 scripts/read_note.py "Daily/2025-01-03.md" --format json
```

### User Request: "Add to my daily note"

1. Determine if specific date or today's note
2. Get content to append
3. Optionally determine which section/heading
4. Use `scripts/append_note.py` with appropriate options
5. Confirm addition

**Example**:
```bash
# Append to end
python3 scripts/append_note.py "Daily/2025-01-03.md" "- Completed task X"

# Insert at specific heading
python3 scripts/append_note.py "Daily/2025-01-03.md" \
  "New research findings" \
  --heading "## Research"
```

### User Request: "Search my notes for X"

1. Extract search query from user request
2. Determine context length needed
3. Use `scripts/search_vault.py` to search
4. Present results with file paths and context
5. Offer to read specific notes if requested

**Example**:
```bash
python3 scripts/search_vault.py "machine learning"
python3 scripts/search_vault.py "TODO" --context-length 200
```

### User Request: "Execute command X"

1. First use `scripts/list_commands.py` to find available commands
2. Identify command ID matching user's intent
3. Use `scripts/execute_command.py` to run the command
4. Report results

**Example**:
```bash
# List commands to find the right one
python3 scripts/list_commands.py --filter "export"

# Execute specific command
python3 scripts/execute_command.py "editor:toggle-bold"
```

## Common Patterns

### Creating Structured Notes

When creating notes with structure:

```bash
# Create with frontmatter and initial structure
python3 scripts/create_note.py "Projects/new-project.md" \
  --frontmatter '{"tags": ["project", "active"], "status": "planning"}' \
  --content "# New Project\n\n## Overview\n\n## Tasks\n\n## Notes"
```

### Daily Note Automation

For daily note operations:

```bash
# Append to today's daily note
TODAY=$(date +%Y-%m-%d)
python3 scripts/append_note.py "Daily/${TODAY}.md" "- Completed task X"

# Add to specific section
python3 scripts/append_note.py "Daily/${TODAY}.md" \
  "New finding" \
  --heading "## Research"
```

### Batch Operations

For operations on multiple notes:
1. Use `scripts/search_vault.py` to find candidate notes
2. Extract file paths from results
3. Loop through paths, using `scripts/read_note.py` and `scripts/append_note.py`

**Example**:
```python
import subprocess
import json

# Search for notes
result = subprocess.run(
    ["python3", "scripts/search_vault.py", "project"],
    capture_output=True,
    text=True
)

# Process each result
# (Parse output and perform operations on each note)
```

## Error Handling

Common errors and solutions:

**"Connection refused"**
→ Ensure Obsidian is running with Local REST API plugin enabled

**"Authentication failed"**
→ Check API key configuration: `python3 scripts/config_helper.py --show`
→ Update key: `python3 scripts/config_helper.py --set-key "your-key"`

**"SSL certificate verify failed"**
→ The plugin uses self-signed certificates; scripts handle this automatically
→ If issues persist, download cert from http://localhost:27123/cert.pem

**"Note not found"**
→ Verify path is correct relative to vault root
→ Use forward slashes, include .md extension

## Setup for New Users

When a user first uses this skill:

1. **Check if configured**:
   ```bash
   python3 scripts/config_helper.py --test
   ```

2. **If not configured**, guide them:
   - Open Obsidian Settings → Community Plugins → Local REST API
   - Click "Copy API Key"
   - Run: `python3 scripts/config_helper.py`
   - Paste API key when prompted

3. **Test basic operation**:
   ```bash
   python3 scripts/list_commands.py
   ```

## Resources

### Scripts (`scripts/`)

Executable utilities for API operations:

- **`obsidian_client.py`** - Core API client module (imported by other scripts)
  - Connection configuration (host, port, API key)
  - Authentication header management
  - Request wrappers (GET, POST, PUT, PATCH, DELETE)
  - SSL certificate handling
  - Error handling and response parsing

- **`create_note.py`** - Create new notes with optional frontmatter
  - Usage: `python3 scripts/create_note.py <path> [--content TEXT] [--frontmatter JSON]`
  - Creates notes at specified vault path
  - Supports YAML frontmatter for metadata
  - Automatically formats frontmatter from JSON

- **`read_note.py`** - Read note content and metadata
  - Usage: `python3 scripts/read_note.py <path> [--format markdown|json]`
  - Default: Returns raw markdown
  - With `--format json`: Returns metadata + content

- **`append_note.py`** - Append or insert content into notes
  - Usage: `python3 scripts/append_note.py <path> <content> [--heading TEXT]`
  - Without `--heading`: Appends to end of note
  - With `--heading`: Inserts content after specified heading

- **`search_vault.py`** - Search vault with simple text queries
  - Usage: `python3 scripts/search_vault.py <query> [--context-length N]`
  - Returns matching notes with context snippets
  - Adjustable context length (default: 100 characters)

- **`list_commands.py`** - List available Obsidian commands
  - Usage: `python3 scripts/list_commands.py [--filter TEXT]`
  - Shows all executable commands in Obsidian
  - Optional filtering by keyword

- **`execute_command.py`** - Execute Obsidian commands programmatically
  - Usage: `python3 scripts/execute_command.py <command-id>`
  - Triggers any Obsidian command
  - Use with list_commands.py to find command IDs

- **`config_helper.py`** - Interactive configuration tool
  - Usage: `python3 scripts/config_helper.py [--show|--test|--set-key KEY]`
  - Interactive setup wizard
  - Configuration testing
  - Secure credential storage

All scripts support `--help` for detailed usage information.

### References (`references/`)

Detailed documentation loaded as needed:

- **`api_reference.md`** - Complete endpoint documentation with examples
  - All API endpoints (vault, commands, search, etc.)
  - Request/response formats
  - Authentication details
  - Error codes and handling
  - SSL certificate information

- **`use_cases.md`** - Practical scenarios and workflow patterns
  - Daily journal automation
  - Task management integration
  - Research note organization
  - Meeting notes generation
  - Batch operations
  - External tool integration

- **`configuration.md`** - Setup and troubleshooting guide
  - Plugin installation steps
  - API key retrieval
  - Network configuration
  - Security considerations
  - Common troubleshooting scenarios

**When to load references:**
- Load `api_reference.md` for complex or advanced API operations
- Load `use_cases.md` when planning multi-step workflows
- Load `configuration.md` when troubleshooting connectivity issues

## Examples

### Example 1: Create Daily Note

**User**: "Create a daily note for today with my morning routine checklist"

**Claude**:
1. Determine today's date
2. Use `scripts/create_note.py` to create Daily/YYYY-MM-DD.md
3. Include structured checklist in content
4. Confirm creation

**Implementation**:
```bash
TODAY=$(date +%Y-%m-%d)
python3 scripts/create_note.py "Daily/${TODAY}.md" \
  --frontmatter '{"date": "'${TODAY}'", "tags": ["daily"]}' \
  --content "# ${TODAY}

## Morning Routine
- [ ] Exercise
- [ ] Breakfast
- [ ] Review today's goals

## Tasks

## Notes"
```

### Example 2: Search and Summarize

**User**: "Find all notes mentioning 'project alpha' and summarize them"

**Claude**:
1. Use `scripts/search_vault.py "project alpha"`
2. Extract file paths from search results
3. Use `scripts/read_note.py` for each result
4. Analyze and summarize content
5. Present comprehensive summary

**Implementation**:
```bash
# Search for notes
python3 scripts/search_vault.py "project alpha"

# Read each matching note
for note in matching_notes; do
    python3 scripts/read_note.py "$note"
done

# Analyze and provide summary to user
```

### Example 3: Append Meeting Notes

**User**: "Add these meeting notes to my work journal"

**Claude**:
1. Identify journal note path from context
2. Format meeting notes with timestamp
3. Use `scripts/append_note.py` with appropriate heading
4. Confirm addition

**Implementation**:
```bash
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
python3 scripts/append_note.py "Work/journal.md" \
  "### Meeting ${TIMESTAMP}
- Discussed Q1 goals
- Action items assigned
- Next meeting: Friday" \
  --heading "## Meetings"
```

## Best Practices

1. **Always verify configuration first** - Use config_helper.py to check connectivity
2. **Use relative paths** - All paths are relative to vault root
3. **Include file extensions** - Always use .md for markdown notes
4. **Handle errors gracefully** - Provide helpful troubleshooting guidance
5. **Respect vault structure** - Ask user before creating new top-level folders
6. **Preserve formatting** - When updating notes, maintain existing structure
7. **Use frontmatter consistently** - Follow vault's existing metadata patterns

## Advanced Operations

### Using the API Client Directly

For custom operations, use the obsidian_client module:

```python
import sys
from pathlib import Path

# Import client
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from obsidian_client import get_client

# Create client
client = get_client()

# Test connection
success, message = client.test_connection()
if not success:
    print(f"Error: {message}")
    sys.exit(1)

# Custom operations
success, data, error = client.get("/vault/note.md")
if success:
    print(data)
else:
    print(f"Error: {error}")
```

### Complex Workflows

For complex multi-step workflows:
1. Read `references/use_cases.md` for patterns
2. Break down into atomic operations
3. Use scripts in sequence
4. Handle errors at each step
5. Provide clear progress updates to user

## Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Connection refused | Ensure Obsidian running, plugin enabled |
| Authentication failed | Update API key: `config_helper.py --set-key "new-key"` |
| File not found | Check path, include .md extension |
| SSL errors | Scripts handle automatically for localhost |
| Module not found | `pip install requests` |

For detailed troubleshooting, load `references/configuration.md`.

## Notes

- Scripts are designed to work independently of this skill
- Can be used in automation scripts, cron jobs, CI/CD pipelines
- All scripts return appropriate exit codes (0 = success)
- Configuration is shared across all scripts
- Safe for concurrent operations (API handles locking)
