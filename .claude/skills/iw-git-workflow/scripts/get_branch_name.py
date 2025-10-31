#!/usr/bin/env python3
"""
Generate git branch name from plan directory.

Parses plan files to extract issue number or plan name and generates
an appropriate branch name following conventions.

Usage:
    python3 get_branch_name.py --plan-path <plan-directory>

Output:
    Branch name like "issue-123-feature-name" or "feature-plan-name"
"""

import argparse
import re
import sys
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to slug format (lowercase, hyphens)."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


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


def extract_plan_title(plan_path: Path) -> str | None:
    """Extract plan title from plan.md file."""
    # Find plan file
    plan_files = list(plan_path.glob("*-plan.md"))
    if not plan_files:
        return None

    plan_file = plan_files[0]
    content = plan_file.read_text()

    # Look for first # heading
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            return title

    return None


def generate_branch_name(plan_path: Path) -> str:
    """
    Generate branch name from plan directory.

    For issue-based plans: issue-<number>-<title-slug>
    For ad-hoc plans: feature-<plan-name>
    """
    issue_number = extract_issue_number(plan_path)

    if issue_number:
        # Issue-based plan
        title = extract_plan_title(plan_path)
        if title:
            title_slug = slugify(title)
            # Limit title slug to reasonable length
            if len(title_slug) > 40:
                title_slug = title_slug[:40].rstrip('-')
            return f"issue-{issue_number}-{title_slug}"
        else:
            return f"issue-{issue_number}"
    else:
        # Ad-hoc plan - use directory name
        # Get plan name from path (last directory component)
        plan_name = plan_path.name
        plan_slug = slugify(plan_name)
        return f"feature-{plan_slug}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate git branch name from plan directory"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        required=True,
        help="Path to the plan directory"
    )

    args = parser.parse_args()

    if not args.plan_path.exists():
        print(f"Error: Plan directory not found: {args.plan_path}", file=sys.stderr)
        sys.exit(1)

    if not args.plan_path.is_dir():
        print(f"Error: Not a directory: {args.plan_path}", file=sys.stderr)
        sys.exit(1)

    branch_name = generate_branch_name(args.plan_path)
    print(branch_name)


if __name__ == "__main__":
    main()
