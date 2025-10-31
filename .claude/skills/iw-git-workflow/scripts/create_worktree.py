#!/usr/bin/env python3
"""
Create git worktree for implementation.

Creates a new branch and worktree in the parent directory for isolated
implementation work. Keeps main working directory clean.

Usage:
    python3 create_worktree.py --plan-path <plan-directory> --base-branch <branch>

Output:
    JSON with worktree path, branch name, and status
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


def get_branch_name(plan_path: Path, script_dir: Path) -> str:
    """Get branch name using get_branch_name.py script."""
    result = subprocess.run(
        ["python3", script_dir / "get_branch_name.py", "--plan-path", str(plan_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error generating branch name: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return result.stdout.strip()


def get_repo_root(directory: Path) -> Path:
    """Get the root directory of the git repository."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        directory
    )
    if returncode != 0:
        print(f"Error: Not a git repository: {directory}", file=sys.stderr)
        sys.exit(1)

    return Path(stdout.strip())


def get_repo_name(repo_root: Path) -> str:
    """Get repository name from directory."""
    return repo_root.name


def create_worktree(
    repo_root: Path,
    branch_name: str,
    base_branch: str
) -> tuple[bool, Path, str]:
    """
    Create worktree in parent directory.

    Returns:
        Tuple of (success, worktree_path, error_message)
    """
    repo_name = get_repo_name(repo_root)
    worktree_name = f"{repo_name}-{branch_name}"
    worktree_path = repo_root.parent / worktree_name

    # Check if worktree already exists
    if worktree_path.exists():
        return False, worktree_path, f"Worktree directory already exists: {worktree_path}"

    # Create worktree with new branch
    returncode, stdout, stderr = run_git_command(
        ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
        repo_root
    )

    if returncode != 0:
        return False, worktree_path, f"Failed to create worktree: {stderr}"

    return True, worktree_path, ""


def main():
    parser = argparse.ArgumentParser(
        description="Create git worktree for implementation"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        required=True,
        help="Path to the plan directory"
    )
    parser.add_argument(
        "--base-branch",
        type=str,
        default="main",
        help="Base branch to create worktree from (default: main)"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Repository directory (default: current directory)"
    )

    args = parser.parse_args()

    if not args.plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan directory not found: {args.plan_path}"
        }), file=sys.stderr)
        sys.exit(1)

    # Get repository root
    repo_root = get_repo_root(args.directory)

    # Get branch name
    script_dir = Path(__file__).parent
    branch_name = get_branch_name(args.plan_path, script_dir)

    # Create worktree
    success, worktree_path, error = create_worktree(
        repo_root,
        branch_name,
        args.base_branch
    )

    if success:
        result = {
            "success": True,
            "worktree_path": str(worktree_path),
            "branch_name": branch_name,
            "base_branch": args.base_branch,
            "repo_root": str(repo_root)
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        result = {
            "success": False,
            "error": error,
            "worktree_path": str(worktree_path),
            "branch_name": branch_name
        }
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
