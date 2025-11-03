# Implementation Plan: Obsidian Local REST API Skill

## Overview

Create a Claude Code skill that wraps the Obsidian Local REST API, enabling Claude to interact with a local Obsidian vault through a secure REST interface. This skill will provide structured workflows for common note-taking automation tasks, bundled utility scripts for API interactions, and comprehensive reference documentation.

## Phases

### Phase 1: Initialize Skill Structure

**Objective**: Create the skill directory structure with all necessary components.

**Tasks**:
1. Use the skill-creator's init_skill.py script to generate the initial structure
2. Create the obsidian-local-api skill in `.claude/skills/`
3. Verify directory structure includes scripts/, references/, and assets/

**Commands**:
```bash
# Initialize the skill using the skill-creator script
python3 .claude/skills/skill-creator/scripts/init_skill.py obsidian-local-api --path .claude/skills
```

**Expected Output**:
```
.claude/skills/obsidian-local-api/
├── SKILL.md
├── scripts/
│   └── example.py
├── references/
│   └── api_reference.md
└── assets/
    └── example_asset.txt
```

**Success Criteria**:
- Skill directory exists with proper structure
- SKILL.md template is present
- All resource directories created

---

### Phase 2: Create API Client Utility Scripts

**Objective**: Build reusable Python scripts for common Obsidian API operations.

**Tasks**:
1. Create a base API client module with authentication and connection handling
2. Implement scripts for core operations: create note, read note, update note, search vault
3. Add error handling and user-friendly output formatting
4. Make scripts executable and self-contained

**Files to Create**:

#### `scripts/obsidian_client.py`
Core API client module with:
- Connection configuration (host, port, API key)
- Authentication header management
- Request wrapper functions (GET, POST, PUT, PATCH, DELETE)
- SSL certificate handling for self-signed certs
- Error handling and response parsing

#### `scripts/create_note.py`
```python
#!/usr/bin/env python3
"""
Create a new note in the Obsidian vault.

Usage:
    create_note.py <path> [--content <content>] [--frontmatter <json>]

Examples:
    create_note.py "Daily/2025-01-03.md" --content "# Today's Notes"
    create_note.py "Projects/new-project.md" --frontmatter '{"tags": ["project"]}'
"""
# - Parse command-line arguments
# - Load API credentials from config or env vars
# - Build note content with optional frontmatter
# - Send PUT request to /vault/{path}
# - Handle errors gracefully
# - Output success message with file path
```

#### `scripts/read_note.py`
```python
#!/usr/bin/env python3
"""
Read a note from the Obsidian vault.

Usage:
    read_note.py <path> [--format json|markdown]

Examples:
    read_note.py "Daily/2025-01-03.md"
    read_note.py "Projects/project.md" --format json
"""
# - Parse path argument
# - Send GET request to /vault/{path}
# - Handle Accept header for JSON vs raw markdown
# - Pretty-print output
# - Return appropriate exit code
```

#### `scripts/append_note.py`
```python
#!/usr/bin/env python3
"""
Append content to an existing note.

Usage:
    append_note.py <path> <content> [--heading <section>]

Examples:
    append_note.py "Daily/2025-01-03.md" "- Task completed"
    append_note.py "Projects/notes.md" "New findings" --heading "## Research"
"""
# - Parse arguments
# - Choose POST (append) or PATCH (insert at heading)
# - Send appropriate request
# - Confirm success
```

#### `scripts/search_vault.py`
```python
#!/usr/bin/env python3
"""
Search the Obsidian vault for notes matching a query.

Usage:
    search_vault.py <query> [--context-length N]

Examples:
    search_vault.py "machine learning"
    search_vault.py "TODO" --context-length 50
"""
# - Parse search query and options
# - Send POST to /search/simple/
# - Format results with file paths and context
# - Display match count
```

#### `scripts/list_commands.py`
```python
#!/usr/bin/env python3
"""
List available Obsidian commands that can be executed via API.

Usage:
    list_commands.py [--filter <text>]

Examples:
    list_commands.py
    list_commands.py --filter "export"
"""
# - Send GET to /commands/
# - Parse command list
# - Optional filtering
# - Display in readable format
```

#### `scripts/execute_command.py`
```python
#!/usr/bin/env python3
"""
Execute an Obsidian command.

Usage:
    execute_command.py <command-id>

Examples:
    execute_command.py "editor:toggle-bold"
    execute_command.py "markdown:export-pdf"
"""
# - Parse command ID
# - Send POST to /commands/{id}/
# - Handle response
# - Report success/failure
```

#### `scripts/config_helper.py`
```python
#!/usr/bin/env python3
"""
Interactive configuration helper for Obsidian API credentials.

Usage:
    config_helper.py [--show] [--set-key <key>] [--set-host <host>] [--set-port <port>]

Examples:
    config_helper.py --set-key "abc123xyz"
    config_helper.py --show
"""
# - Store config in ~/.obsidian-api or project-local .env
# - Interactive prompts for first-time setup
# - Secure key storage
# - Validate connectivity
```

**Implementation Details**:
- Use `requests` library for HTTP operations
- Support environment variables: `OBSIDIAN_API_KEY`, `OBSIDIAN_HOST`, `OBSIDIAN_PORT`
- Default to localhost:27124 (HTTPS)
- Handle SSL certificate verification (self-signed certs common)
- Provide clear error messages for common issues (not running, wrong API key, etc.)

**Success Criteria**:
- All scripts are executable (`chmod +x`)
- Scripts work independently without importing the skill
- Error messages are helpful and actionable
- Scripts return appropriate exit codes (0 for success)
- Configuration can be managed via environment or config file

---

### Phase 3: Create API Reference Documentation

**Objective**: Provide comprehensive reference material for the Obsidian Local REST API that Claude can load as needed.

**Tasks**:
1. Create detailed endpoint reference documentation
2. Document authentication and configuration
3. Include practical examples and use cases
4. Add troubleshooting section

**Files to Create**:

#### `references/api_reference.md`
Complete endpoint documentation including:
- Authentication setup (finding API key in Obsidian settings)
- Base URL and port configuration
- All endpoints organized by category:
  - Vault file operations (GET, PUT, POST, PATCH, DELETE /vault/*)
  - Active file operations (GET, PUT, POST, PATCH, DELETE /active/)
  - Periodic notes (GET, PUT, POST, PATCH, DELETE /periodic/*)
  - Commands (GET /commands/, POST /commands/:id/)
  - Search (POST /search/simple/, POST /search/)
  - Open file (POST /open/*)
- Request/response examples for each endpoint
- Error codes and handling
- SSL certificate considerations

#### `references/use_cases.md`
Practical scenarios and workflows:
- Daily journal automation
- Task management integration
- Research note organization
- Meeting notes generation
- Documentation automation
- Cross-referencing and linking
- Batch operations on multiple notes
- Integration with external tools (browser extensions, mobile apps, CLI tools)

#### `references/configuration.md`
Setup and configuration guide:
- Installing the Obsidian Local REST API plugin
- Finding and copying the API key
- Network configuration (local vs remote access)
- HTTPS vs HTTP settings
- Security considerations
- Certificate management
- Troubleshooting connectivity issues

**Success Criteria**:
- Documentation is comprehensive but scannable
- Examples are practical and copy-pasteable
- Covers both common and advanced use cases
- Troubleshooting section addresses common issues

---

### Phase 4: Write Main SKILL.md

**Objective**: Create the primary skill instruction file that guides Claude's usage of the Obsidian API wrapper.

**Tasks**:
1. Write clear skill description and metadata
2. Define when to use the skill (trigger conditions)
3. Create workflow decision tree for different operations
4. Document how to use bundled scripts and references
5. Include practical examples of user requests

**Structure**:

```markdown
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

## Workflow Decision Tree

### User Request: "Create a note"
1. Ask for note path if not provided (e.g., "Daily/2025-01-03.md")
2. Ask for initial content if not provided
3. Check if frontmatter is needed (tags, metadata)
4. Use `scripts/create_note.py` to create the note
5. Confirm success and show note path

### User Request: "Read a note"
1. Identify note path from user request
2. Determine if JSON format (with metadata) or raw markdown needed
3. Use `scripts/read_note.py` to retrieve content
4. Display content in readable format

### User Request: "Add to my daily note"
1. Determine if specific date or today's note
2. Get content to append
3. Optionally determine which section/heading
4. Use `scripts/append_note.py` with appropriate options
5. Confirm addition

### User Request: "Search my notes for X"
1. Extract search query from user request
2. Determine context length needed
3. Use `scripts/search_vault.py` to search
4. Present results with file paths and context
5. Offer to read specific notes if requested

### User Request: "Execute command X"
1. First use `scripts/list_commands.py` to find available commands
2. Identify command ID matching user's intent
3. Use `scripts/execute_command.py` to run the command
4. Report results

## Common Patterns

### Creating Structured Notes

When creating notes with structure:
```bash
# Create with frontmatter and initial structure
scripts/create_note.py "Projects/new-project.md" \
  --frontmatter '{"tags": ["project", "active"], "status": "planning"}' \
  --content "# New Project\n\n## Overview\n\n## Tasks\n\n## Notes"
```

### Daily Note Automation

For daily note operations:
```bash
# Append to today's daily note
scripts/append_note.py "Daily/$(date +%Y-%m-%d).md" "- Completed task X"

# Add to specific section
scripts/append_note.py "Daily/$(date +%Y-%m-%d).md" "New finding" --heading "## Research"
```

### Batch Operations

For operations on multiple notes:
1. Use `scripts/search_vault.py` to find candidate notes
2. Extract file paths from results
3. Loop through paths, using `scripts/read_note.py` and `scripts/append_note.py`

## Error Handling

Common errors and solutions:

**"Connection refused"**
→ Ensure Obsidian is running with Local REST API plugin enabled

**"Authentication failed"**
→ Check API key configuration: `scripts/config_helper.py --show`
→ Update key: `scripts/config_helper.py --set-key "your-key"`

**"SSL certificate verify failed"**
→ The plugin uses self-signed certificates; scripts handle this automatically
→ If issues persist, download cert from http://localhost:27123/cert.pem

**"Note not found"**
→ Verify path is correct relative to vault root
→ Use forward slashes, include .md extension

## Resources

### Scripts (`scripts/`)

Executable utilities for API operations:
- `obsidian_client.py` - Core API client module (imported by other scripts)
- `create_note.py` - Create new notes with optional frontmatter
- `read_note.py` - Read note content and metadata
- `append_note.py` - Append or insert content into notes
- `search_vault.py` - Search vault with simple text queries
- `list_commands.py` - List available Obsidian commands
- `execute_command.py` - Execute Obsidian commands programmatically
- `config_helper.py` - Interactive configuration tool

All scripts support `--help` for detailed usage information.

### References (`references/`)

Detailed documentation loaded as needed:
- `api_reference.md` - Complete endpoint documentation with examples
- `use_cases.md` - Practical scenarios and workflow patterns
- `configuration.md` - Setup and troubleshooting guide

**When to load references:**
- Load `api_reference.md` for complex or advanced API operations
- Load `use_cases.md` when planning multi-step workflows
- Load `configuration.md` when troubleshooting connectivity issues

## Examples

**User**: "Create a daily note for today with my morning routine checklist"
**Claude**:
1. Determine today's date
2. Use `scripts/create_note.py` to create Daily/YYYY-MM-DD.md
3. Include structured checklist in content
4. Confirm creation

**User**: "Find all notes mentioning 'project alpha' and summarize them"
**Claude**:
1. Use `scripts/search_vault.py "project alpha"`
2. Extract file paths from search results
3. Use `scripts/read_note.py` for each result
4. Analyze and summarize content
5. Present comprehensive summary

**User**: "Add these meeting notes to my work journal"
**Claude**:
1. Identify journal note path from context
2. Format meeting notes with timestamp
3. Use `scripts/append_note.py` with appropriate heading
4. Confirm addition

## Best Practices

1. **Always verify configuration first** - Use config_helper.py to check connectivity
2. **Use relative paths** - All paths are relative to vault root
3. **Include file extensions** - Always use .md for markdown notes
4. **Handle errors gracefully** - Provide helpful troubleshooting guidance
5. **Respect vault structure** - Ask user before creating new top-level folders
6. **Preserve formatting** - When updating notes, maintain existing structure
7. **Use frontmatter consistently** - Follow vault's existing metadata patterns
```

**Success Criteria**:
- SKILL.md is complete and well-structured
- Description clearly indicates when to use the skill
- Workflows are practical and easy to follow
- Examples demonstrate real-world usage
- Resources section explains how to use bundled files

---

### Phase 5: Create Example Assets (Optional)

**Objective**: Provide template files for common note structures.

**Tasks**:
1. Create template files for common note types
2. Include example frontmatter formats
3. Add template selection helper script

**Files to Create** (optional):

#### `assets/templates/daily-note.md`
```markdown
---
date: {{DATE}}
tags: [daily]
---

# {{DATE}}

## Tasks
- [ ]

## Notes


## Reflections

```

#### `assets/templates/meeting-note.md`
```markdown
---
date: {{DATE}}
type: meeting
attendees: []
tags: [meeting]
---

# Meeting: {{TITLE}}

## Agenda


## Discussion


## Action Items
- [ ]

## Next Steps

```

#### `assets/templates/project-note.md`
```markdown
---
title: {{TITLE}}
status: planning
tags: [project]
created: {{DATE}}
---

# {{TITLE}}

## Overview


## Goals


## Tasks
- [ ]

## Resources


## Notes

```

**Success Criteria**:
- Templates follow common Obsidian conventions
- Placeholders are clearly marked
- Templates are practical and reusable

---

### Phase 6: Testing and Validation

**Objective**: Verify all components work correctly and validate the skill structure.

**Tasks**:
1. Test all Python scripts independently
2. Verify scripts handle errors gracefully
3. Test with actual Obsidian instance (if available)
4. Run skill validator from skill-creator
5. Fix any validation errors

**Test Scenarios**:

1. **Configuration**:
   - Run config_helper.py and set up credentials
   - Verify config is stored correctly
   - Test connectivity check

2. **Basic Operations**:
   - Create a test note
   - Read the test note
   - Append content to the test note
   - Search for the test note
   - Delete the test note

3. **Error Handling**:
   - Test with Obsidian not running (expect connection error)
   - Test with wrong API key (expect auth error)
   - Test with non-existent path (expect not found error)
   - Verify error messages are helpful

4. **Skill Validation**:
```bash
# Run the skill validator
python3 .claude/skills/skill-creator/scripts/quick_validate.py .claude/skills/obsidian-local-api
```

**Success Criteria**:
- All scripts execute without errors (when properly configured)
- Error messages are clear and actionable
- Skill passes validation checks
- Documentation is accurate and complete

---

### Phase 7: Documentation and Packaging

**Objective**: Finalize documentation and prepare skill for use.

**Tasks**:
1. Complete all reference documentation
2. Add inline code comments
3. Create README for the skill directory
4. Optionally package the skill for distribution

**Files to Create/Update**:

#### `README.md` (in skill directory)
```markdown
# Obsidian Local REST API Skill

Interact with Obsidian notes through the Local REST API plugin.

## Prerequisites

1. Install Obsidian: https://obsidian.md
2. Install the "Local REST API" plugin from Obsidian's community plugins
3. Enable the plugin and note your API key from settings
4. Python 3.7+ with `requests` library

## Setup

1. Configure API credentials:
   ```bash
   cd .claude/skills/obsidian-local-api
   python3 scripts/config_helper.py
   ```

2. Test connectivity:
   ```bash
   python3 scripts/list_commands.py
   ```

## Usage

The skill is automatically available in Claude Code. Just ask Claude to:
- "Create a note in my Obsidian vault"
- "Search my notes for X"
- "Add to my daily note"
- "Read my project note"

## Manual Script Usage

All scripts can be used independently:

```bash
# Create a note
python3 scripts/create_note.py "Test/note.md" --content "Hello Obsidian"

# Read a note
python3 scripts/read_note.py "Test/note.md"

# Search
python3 scripts/search_vault.py "search term"

# List commands
python3 scripts/list_commands.py
```

## Troubleshooting

See `references/configuration.md` for detailed troubleshooting.

**Common issues:**
- Ensure Obsidian is running
- Check API key is correct in config
- Verify plugin is enabled in Obsidian settings
- Default port is 27124 (HTTPS)

## License

See LICENSE file in parent directory.
```

**Package for Distribution** (optional):
```bash
# Use skill-creator packaging script
python3 .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/obsidian-local-api
```

**Success Criteria**:
- README provides clear setup instructions
- All documentation is complete and accurate
- Code is well-commented
- Skill is ready for use in Claude Code

---

## Implementation Notes

### Technology Stack
- Python 3.7+ for all scripts
- `requests` library for HTTP operations
- Standard library for file operations and JSON parsing
- Environment variables for configuration

### Dependencies
```
requests>=2.25.0
```

### Configuration Options

**Environment Variables**:
- `OBSIDIAN_API_KEY` - API key from Obsidian plugin settings
- `OBSIDIAN_HOST` - Host address (default: localhost)
- `OBSIDIAN_PORT` - Port number (default: 27124)
- `OBSIDIAN_HTTPS` - Use HTTPS (default: true)

**Config File** (alternative to env vars):
- `~/.obsidian-api/config.json` - User-level configuration
- `.obsidian-api.json` - Project-level configuration

### Security Considerations

1. **API Key Storage**: Use secure config files or environment variables, never hardcode
2. **SSL Certificates**: Plugin uses self-signed certs, scripts must handle this
3. **Local Only**: Default to localhost binding for security
4. **Rate Limiting**: Be respectful with API calls
5. **Vault Access**: Full read/write access requires user authorization

### Error Recovery

Scripts should:
- Return non-zero exit codes on failure
- Print error messages to stderr
- Provide actionable guidance in error messages
- Gracefully handle network issues
- Validate inputs before making API calls

### Performance Considerations

- Scripts are lightweight, no heavy dependencies
- API is local, latency is minimal
- Search operations can be slow on large vaults
- Batch operations should be rate-limited if needed

---

## Testing Plan

### Unit Testing
- Test API client connection handling
- Test request/response parsing
- Test error handling paths
- Test configuration loading

### Integration Testing
- Test against live Obsidian instance
- Verify all CRUD operations
- Test search functionality
- Test command execution

### User Acceptance Testing
- Test common workflows end-to-end
- Verify documentation is clear
- Ensure error messages are helpful
- Confirm skill triggers appropriately

---

## Success Criteria

**Skill is successful when**:
1. ✅ All scripts execute correctly when properly configured
2. ✅ Documentation is comprehensive and accurate
3. ✅ Skill passes validation from skill-creator
4. ✅ Common use cases work smoothly (create, read, update, search)
5. ✅ Error handling is robust and user-friendly
6. ✅ Claude can successfully use the skill for Obsidian automation tasks
7. ✅ Configuration is straightforward for users
8. ✅ Scripts can be used both within the skill and independently

---

## Future Enhancements

Potential additions for future versions:
- Advanced search with Dataview DQL queries
- Periodic note templates (daily, weekly, monthly)
- Graph operations (find backlinks, connections)
- Batch import/export functionality
- Markdown parsing utilities
- Link management and validation
- Tag management operations
- Vault statistics and analytics

---

## Related Resources

- Obsidian Local REST API plugin: https://github.com/coddingtonbear/obsidian-local-rest-api
- Interactive API docs: https://coddingtonbear.github.io/obsidian-local-rest-api/
- Obsidian community: https://obsidian.md/community
- Plugin development: https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin
