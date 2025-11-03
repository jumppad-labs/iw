# Obsidian Local REST API Reference

Complete endpoint documentation for the Obsidian Local REST API plugin.

## Overview

The Obsidian Local REST API provides a secure HTTPS interface for programmatic interaction with an Obsidian vault. This reference covers all available endpoints, request/response formats, authentication, and error handling.

**Base URL**: `https://localhost:27124` (default)

**Version**: 3.2.0+

## Authentication

All endpoints except `/` and `/cert.pem` require API key authentication.

### Finding Your API Key

1. Open Obsidian Settings
2. Navigate to Community Plugins → Local REST API
3. Click "Copy API Key"

### Authentication Header

Include the API key in all requests:

```
Authorization: Bearer YOUR_API_KEY
```

### Example Request

```bash
curl -H "Authorization: Bearer abc123xyz456" \
  https://localhost:27124/vault/note.md \
  --insecure
```

Note: `--insecure` flag needed for self-signed certificates.

---

## Status & Information Endpoints

### GET /

**Description**: Get server status and version information

**Authentication**: Not required (public endpoint)

**Response**:
```json
{
  "status": "OK",
  "manifest": { /* plugin manifest */ },
  "versions": {
    "obsidian": "1.0.0",
    "self": "3.2.0"
  },
  "authenticated": true,
  "certificateInfo": { /* SSL certificate info */ }
}
```

### GET /cert.pem

**Description**: Download the self-signed SSL certificate

**Authentication**: Not required (public endpoint)

**Response**: PEM-formatted certificate file

**Usage**: Download and trust this certificate if you need proper SSL verification.

---

## Vault File Operations

Operations on files in the vault by path.

### GET /vault/{path}

**Description**: Read file content or list directory contents

**Authentication**: Required

**Parameters**:
- `path` (in URL): File or directory path relative to vault root

**Headers**:
- `Accept: application/vnd.olrapi.note+json` - Request JSON format with metadata

**Response (Markdown)**:
```
# Note Title

Content of the note...
```

**Response (JSON with metadata)**:
```json
{
  "path": "path/to/note.md",
  "content": "# Note Title\n\nContent...",
  "tags": ["tag1", "tag2"],
  "frontmatter": {
    "title": "Note Title",
    "date": "2025-01-03",
    "custom": "value"
  }
}
```

**Response (Directory listing)**:
```json
{
  "files": [
    "note1.md",
    "note2.md",
    "subdirectory/"
  ]
}
```

**Example**:
```bash
# Read as markdown
curl -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/vault/Daily/2025-01-03.md \
  --insecure

# Read as JSON with metadata
curl -H "Authorization: Bearer $API_KEY" \
  -H "Accept: application/vnd.olrapi.note+json" \
  https://localhost:27124/vault/Daily/2025-01-03.md \
  --insecure
```

### PUT /vault/{path}

**Description**: Create a new note or replace existing note

**Authentication**: Required

**Parameters**:
- `path` (in URL): File path relative to vault root

**Headers**:
- `Content-Type: text/markdown`

**Body**: Note content (markdown)

**Response**: Success confirmation

**Example**:
```bash
curl -X PUT \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: text/markdown" \
  -d "# New Note\n\nThis is my note content." \
  https://localhost:27124/vault/Daily/2025-01-03.md \
  --insecure
```

**With Frontmatter**:
```bash
curl -X PUT \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: text/markdown" \
  -d "---
tags: [daily, journal]
date: 2025-01-03
---

# Daily Note

Content here..." \
  https://localhost:27124/vault/Daily/2025-01-03.md \
  --insecure
```

### POST /vault/{path}

**Description**: Append content to an existing note

**Authentication**: Required

**Parameters**:
- `path` (in URL): File path relative to vault root

**Headers**:
- `Content-Type: text/markdown`

**Body**: Content to append

**Response**: Success confirmation

**Behavior**: Adds newline before appended content if necessary

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: text/markdown" \
  -d "\n- Task completed at $(date)" \
  https://localhost:27124/vault/Daily/2025-01-03.md \
  --insecure
```

### PATCH /vault/{path}

**Description**: Insert content at a specific location within a note

**Authentication**: Required

**Parameters**:
- `path` (in URL): File path relative to vault root

**Headers**:
- `Content-Type: application/json`

**Body** (JSON):
```json
{
  "action": "insert",
  "heading": "## Section Name",
  "content": "Content to insert after this heading"
}
```

**Response**: Success confirmation

**Example**:
```bash
curl -X PATCH \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "insert",
    "heading": "## Tasks",
    "content": "- New task item"
  }' \
  https://localhost:27124/vault/Projects/project.md \
  --insecure
```

**Advanced Operations**:
- Insert at heading boundaries
- Modify specific blocks (by block reference)
- Update frontmatter fields

### DELETE /vault/{path}

**Description**: Delete a file from the vault

**Authentication**: Required

**Parameters**:
- `path` (in URL): File path relative to vault root

**Response**: Success confirmation

**Note**: Only deletes files, not directories

**Example**:
```bash
curl -X DELETE \
  -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/vault/Temp/old-note.md \
  --insecure
```

---

## Active File Operations

Operations on the currently active (open) file in Obsidian's editor.

### GET /active/

**Description**: Get active file content and metadata

**Authentication**: Required

**Response**: Same format as `GET /vault/{path}`

### PUT /active/

**Description**: Replace active file content

**Authentication**: Required

**Body**: New file content

### POST /active/

**Description**: Append content to active file

**Authentication**: Required

**Body**: Content to append

### PATCH /active/

**Description**: Modify specific sections of active file

**Authentication**: Required

**Body**: Insertion operation (same format as vault PATCH)

### DELETE /active/

**Description**: Delete the currently active file

**Authentication**: Required

---

## Command Operations

Execute Obsidian commands programmatically.

### GET /commands/

**Description**: List all available Obsidian commands

**Authentication**: Required

**Response**:
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
    },
    {
      "id": "markdown-importer:open",
      "name": "Markdown Importer: Open"
    }
  ]
}
```

**Example**:
```bash
curl -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/commands/ \
  --insecure
```

### POST /commands/{commandId}/

**Description**: Execute a specific Obsidian command

**Authentication**: Required

**Parameters**:
- `commandId` (in URL): Command identifier from commands list

**Body**: Optional command parameters (depends on command)

**Response**: Command execution result

**Example**:
```bash
# Execute toggle bold command
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/commands/editor:toggle-bold/ \
  --insecure
```

**Use Cases**:
- Trigger exports (PDF, HTML)
- Format text
- Execute plugin commands
- Automate Obsidian features

---

## Search Operations

Search for notes in the vault.

### POST /search/simple/

**Description**: Perform simple text search across vault

**Authentication**: Required

**Body** (JSON):
```json
{
  "query": "search text",
  "contextLength": 100
}
```

**Parameters**:
- `query`: Search text
- `contextLength`: Number of characters of context around matches (default: 100)

**Response**:
```json
[
  {
    "filename": "path/to/note.md",
    "matches": [
      {
        "match": {
          "start": 10,
          "end": 25
        },
        "context": "...text with match highlighted..."
      }
    ]
  }
]
```

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "contextLength": 150
  }' \
  https://localhost:27124/search/simple/ \
  --insecure
```

### POST /search/

**Description**: Advanced search with Dataview DQL or JSON Logic queries

**Authentication**: Required

**Body (DQL)**:
```json
{
  "query": "table file.name, file.tags where type = 'note'",
  "type": "dql"
}
```

**Body (JSON Logic)**:
```json
{
  "query": {
    "===": [
      {"var": "tags"},
      "important"
    ]
  },
  "type": "json"
}
```

**Response**: Query-dependent results

**Note**: Requires Dataview plugin for DQL queries

---

## Periodic Notes Operations

Work with daily, weekly, monthly, quarterly, or yearly notes.

### GET /periodic/{period}

**Description**: Get a periodic note for a specific date

**Authentication**: Required

**Parameters**:
- `period` (in URL): One of `daily`, `weekly`, `monthly`, `quarterly`, `yearly`
- Query parameters for date specification (format depends on period)

**Response**: Note content and metadata

**Example**:
```bash
# Get today's daily note
curl -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/periodic/daily \
  --insecure

# Get specific date's daily note
curl -H "Authorization: Bearer $API_KEY" \
  'https://localhost:27124/periodic/daily?date=2025-01-03' \
  --insecure
```

### PUT /periodic/{period}

**Description**: Create or replace a periodic note

**Authentication**: Required

**Body**: Note content

### POST /periodic/{period}

**Description**: Append content to a periodic note

**Authentication**: Required

**Body**: Content to append

### PATCH /periodic/{period}

**Description**: Modify sections of a periodic note

**Authentication**: Required

**Body**: Insertion operation

### DELETE /periodic/{period}

**Description**: Delete a periodic note

**Authentication**: Required

---

## Open File Operation

### POST /open/{path}

**Description**: Open a file in Obsidian's editor

**Authentication**: Required

**Parameters**:
- `path` (in URL): File path to open
- `newLeaf` (query): Set to `true` to open in new pane

**Response**: Confirmation of file opened

**Example**:
```bash
# Open in current pane
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/open/Projects/project.md \
  --insecure

# Open in new pane
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  'https://localhost:27124/open/Projects/project.md?newLeaf=true' \
  --insecure
```

---

## Error Handling

### Error Response Format

```json
{
  "message": "Description of error",
  "errorCode": 40010
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 40010 | Text content encoding required |
| 40101 | API key authorization required |
| 40102 | Malformed authorization header |
| 40460 | Periodic note period doesn't exist |
| 40461 | Specific periodic note doesn't exist |
| 40462 | File not found |

### HTTP Status Codes

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | File or resource doesn't exist |
| 500 | Internal Server Error | Error in Obsidian plugin |

### Error Examples

**401 Unauthorized**:
```json
{
  "message": "API key authorization required",
  "errorCode": 40101
}
```

**Solution**: Check API key is correct and included in Authorization header.

**404 Not Found**:
```json
{
  "message": "File not found",
  "errorCode": 40462
}
```

**Solution**: Verify file path is correct relative to vault root.

---

## Configuration

### Default Settings

| Setting | Default | Notes |
|---------|---------|-------|
| HTTPS Port | 27124 | Secure, recommended |
| HTTP Port | 27123 | Insecure, disabled by default |
| Host | 127.0.0.1 | Localhost only |
| API Key | Auto-generated | 32-character hex string |

### Network Configuration

**Local Only** (default):
- Bound to 127.0.0.1
- Only accessible from same machine
- Most secure option

**Network Access**:
- Can be configured to bind to 0.0.0.0
- Accessible from other devices on network
- Security warning: Only enable on trusted networks

### SSL Certificates

The plugin uses self-signed certificates for HTTPS. Options:

1. **Accept Insecure** (simplest):
   - Use `--insecure` flag in curl
   - Set `verify=False` in Python requests
   - Only for localhost

2. **Download Certificate**:
   - Get cert from `http://localhost:27123/cert.pem`
   - Install/trust in OS certificate store
   - Use `--cacert cert.pem` in curl

---

## Rate Limiting

No official rate limits, but best practices:
- Avoid excessive rapid requests
- Batch operations when possible
- Be respectful of Obsidian's performance
- Consider search operations can be slow on large vaults

---

## API Version

Check API version via `GET /`:

```bash
curl https://localhost:27124/ --insecure | jq '.versions.self'
```

Output: `"3.2.0"`

---

## Extension API

Other Obsidian plugins can register custom endpoints, extending the API. Consult specific plugin documentation for additional endpoints.

---

## Best Practices

1. **Always use HTTPS** for production (default port 27124)
2. **Store API key securely** - use environment variables or config files with proper permissions
3. **Include .md extension** in file paths
4. **Use forward slashes** in paths (e.g., `Daily/2025-01-03.md`)
5. **Handle errors gracefully** - check status codes and error messages
6. **Test connectivity first** with `GET /` before operations
7. **Respect vault structure** - don't create files in arbitrary locations
8. **Use relative paths** - all paths relative to vault root

---

## Quick Reference

| Operation | Method | Endpoint | Purpose |
|-----------|--------|----------|---------|
| Get status | GET | `/` | Check API is running |
| Read note | GET | `/vault/{path}` | Get note content |
| Create note | PUT | `/vault/{path}` | Create/replace note |
| Append to note | POST | `/vault/{path}` | Add content to end |
| Insert content | PATCH | `/vault/{path}` | Insert at heading |
| Delete note | DELETE | `/vault/{path}` | Remove file |
| List commands | GET | `/commands/` | See available commands |
| Run command | POST | `/commands/{id}/` | Execute command |
| Search vault | POST | `/search/simple/` | Find notes |

---

## Related Resources

- Plugin repository: https://github.com/coddingtonbear/obsidian-local-rest-api
- Interactive docs: https://coddingtonbear.github.io/obsidian-local-rest-api/
- Obsidian API docs: https://docs.obsidian.md/
