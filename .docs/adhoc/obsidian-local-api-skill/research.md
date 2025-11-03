# Research: Obsidian Local REST API Skill

## Obsidian Local REST API Plugin

### Overview
- **Repository**: https://github.com/coddingtonbear/obsidian-local-rest-api
- **License**: MIT
- **Language**: TypeScript (96.3%)
- **Latest Version**: 3.2.0 (as of May 2025)
- **Stars**: 1,500+
- **Active Development**: Yes, regular updates

### Core Capabilities

1. **Note Management**
   - Create new notes (PUT /vault/*)
   - Read note content and metadata (GET /vault/*)
   - Update notes (POST for append, PATCH for insertion)
   - Delete notes (DELETE /vault/*)
   - List directory contents

2. **Active File Operations**
   - Operate on currently open file in editor
   - Same operations as vault operations
   - Useful for editor integration

3. **Periodic Notes**
   - Daily, weekly, monthly, quarterly, yearly notes
   - Automatic date-based note creation
   - Integration with popular periodic notes plugins

4. **Command Execution**
   - List all available Obsidian commands
   - Execute commands programmatically
   - Enables automation of any Obsidian feature

5. **Search Capabilities**
   - Simple text search across vault
   - Advanced search with Dataview DQL
   - JSON Logic query support
   - Context extraction for matches

6. **Extension API**
   - Other plugins can register custom endpoints
   - Enables plugin interoperability
   - Custom automation workflows

### Authentication

**API Key-Based Authentication**:
- Key generated automatically on first setup
- Found in plugin settings within Obsidian
- Included in Authorization header: `Authorization: Bearer YOUR_API_KEY`
- All endpoints require auth except `/` and `/cert.pem`

**Security Model**:
- HTTPS by default (port 27124)
- HTTP optional (port 27123, disabled by default)
- Self-signed SSL certificates
- Bound to localhost by default (127.0.0.1)
- Can be configured for network access with warnings

### API Endpoints

#### Status & Info
- `GET /` - Server status and version info (public)
- `GET /cert.pem` - Download SSL certificate (public)

#### Vault Operations
- `GET /vault/{path}` - Read file or list directory
- `PUT /vault/{path}` - Create or replace file
- `POST /vault/{path}` - Append to file
- `PATCH /vault/{path}` - Insert content at specific location
- `DELETE /vault/{path}` - Delete file

#### Active File Operations
- `GET /active/` - Get active file content
- `PUT /active/` - Replace active file content
- `POST /active/` - Append to active file
- `PATCH /active/` - Modify sections of active file
- `DELETE /active/` - Delete active file

#### Periodic Notes
- `GET /periodic/{period}` - Get periodic note
- `PUT /periodic/{period}` - Create/replace periodic note
- `POST /periodic/{period}` - Append to periodic note
- `PATCH /periodic/{period}` - Modify periodic note
- `DELETE /periodic/{period}` - Delete periodic note
- Periods: daily, weekly, monthly, quarterly, yearly

#### Commands
- `GET /commands/` - List all commands
- `POST /commands/{commandId}/` - Execute command

#### Search
- `POST /search/simple/` - Simple text search
- `POST /search/` - Advanced search (DQL/JSON Logic)

#### Open File
- `POST /open/{path}` - Open file in Obsidian editor

### Request/Response Formats

**JSON Metadata Response** (with Accept header):
```json
{
  "path": "path/to/note.md",
  "content": "# Note content here",
  "tags": ["tag1", "tag2"],
  "frontmatter": {
    "title": "Note Title",
    "date": "2025-01-03",
    "custom": "value"
  }
}
```

**Simple Text Response** (default):
```
# Note content here

Content body...
```

**Search Results**:
```json
[
  {
    "filename": "path/to/note.md",
    "matches": [
      {
        "match": {"start": 10, "end": 25},
        "context": "...surrounding text with match highlighted..."
      }
    ]
  }
]
```

**Command List**:
```json
{
  "commands": [
    {
      "id": "editor:toggle-bold",
      "name": "Toggle bold"
    },
    {
      "id": "command-palette:open",
      "name": "Open command palette"
    }
  ]
}
```

**Error Response**:
```json
{
  "message": "Description of error",
  "errorCode": 40010
}
```

### Error Codes
- `40010` - Text content encoding required
- `40101` - API key authorization required
- `40102` - Malformed authorization header
- `40460` - Periodic note period doesn't exist
- `40461` - Specific periodic note doesn't exist
- `40462` - File not found

### Configuration

**Default Settings**:
| Setting | Default | Notes |
|---------|---------|-------|
| HTTPS Port | 27124 | Secure, recommended |
| HTTP Port | 27123 | Insecure, disabled by default |
| Host | 127.0.0.1 | Localhost only |
| API Key | Auto-generated | 32-character hex string |
| Authorization Header | "Authorization" | Customizable |

**Advanced Settings**:
- Custom binding address (for network access)
- Custom ports
- HTTP enable/disable
- Certificate management

### Use Cases

**Personal Automation**:
- Automated daily note creation
- Task management integration
- Meeting notes from calendar
- Research note organization
- Journal entry logging

**Development Workflows**:
- Documentation generation
- Code snippet collection
- Issue tracking notes
- Project planning notes
- Technical documentation

**Content Management**:
- Batch note creation from data
- Content migration to/from Obsidian
- Note templates and scaffolding
- Cross-referencing and linking
- Metadata management

**Integration**:
- Browser extensions
- Mobile apps
- CLI tools
- CI/CD documentation
- External knowledge bases

## Existing Skills Analysis

### Pattern: iw-github-issue-reader

**Structure**:
```
iw-github-issue-reader/
├── SKILL.md
└── scripts/
    └── fetch_issue.py
```

**Key Insights**:
- Single Python script for core functionality
- Script is self-contained and executable
- SKILL.md provides usage instructions
- No references/ directory (API docs inline)
- Script uses gh CLI (external tool)

**Similarities to Our Skill**:
- External API interaction
- Python script for operations
- Needs authentication
- Structured output format

**Differences**:
- We have multiple operations (not just fetch)
- We need configuration management
- We have more complex workflows

### Pattern: skill-creator

**Structure**:
```
skill-creator/
├── SKILL.md
├── scripts/
│   ├── init_skill.py
│   ├── package_skill.py
│   └── quick_validate.py
└── references/
    └── (none, guidance in SKILL.md)
```

**Key Insights**:
- Multiple scripts for different operations
- Each script has clear single responsibility
- Comprehensive SKILL.md with examples
- Detailed usage instructions
- Scripts are standalone utilities

**Similarities to Our Skill**:
- Multiple operational scripts
- Each script has specific purpose
- Need clear documentation

### Pattern: go-dev-guidelines

**Structure**:
```
go-dev-guidelines/
├── SKILL.md
└── references/
    ├── project-structure.md
    ├── testing.md
    └── patterns.md
```

**Key Insights**:
- No scripts (guidelines only)
- Multiple reference documents
- Organized by topic
- SKILL.md references the detailed docs

**Applicability**:
- We should use references/ for detailed API docs
- Keep SKILL.md high-level
- Progressive disclosure of information

### Best Practices Identified

1. **Script Design**:
   - Standalone executables
   - Clear error messages
   - Help text (--help)
   - Exit codes for success/failure
   - Use standard libraries when possible

2. **Documentation**:
   - SKILL.md: High-level workflows and when to use
   - references/: Detailed technical documentation
   - README.md: User setup guide
   - Inline comments: Implementation details

3. **File Organization**:
   - scripts/: Executable Python/bash scripts
   - references/: Markdown documentation
   - assets/: Templates and resources
   - Each file has clear purpose

4. **Skill Metadata**:
   - Descriptive name (hyphen-case)
   - Detailed description (when to use)
   - Clear trigger conditions

## Python HTTP Client Libraries

### requests (Chosen)
**Pros**:
- Most popular Python HTTP library
- Simple, intuitive API
- Excellent documentation
- Handles auth, SSL, sessions
- JSON support built-in
- Widely available

**Cons**:
- External dependency (not stdlib)
- Synchronous only

**Example**:
```python
import requests

response = requests.get(
    'https://localhost:27124/vault/note.md',
    headers={'Authorization': f'Bearer {api_key}'},
    verify=False  # self-signed cert
)
```

### urllib (Alternative)
**Pros**:
- Standard library (no dependencies)
- Available everywhere

**Cons**:
- More verbose API
- Manual header management
- JSON handling manual
- SSL context setup complex

**Decision**: Use `requests` for simplicity and better UX

## Configuration Management Approaches

### Environment Variables
```bash
export OBSIDIAN_API_KEY="abc123"
export OBSIDIAN_HOST="localhost"
export OBSIDIAN_PORT="27124"
```

**Pros**: Simple, no files, works with CI/CD
**Cons**: Not persistent, hard to manage multiple configs

### JSON Config File
```json
{
  "api_key": "abc123",
  "host": "localhost",
  "port": 27124,
  "https": true
}
```

**Pros**: Persistent, easy to edit, supports multiple vaults
**Cons**: Manual file creation, permissions management

### Interactive Setup (config_helper.py)
```python
# Prompts user for settings
# Stores in ~/.obsidian-api/config.json
# Tests connectivity
# Provides clear feedback
```

**Decision**: Support all three (env vars, config file, interactive), with clear precedence

## SSL Certificate Handling

### Problem
Obsidian Local REST API uses self-signed certificates for HTTPS

### Options

1. **Disable Verification** (for localhost):
```python
requests.get(url, verify=False)
```
**Pros**: Simple, works immediately
**Cons**: Ignores all SSL issues
**Acceptable for**: localhost connections

2. **Download and Trust Certificate**:
```bash
curl http://localhost:27123/cert.pem > obsidian.pem
# Use verify='obsidian.pem' in requests
```
**Pros**: Proper SSL verification
**Cons**: Extra setup step

3. **Conditional Verification**:
```python
verify = False if host == 'localhost' else True
```

**Decision**: Disable verification for localhost, require proper certs for remote

## Alternative Implementations Considered

### Single CLI Tool with Subcommands
```bash
obsidian-cli note create "path/to/note.md"
obsidian-cli note read "path/to/note.md"
obsidian-cli vault search "query"
```

**Pros**: Single entry point, clear namespace
**Cons**: More complex, harder to invoke from Claude, less flexible

**Rejected**: Separate scripts are simpler and more flexible

### REST Client Library
Create a full Python library:
```python
from obsidian_api import ObsidianClient

client = ObsidianClient(api_key='...')
client.notes.create('path', content='...')
```

**Pros**: Programmatic interface, type hints, documentation
**Cons**: More complex, overkill for skill needs, harder to use standalone

**Rejected**: Scripts are sufficient for skill needs

### Direct cURL Commands in SKILL.md
Provide curl examples instead of scripts:
```bash
curl -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/vault/note.md
```

**Pros**: No scripts needed, simple
**Cons**: Platform-specific, no error handling, hard to maintain

**Rejected**: Scripts provide better UX

## Testing Approach

### Manual Testing Requirements
1. **Obsidian Installation**: Need Obsidian installed
2. **Plugin Installation**: Need Local REST API plugin
3. **Test Vault**: Create test vault with sample notes
4. **API Key**: Copy key from plugin settings

### Test Scenarios

**Happy Path**:
1. Configure API credentials
2. Create test note
3. Read test note back
4. Append content
5. Search for note
6. List commands
7. Execute safe command

**Error Paths**:
1. Connection refused (Obsidian not running)
2. Auth failure (wrong API key)
3. Not found (invalid path)
4. Permission denied
5. Invalid request

### Automation Possibilities
- Mock HTTP responses for unit tests
- Docker container with Obsidian headless (if available)
- CI/CD with test vault

## Future Enhancement Research

### Periodic Notes Deep Dive
Popular Obsidian plugins for periodic notes:
- Calendar plugin
- Daily Notes (core plugin)
- Periodic Notes plugin
- Templater integration

**API Support**: Full CRUD on /periodic/* endpoints
**Use Cases**: Automated daily/weekly note creation, template application

### Advanced Search Features
**Dataview DQL**:
```
TABLE file.name, file.tags
WHERE type = "meeting" AND date > date(today) - dur(7 days)
```

**Use Cases**: Complex queries, metadata-based search, relational queries

### Graph Operations
Not exposed by API currently, but could be valuable:
- Get backlinks for note
- Find orphaned notes
- Analyze connection clusters
- Path between notes

### Batch Operations
API doesn't have native batch support, but could implement:
- Batch read multiple notes
- Bulk create from data
- Mass tagging operations
- Content transformation pipelines

## Security Considerations

### API Key Storage
**Sensitive Data**: API key grants full vault access

**Storage Options**:
1. Config file with 600 permissions (user-only read/write)
2. Environment variables (session-only)
3. Keychain/credential manager (OS-specific)

**Decision**: Config file with proper permissions, clear warnings in docs

### Network Exposure
**Default**: localhost only (safe)
**Optional**: Network binding (warn users about security implications)

**Guidance**:
- Never expose to public internet
- Use SSH tunneling for remote access
- VPN for secure network access
- Consider firewall rules

### Vault Access
**Risk**: Full read/write access to entire vault

**Mitigations**:
- Don't implement delete operations in initial version
- Validate paths before operations
- Recommend vault backups
- Clear documentation of permissions
- User must explicitly enable plugin

### SSL/TLS
**Self-Signed Certificates**: Trade-off between security and UX

**Decision**: Acceptable for localhost, document implications

## Documentation Best Practices

### From Successful Skills

1. **Clear Trigger Conditions**: Describe exactly when skill should be used
2. **Practical Examples**: Show real user requests and how skill handles them
3. **Progressive Disclosure**: Keep SKILL.md high-level, details in references
4. **Error Guidance**: Explain common errors and how to fix them
5. **Setup Instructions**: Make first-time setup obvious and easy
6. **Script Documentation**: Each script should have help text and examples

### Documentation Structure

**SKILL.md** (4-5k words):
- Overview and purpose
- When to use
- Prerequisites
- Workflow decision trees
- Common patterns
- Resources reference
- Examples

**references/api_reference.md** (8-10k words):
- Complete endpoint documentation
- Request/response formats
- Authentication details
- Error codes
- Technical details

**references/use_cases.md** (3-4k words):
- Practical scenarios
- Workflow patterns
- Integration examples
- Best practices

**references/configuration.md** (2-3k words):
- Setup instructions
- Configuration options
- Troubleshooting
- Security guidance

**README.md** (1-2k words):
- Quick start
- Installation
- Basic usage
- Links to detailed docs

## Validation Checklist

From skill-creator validation script:
- [ ] SKILL.md exists and has valid YAML frontmatter
- [ ] name field matches directory name
- [ ] description is descriptive (>50 chars) and includes "when to use"
- [ ] SKILL.md has substantial content (>500 words)
- [ ] All scripts are executable
- [ ] All referenced files exist
- [ ] No TODOs in SKILL.md
- [ ] Proper skill structure

## Dependencies

### Required
- Python 3.7+
- requests library (`pip install requests`)

### Optional
- Obsidian (for testing)
- Local REST API plugin (for functionality)

### Installation
```bash
pip install requests
# or
pip install -r requirements.txt
```

## Competitive Analysis

### Similar Tools

**Obsidian CLI** (community tool):
- Direct filesystem operations
- No API needed
- Markdown parsing
- Limited to file operations

**Obsidian API (official)**:
- Plugin API (JavaScript)
- Not accessible externally
- Different use case (in-app plugins)

**obsidian-cli-wrapper** (GitHub):
- Shell scripts around local filesystem
- No server needed
- Basic operations only

**This Skill's Differentiation**:
- Uses official REST API
- Claude Code integration
- Workflow automation focus
- Comprehensive operation set
- Better error handling
- Python ecosystem integration

## Open Source Examples

### Similar API Client Implementations

1. **GitHub CLI (gh)**:
   - Subcommand structure
   - JSON output option
   - Config file management
   - Excellent error messages

2. **AWS CLI**:
   - Configuration profiles
   - Environment variable support
   - Credential management
   - Extensive documentation

3. **Notion API Python Client**:
   - Class-based API wrapper
   - Type hints
   - Async support
   - Good examples

**Lessons Applied**:
- Clear error messages
- Flexible configuration
- Help text for all commands
- JSON output options
- Examples in documentation

## Conclusion

This research supports the planned implementation approach:
- Python scripts with requests library
- Multiple focused scripts (not monolithic CLI)
- Comprehensive documentation in references/
- Interactive configuration helper
- Focus on core operations (create, read, append, search)
- Future enhancements possible (periodic notes, advanced search)
- Security-conscious defaults
- Clear error handling and user guidance
