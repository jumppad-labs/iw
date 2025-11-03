# Obsidian Local REST API Skill

Interact with Obsidian notes through the Local REST API plugin.

## Prerequisites

1. Install Obsidian: https://obsidian.md
2. Install the "Local REST API" plugin from Obsidian's community plugins
3. Enable the plugin and note your API key from settings
4. Python 3.7+ with `requests` library

## Setup

1. Install Python dependencies:
   ```bash
   pip install requests
   ```

2. Configure API credentials:
   ```bash
   cd .claude/skills/obsidian-local-api
   python3 scripts/config_helper.py
   ```

   Follow prompts to enter your API key (from Obsidian settings).

3. Test connectivity:
   ```bash
   python3 scripts/config_helper.py --test
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

# Append content
python3 scripts/append_note.py "Test/note.md" "Additional content"

# Search vault
python3 scripts/search_vault.py "search term"

# List commands
python3 scripts/list_commands.py

# Execute command
python3 scripts/execute_command.py "editor:toggle-bold"
```

All scripts support `--help` for detailed usage.

## Troubleshooting

See `references/configuration.md` for detailed troubleshooting.

**Common issues:**
- Ensure Obsidian is running
- Check API key is correct: `python3 scripts/config_helper.py --show`
- Verify plugin is enabled in Obsidian settings
- Default port is 27124 (HTTPS)

## Configuration

Configuration is loaded from (in order):
1. Environment variables (`OBSIDIAN_API_KEY`, etc.)
2. Project config (`.obsidian-api.json`)
3. User config (`~/.obsidian-api/config.json`)
4. Defaults (localhost:27124, HTTPS)

## Resources

- **scripts/** - Executable Python utilities for API operations
- **references/** - Detailed API documentation and guides
- **assets/templates/** - Example note templates

## Security

- API keys are stored securely with user-only permissions (600)
- HTTPS is used by default (self-signed certificates handled automatically)
- Localhost-only binding by default for maximum security

## License

See LICENSE file in repository root.
