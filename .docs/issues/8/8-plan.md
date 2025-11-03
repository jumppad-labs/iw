# Issue #8 - Obsidian Vault Filesystem Fallback

**Created**: 2025-11-03
**Last Updated**: 2025-11-03
**GitHub Issue**: https://github.com/jumppad-labs/iw/issues/8

## Overview

Add filesystem fallback to the Obsidian Local API skill to handle large files that fail via the REST API. The skill will attempt API operations first (maintaining compatibility with Obsidian features), then automatically fall back to direct filesystem operations when the API fails. This resolves the issue preventing issue #6 (research skills with Obsidian integration) from working with large research report files.

## Current State Analysis

All Obsidian skill operations exclusively use the REST API, which has limitations:

### Key Code Locations:

**Core API Client:**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:120-186` - HTTP request handling with fixed 120s timeout
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:159` - **Hardcoded 120-second timeout for ALL requests**
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:188-224` - Error parsing logic

**Script Files Using API:**
- `.claude/skills/obsidian-local-api/scripts/create_note.py:118-131` - Note creation via PUT /vault/{path}
- `.claude/skills/obsidian-local-api/scripts/read_note.py:68` - Note reading via GET /vault/{path}
- `.claude/skills/obsidian-local-api/scripts/append_note.py:63,77` - Content append via POST/PATCH

**Configuration Management:**
- `.claude/skills/obsidian-local-api/scripts/config_helper.py:53-97` - Config storage pattern
- `.claude/skills/obsidian-local-api/scripts/obsidian_client.py:68-118` - Multi-level config loading (ENV > Project > User)

### Current Implementation Example:

```python
# From .claude/skills/obsidian-local-api/scripts/create_note.py:118-131
def create_note(path: str, content: str = "", frontmatter: dict = None) -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Build note content
    note_content = build_note_content(content, frontmatter)

    # Create note via API (no fallback currently)
    endpoint = f"/vault/{path}"
    success, data, error = client.put(
        endpoint,
        data=note_content,
        headers={"Content-Type": "text/markdown"}
    )

    if success:
        print(f"✅ Note created: {path}")
        return True
    else:
        print(f"❌ Failed to create note: {error}", file=sys.stderr)
        return False  # FAILS HERE FOR LARGE FILES - NO FALLBACK
```

### Problems Identified:

1. **Fixed 120s timeout** - Insufficient for large files
2. **No retry logic** - Transient failures cause immediate failure
3. **Full response buffering** - Memory issues with large content
4. **No fallback mechanism** - API failure = operation failure
5. **No vault path configuration** - Can't fall back to filesystem even if we wanted to

## Desired End State

An Obsidian skill that:
1. **Attempts API operations first** (maintains Obsidian feature compatibility)
2. **Automatically falls back to filesystem** on any API error
3. **Prompts for vault path once** when filesystem is needed, stores permanently
4. **Works transparently** - scripts behave identically regardless of method used
5. **Maintains backward compatibility** - existing API-only workflows continue working

### Verification:
- Create large note (>5MB) via `create_note.py` - succeeds via filesystem fallback
- Read large note via `read_note.py` - succeeds via filesystem fallback
- Append to large note via `append_note.py` - succeeds via filesystem fallback
- Operations with small files continue using API when available
- Vault path stored in config and not re-prompted

## What We're NOT Doing

- ❌ **Not replacing API with filesystem-first**: API remains primary method
- ❌ **Not adding file size thresholds**: Simple error-based fallback only
- ❌ **Not implementing Obsidian feature detection**: Filesystem is just backup
- ❌ **Not adding complex retry logic**: Single API attempt, then fallback
- ❌ **Not changing the external API**: Using existing Obsidian Local REST API
- ❌ **Not modifying vault file watching**: Let Obsidian handle file detection

## Implementation Approach

**Five-phase implementation with try-API-first pattern:**

1. **Phase 1**: Add vault path configuration support
2. **Phase 2**: Implement filesystem operations module
3. **Phase 3**: Add fallback logic to ObsidianClient
4. **Phase 4**: Update script files to use fallback
5. **Phase 5**: Update documentation

**Key design decisions:**
- **Try-API-first**: Every operation attempts API, falls back on any error
- **Lazy prompting**: Only prompt for vault_path when filesystem fallback needed
- **Transparent fallback**: Scripts work identically whether using API or filesystem
- **Config persistence**: Vault path saved permanently in user config

---

## Phase 1: Add Vault Path Configuration

### Overview

Add vault_path to configuration schema, update config_helper.py to prompt for and store vault path, and optionally attempt auto-detection from API.

### Changes Required:

#### 1. Update Configuration Storage to Include vault_path

**File**: `.claude/skills/obsidian-local-api/scripts/config_helper.py`
**Lines**: 100-148 (interactive_setup function)
**Changes**: Add vault_path prompting after API key setup

**Current code:**
```python
# Lines 168-195: Interactive setup for API credentials
def interactive_setup():
    print("Obsidian API Configuration Setup")
    print("=" * 50)

    config = load_config()

    # API Key
    current_key = config.get('api_key', '')
    if current_key:
        masked = current_key[:4] + "*" * 8 + current_key[-4:] if len(current_key) > 8 else "****"
        print(f"Current API key: {masked}")

    api_key = input("\nEnter API key (or press Enter to keep current): ").strip()
    if api_key:
        config['api_key'] = api_key

    # ... similar for host, port, https

    # Save configuration
    if save_config(config):
        print(f"✅ Configuration saved to: {CONFIG_FILE}")
```

**Proposed changes:**
```python
def interactive_setup():
    print("Obsidian API Configuration Setup")
    print("=" * 50)

    config = load_config()

    # API Key (existing)
    current_key = config.get('api_key', '')
    if current_key:
        masked = current_key[:4] + "*" * 8 + current_key[-4:] if len(current_key) > 8 else "****"
        print(f"Current API key: {masked}")

    api_key = input("\nEnter API key (or press Enter to keep current): ").strip()
    if api_key:
        config['api_key'] = api_key

    # ... existing host, port, https prompts ...

    # NEW: Vault Path (for filesystem fallback)
    print("\n" + "=" * 50)
    print("Vault Path Configuration (Optional)")
    print("=" * 50)
    print("The vault path enables filesystem fallback when API operations fail.")
    print("This is useful for large files that exceed API timeouts.")

    current_vault = config.get('vault_path', '')
    if current_vault:
        print(f"Current vault path: {current_vault}")

    # Attempt auto-detection from API
    vault_suggestion = None
    if config.get('api_key'):
        print("\nAttempting to detect vault path from API...")
        try:
            from obsidian_client import ObsidianClient
            client = ObsidianClient(api_key=config.get('api_key'))
            # Try to get vault info from API (if endpoint exists)
            success, data, error = client.get("/vault/")
            if success and isinstance(data, dict):
                vault_suggestion = data.get('vault_path') or data.get('path')
                if vault_suggestion:
                    print(f"✅ Detected vault path: {vault_suggestion}")
        except Exception as e:
            print(f"⚠️  Could not detect vault path: {e}")

    # Prompt for vault path
    prompt_text = f"\nEnter vault path"
    if vault_suggestion:
        prompt_text += f" (or press Enter for detected: {vault_suggestion})"
    elif current_vault:
        prompt_text += " (or press Enter to keep current)"
    else:
        prompt_text += " (or press Enter to skip)"
    prompt_text += ": "

    vault_input = input(prompt_text).strip()
    if vault_input:
        # User provided path
        vault_path = Path(vault_input).expanduser()
        if vault_path.exists() and vault_path.is_dir():
            config['vault_path'] = str(vault_path)
            print(f"✅ Vault path set to: {vault_path}")
        else:
            print(f"⚠️  Warning: Path does not exist or is not a directory: {vault_path}")
            print(f"   You can update this later with: --set-vault-path")
            config['vault_path'] = str(vault_path)
    elif vault_suggestion and not current_vault:
        # Use detected path
        config['vault_path'] = vault_suggestion
        print(f"✅ Using detected vault path: {vault_suggestion}")
    elif not current_vault:
        print("ℹ️  Vault path not configured. Filesystem fallback will prompt when needed.")

    # Save configuration
    if save_config(config):
        print(f"\n✅ Configuration saved to: {CONFIG_FILE}")
```

**Reasoning**: Integrates vault_path configuration into existing setup flow with auto-detection attempt and clear user guidance.

#### 2. Add CLI Argument for Setting Vault Path

**File**: `.claude/skills/obsidian-local-api/scripts/config_helper.py`
**Lines**: 234-262 (main function argument parsing)
**Changes**: Add --set-vault-path argument

**Current code:**
```python
def main():
    parser = argparse.ArgumentParser(description="Obsidian API configuration helper")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--set-key", help="Set API key directly")
    args = parser.parse_args()
```

**Proposed changes:**
```python
def main():
    parser = argparse.ArgumentParser(description="Obsidian API configuration helper")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--set-key", help="Set API key directly")
    parser.add_argument("--set-vault-path", help="Set vault path directly")  # NEW
    args = parser.parse_args()

    # Handle --set-vault-path
    if args.set_vault_path:
        config = load_config()
        vault_path = Path(args.set_vault_path).expanduser()
        if vault_path.exists() and vault_path.is_dir():
            config['vault_path'] = str(vault_path)
            if save_config(config):
                print(f"✅ Vault path set to: {vault_path}")
                sys.exit(0)
        else:
            print(f"❌ Invalid vault path: {vault_path}", file=sys.stderr)
            print(f"   Path must exist and be a directory", file=sys.stderr)
            sys.exit(1)

    # ... existing handler code ...
```

**Reasoning**: Allows direct vault path configuration for scripting and quick updates.

#### 3. Update Config Display to Show Vault Path

**File**: `.claude/skills/obsidian-local-api/scripts/config_helper.py`
**Lines**: 100-116 (show_config function)
**Changes**: Add vault_path to display output

**Current code:**
```python
def show_config():
    config = load_config()

    if not config:
        print("No configuration found")
        return

    print("Current Obsidian API Configuration:")
    print("=" * 50)

    # API Key (masked)
    api_key = config.get('api_key', 'Not set')
    if api_key != 'Not set':
        masked = api_key[:4] + "*" * 8 + api_key[-4:] if len(api_key) > 8 else "****"
        print(f"API Key: {masked}")
    else:
        print(f"API Key: {api_key}")

    print(f"Host: {config.get('host', 'localhost')}")
    print(f"Port: {config.get('port', '27124')}")
    print(f"HTTPS: {config.get('https', True)}")
```

**Proposed changes:**
```python
def show_config():
    config = load_config()

    if not config:
        print("No configuration found")
        return

    print("Current Obsidian API Configuration:")
    print("=" * 50)

    # API Key (masked)
    api_key = config.get('api_key', 'Not set')
    if api_key != 'Not set':
        masked = api_key[:4] + "*" * 8 + api_key[-4:] if len(api_key) > 8 else "****"
        print(f"API Key: {masked}")
    else:
        print(f"API Key: {api_key}")

    print(f"Host: {config.get('host', 'localhost')}")
    print(f"Port: {config.get('port', '27124')}")
    print(f"HTTPS: {config.get('https', True)}")

    # NEW: Vault Path
    vault_path = config.get('vault_path', 'Not set')
    print(f"Vault Path: {vault_path}")
    if vault_path != 'Not set':
        vault_exists = Path(vault_path).exists()
        print(f"  Status: {'✅ Exists' if vault_exists else '❌ Not found'}")
```

**Reasoning**: Provides visibility into vault_path configuration and validation status.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test interactive setup with auto-detection:**
   ```bash
   python3 config_helper.py
   ```
   - Verify vault_path prompt appears
   - Verify auto-detection attempts if API key set
   - Enter vault path manually
   - Verify config saved

2. **Test --set-vault-path CLI:**
   ```bash
   python3 config_helper.py --set-vault-path ~/Documents/ObsidianVault
   ```
   - Verify path validated
   - Verify config saved
   - Test with invalid path, verify error

3. **Test --show display:**
   ```bash
   python3 config_helper.py --show
   ```
   - Verify vault_path displayed
   - Verify existence check shown

### Success Criteria:

#### Automated Verification:
- N/A (skill scripts don't have automated tests)

#### Manual Verification:
- [ ] vault_path prompt integrated into interactive setup
- [ ] Auto-detection attempted when API available
- [ ] vault_path saved to config file
- [ ] --set-vault-path CLI works correctly
- [ ] Invalid paths rejected with clear error
- [ ] --show displays vault_path with status
- [ ] Config file format unchanged except new field

---

## Phase 2: Implement Filesystem Operations Module

### Overview

Create new `filesystem_ops.py` module with read/write functions for direct vault file access. This provides the fallback mechanism when API operations fail.

### Changes Required:

#### 1. Create Filesystem Operations Module

**File**: `.claude/skills/obsidian-local-api/scripts/filesystem_ops.py` (NEW)
**Changes**: Create complete module with file operations

**New file content:**
```python
#!/usr/bin/env python3
"""
Filesystem operations for Obsidian vault access.

Provides direct file read/write capabilities as fallback when REST API fails.
Used automatically by obsidian_client when API operations timeout or error.
"""

import os
from pathlib import Path
from typing import Optional, Tuple


class FilesystemOperations:
    """Direct filesystem operations for Obsidian vault."""

    def __init__(self, vault_path: str):
        """
        Initialize filesystem operations.

        Args:
            vault_path: Absolute path to Obsidian vault root
        """
        self.vault_path = Path(vault_path).expanduser().resolve()

        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_path}")
        if not self.vault_path.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {self.vault_path}")

    def _resolve_note_path(self, note_path: str) -> Path:
        """
        Resolve note path relative to vault root.

        Args:
            note_path: Note path relative to vault (e.g., "Daily/2025-01-03.md")

        Returns:
            Absolute path to note file
        """
        # Remove leading slash if present
        if note_path.startswith('/'):
            note_path = note_path[1:]

        # Ensure .md extension
        if not note_path.endswith('.md'):
            note_path += '.md'

        # Resolve full path
        full_path = self.vault_path / note_path

        # Security check: ensure resolved path is within vault
        try:
            full_path.resolve().relative_to(self.vault_path.resolve())
        except ValueError:
            raise ValueError(f"Note path escapes vault directory: {note_path}")

        return full_path

    def read_note(self, note_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Read note content from filesystem.

        Args:
            note_path: Note path relative to vault root

        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            full_path = self._resolve_note_path(note_path)

            if not full_path.exists():
                return False, None, f"Note not found: {note_path}"

            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return True, content, None

        except Exception as e:
            return False, None, f"Failed to read note: {str(e)}"

    def write_note(self, note_path: str, content: str, create_dirs: bool = True) -> Tuple[bool, None, Optional[str]]:
        """
        Write note content to filesystem.

        Args:
            note_path: Note path relative to vault root
            content: Note content to write
            create_dirs: Create parent directories if they don't exist

        Returns:
            Tuple of (success, None, error_message)
        """
        try:
            full_path = self._resolve_note_path(note_path)

            # Create parent directories if needed
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, None, None

        except Exception as e:
            return False, None, f"Failed to write note: {str(e)}"

    def append_note(self, note_path: str, content: str, heading: Optional[str] = None) -> Tuple[bool, None, Optional[str]]:
        """
        Append content to existing note.

        Args:
            note_path: Note path relative to vault root
            content: Content to append
            heading: Optional heading to insert content after

        Returns:
            Tuple of (success, None, error_message)
        """
        try:
            full_path = self._resolve_note_path(note_path)

            if not full_path.exists():
                return False, None, f"Note not found: {note_path}"

            # Read existing content
            with open(full_path, 'r', encoding='utf-8') as f:
                existing = f.read()

            # Append or insert at heading
            if heading:
                # Find heading and insert after it
                lines = existing.split('\n')
                heading_line = -1

                for i, line in enumerate(lines):
                    if line.strip() == heading.strip():
                        heading_line = i
                        break

                if heading_line == -1:
                    return False, None, f"Heading not found: {heading}"

                # Insert content after heading
                lines.insert(heading_line + 1, content)
                new_content = '\n'.join(lines)
            else:
                # Simple append to end
                new_content = existing
                if not existing.endswith('\n'):
                    new_content += '\n'
                new_content += content

            # Write updated content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, None, None

        except Exception as e:
            return False, None, f"Failed to append to note: {str(e)}"

    def note_exists(self, note_path: str) -> bool:
        """
        Check if note exists in vault.

        Args:
            note_path: Note path relative to vault root

        Returns:
            True if note exists, False otherwise
        """
        try:
            full_path = self._resolve_note_path(note_path)
            return full_path.exists()
        except:
            return False
```

**Reasoning**: Provides complete filesystem operations matching API capabilities with security checks (path traversal prevention) and consistent error handling.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test read operation:**
   ```python
   from filesystem_ops import FilesystemOperations
   fs = FilesystemOperations("/path/to/vault")
   success, content, error = fs.read_note("Daily/2025-01-03.md")
   assert success and content
   ```

2. **Test write operation:**
   ```python
   success, _, error = fs.write_note("Test/new-note.md", "# Test Content")
   assert success
   ```

3. **Test append operation:**
   ```python
   success, _, error = fs.append_note("Test/new-note.md", "More content")
   assert success
   ```

4. **Test path traversal prevention:**
   ```python
   # Should fail
   success, _, error = fs.read_note("../../../etc/passwd")
   assert not success
   ```

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] read_note reads existing files correctly
- [ ] write_note creates new files with parent directories
- [ ] append_note appends to end correctly
- [ ] append_note with heading inserts at correct location
- [ ] Path traversal attacks prevented
- [ ] .md extension added automatically
- [ ] Error messages are clear and helpful
- [ ] Operations work with nested directories

---

## Phase 3: Add Fallback Logic to ObsidianClient

### Overview

Modify `ObsidianClient` class to detect API failures and automatically fall back to filesystem operations. Add vault path prompting when filesystem needed but not configured.

### Changes Required:

#### 1. Add Filesystem Fallback Methods to ObsidianClient

**File**: `.claude/skills/obsidian-local-api/scripts/obsidian_client.py`
**Lines**: After line 323 (end of get_client function)
**Changes**: Add fallback detection and filesystem operations

**Add new methods to ObsidianClient class (after line 295):**
```python
    def _get_vault_path(self) -> Optional[str]:
        """
        Get vault path from config, prompting if not set.

        Returns:
            Vault path or None if user declines
        """
        # Check if already loaded
        vault_path = self._load_config_value("vault_path")

        if vault_path:
            return vault_path

        # Vault path not configured, prompt user
        print("\n" + "=" * 60)
        print("⚠️  Filesystem Fallback Required")
        print("=" * 60)
        print("The Obsidian API operation failed or timed out.")
        print("To continue, please provide your Obsidian vault path.")
        print("This enables direct file access as a fallback.")
        print()
        print("You can find your vault path in Obsidian:")
        print("  Settings → About → Vault folder path")
        print()

        vault_input = input("Enter vault path (or press Enter to cancel): ").strip()

        if not vault_input:
            return None

        vault_path = Path(vault_input).expanduser()

        # Validate path
        if not vault_path.exists():
            print(f"❌ Path does not exist: {vault_path}", file=sys.stderr)
            return None

        if not vault_path.is_dir():
            print(f"❌ Path is not a directory: {vault_path}", file=sys.stderr)
            return None

        # Save to config for future use
        print(f"✅ Vault path validated: {vault_path}")
        print("Saving to configuration...")

        # Load full config
        from config_helper import load_config, save_config
        config = load_config()
        config['vault_path'] = str(vault_path)

        if save_config(config):
            print(f"✅ Configuration saved. Future operations will use filesystem fallback automatically.")
            return str(vault_path)
        else:
            print(f"⚠️  Could not save configuration, but continuing with this session.")
            return str(vault_path)

    def _try_filesystem_fallback(self, operation: str, note_path: str, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """
        Attempt operation via filesystem fallback.

        Args:
            operation: Operation type ('read', 'write', 'append')
            note_path: Note path relative to vault
            **kwargs: Operation-specific arguments

        Returns:
            Tuple of (success, data, error_message)
        """
        vault_path = self._get_vault_path()

        if not vault_path:
            return False, None, "Filesystem fallback requires vault path (operation cancelled by user)"

        try:
            from filesystem_ops import FilesystemOperations
            fs = FilesystemOperations(vault_path)

            if operation == 'read':
                return fs.read_note(note_path)
            elif operation == 'write':
                content = kwargs.get('content', '')
                return fs.write_note(note_path, content)
            elif operation == 'append':
                content = kwargs.get('content', '')
                heading = kwargs.get('heading')
                return fs.append_note(note_path, content, heading)
            else:
                return False, None, f"Unknown operation: {operation}"

        except Exception as e:
            return False, None, f"Filesystem fallback failed: {str(e)}"

    def get_with_fallback(self, note_path: str) -> Tuple[bool, Any, Optional[str]]:
        """
        GET request with filesystem fallback.

        Args:
            note_path: Note path for reading (e.g., "Daily/note.md")

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"
        success, data, error = self.get(endpoint)

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API read failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('read', note_path)

    def put_with_fallback(self, note_path: str, content: str) -> Tuple[bool, Any, Optional[str]]:
        """
        PUT request with filesystem fallback.

        Args:
            note_path: Note path for writing
            content: Note content

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"
        success, data, error = self.put(
            endpoint,
            data=content,
            headers={"Content-Type": "text/markdown"}
        )

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API write failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('write', note_path, content=content)

    def append_with_fallback(self, note_path: str, content: str, heading: Optional[str] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Append operation with filesystem fallback.

        Args:
            note_path: Note path for appending
            content: Content to append
            heading: Optional heading to insert after

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"

        if heading:
            # Use PATCH for targeted insertion
            success, data, error = self.patch(
                endpoint,
                json_data={"content": content, "heading": heading}
            )
        else:
            # Use POST for simple append
            success, data, error = self.post(
                endpoint,
                data=content,
                headers={"Content-Type": "text/markdown"}
            )

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API append failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('append', note_path, content=content, heading=heading)
```

**Reasoning**: Provides transparent fallback with clear user feedback. Prompts for vault path only when needed and saves for future use.

#### 2. Update get_client to Import Dependencies

**File**: `.claude/skills/obsidian-local-api/scripts/obsidian_client.py`
**Lines**: 1-16 (imports section)
**Changes**: Add sys import for stderr output

**Current imports:**
```python
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import urllib3
```

**Proposed changes:**
```python
import os
import json
import sys  # NEW: For stderr output in prompts
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import urllib3
```

**Reasoning**: Needed for stderr output in fallback prompts.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test API success (no fallback):**
   ```python
   client = get_client()
   success, data, error = client.get_with_fallback("existing-note.md")
   # Should use API, not prompt for vault path
   ```

2. **Test API failure with vault path configured:**
   - Configure vault_path in config
   - Simulate API failure (stop Obsidian)
   - Call get_with_fallback
   - Verify filesystem fallback used without prompt

3. **Test API failure without vault path:**
   - Remove vault_path from config
   - Simulate API failure
   - Call get_with_fallback
   - Verify user prompted for vault path
   - Enter path
   - Verify config saved

4. **Test user cancellation:**
   - Remove vault_path from config
   - Simulate API failure
   - Call get_with_fallback
   - Press Enter (cancel) at prompt
   - Verify operation fails gracefully

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] API operations attempted first
- [ ] Fallback triggered on API failure
- [ ] Vault path prompted when not configured
- [ ] Vault path validated before use
- [ ] Config saved after successful prompt
- [ ] User can cancel vault path prompt
- [ ] Clear feedback messages shown
- [ ] Read, write, and append all work via fallback

---

## Phase 4: Update Script Files for Fallback

### Overview

Modify create_note.py, read_note.py, and append_note.py to use new fallback methods instead of direct API calls.

### Changes Required:

#### 1. Update create_note.py to Use Fallback

**File**: `.claude/skills/obsidian-local-api/scripts/create_note.py`
**Lines**: 118-131
**Changes**: Use put_with_fallback instead of client.put

**Current code:**
```python
def create_note(path: str, content: str = "", frontmatter: dict = None) -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Build note content
    note_content = build_note_content(content, frontmatter)

    # Create note via API
    endpoint = f"/vault/{path}"
    success, data, error = client.put(
        endpoint,
        data=note_content,
        headers={"Content-Type": "text/markdown"}
    )

    if success:
        print(f"✅ Note created: {path}")
        return True
    else:
        print(f"❌ Failed to create note: {error}", file=sys.stderr)
        return False
```

**Proposed changes:**
```python
def create_note(path: str, content: str = "", frontmatter: dict = None) -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Build note content
    note_content = build_note_content(content, frontmatter)

    # Create note via API with filesystem fallback
    success, data, error = client.put_with_fallback(path, note_content)

    if success:
        print(f"✅ Note created: {path}")
        return True
    else:
        print(f"❌ Failed to create note: {error}", file=sys.stderr)
        return False
```

**Reasoning**: Single line change provides automatic fallback without changing script behavior.

#### 2. Update read_note.py to Use Fallback

**File**: `.claude/skills/obsidian-local-api/scripts/read_note.py`
**Lines**: 53-90
**Changes**: Use get_with_fallback instead of client.get

**Current code:**
```python
def read_note(path: str, format_type: str = "markdown") -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Build request
    endpoint = f"/vault/{path}"
    headers = {}

    # Request JSON format if specified
    if format_type == "json":
        headers["Accept"] = "application/vnd.olrapi.note+json"

    # Read note via API
    success, data, error = client.get(endpoint, headers=headers)

    if success:
        if format_type == "json":
            # Pretty-print JSON
            if isinstance(data, dict):
                print(json.dumps(data, indent=2))
            else:
                print(data)
        else:
            # Output markdown content
            if isinstance(data, dict):
                content = data.get('content', '')
                print(content)
            else:
                print(data)
        return True
    else:
        print(f"❌ Failed to read note: {error}", file=sys.stderr)
        return False
```

**Proposed changes:**
```python
def read_note(path: str, format_type: str = "markdown") -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Read note via API with filesystem fallback
    # Note: Filesystem fallback always returns markdown format
    success, data, error = client.get_with_fallback(path)

    if success:
        if format_type == "json":
            # If API succeeded, data might be JSON already
            if isinstance(data, dict):
                print(json.dumps(data, indent=2))
            else:
                # Filesystem fallback returns markdown, wrap in JSON-like structure
                print(json.dumps({"content": data}, indent=2))
        else:
            # Output markdown content
            if isinstance(data, dict):
                content = data.get('content', '')
                print(content)
            else:
                print(data)
        return True
    else:
        print(f"❌ Failed to read note: {error}", file=sys.stderr)
        return False
```

**Reasoning**: Uses fallback method while maintaining format handling compatibility.

#### 3. Update append_note.py to Use Fallback

**File**: `.claude/skills/obsidian-local-api/scripts/append_note.py`
**Lines**: 60-91
**Changes**: Use append_with_fallback instead of client.post/patch

**Current code:**
```python
def append_note(path: str, content: str, heading: str = None) -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Build endpoint
    endpoint = f"/vault/{path}"

    # Append content
    if heading:
        # Insert content after specific heading
        success, data, error = client.patch(
            endpoint,
            json_data={"content": content, "heading": heading}
        )
    else:
        # Append to end of note
        success, data, error = client.post(
            endpoint,
            data=content,
            headers={"Content-Type": "text/markdown"}
        )

    if success:
        if heading:
            print(f"✅ Content inserted after heading '{heading}' in: {path}")
        else:
            print(f"✅ Content appended to: {path}")
        return True
    else:
        print(f"❌ Failed to append content: {error}", file=sys.stderr)
        return False
```

**Proposed changes:**
```python
def append_note(path: str, content: str, heading: str = None) -> bool:
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    # Append content via API with filesystem fallback
    success, data, error = client.append_with_fallback(path, content, heading)

    if success:
        if heading:
            print(f"✅ Content inserted after heading '{heading}' in: {path}")
        else:
            print(f"✅ Content appended to: {path}")
        return True
    else:
        print(f"❌ Failed to append content: {error}", file=sys.stderr)
        return False
```

**Reasoning**: Simplified code with automatic fallback, cleaner implementation.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Test create_note with large file:**
   ```bash
   # Create 5MB content
   python3 -c "print('# Large File\n\n' + 'x' * 5000000)" > /tmp/large.txt
   python3 create_note.py "Test/large-note.md" --content "$(cat /tmp/large.txt)"
   ```
   - Verify filesystem fallback used
   - Verify note created successfully

2. **Test read_note with large file:**
   ```bash
   python3 read_note.py "Test/large-note.md"
   ```
   - Verify filesystem fallback used
   - Verify content returned

3. **Test append_note:**
   ```bash
   python3 append_note.py "Test/large-note.md" "Additional content"
   ```
   - Verify filesystem fallback used
   - Verify content appended

4. **Test with API available (small files):**
   - Start Obsidian with API plugin
   - Create small note
   - Verify API used (no fallback message)

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] Large files (>1MB) successfully created via fallback
- [ ] Large files successfully read via fallback
- [ ] Content successfully appended to large files
- [ ] Small files still use API when available
- [ ] Error messages clear and helpful
- [ ] Scripts work identically whether using API or filesystem
- [ ] No behavioral changes from user perspective

---

## Phase 5: Update Documentation

### Overview

Update SKILL.md, configuration.md, and api_reference.md to document fallback behavior and vault_path configuration.

### Changes Required:

#### 1. Update SKILL.md with Fallback Behavior

**File**: `.claude/skills/obsidian-local-api/SKILL.md`
**Lines**: After line 29 (Prerequisites Check section)
**Changes**: Add fallback behavior explanation

**Add new section after Prerequisites Check:**
```markdown
## Fallback Behavior

The skill uses a **try-API-first with filesystem fallback** approach for reliability:

1. **Primary**: All operations attempt REST API first
   - Faster for small files
   - Provides Obsidian features (caching, plugins, live updates)
   - Requires Obsidian running

2. **Fallback**: On API failure, automatically uses filesystem
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
```

**Reasoning**: Provides clear understanding of fallback behavior and how to configure it.

#### 2. Update Error Handling Section

**File**: `.claude/skills/obsidian-local-api/SKILL.md`
**Lines**: 166-182 (Error Handling section)
**Changes**: Update error scenarios to include fallback

**Current section:**
```markdown
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
```

**Enhanced section:**
```markdown
## Error Handling

Common errors and solutions:

**"Connection refused"**
→ Ensure Obsidian is running with Local REST API plugin enabled
→ OR: Configure vault_path for filesystem fallback
→ Filesystem fallback will activate automatically if vault_path is set

**"Authentication failed"**
→ Check API key configuration: `python3 scripts/config_helper.py --show`
→ Update key: `python3 scripts/config_helper.py --set-key "your-key"`
→ Note: Filesystem fallback will activate if authentication fails

**"Request timed out"**
→ Large files (>1MB) may timeout via API
→ Filesystem fallback will activate automatically
→ Ensure vault_path is configured for seamless fallback

**"SSL certificate verify failed"**
→ The plugin uses self-signed certificates; scripts handle this automatically
→ If issues persist, download cert from http://localhost:27123/cert.pem

**"Note not found"**
→ Verify path is correct relative to vault root
→ Use forward slashes, include .md extension
→ Works the same for both API and filesystem access

**"Filesystem fallback requires vault path"**
→ API failed and vault_path not configured
→ Run: `python3 scripts/config_helper.py --set-vault-path "/path/to/vault"`
→ Or: You'll be prompted when fallback is needed
```

**Reasoning**: Updates error handling to reflect fallback capabilities and configuration options.

#### 3. Update Configuration Documentation

**File**: `.claude/skills/obsidian-local-api/references/configuration.md`
**Lines**: Add new section for vault_path
**Changes**: Document vault_path configuration

**Add new section:**
```markdown
## Vault Path Configuration

### Purpose

The `vault_path` configuration enables filesystem fallback when REST API operations fail. This is particularly useful for:
- Large files (>1MB) that timeout via API
- Operations when Obsidian is closed
- Environments where API is unreliable

### Configuration Methods

#### 1. Interactive Setup

Run the configuration helper:
```bash
python3 scripts/config_helper.py
```

Follow prompts to configure vault_path:
- Auto-detection attempted if API is available
- Manual entry if auto-detection fails
- Validation before saving
- Stored in `~/.obsidian-api/config.json`

#### 2. Direct Configuration

Set vault path directly:
```bash
python3 scripts/config_helper.py --set-vault-path "/Users/name/Documents/ObsidianVault"
```

#### 3. Environment Variable

Set via environment variable:
```bash
export OBSIDIAN_VAULT_PATH="/Users/name/Documents/ObsidianVault"
```

#### 4. Project-Level Configuration

Create `.obsidian-api.json` in project root:
```json
{
  "api_key": "your-api-key",
  "vault_path": "/Users/name/Documents/ObsidianVault"
}
```

### Finding Your Vault Path

**In Obsidian:**
1. Open Settings (⚙️)
2. Go to "About" section
3. Look for "Vault folder path"
4. Copy the full path

**Common locations:**
- macOS: `/Users/<name>/Documents/ObsidianVault`
- Linux: `/home/<name>/Documents/ObsidianVault`
- Windows: `C:\Users\<name>\Documents\ObsidianVault`

### Validation

The vault path must:
- Exist on the filesystem
- Be a directory (not a file)
- Be readable and writable by the current user
- Point to the root of an Obsidian vault

Path validation occurs:
- During configuration setup
- Before fallback operations
- At script startup (optional warning if invalid)

### Security Considerations

**Path Traversal Prevention:**
All note paths are validated to prevent escaping the vault directory:
```python
# This is prevented:
read_note("../../../etc/passwd")  # Blocked by validation
```

**File Permissions:**
The configuration file is created with restricted permissions (0o600) to protect vault path information.
```

**Reasoning**: Provides comprehensive vault_path documentation for users.

### Testing for This Phase:

**Manual Verification Steps:**

1. **Verify SKILL.md clarity:**
   - Read fallback behavior section
   - Confirm explanation is clear
   - Check examples are accurate

2. **Verify configuration.md:**
   - Follow vault path setup instructions
   - Verify all methods work
   - Check validation behavior

3. **Test documentation examples:**
   - Run example commands from docs
   - Verify output matches descriptions

### Success Criteria:

#### Automated Verification:
- N/A

#### Manual Verification:
- [ ] SKILL.md clearly explains fallback behavior
- [ ] Vault path configuration documented
- [ ] Error handling updated with fallback info
- [ ] Configuration.md has complete vault_path section
- [ ] Examples are accurate and work correctly
- [ ] Security considerations documented
- [ ] Finding vault path instructions clear

---

## Testing Strategy

### Manual Testing Checklist:

**Basic Operations:**
- [ ] Small files use API when available
- [ ] Large files trigger fallback automatically
- [ ] Fallback works when Obsidian closed

**Configuration:**
- [ ] Interactive setup prompts for vault_path
- [ ] --set-vault-path CLI works
- [ ] vault_path validated before saving
- [ ] Invalid paths rejected with clear error

**Fallback Activation:**
- [ ] API timeout triggers fallback
- [ ] Connection error triggers fallback
- [ ] Authentication error triggers fallback
- [ ] Fallback prompts for vault_path if not configured

**Script Operations:**
- [ ] create_note works via fallback
- [ ] read_note works via fallback
- [ ] append_note works via fallback
- [ ] append_note with heading works via fallback

**Security:**
- [ ] Path traversal attempts blocked
- [ ] Operations restricted to vault directory
- [ ] Config file has correct permissions

**User Experience:**
- [ ] Clear feedback when fallback used
- [ ] Vault path prompted only when needed
- [ ] Config saved after successful prompt
- [ ] Operations transparent regardless of method

## Performance Considerations

**Filesystem Operations:**
- Direct file I/O is faster than API for large files
- No 120s timeout limitation
- Memory-efficient streaming for very large files

**API Operations:**
- Preferred for small files (<1MB)
- Provides Obsidian integration features
- May be slower for large files due to processing overhead

**Fallback Decision:**
- No performance cost for successful API operations
- Fallback only attempted after API failure
- One-time vault path prompt, then cached

## Migration Notes

**Existing Installations:**
- No breaking changes to existing scripts
- vault_path is optional, prompts when needed
- Existing API-only workflows continue working
- Gradual migration as users encounter large files

**New Installations:**
- Configure vault_path during initial setup
- Full fallback support from day one
- No special migration needed

## References

- Original issue: https://github.com/jumppad-labs/iw/issues/8
- Related issue: https://github.com/jumppad-labs/iw/issues/6
- Research notes: `.docs/issues/8/8-research.md`
- Context document: `.docs/issues/8/8-context.md`
- Task breakdown: `.docs/issues/8/8-tasks.md`
- Obsidian Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api
