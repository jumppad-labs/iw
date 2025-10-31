#!/usr/bin/env python3
"""
Update task status in tasks.md file.

Marks tasks as completed (or other status) in the task checklist.
Supports pattern matching to find the correct task.

Usage:
    python3 update_task.py <tasks-file> <task-pattern> --status <status>

Examples:
    python3 update_task.py tasks.md "Create user model" --status done
    python3 update_task.py tasks.md "Add tests" --status done
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def find_and_update_task(
    content: str,
    task_pattern: str,
    new_status: str
) -> tuple[str, bool]:
    """
    Find task matching pattern and update its status.

    Args:
        content: Full content of tasks.md
        task_pattern: Pattern to search for in task descriptions
        new_status: New status ('done' or 'pending')

    Returns:
        Tuple of (updated_content, was_found)
    """
    lines = content.split("\n")
    updated_lines = []
    found = False

    # Convert status to checkbox marker
    marker = "x" if new_status == "done" else " "

    for line in lines:
        # Check if this is a task line
        task_match = re.match(r"^(-\s+\[)([ x])(\]\s+.+)$", line)
        if task_match:
            # Check if task description matches pattern
            task_desc = task_match.group(3)[2:]  # Remove "] " prefix
            if task_pattern.lower() in task_desc.lower():
                # Update the status marker
                updated_line = f"{task_match.group(1)}{marker}{task_match.group(3)}"
                updated_lines.append(updated_line)
                found = True
                continue

        # Keep line as is
        updated_lines.append(line)

    return "\n".join(updated_lines), found


def main():
    parser = argparse.ArgumentParser(
        description="Update task status in tasks.md file"
    )
    parser.add_argument(
        "tasks_file",
        type=Path,
        help="Path to the tasks.md file"
    )
    parser.add_argument(
        "task_pattern",
        type=str,
        help="Pattern to search for in task description"
    )
    parser.add_argument(
        "--status",
        type=str,
        choices=["done", "pending"],
        default="done",
        help="New status for the task (default: done)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )

    args = parser.parse_args()

    if not args.tasks_file.exists():
        print(f"Error: Tasks file not found: {args.tasks_file}", file=sys.stderr)
        sys.exit(1)

    # Read current content
    content = args.tasks_file.read_text()

    # Find and update task
    updated_content, found = find_and_update_task(
        content,
        args.task_pattern,
        args.status
    )

    if not found:
        print(f"Warning: No task found matching pattern: '{args.task_pattern}'", file=sys.stderr)
        sys.exit(1)

    # Write updated content (unless dry run)
    if args.dry_run:
        print("DRY RUN - Would update task status")
        print(f"Pattern: {args.task_pattern}")
        print(f"Status: {args.status}")
    else:
        args.tasks_file.write_text(updated_content)
        print(f"✓ Updated task status to '{args.status}': {args.task_pattern}")


if __name__ == "__main__":
    main()
