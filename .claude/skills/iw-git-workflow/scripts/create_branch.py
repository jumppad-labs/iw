#!/usr/bin/env python3
"""
Create a new git branch for implementation work.

Usage:
    python3 create_branch.py --plan-path .docs/issues/123 [--base-branch main]
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
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_repo_root(directory: Path) -> Path | None:
    """Get the git repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())

def get_current_branch(repo_root: Path) -> str | None:
    """Get current branch name."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        repo_root
    )
    if returncode != 0:
        return None
    return stdout.strip()

def check_branch_exists(repo_root: Path, branch_name: str) -> bool:
    """Check if branch already exists."""
    returncode, _, _ = run_git_command(
        ["git", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
        repo_root
    )
    return returncode == 0

def create_branch(
    repo_root: Path,
    branch_name: str,
    base_branch: str
) -> tuple[bool, str]:
    """
    Create new branch from base branch.

    Returns:
        Tuple of (success, error_message)
    """
    # Check if branch already exists
    if check_branch_exists(repo_root, branch_name):
        return False, f"Branch '{branch_name}' already exists"

    # Create and checkout new branch
    returncode, stdout, stderr = run_git_command(
        ["git", "checkout", "-b", branch_name, base_branch],
        repo_root
    )

    if returncode != 0:
        return False, f"Failed to create branch: {stderr}"

    return True, ""

def main():
    parser = argparse.ArgumentParser(description="Create implementation branch")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    parser.add_argument("--base-branch", default="main", help="Base branch to branch from")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "success": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Import get_branch_name helper
    sys.path.insert(0, str(Path(__file__).parent))
    from get_branch_name import generate_branch_name

    # Generate branch name from plan
    branch_name = generate_branch_name(plan_path)

    # Get current branch
    current_branch = get_current_branch(repo_root)

    # Create the branch
    success, error = create_branch(repo_root, branch_name, args.base_branch)

    if success:
        print(json.dumps({
            "success": True,
            "branch_name": branch_name,
            "base_branch": args.base_branch,
            "previous_branch": current_branch,
            "repo_root": str(repo_root)
        }))
        sys.exit(0)
    else:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
