#!/usr/bin/env python3
"""
Check if git working directory is clean.

Verifies that there are no uncommitted changes, staged files, or untracked files
(except those in .gitignore). Used before starting implementation to ensure safe
state for creating branches.

Usage:
    python3 check_clean.py [--directory <path>]

Returns:
    Exit code 0 if clean, non-zero if dirty
    Outputs JSON with status and list of issues
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_git_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def check_git_status(directory: Path) -> dict:
    """
    Check git status for uncommitted changes and branch information.

    Returns dict with:
        - clean: bool
        - modified: list of modified files
        - staged: list of staged files
        - untracked: list of untracked files
        - current_branch: str (current branch name)
        - is_implementation_branch: bool (true if on issue-* or feature-* branch)
    """
    # Check for modified files
    returncode, stdout, _ = run_git_command(
        ["git", "diff", "--name-only"],
        directory
    )
    modified = [f.strip() for f in stdout.split("\n") if f.strip()]

    # Check for staged files
    returncode, stdout, _ = run_git_command(
        ["git", "diff", "--cached", "--name-only"],
        directory
    )
    staged = [f.strip() for f in stdout.split("\n") if f.strip()]

    # Check for untracked files
    returncode, stdout, _ = run_git_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        directory
    )
    untracked = [f.strip() for f in stdout.split("\n") if f.strip()]

    # Get current branch name
    returncode, branch_stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        directory
    )
    current_branch = branch_stdout.strip() if returncode == 0 else None

    # Detect if on implementation branch (issue-* or feature-*)
    is_implementation_branch = False
    if current_branch:
        is_implementation_branch = (
            current_branch.startswith("issue-") or
            current_branch.startswith("feature-")
        )

    is_clean = len(modified) == 0 and len(staged) == 0 and len(untracked) == 0

    return {
        "clean": is_clean,
        "modified": modified,
        "staged": staged,
        "untracked": untracked,
        "current_branch": current_branch,
        "is_implementation_branch": is_implementation_branch
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check if git working directory is clean"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Directory to check (default: current directory)"
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(json.dumps({
            "error": f"Directory does not exist: {args.directory}"
        }), file=sys.stderr)
        sys.exit(1)

    # Check if directory is a git repository
    returncode, _, _ = run_git_command(
        ["git", "rev-parse", "--git-dir"],
        args.directory
    )
    if returncode != 0:
        print(json.dumps({
            "error": f"Not a git repository: {args.directory}"
        }), file=sys.stderr)
        sys.exit(1)

    # Check git status
    status = check_git_status(args.directory)

    # Output result
    print(json.dumps(status, indent=2))

    # Exit with appropriate code
    sys.exit(0 if status["clean"] else 1)


if __name__ == "__main__":
    main()
