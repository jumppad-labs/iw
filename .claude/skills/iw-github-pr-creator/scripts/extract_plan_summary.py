#!/usr/bin/env python3
"""
Extract summary information from implementation plan files.

Parses plan files to extract title, phases, issue number, and testing
instructions for use in PR creation.

Usage:
    python3 extract_plan_summary.py --plan-path <plan-directory>

Output:
    JSON with plan summary information
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_issue_number(plan_path: Path) -> int | None:
    """Extract issue number from plan path or files."""
    # Check if path contains 'issues/<number>/'
    match = re.search(r'/issues/(\d+)/', str(plan_path))
    if match:
        return int(match.group(1))

    # Check for files named like '<number>-plan.md'
    for file_path in plan_path.glob("*-plan.md"):
        match = re.match(r'(\d+)-', file_path.name)
        if match:
            return int(match.group(1))

    return None


def extract_title(plan_file: Path) -> str:
    """Extract plan title from first heading."""
    content = plan_file.read_text()

    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()

    return "Implementation"


def extract_phases(plan_file: Path) -> list[dict]:
    """Extract phase names and numbers from plan file."""
    content = plan_file.read_text()
    phases = []

    phase_pattern = re.compile(r"^###+\s+Phase\s+(\d+):\s+(.+)$")

    for line in content.split("\n"):
        match = phase_pattern.match(line)
        if match:
            phase_num = int(match.group(1))
            phase_name = match.group(2).strip()
            phases.append({
                "number": phase_num,
                "name": phase_name
            })

    return phases


def extract_testing_steps(plan_file: Path) -> dict:
    """Extract automated and manual testing steps."""
    content = plan_file.read_text()
    lines = content.split("\n")

    automated = []
    manual = []

    in_automated = False
    in_manual = False

    for line in lines:
        # Check for testing section headers
        line_lower = line.lower()
        if "automated verification" in line_lower or "automated testing" in line_lower:
            in_automated = True
            in_manual = False
            continue
        elif "manual verification" in line_lower or "manual testing" in line_lower:
            in_manual = True
            in_automated = False
            continue
        elif line.startswith("#"):
            # New section, reset flags
            in_automated = False
            in_manual = False
            continue

        # Extract list items
        if line.strip().startswith("-") or line.strip().startswith("*"):
            item = line.strip()[1:].strip()
            # Remove checkbox markers if present
            item = re.sub(r'^\[ \]\s*', '', item)
            item = re.sub(r'^\[x\]\s*', '', item)

            if in_automated and item:
                automated.append(item)
            elif in_manual and item:
                manual.append(item)

    return {
        "automated": automated,
        "manual": manual
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract summary from implementation plan files"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        required=True,
        help="Path to the plan directory"
    )

    args = parser.parse_args()

    if not args.plan_path.exists():
        print(json.dumps({
            "error": f"Plan directory not found: {args.plan_path}"
        }), file=sys.stderr)
        sys.exit(1)

    # Find plan file
    plan_files = list(args.plan_path.glob("*-plan.md"))
    if not plan_files:
        print(json.dumps({
            "error": f"No *-plan.md file found in {args.plan_path}"
        }), file=sys.stderr)
        sys.exit(1)

    plan_file = plan_files[0]

    # Extract information
    title = extract_title(plan_file)
    phases = extract_phases(plan_file)
    issue_number = extract_issue_number(args.plan_path)
    testing = extract_testing_steps(plan_file)

    # Build result
    result = {
        "title": title,
        "phases": phases,
        "issue_number": issue_number,
        "testing": testing,
        "plan_file": str(plan_file.relative_to(args.plan_path.parent))
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
