#!/usr/bin/env python3
"""
Check if current branch is valid for implementation work.

Usage:
    python3 check_branch.py --plan-path .docs/issues/123
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

def check_branch_for_plan(
    repo_root: Path,
    plan_path: Path
) -> tuple[bool, str, str]:
    """
    Check if we're on the correct branch for this plan.

    Returns:
        Tuple of (is_valid, current_branch, error_message)
    """
    # Get expected branch name
    sys.path.insert(0, str(Path(__file__).parent))
    from get_branch_name import generate_branch_name

    expected_branch = generate_branch_name(plan_path)

    # Get current branch
    current_branch = get_current_branch(repo_root)
    if not current_branch:
        return False, "", "Could not determine current branch"

    # Check if on expected branch
    if current_branch != expected_branch:
        return False, current_branch, f"Expected to be on branch '{expected_branch}', but currently on '{current_branch}'"

    return True, current_branch, ""

def main():
    parser = argparse.ArgumentParser(description="Check branch validity")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    args = parser.parse_args()

    plan_path = Path(args.plan_path).resolve()
    if not plan_path.exists():
        print(json.dumps({
            "valid": False,
            "error": f"Plan path does not exist: {plan_path}"
        }))
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(plan_path)
    if not repo_root:
        print(json.dumps({
            "valid": False,
            "error": "Not in a git repository"
        }))
        sys.exit(1)

    # Check branch
    is_valid, current_branch, error = check_branch_for_plan(repo_root, plan_path)

    if is_valid:
        print(json.dumps({
            "valid": True,
            "current_branch": current_branch
        }))
        sys.exit(0)
    else:
        print(json.dumps({
            "valid": False,
            "current_branch": current_branch,
            "error": error
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
