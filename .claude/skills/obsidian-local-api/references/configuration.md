# Obsidian Local REST API - Configuration & Troubleshooting

Complete setup guide and troubleshooting documentation.

## Prerequisites

### Install Obsidian

1. Download Obsidian from https://obsidian.md
2. Install for your platform (Windows, macOS, Linux)
3. Create or open a vault

### Install Local REST API Plugin

1. Open Obsidian Settings (gear icon)
2. Navigate to **Community Plugins**
3. Click **Browse** to open community plugins browser
4. Search for **"Local REST API"**
5. Click **Install** on the "Local REST API" plugin
6. Click **Enable** to activate the plugin

### Find Your API Key

1. Open Obsidian Settings
2. Navigate to **Community Plugins → Local REST API**
3. Click **"Copy API Key"** button
4. Save this key securely - you'll need it for authentication

---

## Script Configuration

### Option 1: Interactive Setup (Recommended)

Use the configuration helper for guided setup:

```bash
python3 scripts/config_helper.py
```

This will prompt you for:
- API key (paste from Obsidian settings)
- Host (default: localhost)
- Port (default: 27124)
- HTTPS preference (default: yes)

Configuration is saved to `~/.obsidian-api/config.json`

### Option 2: Command-Line Setup

Set configuration values directly:

```bash
# Set API key
python3 scripts/config_helper.py --set-key "your-api-key-here"

# Set host (if not using localhost)
python3 scripts/config_helper.py --set-host "localhost"

# Set port (if using non-default)
python3 scripts/config_helper.py --set-port 27124
```

### Option 3: Environment Variables

Set environment variables instead of config file:

```bash
# In your shell config (.bashrc, .zshrc, etc.)
export OBSIDIAN_API_KEY="your-api-key-here"
export OBSIDIAN_HOST="localhost"
export OBSIDIAN_PORT="27124"
export OBSIDIAN_HTTPS="true"
```

**For single session**:
```bash
export OBSIDIAN_API_KEY="abc123xyz"
python3 scripts/create_note.py "test.md" --content "Hello"
```

### Option 4: Project-Level Configuration

Create `.obsidian-api.json` in your project directory:

```json
{
  "api_key": "your-api-key-here",
  "host": "localhost",
  "port": 27124,
  "https": true
}
```

**Important**: Add `.obsidian-api.json` to `.gitignore` to avoid committing secrets!

---

## Configuration Precedence

Configuration is loaded in this order (first found wins):

1. Environment variables (`OBSIDIAN_API_KEY`, etc.)
2. Project-level config (`./.obsidian-api.json`)
3. User-level config (`~/.obsidian-api/config.json`)
4. Defaults (localhost:27124, HTTPS)

---

## Testing Your Setup

### Test Connection

```bash
python3 scripts/config_helper.py --test
```

Expected output:
```
✅ Connected to Obsidian Local REST API v3.2.0

Connection details:
  Host: localhost
  Port: 27124
  Protocol: HTTPS
```

### Test Basic Operations

```bash
# List available commands (should return list)
python3 scripts/list_commands.py

# Create a test note
python3 scripts/create_note.py "Test/test-note.md" \
  --content "# Test Note\n\nThis is a test."

# Read the note back
python3 scripts/read_note.py "Test/test-note.md"

# Search for the note
python3 scripts/search_vault.py "test"
```

If all these work, your setup is complete!

---

## Network Configuration

### Local Access Only (Default)

By default, the API is bound to `127.0.0.1` (localhost):
- Only accessible from the same machine
- Most secure configuration
- Recommended for personal use

**No additional configuration needed.**

### Network Access (Advanced)

To access the API from other devices on your network:

1. **In Obsidian Settings**:
   - Go to Community Plugins → Local REST API
   - Enable "Allow External Connections"
   - Note security warnings

2. **Update Script Configuration**:
   ```bash
   # Use machine's IP address instead of localhost
   python3 scripts/config_helper.py --set-host "192.168.1.100"
   ```

3. **Firewall Configuration**:
   - Allow incoming connections on port 27124
   - Consult your OS firewall documentation

**Security Warning**: Network access exposes your vault to anyone with your API key. Only enable on trusted networks.

---

## SSL Certificate Configuration

### Self-Signed Certificates

The plugin uses self-signed SSL certificates. By default, scripts accept these certificates (insecure mode).

**No action needed for localhost usage.**

### Trust the Certificate (Optional)

For proper SSL verification:

1. **Download Certificate**:
   ```bash
   curl http://localhost:27123/cert.pem -o obsidian-cert.pem
   ```

2. **Install Certificate**:

   **macOS**:
   ```bash
   sudo security add-trusted-cert -d -r trustRoot \
     -k /Library/Keychains/System.keychain obsidian-cert.pem
   ```

   **Linux** (Ubuntu/Debian):
   ```bash
   sudo cp obsidian-cert.pem /usr/local/share/ca-certificates/obsidian.crt
   sudo update-ca-certificates
   ```

   **Windows**:
   - Double-click `obsidian-cert.pem`
   - Install to "Trusted Root Certification Authorities"

3. **Update Scripts** (if needed):
   Scripts already handle this automatically.

---

## Port Configuration

### Default Ports

| Protocol | Port | Usage |
|----------|------|-------|
| HTTPS | 27124 | Secure (default, recommended) |
| HTTP | 27123 | Insecure (disabled by default) |

### Change Ports

If default ports conflict with other services:

1. **In Obsidian Settings**:
   - Community Plugins → Local REST API
   - Change HTTPS Port or HTTP Port
   - Restart Obsidian

2. **Update Script Configuration**:
   ```bash
   python3 scripts/config_helper.py --set-port 27125
   ```

### Use HTTP (Not Recommended)

To use insecure HTTP:

1. **Enable in Obsidian**:
   - Settings → Community Plugins → Local REST API
   - Enable "HTTP Server"

2. **Update Scripts**:
   ```bash
   # Set environment variable
   export OBSIDIAN_HTTPS="false"
   export OBSIDIAN_PORT="27123"
   ```

**Security Warning**: HTTP traffic is unencrypted. Only use for testing or in secure environments.

---

## Troubleshooting

### Connection Refused

**Symptom**: `Connection refused` error when running scripts

**Causes & Solutions**:

1. **Obsidian not running**:
   - Start Obsidian

2. **Plugin not enabled**:
   - Settings → Community Plugins → Local REST API
   - Ensure it's enabled (toggle should be on)

3. **Wrong port**:
   - Check port in Obsidian settings
   - Update config: `python3 scripts/config_helper.py --set-port 27124`

4. **Firewall blocking**:
   - Allow connections on port 27124
   - Check OS firewall settings

**Test**:
```bash
curl https://localhost:27124/ --insecure
```

Should return JSON with server status.

### Authentication Failed (401)

**Symptom**: `Authentication failed` or `API key authorization required`

**Causes & Solutions**:

1. **Wrong API key**:
   - Copy fresh key from Obsidian settings
   - Update: `python3 scripts/config_helper.py --set-key "new-key"`

2. **API key not configured**:
   - Run: `python3 scripts/config_helper.py`
   - Enter API key when prompted

3. **Typo in key**:
   - Verify with: `python3 scripts/config_helper.py --show`
   - Re-enter if incorrect

**Test**:
```bash
python3 scripts/config_helper.py --test
```

### File Not Found (404)

**Symptom**: `Note not found` when reading/updating notes

**Causes & Solutions**:

1. **Incorrect path**:
   - Paths are relative to vault root
   - Use forward slashes: `Daily/2025-01-03.md`
   - Include `.md` extension

2. **File doesn't exist**:
   - Create with: `python3 scripts/create_note.py "path/to/note.md"`

3. **Wrong vault**:
   - Ensure Obsidian has correct vault open
   - Check vault path in Obsidian settings

**Test**:
```bash
# List vault root
curl -H "Authorization: Bearer YOUR_KEY" \
  https://localhost:27124/vault/ --insecure
```

### SSL Certificate Errors

**Symptom**: SSL verification failed

**Solution**:
Scripts automatically handle self-signed certificates. If issues persist:

1. **Download certificate** (see SSL Configuration above)
2. **Use HTTP temporarily** for testing (not recommended for production)

### Python ImportError

**Symptom**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
pip install requests
# or
pip3 install requests
```

### Permission Denied

**Symptom**: Permission errors when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.py

# Or run with python explicitly
python3 scripts/create_note.py ...
```

### Config File Not Found

**Symptom**: Scripts can't find configuration

**Solution**:
```bash
# Create config directory
mkdir -p ~/.obsidian-api

# Run interactive setup
python3 scripts/config_helper.py
```

---

## Security Best Practices

### API Key Storage

1. **Never commit API keys** to version control
2. **Use config files with proper permissions**:
   ```bash
   chmod 600 ~/.obsidian-api/config.json
   ```
3. **Don't share API keys** - generate new keys if exposed
4. **Use environment variables** for temporary/CI use

### Network Security

1. **Localhost only** for personal use
2. **VPN/SSH tunnel** for remote access
3. **Firewall rules** to restrict access
4. **HTTPS always** for network connections

### Vault Backups

1. **Regular backups** before automation
2. **Version control** (git) for vault
3. **Test scripts** on sample notes first
4. **Backup before bulk operations**

---

## Advanced Configuration

### Multiple Vaults

To work with multiple vaults:

1. **Switch vault in Obsidian**
2. **Scripts automatically use active vault**

Or create vault-specific configs:

```bash
# Vault 1 config
echo '{"api_key": "key1", "port": 27124}' > .vault1-config.json

# Vault 2 config
echo '{"api_key": "key2", "port": 27125}' > .vault2-config.json

# Use specific config
OBSIDIAN_API_KEY=$(jq -r .api_key .vault1-config.json) \
  python3 scripts/create_note.py "note.md"
```

### Custom Port per Vault

Run multiple Obsidian instances on different ports:

1. **Instance 1**: Default (port 27124)
2. **Instance 2**: Custom port (27125)

Configure per vault as needed.

### Automation with Cron

Schedule regular operations:

```bash
# Edit crontab
crontab -e

# Add entries
0 6 * * * /path/to/daily-note-script.sh
0 * * * * /path/to/sync-tasks.sh
```

### CI/CD Integration

Use in continuous integration:

```yaml
# .github/workflows/docs.yml
jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Update Obsidian docs
        env:
          OBSIDIAN_API_KEY: ${{ secrets.OBSIDIAN_KEY }}
          OBSIDIAN_HOST: obsidian.example.com
        run: |
          python3 scripts/update-docs.py
```

---

## Performance Optimization

### Batch Operations

Instead of individual API calls:

```python
# Inefficient: Multiple separate calls
for file in files:
    create_note(file)

# Better: Batch with minimal overhead
for file in files:
    create_note(file)
    time.sleep(0.1)  # Small delay between requests
```

### Search Optimization

For large vaults:

1. **Use specific search terms** (not broad queries)
2. **Limit context length** to reduce payload size
3. **Cache results** when possible

### Rate Limiting

Be respectful of Obsidian's performance:

```python
import time

def rate_limited_operation(func, *args):
    result = func(*args)
    time.sleep(0.2)  # 200ms delay between operations
    return result
```

---

## Logging and Debugging

### Enable Debug Logging

Add logging to scripts:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("API request to: %s", endpoint)
```

### Monitor API Calls

Use verbose curl for debugging:

```bash
curl -v -H "Authorization: Bearer $API_KEY" \
  https://localhost:27124/vault/note.md --insecure
```

---

## Getting Help

### Check Plugin Status

In Obsidian:
1. Settings → Community Plugins
2. Find "Local REST API"
3. Check version and enabled status

### Plugin Logs

View plugin console in Obsidian:
1. Help → Toggle Developer Tools
2. Check Console tab for errors

### Community Support

- GitHub Issues: https://github.com/coddingtonbear/obsidian-local-rest-api/issues
- Obsidian Forum: https://forum.obsidian.md
- Discord: https://discord.gg/obsidianmd

---

## Quick Reference

| Issue | Solution |
|-------|----------|
| Connection refused | Start Obsidian, enable plugin |
| Authentication failed | Update API key |
| File not found | Check path, include .md |
| SSL errors | Scripts handle automatically |
| Missing requests module | `pip install requests` |
| Permission denied | `chmod +x scripts/*.py` |

---

## Configuration File Format

### User Config (`~/.obsidian-api/config.json`)

```json
{
  "api_key": "your-32-character-api-key",
  "host": "localhost",
  "port": 27124,
  "https": true
}
```

### Environment Variables

```bash
OBSIDIAN_API_KEY="your-api-key"
OBSIDIAN_HOST="localhost"
OBSIDIAN_PORT="27124"
OBSIDIAN_HTTPS="true"
```

---

## Related Resources

- Plugin documentation: https://github.com/coddingtonbear/obsidian-local-rest-api
- Obsidian help: https://help.obsidian.md
- Community plugins: https://obsidian.md/plugins
