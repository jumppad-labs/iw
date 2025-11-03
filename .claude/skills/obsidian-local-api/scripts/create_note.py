#!/usr/bin/env python3
"""
Create a new note in the Obsidian vault.

This script creates a new note at the specified path with optional content
and frontmatter metadata.

Usage:
    create_note.py <path> [options]

Arguments:
    path                Note path relative to vault root (e.g., "Daily/2025-01-03.md")

Options:
    --content TEXT      Initial note content
    --frontmatter JSON  Frontmatter metadata as JSON string
    --help             Show this help message

Examples:
    # Create empty note
    create_note.py "Daily/2025-01-03.md"

    # Create note with content
    create_note.py "Daily/2025-01-03.md" --content "# Today's Notes"

    # Create note with frontmatter and content
    create_note.py "Projects/new-project.md" \
        --frontmatter '{"tags": ["project", "active"], "status": "planning"}' \
        --content "# New Project\n\n## Overview\n\n## Tasks"

Requires:
    - Obsidian running with Local REST API plugin enabled
    - API key configured (use config_helper.py)
"""

import sys
import argparse
import json
from pathlib import Path

# Add script directory to path to import obsidian_client
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from obsidian_client import get_client


def format_frontmatter(frontmatter: dict) -> str:
    """
    Format frontmatter dict as YAML.

    Args:
        frontmatter: Dictionary of frontmatter fields

    Returns:
        Formatted YAML frontmatter string
    """
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def build_note_content(content: str = "", frontmatter: dict = None) -> str:
    """
    Build complete note content with optional frontmatter.

    Args:
        content: Note body content
        frontmatter: Optional frontmatter dict

    Returns:
        Complete note content
    """
    parts = []

    if frontmatter:
        parts.append(format_frontmatter(frontmatter))
        parts.append("")  # Blank line after frontmatter

    if content:
        parts.append(content)

    return "\n".join(parts)


def create_note(path: str, content: str = "", frontmatter: dict = None) -> bool:
    """
    Create a note in Obsidian vault.

    Args:
        path: Note path relative to vault root
        content: Note content
        frontmatter: Optional frontmatter metadata

    Returns:
        True if successful, False otherwise
    """
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new note in Obsidian vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Daily/2025-01-03.md"
  %(prog)s "Daily/2025-01-03.md" --content "# Today's Notes"
  %(prog)s "Projects/new-project.md" --frontmatter '{"tags": ["project"]}'
        """
    )

    parser.add_argument(
        "path",
        help="Note path relative to vault root (e.g., 'Daily/2025-01-03.md')"
    )
    parser.add_argument(
        "--content",
        default="",
        help="Initial note content"
    )
    parser.add_argument(
        "--frontmatter",
        help="Frontmatter metadata as JSON string"
    )

    args = parser.parse_args()

    # Parse frontmatter if provided
    frontmatter = None
    if args.frontmatter:
        try:
            frontmatter = json.loads(args.frontmatter)
            if not isinstance(frontmatter, dict):
                print("Error: Frontmatter must be a JSON object", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in frontmatter: {e}", file=sys.stderr)
            sys.exit(1)

    # Create note
    success = create_note(args.path, args.content, frontmatter)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
