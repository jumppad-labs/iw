# Context: Obsidian Local REST API Skill

## Background

### What is Obsidian?
Obsidian is a powerful knowledge management and note-taking application built on local markdown files. It emphasizes:
- Local-first storage (all notes are markdown files in a vault)
- Bidirectional linking between notes
- Graph visualization of note connections
- Extensive plugin ecosystem
- Privacy and data ownership

### What is the Obsidian Local REST API Plugin?
The Local REST API plugin for Obsidian exposes a secure REST interface that allows external tools to interact with an Obsidian vault programmatically. Key features:
- Secure HTTPS interface with API key authentication
- Full CRUD operations on notes
- Search capabilities
- Command execution
- Periodic notes support
- Self-signed SSL certificates for local security

### Why Create This Skill?
This skill enables Claude Code to:
1. Automate note-taking workflows
2. Integrate Obsidian with external tools and processes
3. Perform batch operations on vault content
4. Generate and update notes programmatically
5. Search and analyze vault content
6. Enhance productivity for Obsidian users

## Design Decisions

### Why Python for Scripts?
**Decision**: Use Python 3.7+ for all utility scripts

**Rationale**:
- Python is widely available and easy to install
- `requests` library provides excellent HTTP client functionality
- Standard library has robust JSON and file handling
- Scripts are cross-platform (Linux, macOS, Windows)
- Easy to read and maintain
- No compilation step needed

**Alternatives Considered**:
- Bash/curl: Less structured, harder error handling, platform-specific
- Node.js: Additional runtime dependency, less common in CLI tools
- Go: Requires compilation, overkill for simple API wrappers

### Why Bundled Scripts vs API Calls in SKILL.md?
**Decision**: Provide reusable Python scripts rather than inline API call instructions

**Rationale**:
- Scripts are executable independently (useful outside Claude)
- Consistent error handling across operations
- Reduces token usage (execute scripts vs generating code each time)
- Easier to test and validate
- More maintainable (update script vs update skill instructions)
- Follows pattern from existing skills (iw-github-issue-reader)

### Configuration Approach
**Decision**: Support both environment variables and config files

**Rationale**:
- Environment variables: Easy for temporary/CI use
- Config files: Better for persistent local setup
- Provide config_helper.py for user-friendly setup
- Follow XDG/standard paths (~/.obsidian-api/)

**Configuration Hierarchy**:
1. Command-line arguments (highest priority)
2. Environment variables
3. Project-local config file (.obsidian-api.json)
4. User-level config file (~/.obsidian-api/config.json)
5. Defaults (lowest priority)

### SSL Certificate Handling
**Decision**: Allow insecure SSL connections by default for localhost

**Rationale**:
- Obsidian plugin uses self-signed certificates
- Downloading and trusting cert adds setup complexity
- Localhost traffic is inherently secure (not leaving machine)
- Scripts can optionally verify cert if user provides path

**Security Trade-off**: This is acceptable because:
- API is bound to localhost by default
- Still requires API key authentication
- User explicitly enables the plugin
- Traffic never leaves the machine

### Script Granularity
**Decision**: Create separate scripts for each major operation (create, read, append, search, etc.)

**Rationale**:
- Clear single responsibility
- Easier to understand and use
- Better help text per script
- Simpler error handling
- Follows Unix philosophy (do one thing well)

**Alternative**: Single "obsidian-cli" tool with subcommands
- Rejected: More complex, harder to invoke from Claude, less flexible

### Reference Documentation Structure
**Decision**: Split references into three files: api_reference.md, use_cases.md, configuration.md

**Rationale**:
- Progressive disclosure: Load only what's needed
- api_reference.md: Technical endpoint details
- use_cases.md: Practical workflow guidance
- configuration.md: Setup and troubleshooting
- Keeps individual files focused and scannable
- Reduces context window usage

### Template Assets (Optional)
**Decision**: Include optional template assets for common note types

**Rationale**:
- Provides starting point for structured notes
- Demonstrates frontmatter conventions
- Optional: Can be deleted if not needed
- Small file size, minimal overhead
- Useful for users new to Obsidian

## Technical Constraints

### API Limitations
1. **Local only**: API only accessible from localhost by default
2. **Obsidian must be running**: API unavailable if app is closed
3. **Plugin required**: Users must install and enable the plugin
4. **Rate limits**: No official limits, but excessive requests could impact app performance
5. **Synchronous operations**: API doesn't support batch or async operations natively
6. **Path conventions**: All paths relative to vault root, must use forward slashes

### Python Version Support
- Minimum: Python 3.7 (for typing support, subprocess improvements)
- Target: Python 3.8+ (most common in 2025)
- Maximum: No upper limit, use compatible features

### Dependencies
- `requests`: Only external dependency
- Standard library only otherwise
- Keep dependencies minimal for easy installation

### Platform Compatibility
- Linux: Primary target
- macOS: Full support
- Windows: Should work, but test carefully (path handling, SSL)

## User Workflow

### Typical User Journey

1. **Initial Setup**:
   - User has Obsidian installed
   - User installs Local REST API plugin from community plugins
   - User enables plugin and copies API key
   - User runs `config_helper.py` to store credentials
   - Scripts test connectivity

2. **Daily Usage with Claude**:
   - User asks Claude: "Add to my daily note"
   - Claude detects Obsidian operation, invokes skill
   - Skill uses append_note.py to update note
   - Claude confirms success to user

3. **Advanced Automation**:
   - User requests: "Search my notes for project X and create a summary"
   - Claude uses search_vault.py to find notes
   - Claude uses read_note.py to retrieve content
   - Claude analyzes and creates summary
   - Claude uses create_note.py to save summary

4. **Manual Script Usage**:
   - Power users can invoke scripts directly
   - Useful for shell scripting and automation
   - Integration with other tools (cron, Make, etc.)

### Error Recovery
Common user issues and how skill handles them:

1. **Obsidian not running**:
   - Error: "Connection refused"
   - Guidance: "Start Obsidian and ensure Local REST API plugin is enabled"

2. **Wrong API key**:
   - Error: "Authentication failed (401)"
   - Guidance: "Check API key in plugin settings, update with config_helper.py"

3. **Note not found**:
   - Error: "Note not found (404)"
   - Guidance: "Verify path is correct, relative to vault root"

4. **Permission issues**:
   - Error: Script not executable
   - Guidance: "Run chmod +x scripts/*.py"

## API Endpoint Coverage

### Implemented in Phase 2
- ✅ GET /vault/* (read_note.py)
- ✅ PUT /vault/* (create_note.py)
- ✅ POST /vault/* (append_note.py - simple append)
- ✅ PATCH /vault/* (append_note.py - heading insertion)
- ❌ DELETE /vault/* (not implementing delete for safety)
- ✅ POST /search/simple/ (search_vault.py)
- ✅ GET /commands/ (list_commands.py)
- ✅ POST /commands/:id/ (execute_command.py)

### Not Implemented (Future Enhancements)
- GET/POST/PATCH/DELETE /active/ (active file operations)
- GET/POST/PATCH/DELETE /periodic/* (periodic notes - could add later)
- POST /search/ (advanced search with DQL/JSON Logic)
- POST /open/* (open file in Obsidian)

### Rationale for Scope
**Phase 2 focuses on core operations**:
- Most common use cases: create, read, append, search
- Command execution for advanced automation
- Safer operations (no delete)
- Foundation for future enhancements

**Future additions** based on user feedback:
- Periodic notes if daily/weekly note automation is popular
- Active file operations if editor integration is requested
- Advanced search if simple search proves insufficient
- File opening for navigation workflows

## Integration with Existing Skills

### Complementary Skills
This skill works well with:
- **iw-planner**: Create implementation notes in Obsidian
- **iw-executor**: Log progress to daily notes
- **iw-github-issue-reader**: Export issue data to notes
- General productivity and note-taking workflows

### Skill Composition
Users might request:
- "Fetch issue #123 and create an Obsidian note for it"
  - Uses iw-github-issue-reader + obsidian-local-api
- "Create a plan and log it to my Obsidian vault"
  - Uses iw-planner + obsidian-local-api

## Testing Strategy

### Unit Testing
- Mock HTTP responses for client module
- Test parsing and error handling
- Test configuration loading

### Integration Testing
- Requires running Obsidian instance
- Test against real API
- Verify operations in actual vault

### Manual Testing
- Test with Claude Code end-to-end
- Verify skill triggers appropriately
- Test error messages are helpful
- Confirm workflows are smooth

### Test Data
Create test vault structure:
```
test-vault/
├── Daily/
│   └── 2025-01-03.md
├── Projects/
│   └── test-project.md
└── Inbox/
    └── scratch.md
```

## Success Metrics

### Functional Success
- ✅ All core scripts work correctly
- ✅ Error handling is robust
- ✅ Documentation is clear and complete
- ✅ Skill passes validation

### User Experience Success
- ✅ Setup takes < 5 minutes
- ✅ Common operations "just work"
- ✅ Error messages lead to quick resolution
- ✅ Claude triggers skill appropriately

### Technical Success
- ✅ Scripts are cross-platform compatible
- ✅ Minimal dependencies
- ✅ Code is maintainable
- ✅ Performance is acceptable

## Risks and Mitigations

### Risk: Plugin API Changes
**Mitigation**: Document API version, test with latest plugin, use stable endpoints

### Risk: Cross-Platform Compatibility
**Mitigation**: Test on multiple platforms, use Path library, handle line endings

### Risk: SSL Certificate Issues
**Mitigation**: Handle self-signed certs gracefully, document cert management

### Risk: User Configuration Errors
**Mitigation**: Provide config_helper.py, clear error messages, troubleshooting docs

### Risk: Vault Corruption
**Mitigation**: Don't implement delete, validate inputs, recommend backups

## Open Questions

1. **Should we support remote Obsidian instances?**
   - Current: localhost only
   - Future: Could support remote with proper security warnings

2. **Should we implement periodic notes in Phase 2?**
   - Decision: No, add in future if requested
   - Rationale: Keep initial scope manageable

3. **How to handle vault selection?**
   - Current: Single vault in config
   - Future: Support multiple vaults with --vault flag

4. **Should scripts support stdin/stdout for piping?**
   - Current: Command-line arguments only
   - Future: Could add stdin for content, JSON output for piping

## References

- Obsidian Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api
- Interactive API docs: https://coddingtonbear.github.io/obsidian-local-rest-api/
- Obsidian: https://obsidian.md
- Skill Creator Guide: `.claude/skills/skill-creator/SKILL.md`
- Similar Skills: `.claude/skills/iw-github-issue-reader/`

## Learnings & Corrections

This section will be updated during implementation with any discoveries or corrections.

### [Date] - [Title]
**Context**: [What we were working on]
**Learning**: [What we discovered]
**Impact**: [How it affects the plan]
**Related**: [Links to relevant resources]
