# Obsidian Local REST API - Use Cases & Workflows

Practical scenarios and workflow patterns for automating Obsidian operations.

## Daily Journal Automation

### Auto-Create Daily Notes

**Scenario**: Automatically create daily notes with consistent structure each morning.

**Workflow**:
1. Run scheduled script (cron/systemd timer)
2. Generate today's date
3. Create note with template structure
4. Include day-specific metadata

**Implementation**:
```bash
#!/bin/bash
# daily-note.sh - Run via cron at 6:00 AM

DATE=$(date +%Y-%m-%d)
DAY=$(date +%A)

scripts/create_note.py "Daily/${DATE}.md" \
  --frontmatter '{
    "date": "'${DATE}'",
    "day": "'${DAY}'",
    "tags": ["daily", "journal"]
  }' \
  --content "# ${DATE} - ${DAY}

## Tasks
- [ ]

## Notes


## Reflections

"
```

**Cron Entry**:
```
0 6 * * * /path/to/daily-note.sh
```

### Append Throughout Day

**Scenario**: Add tasks, notes, and reflections to today's note as they occur.

**Workflows**:

**Quick task capture**:
```bash
# Add task to today's note
TODAY=$(date +%Y-%m-%d)
scripts/append_note.py "Daily/${TODAY}.md" \
  "- [ ] Review PR #123" \
  --heading "## Tasks"
```

**Log meetings**:
```bash
scripts/append_note.py "Daily/${TODAY}.md" \
  "### Meeting with Team
- Discussed project timeline
- Action: Update docs by Friday" \
  --heading "## Notes"
```

---

## Task Management Integration

### Sync Tasks from External Tools

**Scenario**: Import tasks from project management tools into Obsidian.

**Workflow**:
1. Fetch tasks from API (Jira, Asana, etc.)
2. Format as Obsidian tasks
3. Create/update project notes

**Example** (pseudo-code):
```python
import requests
from obsidian_client import get_client

# Fetch tasks from external API
tasks = fetch_jira_tasks(project_id="PROJ-123")

# Format for Obsidian
task_list = "\n".join([f"- [ ] {task['summary']}" for task in tasks])

# Update project note
client = get_client()
client.patch("/vault/Projects/PROJ-123.md", json_data={
    "action": "insert",
    "heading": "## Open Tasks",
    "content": task_list
})
```

### Mark Tasks Complete

**Scenario**: Mark tasks as done and log completion time.

**Workflow**:
1. Search for specific task
2. Read note content
3. Update task checkbox
4. Append completion log

**Implementation**:
```python
# Mark task complete and log
def complete_task(note_path, task_text):
    client = get_client()

    # Read current content
    success, data, error = client.get(f"/vault/{note_path}")
    if not success:
        print(f"Error: {error}")
        return

    # Replace unchecked task with checked
    updated = data.replace(f"- [ ] {task_text}", f"- [x] {task_text}")

    # Update note
    client.put(f"/vault/{note_path}", data=updated)

    # Log completion
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    client.post(f"/vault/{note_path}",
                data=f"\n\n**Completed {timestamp}**: {task_text}")

complete_task("Daily/2025-01-03.md", "Review PR #123")
```

---

## Research Note Organization

### Create Literature Notes from Articles

**Scenario**: Automatically create notes for articles/papers you're reading.

**Workflow**:
1. Parse article metadata (title, author, URL)
2. Create structured note
3. Add to reading list index

**Implementation**:
```python
def create_literature_note(title, author, url, summary):
    client = get_client()

    # Sanitize title for filename
    filename = title.lower().replace(" ", "-").replace("/", "-")
    path = f"Literature/{filename}.md"

    # Create note with metadata
    frontmatter = {
        "title": title,
        "author": author,
        "url": url,
        "type": "literature",
        "tags": ["reading", "research"]
    }

    content = f"""# {title}

**Author**: {author}
**Source**: {url}

## Summary

{summary}

## Key Points

-

## Questions

-

## Related Notes

-
"""

    create_note(path, content, frontmatter)

    # Add to reading index
    client.post("/vault/Literature/index.md",
                data=f"\n- [[{filename}]] - {author}")

create_literature_note(
    "Machine Learning Basics",
    "John Doe",
    "https://example.com/ml-basics",
    "Introduction to ML concepts..."
)
```

### Cross-Reference Notes

**Scenario**: Build connections between related research notes.

**Workflow**:
1. Search for related topics
2. Extract note titles
3. Add backlinks to notes

**Implementation**:
```python
def add_related_notes(note_path, search_terms):
    client = get_client()

    # Search for related notes
    results = []
    for term in search_terms:
        success, data, _ = client.post("/search/simple/", json_data={
            "query": term,
            "contextLength": 50
        })
        if success:
            results.extend([r['filename'] for r in data])

    # Remove duplicates and current note
    related = list(set(results))
    related = [r for r in related if r != note_path]

    # Format as links
    links = "\n".join([f"- [[{r}]]" for r in related[:5]])

    # Append to note
    client.patch(f"/vault/{note_path}", json_data={
        "action": "insert",
        "heading": "## Related Notes",
        "content": links
    })

add_related_notes(
    "Research/machine-learning.md",
    ["neural networks", "deep learning", "AI"]
)
```

---

## Meeting Notes Generation

### Create Meeting Notes from Calendar

**Scenario**: Generate meeting note templates from calendar events.

**Workflow**:
1. Fetch today's calendar events
2. Create note for each meeting
3. Include attendees and agenda

**Implementation**:
```python
def create_meeting_note(event):
    client = get_client()

    date = event['start'].strftime("%Y-%m-%d")
    time = event['start'].strftime("%H:%M")
    title = event['title']

    # Sanitize for filename
    filename = f"Meetings/{date}-{title.replace(' ', '-').lower()}.md"

    attendees = ", ".join([a['email'] for a in event['attendees']])

    frontmatter = {
        "date": date,
        "time": time,
        "type": "meeting",
        "attendees": [a['email'] for a in event['attendees']],
        "tags": ["meeting"]
    }

    content = f"""# Meeting: {title}

**Date**: {date}
**Time**: {time}
**Attendees**: {attendees}

## Agenda

{event.get('description', '')}

## Discussion


## Action Items

- [ ]

## Next Steps

"""

    create_note(filename, content, frontmatter)

    print(f"Created: {filename}")

# Fetch from Google Calendar, Outlook, etc.
for event in get_todays_meetings():
    create_meeting_note(event)
```

### Post-Meeting Summary

**Scenario**: After meeting, append notes and action items.

**Workflow**:
1. Identify meeting note
2. Append discussion points
3. Extract action items
4. Link to relevant project notes

**Implementation**:
```bash
# Capture meeting notes quickly
MEETING="Meetings/2025-01-03-standup.md"

scripts/append_note.py "$MEETING" "
## Discussion

- Sprint progress: 80% complete
- Blockers: None
- Next sprint planning Friday

## Action Items

- [ ] @alice: Update documentation
- [ ] @bob: Code review PR #456
- [ ] @charlie: Deploy to staging
" --heading "## Discussion"
```

---

## Documentation Automation

### Generate API Documentation from Code

**Scenario**: Extract API endpoints from code and create documentation notes.

**Workflow**:
1. Parse source code for endpoints
2. Extract parameters and descriptions
3. Create structured API docs in Obsidian

**Implementation**:
```python
def document_api_endpoint(endpoint_data):
    client = get_client()

    path = f"Docs/API/{endpoint_data['path'].replace('/', '-')}.md"

    content = f"""# API: {endpoint_data['method']} {endpoint_data['path']}

## Description

{endpoint_data['description']}

## Parameters

{format_parameters(endpoint_data['parameters'])}

## Request Example

```json
{endpoint_data['request_example']}
```

## Response Example

```json
{endpoint_data['response_example']}
```

## Error Codes

{format_errors(endpoint_data['errors'])}
"""

    create_note(path, content)

# Parse your codebase and generate docs
for endpoint in parse_api_endpoints():
    document_api_endpoint(endpoint)
```

### Sync Documentation with Code

**Scenario**: Keep docs updated when code changes.

**Workflow**:
1. Detect code changes (git hooks)
2. Re-generate documentation
3. Update existing notes

**Git Hook** (post-commit):
```bash
#!/bin/bash
# .git/hooks/post-commit

# Check if API code changed
if git diff --name-only HEAD~1 HEAD | grep -q "api/"; then
    python scripts/generate-api-docs.py
    echo "API documentation updated in Obsidian"
fi
```

---

## Batch Operations

### Tag All Notes in Directory

**Scenario**: Add tags to multiple notes at once.

**Workflow**:
1. List notes in directory
2. Read each note
3. Add/update frontmatter tags
4. Write back

**Implementation**:
```python
def tag_notes_in_directory(directory, tags):
    client = get_client()

    # List directory (simplified - actual implementation varies)
    success, data, _ = client.get(f"/vault/{directory}/")
    if not success or 'files' not in data:
        return

    for file in data['files']:
        if not file.endswith('.md'):
            continue

        path = f"{directory}/{file}"

        # Read note with metadata
        success, note_data, _ = client.get(
            f"/vault/{path}",
            headers={"Accept": "application/vnd.olrapi.note+json"}
        )

        if not success:
            continue

        # Update frontmatter
        frontmatter = note_data.get('frontmatter', {})
        existing_tags = frontmatter.get('tags', [])
        new_tags = list(set(existing_tags + tags))
        frontmatter['tags'] = new_tags

        # Reconstruct note with updated frontmatter
        # (Implementation details vary based on format)
        # ...

        print(f"Tagged: {path}")

tag_notes_in_directory("Projects/2024", ["archived", "completed"])
```

### Bulk Rename Notes

**Scenario**: Rename notes following new naming convention.

**Workflow**:
1. Search for notes matching pattern
2. Generate new names
3. Create new notes with content
4. Update backlinks (manual follow-up)

---

## Integration with External Tools

### Browser Extension Integration

**Scenario**: Save web pages to Obsidian with one click.

**Workflow**:
1. Browser extension captures page metadata
2. POST to local script/server
3. Script creates Obsidian note via API

**Browser Extension** (background script):
```javascript
// Save current tab to Obsidian
async function saveToObsidian() {
  const tab = await chrome.tabs.query({active: true})[0];

  const response = await fetch('http://localhost:8080/save', {
    method: 'POST',
    body: JSON.stringify({
      title: tab.title,
      url: tab.url,
      content: await getPageContent()
    })
  });
}
```

**Local Server**:
```python
from flask import Flask, request
from obsidian_client import get_client

app = Flask(__name__)

@app.route('/save', methods=['POST'])
def save_note():
    data = request.json

    client = get_client()
    filename = sanitize_filename(data['title'])
    path = f"Clippings/{filename}.md"

    content = f"""# {data['title']}

**Source**: {data['url']}
**Saved**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

{data['content']}
"""

    client.put(f"/vault/{path}", data=content)
    return {"success": True}

app.run(port=8080)
```

### Mobile App Sync

**Scenario**: Add quick notes from mobile app.

**Workflow**:
1. Mobile app collects input
2. POST to server/API gateway
3. Server creates note in Obsidian

---

## Command Automation

### Execute Obsidian Commands

**Scenario**: Trigger Obsidian features programmatically.

**Examples**:

**Export to PDF**:
```bash
scripts/list_commands.py --filter "pdf"
scripts/execute_command.py "markdown-export:pdf"
```

**Format Document**:
```bash
scripts/execute_command.py "editor:format-table"
```

**Backup Vault**:
```bash
scripts/execute_command.py "obsidian-git:push"
```

---

## Best Practices

1. **Error Handling**: Always check return codes and handle failures gracefully
2. **Rate Limiting**: Don't overwhelm the API with rapid requests
3. **Atomic Operations**: Keep individual operations focused and reversible
4. **Backups**: Maintain vault backups before bulk operations
5. **Testing**: Test scripts on sample notes before running on full vault
6. **Logging**: Log operations for debugging and audit trails
7. **Idempotency**: Design scripts to be safely re-runnable

---

## Workflow Templates

### Python Script Template

```python
#!/usr/bin/env python3
"""
Script description and usage.
"""

import sys
from pathlib import Path

# Add script directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from obsidian_client import get_client

def main():
    client = get_client()

    # Test connection
    success, message = client.test_connection()
    if not success:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

    # Your automation logic here
    # ...

    print("✅ Operation completed")

if __name__ == "__main__":
    main()
```

### Bash Script Template

```bash
#!/bin/bash
# Script description and usage

set -euo pipefail

# Configuration
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY=$(date +%Y-%m-%d)

# Your automation logic here
python3 "$SCRIPTS_DIR/create_note.py" "Daily/${TODAY}.md" \
  --content "# Today's Notes"

echo "✅ Operation completed"
```

---

## Related Resources

- Obsidian API: https://docs.obsidian.md/
- Community Plugins: https://obsidian.md/plugins
- Automation Examples: https://github.com/topics/obsidian-automation
