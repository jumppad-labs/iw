#!/usr/bin/env python3
"""
Implementation Workflow Installer Script

Manages installation, updates, and removal of the Implementation Workflow
for Claude Code. Fetches files directly from GitHub.

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
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# GitHub repository configuration
GITHUB_USER = "jumppad-labs"
GITHUB_REPO = "iw"
GITHUB_BRANCH = "main"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

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

    def _fetch_url(self, url: str, retry: int = 3) -> Optional[bytes]:
        """
        Fetch content from URL with retry logic.

        Args:
            url: URL to fetch
            retry: Number of retries

        Returns:
            Content bytes or None on failure
        """
        for attempt in range(retry):
            try:
                req = Request(url)
                req.add_header("User-Agent", "implementation-workflow-installer")
                with urlopen(req, timeout=10) as response:
                    return response.read()
            except (URLError, HTTPError) as e:
                if attempt == retry - 1:
                    print(f"  Error fetching {url}: {e}")
                    return None
                print(f"  Retry {attempt + 1}/{retry} for {url}...")
        return None

    def _fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON from URL."""
        content = self._fetch_url(url)
        if content:
            try:
                return json.loads(content.decode("utf-8"))
            except json.JSONDecodeError as e:
                print(f"  Error decoding JSON from {url}: {e}")
        return None

    def _list_directory_contents(self, path: str) -> List[Dict]:
        """
        List contents of a directory in the GitHub repo.

        Args:
            path: Path in repo (e.g., ".claude/skills/iw-planner")

        Returns:
            List of file/directory info dicts
        """
        url = f"{GITHUB_API_BASE}/contents/{path}?ref={GITHUB_BRANCH}"
        result = self._fetch_json(url)
        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result] if isinstance(result, dict) else []

    def _download_file(self, repo_path: str, local_path: Path) -> bool:
        """
        Download a file from GitHub to local path.

        Args:
            repo_path: Path in GitHub repo
            local_path: Local destination path

        Returns:
            True if successful
        """
        url = f"{GITHUB_RAW_BASE}/{repo_path}"
        content = self._fetch_url(url)

        if content is None:
            self.failed_files.append((repo_path, "Failed to download"))
            return False

        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)
            self.installed_files.append(local_path)
            return True
        except IOError as e:
            self.failed_files.append((repo_path, f"Failed to write: {e}"))
            return False

    def _download_directory(self, repo_path: str, local_dir: Path, recursive: bool = True) -> int:
        """
        Download entire directory from GitHub.

        Args:
            repo_path: Directory path in GitHub repo
            local_dir: Local destination directory
            recursive: Whether to recurse into subdirectories

        Returns:
            Number of files downloaded
        """
        contents = self._list_directory_contents(repo_path)
        if not contents:
            return 0

        count = 0
        for item in contents:
            name = item.get("name", "")
            item_type = item.get("type", "")
            item_path = item.get("path", "")

            if item_type == "file":
                local_file = local_dir / name
                if self._download_file(item_path, local_file):
                    count += 1
            elif item_type == "dir" and recursive:
                subdir = local_dir / name
                count += self._download_directory(item_path, subdir, recursive=True)

        return count

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

        Returns:
            True if successful
        """
        print(f"Installing Implementation Workflow to: {self.target_dir}")
        print()

        # Create base directories
        print("Creating directory structure...")
        (self.target_dir / "skills").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "commands").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "hooks").mkdir(parents=True, exist_ok=True)
        print("  ✓ Directory structure created")
        print()

        # Install skills
        print(f"Installing {len(SKILLS)} skills...")
        for skill in SKILLS:
            print(f"  Installing {skill}...")
            skill_dir = self.target_dir / "skills" / skill
            skill_dir.mkdir(parents=True, exist_ok=True)

            # Download SKILL.md
            skill_md_path = f".claude/skills/{skill}/SKILL.md"
            if not self._download_file(skill_md_path, skill_dir / "SKILL.md"):
                print(f"    Warning: Failed to download {skill}/SKILL.md")

            # Download scripts directory if it exists
            scripts_path = f".claude/skills/{skill}/scripts"
            scripts_dir = skill_dir / "scripts"
            scripts_count = self._download_directory(scripts_path, scripts_dir)
            if scripts_count > 0:
                print(f"    ✓ {scripts_count} script(s) installed")

            # Download assets directory if it exists
            assets_path = f".claude/skills/{skill}/assets"
            assets_dir = skill_dir / "assets"
            assets_count = self._download_directory(assets_path, assets_dir)
            if assets_count > 0:
                print(f"    ✓ {assets_count} asset(s) installed")

            # Download references directory if it exists (for go-dev-guidelines)
            refs_path = f".claude/skills/{skill}/references"
            refs_dir = skill_dir / "references"
            refs_count = self._download_directory(refs_path, refs_dir)
            if refs_count > 0:
                print(f"    ✓ {refs_count} reference(s) installed")

        print(f"  ✓ All skills installed")
        print()

        # Install commands
        print(f"Installing {len(COMMANDS)} commands...")
        commands_dir = self.target_dir / "commands"
        for command in COMMANDS:
            command_path = f".claude/commands/{command}"
            if self._download_file(command_path, commands_dir / command):
                print(f"  ✓ {command}")
        print()

        # Install hooks
        print(f"Installing {len(HOOKS)} hooks...")
        hooks_dir = self.target_dir / "hooks"
        for hook in HOOKS:
            hook_path = f".claude/hooks/{hook}"
            local_hook = hooks_dir / hook
            if self._download_file(hook_path, local_hook):
                self._make_executable(local_hook)
                print(f"  ✓ {hook}")
        print()

        # Summary
        print("=" * 50)
        print("Installation Complete!")
        print("=" * 50)
        print()
        print(f"Location: {self.target_dir}")
        print(f"Installed: {len(SKILLS)} skills, {len(COMMANDS)} commands, {len(HOOKS)} hooks")
        print(f"Files: {len(self.installed_files)}")

        if self.failed_files:
            print()
            print(f"Warning: {len(self.failed_files)} file(s) failed to download:")
            for path, error in self.failed_files:
                print(f"  - {path}: {error}")

        print()
        print("Next steps:")
        print("  1. Restart Claude Code or start new session")
        print("  2. Run /iw-help to see workflow guidance")
        print("  3. Use /iw-plan to create your first plan")
        print()

        return len(self.failed_files) == 0

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
