#!/usr/bin/env python3
"""Add a finding to the research findings file."""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def add_finding(research_name: str, theme: str, finding: str, source_ref: str):
    """Add finding to findings.md under specified theme."""
    research_dir = Path(".docs/research") / research_name
    findings_file = research_dir / "findings.md"

    # Create findings.md if doesn't exist
    if not findings_file.exists():
        with open(findings_file, 'w') as f:
            f.write(f"# Research Findings: {research_name}\n\n")
            f.write("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n")

    # Read existing content
    with open(findings_file, 'r') as f:
        content = f.read()

    # Update last updated timestamp
    content = content.split('\n')
    for i, line in enumerate(content):
        if line.startswith('**Last Updated**:'):
            content[i] = f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            break
    content = '\n'.join(content)

    # Check if theme exists
    theme_header = f"## {theme}"
    if theme_header not in content:
        # Add new theme section at the end
        content = content.rstrip() + f"\n\n{theme_header}\n\n"

    # Find theme section and append finding
    lines = content.split('\n')
    new_lines = []
    in_theme = False
    added = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.strip() == theme_header:
            in_theme = True
        elif in_theme and line.startswith('## ') and line.strip() != theme_header:
            # Reached next theme, insert before it
            new_lines.insert(-1, f"- {finding} *(Source: {source_ref})*")
            new_lines.insert(-1, "")
            added = True
            in_theme = False

    if not added and in_theme:
        # Add at end of file
        new_lines.append(f"- {finding} *(Source: {source_ref})*")

    # Write back
    with open(findings_file, 'w') as f:
        f.write('\n'.join(new_lines))

    print(f"✅ Finding added to theme '{theme}' in {findings_file}")


def main():
    parser = argparse.ArgumentParser(description="Add finding to research")
    parser.add_argument("research_name", help="Research project name")
    parser.add_argument("theme", help="Theme/category for this finding")
    parser.add_argument("finding", help="The finding or insight")
    parser.add_argument("source_ref", help="Source reference (e.g., 'Paper #1', 'GitHub repo X')")

    args = parser.parse_args()
    add_finding(args.research_name, args.theme, args.finding, args.source_ref)
    return 0


if __name__ == "__main__":
    sys.exit(main())
