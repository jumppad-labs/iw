#!/usr/bin/env python3
"""
Implementation Workflow Bootstrap Script

Cross-platform installer for the iw-install skill, which can then
install the full Implementation Workflow.

Supports Windows, macOS, and Linux without requiring bash.

Usage:
    python3 bootstrap.py
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import urllib.request
import urllib.error
from pathlib import Path

# Configuration
REPO_URL = "https://raw.githubusercontent.com/jumppad-labs/iw/main"
SKILL_NAME = "iw-install"


def print_header():
    """Print welcome banner."""
    print("=" * 46)
    print("Implementation Workflow Bootstrap")
    print("=" * 46)
    print()
    print("This script will install the iw-install skill,")
    print("which you can then use to install the full workflow.")
    print()


def get_installation_choice():
    """
    Prompt user for installation location.

    Returns:
        tuple: (install_dir: Path, install_type: str)
    """
    print("Where would you like to install the workflow?")
    print()
    print("1) Project-level (.claude in current directory)")
    print("   - Committed to version control")
    print("   - Shared with team members")
    print("   - Project-specific configuration")
    print()
    print("2) User-level (~/.claude in home directory)")
    print("   - Available in all projects")
    print("   - Personal configuration")
    print("   - Not committed to repos")
    print()

    while True:
        choice = input("Enter choice [1 or 2]: ").strip()

        if choice == "1":
            install_dir = Path.cwd() / ".claude"
            install_type = "project"
            print()
            print(f"Installing to project-level: {install_dir}")
            return install_dir, install_type
        elif choice == "2":
            install_dir = Path.home() / ".claude"
            install_type = "user"
            print()
            print(f"Installing to user-level: {install_dir}")
            return install_dir, install_type
        else:
            print("Invalid choice. Please enter 1 or 2.")


def download_file(url: str, dest_path: Path) -> bool:
    """
    Download a file from URL to destination path.

    Args:
        url: Source URL to download from
        dest_path: Destination file path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()

        # Ensure parent directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        dest_path.write_bytes(content)
        return True

    except urllib.error.URLError as e:
        print(f"  Error: Failed to download {url}")
        print(f"  {e}")
        return False
    except IOError as e:
        print(f"  Error: Failed to write to {dest_path}")
        print(f"  {e}")
        return False


def main():
    """Main bootstrap process."""
    print_header()

    # Get installation location from user
    install_dir, install_type = get_installation_choice()

    print()
    print("Creating directory structure...")

    # Create directory structure
    skill_dir = install_dir / "skills" / SKILL_NAME / "scripts"
    commands_dir = install_dir / "commands"

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        commands_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"  Error: Could not create directories: {e}")
        return 1

    # Download files
    files_to_download = [
        (
            f"{REPO_URL}/.claude/skills/{SKILL_NAME}/SKILL.md",
            install_dir / "skills" / SKILL_NAME / "SKILL.md"
        ),
        (
            f"{REPO_URL}/.claude/skills/{SKILL_NAME}/scripts/manage_workflow.py",
            install_dir / "skills" / SKILL_NAME / "scripts" / "manage_workflow.py"
        ),
        (
            f"{REPO_URL}/.claude/commands/iw-install.md",
            install_dir / "commands" / "iw-install.md"
        ),
    ]

    print("Downloading iw-install skill...")

    for url, dest in files_to_download:
        if not download_file(url, dest):
            print()
            print("=" * 46)
            print("Bootstrap Failed!")
            print("=" * 46)
            print()
            print("Could not download required files. Check:")
            print("  - Internet connection is working")
            print("  - GitHub is accessible")
            print()
            return 1

    print()
    print("=" * 46)
    print("Bootstrap Complete!")
    print("=" * 46)
    print()
    print("The iw-install skill has been installed to:")
    print(f"  {install_dir / 'skills' / SKILL_NAME}")
    print()
    print("Next steps:")
    print()
    print("1. Start or restart Claude Code")
    print()
    print("2. Run the installation command:")
    if install_type == "project":
        print("   /iw-install")
        print()
        print("   This will install the full workflow to your project.")
    else:
        print("   /iw-install --user")
        print()
        print("   This will install the full workflow to ~/.claude/")
    print()
    print("3. Start using the workflow:")
    print("   /iw-help          - Show workflow guidance")
    print("   /iw-plan <task>   - Create implementation plan")
    print()
    print("For more information, see:")
    print("  https://github.com/jumppad-labs/iw")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
