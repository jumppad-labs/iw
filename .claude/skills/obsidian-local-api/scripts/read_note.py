#!/usr/bin/env python3
"""
Read a note from the Obsidian vault.

This script retrieves note content from the vault, optionally including
metadata in JSON format.

Usage:
    read_note.py <path> [options]

Arguments:
    path           Note path relative to vault root (e.g., "Daily/2025-01-03.md")

Options:
    --format FORMAT  Output format: 'markdown' (default) or 'json'
    --help          Show this help message

Examples:
    # Read note as markdown
    read_note.py "Daily/2025-01-03.md"

    # Read note with metadata as JSON
    read_note.py "Projects/project.md" --format json

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


def read_note(path: str, format_type: str = "markdown") -> bool:
    """
    Read a note from Obsidian vault.

    Args:
        path: Note path relative to vault root
        format_type: Output format ('markdown' or 'json')

    Returns:
        True if successful, False otherwise
    """
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
                # Extracted JSON format, get content field
                content = data.get('content', '')
                print(content)
            else:
                # Plain text response
                print(data)
        return True
    else:
        print(f"❌ Failed to read note: {error}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Read a note from Obsidian vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Daily/2025-01-03.md"
  %(prog)s "Projects/project.md" --format json
        """
    )

    parser.add_argument(
        "path",
        help="Note path relative to vault root (e.g., 'Daily/2025-01-03.md')"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Read note
    success = read_note(args.path, args.format)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
