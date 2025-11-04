#!/usr/bin/env python3
"""
Commit plan files to the current branch.

Usage:
    python3 commit_plan_files.py --plan-path .docs/issues/123
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

def commit_plan_files(
    repo_root: Path,
    plan_path: Path
) -> tuple[bool, str, str]:
    """
    Commit all plan files in the plan directory.

    Returns:
        Tuple of (success, commit_hash, error_message)
    """
    # Stage all files in plan directory
    returncode, stdout, stderr = run_git_command(
        ["git", "add", str(plan_path)],
        repo_root
    )

    if returncode != 0:
        return False, "", f"Failed to stage files: {stderr}"

    # Check if there are changes to commit
    returncode, stdout, stderr = run_git_command(
        ["git", "diff", "--cached", "--quiet"],
        repo_root
    )

    if returncode == 0:
        # No changes to commit
        return True, "", "No changes to commit"

    # Extract issue number or plan name for commit message
    plan_name = plan_path.name
    if plan_path.parent.name == "issues":
        commit_message = f"Add implementation plan for issue #{plan_name}"
    else:
        commit_message = f"Add implementation plan: {plan_name}"

    # Create commit
    returncode, stdout, stderr = run_git_command(
        ["git", "commit", "-m", commit_message],
        repo_root
    )

    if returncode != 0:
        return False, "", f"Failed to create commit: {stderr}"

    # Get commit hash
    returncode, commit_hash, _ = run_git_command(
        ["git", "rev-parse", "HEAD"],
        repo_root
    )

    return True, commit_hash.strip(), ""

def main():
    parser = argparse.ArgumentParser(description="Commit plan files")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
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

    # Commit plan files
    success, commit_hash, error = commit_plan_files(repo_root, plan_path)

    if success:
        result = {
            "success": True,
            "commit_hash": commit_hash if commit_hash else None,
            "message": "Plan files committed successfully" if commit_hash else "No changes to commit"
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
