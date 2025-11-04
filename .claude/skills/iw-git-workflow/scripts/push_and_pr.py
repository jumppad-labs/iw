#!/usr/bin/env python3
"""
Push current branch and optionally create pull request.

Usage:
    python3 push_and_pr.py --plan-path .docs/issues/123 [--create-pr] [--base-branch main]
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

def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
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

def push_branch(repo_root: Path, branch_name: str) -> tuple[bool, str]:
    """Push branch to remote with upstream tracking."""
    returncode, stdout, stderr = run_git_command(
        ["git", "push", "-u", "origin", branch_name],
        repo_root
    )

    if returncode != 0:
        return False, f"Failed to push branch: {stderr}"

    return True, ""

def create_pr(
    repo_root: Path,
    branch_name: str,
    plan_path: Path | None,
    base_branch: str
) -> tuple[bool, str, str]:
    """Create PR using iw-github-pr-creator skill."""
    # Find iw-github-pr-creator script
    script_path = Path(__file__).parent.parent.parent / "iw-github-pr-creator" / "scripts" / "create_pr.py"

    if not script_path.exists():
        return False, "", "iw-github-pr-creator script not found - ensure skill is installed"

    cmd = [
        "python3",
        str(script_path),
        "--branch", branch_name,
        "--base", base_branch,
        "--directory", str(repo_root)
    ]

    if plan_path:
        cmd.extend(["--plan-path", str(plan_path)])

    returncode, stdout, stderr = run_command(cmd, repo_root)

    if returncode != 0:
        return False, "", f"Failed to create PR: {stderr}"

    try:
        result = json.loads(stdout)
        pr_url = result.get("url", "")
        return True, pr_url, ""
    except json.JSONDecodeError:
        return False, "", "Failed to parse PR creation result"

def main():
    parser = argparse.ArgumentParser(description="Push branch and create PR")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    parser.add_argument("--create-pr", action="store_true", help="Create pull request")
    parser.add_argument("--base-branch", default="main", help="Base branch for PR")
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

    # Get current branch
    branch_name = get_current_branch(repo_root)
    if not branch_name:
        print(json.dumps({
            "success": False,
            "error": "Could not determine current branch"
        }))
        sys.exit(1)

    result = {
        "success": True,
        "branch_name": branch_name
    }

    # Push branch
    success, error = push_branch(repo_root, branch_name)
    if not success:
        print(json.dumps({
            "success": False,
            "error": error
        }))
        sys.exit(1)

    result["pushed"] = True

    # Create PR if requested
    if args.create_pr:
        success, pr_url, error = create_pr(repo_root, branch_name, plan_path, args.base_branch)
        if success:
            result["pr_created"] = True
            result["pr_url"] = pr_url
        else:
            # PR creation failure is not fatal
            result["pr_created"] = False
            result["pr_error"] = error

    print(json.dumps(result))
    sys.exit(0)

if __name__ == "__main__":
    main()
