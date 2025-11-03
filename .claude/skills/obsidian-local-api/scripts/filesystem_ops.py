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
