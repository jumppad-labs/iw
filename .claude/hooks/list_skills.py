#!/usr/bin/env python3
"""
Hook script to list available skills for Claude Code.

This script is executed at session start to remind Claude of available skills.
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import re
from pathlib import Path


def get_git_root():
    """
    Get git repository root directory.

    Returns:
        Path or None: Root directory if in git repo, None otherwise
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def extract_description(skill_md: Path) -> str:
    """
    Extract description from SKILL.md YAML frontmatter.

    Args:
        skill_md: Path to SKILL.md file

    Returns:
        str: Description or empty string if not found
    """
    try:
        content = skill_md.read_text(encoding='utf-8')
    except (IOError, UnicodeDecodeError):
        return ""

    # Parse YAML frontmatter
    # Format: --- at start, description: value, --- at end
    in_frontmatter = False
    in_description = False
    description_lines = []

    for line in content.split('\n'):
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            if not in_frontmatter and description_lines:
                # End of frontmatter, we have description
                break
            continue

        if not in_frontmatter:
            continue

        # Check if line starts a new field
        if re.match(r'^[a-z].*:', line):
            in_description = line.strip().startswith('description:')
            if in_description:
                # Extract value after "description:"
                value = line.split(':', 1)[1].strip()
                if value:
                    description_lines.append(value)
        elif in_description:
            # Continuation of description (multi-line)
            description_lines.append(line.strip())

    return ' '.join(description_lines)


def main():
    """List all available skills."""
    # Find skill directories
    skill_dirs = []

    # Check project-level skills (if in git repo)
    git_root = get_git_root()
    if git_root:
        project_skills = git_root / ".claude" / "skills"
        if project_skills.is_dir():
            skill_dirs.append(project_skills)

    # Check user-level skills
    user_skills = Path.home() / ".claude" / "skills"
    if user_skills.is_dir():
        skill_dirs.append(user_skills)

    # Exit if no skill directories found
    if not skill_dirs:
        return

    # Count total skills
    skill_count = 0
    for skills_dir in skill_dirs:
        skill_count += sum(1 for _ in skills_dir.iterdir() if _.is_dir())

    if skill_count == 0:
        return

    # Output header
    print(f"Available Skills ({skill_count}):")
    print()

    # List each skill
    for skills_dir in skill_dirs:
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_name = skill_dir.name
            skill_md = skill_dir / "SKILL.md"

            if skill_md.exists():
                description = extract_description(skill_md)
                if description:
                    print(f"- {skill_name}: {description}")
                else:
                    print(f"- {skill_name}")
            else:
                print(f"- {skill_name} (no SKILL.md found)")

    print()


if __name__ == "__main__":
    main()
