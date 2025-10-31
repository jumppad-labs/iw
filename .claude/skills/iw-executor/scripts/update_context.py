#!/usr/bin/env python3
"""
Update context.md with new findings and discoveries.

Appends new content to specified sections in context.md.
Creates section if it doesn't exist.

Usage:
    python3 update_context.py <context-file> --section <section-name> --content <new-content>

Examples:
    python3 update_context.py context.md --section "Key Findings" --content "Database uses connection pooling"
    python3 update_context.py context.md --section "Implementation Notes" --content "Error handling uses custom wrapper"
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


def find_section(content: str, section_name: str) -> tuple[int, int]:
    """
    Find section in markdown content.

    Returns:
        Tuple of (start_line, end_line) or (-1, -1) if not found
    """
    lines = content.split("\n")
    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        # Look for section header (## or ###)
        if re.match(r"^###+\s+", line):
            section_title = re.sub(r"^###+\s+", "", line).strip()

            if section_title.lower() == section_name.lower():
                start_line = i
                # Find end of section (next header or end of file)
                for j in range(i + 1, len(lines)):
                    if re.match(r"^###+\s+", lines[j]):
                        end_line = j
                        break
                if end_line == -1:
                    end_line = len(lines)
                break

    return start_line, end_line


def add_to_section(
    content: str,
    section_name: str,
    new_content: str,
    add_timestamp: bool = True
) -> str:
    """
    Add content to a section in the markdown file.

    If section doesn't exist, creates it at the end.
    """
    lines = content.split("\n")
    start_line, end_line = find_section(content, section_name)

    # Prepare the content to add
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if add_timestamp:
        content_to_add = f"- [{timestamp}] {new_content}"
    else:
        content_to_add = f"- {new_content}"

    if start_line == -1:
        # Section doesn't exist, create it at the end
        if not content.endswith("\n\n"):
            lines.append("")
        lines.append(f"## {section_name}")
        lines.append("")
        lines.append(content_to_add)
        lines.append("")
    else:
        # Section exists, add to end of section
        # Insert before the next section or end of file
        insert_position = end_line
        lines.insert(insert_position, content_to_add)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Update context.md with new findings"
    )
    parser.add_argument(
        "context_file",
        type=Path,
        help="Path to the context.md file"
    )
    parser.add_argument(
        "--section",
        type=str,
        required=True,
        help="Section name to add content to"
    )
    parser.add_argument(
        "--content",
        type=str,
        required=True,
        help="Content to add to the section"
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Don't add timestamp to the entry"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without making changes"
    )

    args = parser.parse_args()

    if not args.context_file.exists():
        print(f"Error: Context file not found: {args.context_file}", file=sys.stderr)
        sys.exit(1)

    # Read current content
    content = args.context_file.read_text()

    # Add content to section
    updated_content = add_to_section(
        content,
        args.section,
        args.content,
        add_timestamp=not args.no_timestamp
    )

    # Write updated content (unless dry run)
    if args.dry_run:
        print("DRY RUN - Would add to context:")
        print(f"Section: {args.section}")
        print(f"Content: {args.content}")
    else:
        args.context_file.write_text(updated_content)
        print(f"✓ Added to '{args.section}': {args.content}")


if __name__ == "__main__":
    main()
