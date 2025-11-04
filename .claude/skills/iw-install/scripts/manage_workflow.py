#!/usr/bin/env python3
"""
Implementation Workflow Installer Script

Manages installation, updates, and removal of the Implementation Workflow
for Claude Code. Uses git clone to fetch files from GitHub.

Usage:
    python3 manage_workflow.py install --location project
    python3 manage_workflow.py update --location user
    python3 manage_workflow.py uninstall --location project
    python3 manage_workflow.py verify --location project
    python3 manage_workflow.py list --location project
"""

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# GitHub repository configuration
GITHUB_USER = "jumppad-labs"
GITHUB_REPO = "iw"
GITHUB_BRANCH = "main"
# Note: No longer need GITHUB_API_BASE or GITHUB_RAW_BASE (git clone instead)

# Workflow components to install
SKILLS = [
    "iw-planner",
    "iw-executor",
    "iw-workflow",
    "iw-learnings",
    "iw-init",
    "iw-github-issue-reader",
    "iw-github-pr-creator",
    "iw-git-workflow",
    "go-dev-guidelines",
    "skill-creator",
    "iw-install",  # Self-reference
]

COMMANDS = [
    "iw-plan.md",
    "iw-implement.md",
    "iw-help.md",
    "iw-install.md",
]

HOOKS = [
    "load_workflow.sh",
    "list_skills.sh",
]


class WorkflowInstaller:
    """Manages Installation Workflow installation."""

    def __init__(self, location: str = "project", force: bool = True):
        """
        Initialize installer.

        Args:
            location: "project" for .claude/ or "user" for ~/.claude/
            force: Force overwrite existing files
        """
        self.location = location
        self.force = force
        self.target_dir = self._get_target_dir()
        self.installed_files: List[Path] = []
        self.failed_files: List[Tuple[str, str]] = []

    def _get_target_dir(self) -> Path:
        """Get target installation directory."""
        if self.location == "user":
            return Path.home() / ".claude"
        else:
            return Path.cwd() / ".claude"

    def _clone_repository(self) -> Optional[Path]:
        """
        Clone the workflow repository to a temporary directory.

        Uses git clone with --depth 1 for a shallow clone (faster, less disk space).

        Returns:
            Path to temporary clone directory, or None on failure
        """
        import tempfile
        import shutil

        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="iw-install-"))
        repo_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}.git"

        try:
            # Perform shallow clone (only latest commit)
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", GITHUB_BRANCH, repo_url, str(temp_dir)],
                check=True,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout for clone operation
            )

            # Verify .claude directory exists in clone
            claude_dir = temp_dir / ".claude"
            if not claude_dir.exists():
                print(f"  Error: .claude directory not found in cloned repository")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None

            return temp_dir

        except subprocess.TimeoutExpired:
            print(f"  Error: Git clone timed out after 60 seconds")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        except subprocess.CalledProcessError as e:
            print(f"  Error: Git clone failed: {e.stderr}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        except FileNotFoundError:
            print(f"  Error: git command not found. Please install git:")
            print(f"    Ubuntu/Debian: sudo apt-get install git")
            print(f"    macOS: brew install git")
            print(f"    Windows: https://git-scm.com/download/win")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        except Exception as e:
            print(f"  Error: Unexpected error during clone: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

    def _copy_files_from_clone(self, clone_dir: Path) -> bool:
        """
        Copy .claude directory contents from cloned repo to target location.

        Args:
            clone_dir: Path to temporary clone directory

        Returns:
            True if successful, False otherwise
        """
        import shutil

        source_claude = clone_dir / ".claude"

        if not source_claude.exists():
            print("  Error: .claude directory not found in clone")
            return False

        try:
            # Create target directories if they don't exist
            self.target_dir.mkdir(parents=True, exist_ok=True)

            # Copy each subdirectory (skills, commands, hooks)
            for subdir_name in ["skills", "commands", "hooks"]:
                source_subdir = source_claude / subdir_name

                if not source_subdir.exists():
                    print(f"  Warning: {subdir_name}/ not found in clone, skipping")
                    continue

                target_subdir = self.target_dir / subdir_name

                # Copy entire subdirectory
                # dirs_exist_ok=True allows overwriting existing files
                shutil.copytree(source_subdir, target_subdir, dirs_exist_ok=True)

                # Count files copied for reporting
                file_count = sum(1 for _ in target_subdir.rglob('*') if _.is_file())
                self.installed_files.extend(target_subdir.rglob('*'))
                print(f"  ✓ Copied {file_count} files to {subdir_name}/")

            # Make hook scripts executable
            hooks_dir = self.target_dir / "hooks"
            if hooks_dir.exists():
                for hook_file in hooks_dir.glob("*.sh"):
                    self._make_executable(hook_file)

            return True

        except PermissionError as e:
            print(f"  Error: Permission denied when copying files: {e}")
            print(f"  Check that you have write permissions to {self.target_dir}")
            return False

        except OSError as e:
            print(f"  Error: Failed to copy files: {e}")
            return False

        except Exception as e:
            print(f"  Error: Unexpected error during copy: {e}")
            return False

    def _cleanup_clone(self, clone_dir: Path):
        """
        Remove temporary clone directory.

        Args:
            clone_dir: Path to temporary clone to remove
        """
        import shutil

        try:
            if clone_dir and clone_dir.exists():
                shutil.rmtree(clone_dir)
        except Exception as e:
            # Non-fatal error, just warn
            print(f"  Warning: Failed to clean up temporary directory {clone_dir}: {e}")
            print(f"  You may want to manually remove it later")

    def _make_executable(self, file_path: Path):
        """Make a file executable."""
        try:
            current = file_path.stat().st_mode
            file_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError as e:
            print(f"  Warning: Could not make {file_path} executable: {e}")

    def install(self) -> bool:
        """
        Install the Implementation Workflow.

        Clones the repository and copies files to target location.

        Returns:
            True if successful
        """
        print(f"Installing Implementation Workflow to: {self.target_dir}")
        print()

        # Step 1: Clone repository
        print("Cloning workflow repository...")
        clone_dir = self._clone_repository()

        if clone_dir is None:
            print()
            print("=" * 50)
            print("Installation Failed!")
            print("=" * 50)
            print()
            print("Could not clone repository. Check:")
            print("  - Git is installed: git --version")
            print("  - Network connection is working")
            print("  - GitHub is accessible: ping github.com")
            print()
            return False

        print(f"  ✓ Repository cloned to temporary directory")
        print()

        # Step 2: Copy files from clone to target
        print(f"Copying workflow files to {self.target_dir}...")
        success = self._copy_files_from_clone(clone_dir)

        # Step 3: Cleanup temporary clone
        print()
        print("Cleaning up temporary files...")
        self._cleanup_clone(clone_dir)
        print("  ✓ Temporary files removed")

        if not success:
            print()
            print("=" * 50)
            print("Installation Failed!")
            print("=" * 50)
            print()
            print("Failed to copy files. Check:")
            print(f"  - Write permissions: ls -ld {self.target_dir}")
            print(f"  - Available disk space: df -h {self.target_dir}")
            print()
            return False

        # Step 4: Display success summary
        print()
        print("=" * 50)
        print("Installation Complete!")
        print("=" * 50)
        print()
        print(f"Location: {self.target_dir}")
        print(f"Installed: {len(SKILLS)} skills, {len(COMMANDS)} commands, {len(HOOKS)} hooks")
        print(f"Files: {len(self.installed_files)}")
        print()
        print("Next steps:")
        print("  1. Restart Claude Code or start new session")
        print("  2. Run /iw-help to see workflow guidance")
        print("  3. Use /iw-plan to create your first plan")
        print()

        return True

    def update(self) -> bool:
        """
        Update existing installation.

        Returns:
            True if successful
        """
        if not self.target_dir.exists():
            print(f"Error: No installation found at {self.target_dir}")
            print("Run 'install' first.")
            return False

        print(f"Updating Implementation Workflow at: {self.target_dir}")
        print()
        print("Fetching latest version from GitHub...")
        print()

        # Perform installation (will overwrite existing files)
        return self.install()

    def uninstall(self) -> bool:
        """
        Uninstall the Implementation Workflow.

        Returns:
            True if successful
        """
        if not self.target_dir.exists():
            print(f"No installation found at {self.target_dir}")
            return True

        print(f"Uninstalling Implementation Workflow from: {self.target_dir}")
        print()

        removed_count = 0

        # Remove skills
        print("Removing skills...")
        skills_dir = self.target_dir / "skills"
        if skills_dir.exists():
            for skill in SKILLS:
                skill_dir = skills_dir / skill
                if skill_dir.exists():
                    try:
                        # Remove directory recursively
                        import shutil
                        shutil.rmtree(skill_dir)
                        print(f"  ✓ Removed {skill}")
                        removed_count += 1
                    except OSError as e:
                        print(f"  Error removing {skill}: {e}")
        print()

        # Remove commands
        print("Removing commands...")
        commands_dir = self.target_dir / "commands"
        if commands_dir.exists():
            for command in COMMANDS:
                command_file = commands_dir / command
                if command_file.exists():
                    try:
                        command_file.unlink()
                        print(f"  ✓ Removed {command}")
                        removed_count += 1
                    except OSError as e:
                        print(f"  Error removing {command}: {e}")
        print()

        # Remove hooks
        print("Removing hooks...")
        hooks_dir = self.target_dir / "hooks"
        if hooks_dir.exists():
            for hook in HOOKS:
                hook_file = hooks_dir / hook
                if hook_file.exists():
                    try:
                        hook_file.unlink()
                        print(f"  ✓ Removed {hook}")
                        removed_count += 1
                    except OSError as e:
                        print(f"  Error removing {hook}: {e}")
        print()

        print("=" * 50)
        print("Uninstall Complete!")
        print("=" * 50)
        print()
        print(f"Removed {removed_count} component(s)")
        print(f"Location: {self.target_dir}")
        print()
        print("Note: Custom skills and commands were preserved.")
        print()

        return True

    def verify(self) -> bool:
        """
        Verify installation integrity.

        Returns:
            True if installation is valid
        """
        print(f"Verifying installation at: {self.target_dir}")
        print()

        if not self.target_dir.exists():
            print("✗ Installation directory does not exist")
            return False

        missing = []
        present = []

        # Check skills
        print("Checking skills...")
        for skill in SKILLS:
            skill_md = self.target_dir / "skills" / skill / "SKILL.md"
            if skill_md.exists():
                present.append(f"skills/{skill}/SKILL.md")
                print(f"  ✓ {skill}")
            else:
                missing.append(f"skills/{skill}/SKILL.md")
                print(f"  ✗ {skill} (SKILL.md missing)")
        print()

        # Check commands
        print("Checking commands...")
        for command in COMMANDS:
            command_file = self.target_dir / "commands" / command
            if command_file.exists():
                present.append(f"commands/{command}")
                print(f"  ✓ {command}")
            else:
                missing.append(f"commands/{command}")
                print(f"  ✗ {command}")
        print()

        # Check hooks
        print("Checking hooks...")
        for hook in HOOKS:
            hook_file = self.target_dir / "hooks" / hook
            if hook_file.exists():
                present.append(f"hooks/{hook}")
                print(f"  ✓ {hook}")
            else:
                missing.append(f"hooks/{hook}")
                print(f"  ✗ {hook}")
        print()

        # Summary
        print("=" * 50)
        if missing:
            print(f"Verification Failed: {len(missing)} component(s) missing")
            print("=" * 50)
            print()
            print("Missing components:")
            for item in missing:
                print(f"  - {item}")
            print()
            print("Run 'update' to repair installation.")
            return False
        else:
            print("Verification Passed!")
            print("=" * 50)
            print()
            print(f"All {len(present)} components present and accounted for.")
            return True

    def list_installed(self) -> bool:
        """
        List installed components.

        Returns:
            True if installation exists
        """
        if not self.target_dir.exists():
            print(f"No installation found at {self.target_dir}")
            return False

        print(f"Implementation Workflow at: {self.target_dir}")
        print()

        # List skills
        print("Skills:")
        skills_dir = self.target_dir / "skills"
        if skills_dir.exists():
            for skill in SKILLS:
                skill_dir = skills_dir / skill
                if skill_dir.exists():
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        print(f"  ✓ {skill}")
                    else:
                        print(f"  ? {skill} (SKILL.md missing)")
                else:
                    print(f"  ✗ {skill} (not installed)")
        print()

        # List commands
        print("Commands:")
        commands_dir = self.target_dir / "commands"
        if commands_dir.exists():
            for command in COMMANDS:
                command_file = commands_dir / command
                if command_file.exists():
                    print(f"  ✓ /{command.replace('.md', '')}")
                else:
                    print(f"  ✗ /{command.replace('.md', '')} (not installed)")
        print()

        # List hooks
        print("Hooks:")
        hooks_dir = self.target_dir / "hooks"
        if hooks_dir.exists():
            for hook in HOOKS:
                hook_file = hooks_dir / hook
                if hook_file.exists():
                    print(f"  ✓ {hook}")
                else:
                    print(f"  ✗ {hook} (not installed)")
        print()

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Implementation Workflow installation"
    )
    parser.add_argument(
        "action",
        choices=["install", "update", "uninstall", "verify", "list"],
        help="Action to perform",
    )
    parser.add_argument(
        "--location",
        choices=["project", "user"],
        default="project",
        help="Installation location (default: project)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Force overwrite existing files (default: True)",
    )

    args = parser.parse_args()

    installer = WorkflowInstaller(location=args.location, force=args.force)

    actions = {
        "install": installer.install,
        "update": installer.update,
        "uninstall": installer.uninstall,
        "verify": installer.verify,
        "list": installer.list_installed,
    }

    try:
        success = actions[args.action]()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
