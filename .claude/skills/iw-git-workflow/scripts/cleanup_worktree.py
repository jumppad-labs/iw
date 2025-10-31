#!/usr/bin/env python3
"""
Cleanup worktree after implementation complete.

Pushes branch to remote, optionally creates PR using iw-github-pr-creator skill,
and removes the worktree. Returns main repository to clean state.

Usage:
    python3 cleanup_worktree.py --worktree-path <path> [--create-pr] [--no-push] [--plan-path <path>]

Output:
    JSON with push status, PR URL (if created), and cleanup status
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


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_branch_name(worktree_path: Path) -> str | None:
    """Get the current branch name in worktree."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        worktree_path
    )
    if returncode != 0:
        return None
    return stdout.strip()


def get_repo_root(worktree_path: Path) -> Path | None:
    """Get the main repository root."""
    returncode, stdout, _ = run_git_command(
        ["git", "rev-parse", "--show-toplevel"],
        worktree_path
    )
    if returncode != 0:
        return None
    return Path(stdout.strip())


def push_branch(worktree_path: Path, branch_name: str) -> tuple[bool, str]:
    """
    Push branch to remote.

    Returns:
        Tuple of (success, error_message)
    """
    # Push with upstream tracking
    returncode, stdout, stderr = run_git_command(
        ["git", "push", "-u", "origin", branch_name],
        worktree_path
    )

    if returncode != 0:
        return False, f"Failed to push branch: {stderr}"

    return True, ""


def find_plan_path(worktree_path: Path) -> Path | None:
    """Find plan directory in worktree."""
    docs_dir = worktree_path / ".docs"
    if not docs_dir.exists():
        return None

    # Look for plan files
    plan_files = list(docs_dir.glob("**/*-plan.md"))
    if not plan_files:
        return None

    # Return the directory containing the plan file
    return plan_files[0].parent


def create_pr_with_github_pr_creator(
    worktree_path: Path,
    branch_name: str,
    plan_path: Path | None,
    base_branch: str = "main"
) -> tuple[bool, str, str]:
    """
    Create PR using iw-github-pr-creator skill.

    Returns:
        Tuple of (success, pr_url, error_message)
    """
    # Find iw-github-pr-creator script
    # Assume it's in sibling skills directory
    script_path = Path(__file__).parent.parent.parent / "iw-github-pr-creator" / "scripts" / "create_pr.py"

    if not script_path.exists():
        return False, "", "iw-github-pr-creator script not found - ensure iw-github-pr-creator skill is installed"

    cmd = [
        "python3",
        str(script_path),
        "--branch", branch_name,
        "--base", base_branch,
        "--directory", str(worktree_path)
    ]

    # Add plan path if available
    if plan_path:
        cmd.extend(["--plan-path", str(plan_path)])

    returncode, stdout, stderr = run_command(cmd, worktree_path)

    if returncode != 0:
        return False, "", f"Failed to create PR: {stderr}"

    # Parse JSON output to get PR URL
    try:
        result = json.loads(stdout)
        pr_url = result.get("url", "")
        return True, pr_url, ""
    except json.JSONDecodeError:
        return False, "", "Failed to parse PR creation result"


def remove_worktree(repo_root: Path, worktree_path: Path) -> tuple[bool, str]:
    """
    Remove the worktree.

    Returns:
        Tuple of (success, error_message)
    """
    # Remove worktree using git worktree remove
    returncode, stdout, stderr = run_git_command(
        ["git", "worktree", "remove", str(worktree_path)],
        repo_root
    )

    if returncode != 0:
        # Try force remove if normal remove fails
        returncode, stdout, stderr = run_git_command(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            repo_root
        )
        if returncode != 0:
            return False, f"Failed to remove worktree: {stderr}"

    return True, ""


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup worktree after implementation"
    )
    parser.add_argument(
        "--worktree-path",
        type=Path,
        required=True,
        help="Path to the worktree to cleanup"
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Create pull request before cleanup (uses iw-github-pr-creator skill)"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        help="Path to plan directory (optional, will auto-detect if not provided)"
    )
    parser.add_argument(
        "--base-branch",
        type=str,
        default="main",
        help="Base branch for PR (default: main)"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Skip pushing to remote (for testing)"
    )

    args = parser.parse_args()

    if not args.worktree_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Worktree path not found: {args.worktree_path}"
        }), file=sys.stderr)
        sys.exit(1)

    # Get branch name
    branch_name = get_branch_name(args.worktree_path)
    if not branch_name:
        print(json.dumps({
            "success": False,
            "error": "Failed to get branch name from worktree"
        }), file=sys.stderr)
        sys.exit(1)

    # Get repo root
    repo_root = get_repo_root(args.worktree_path)
    if not repo_root:
        print(json.dumps({
            "success": False,
            "error": "Failed to find repository root"
        }), file=sys.stderr)
        sys.exit(1)

    result = {
        "success": True,
        "branch_name": branch_name,
        "worktree_path": str(args.worktree_path),
        "pushed": False,
        "pr_created": False,
        "pr_url": "",
        "worktree_removed": False
    }

    # Push branch
    if not args.no_push:
        success, error = push_branch(args.worktree_path, branch_name)
        if not success:
            result["success"] = False
            result["error"] = error
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)
        result["pushed"] = True

    # Create PR if requested
    if args.create_pr:
        # Find plan path if not provided
        plan_path = args.plan_path
        if not plan_path:
            plan_path = find_plan_path(args.worktree_path)

        # Use iw-github-pr-creator skill to create PR
        success, pr_url, error = create_pr_with_github_pr_creator(
            args.worktree_path,
            branch_name,
            plan_path,
            args.base_branch
        )

        if success:
            result["pr_created"] = True
            result["pr_url"] = pr_url
        else:
            # PR creation failure is not fatal, continue with cleanup
            result["pr_error"] = error

    # Remove worktree
    success, error = remove_worktree(repo_root, args.worktree_path)
    if not success:
        result["success"] = False
        result["error"] = error
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    result["worktree_removed"] = True

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
