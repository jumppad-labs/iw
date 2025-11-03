#!/usr/bin/env python3
"""
Append content to an existing note.

This script appends content to a note, either at the end or at a specific
heading location within the note.

Usage:
    append_note.py <path> <content> [options]

Arguments:
    path              Note path relative to vault root
    content           Content to append

Options:
    --heading TEXT    Heading to insert after (uses PATCH for insertion)
    --help           Show this help message

Examples:
    # Append to end of note
    append_note.py "Daily/2025-01-03.md" "- Task completed"

    # Insert content after specific heading
    append_note.py "Projects/notes.md" "New findings" --heading "## Research"

    # Append multiple lines
    append_note.py "Daily/2025-01-03.md" "## Notes\n\n- Point 1\n- Point 2"

Requires:
    - Obsidian running with Local REST API plugin enabled
    - API key configured (use config_helper.py)
"""

import sys
import argparse
from pathlib import Path

# Add script directory to path to import obsidian_client
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from obsidian_client import get_client


def append_to_note(path: str, content: str, heading: str = None) -> bool:
    """
    Append content to a note.

    Args:
        path: Note path relative to vault root
        content: Content to append
        heading: Optional heading to insert after

    Returns:
        True if successful, False otherwise
    """
    client = get_client()

    # Ensure path has .md extension
    if not path.endswith('.md'):
        path += '.md'

    endpoint = f"/vault/{path}"

    if heading:
        # Use PATCH to insert at specific heading
        success, data, error = client.patch(
            endpoint,
            json_data={
                "action": "insert",
                "heading": heading,
                "content": content
            }
        )
    else:
        # Use POST to append to end
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Append content to an existing note",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Daily/2025-01-03.md" "- Task completed"
  %(prog)s "Projects/notes.md" "New findings" --heading "## Research"
        """
    )

    parser.add_argument(
        "path",
        help="Note path relative to vault root (e.g., 'Daily/2025-01-03.md')"
    )
    parser.add_argument(
        "content",
        help="Content to append"
    )
    parser.add_argument(
        "--heading",
        help="Heading to insert after (uses PATCH for targeted insertion)"
    )

    args = parser.parse_args()

    # Append content
    success = append_to_note(args.path, args.content, args.heading)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
