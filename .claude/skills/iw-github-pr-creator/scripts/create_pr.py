#!/usr/bin/env python3
"""
Create GitHub pull request using gh CLI.

Creates PRs with proper formatting, extracting information from plan files
or using generic templates based on branch commits.

Usage:
    python3 create_pr.py --branch <branch> --base <base> [options]

Options:
    --plan-path <path>     Path to plan directory (for plan-based PRs)
    --template <type>      Template type (feature, bugfix, docs, refactor, chore)
    --title <title>        PR title (optional, extracted from plan if available)
    --draft                Create as draft PR
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def extract_plan_summary(plan_path: Path, script_dir: Path) -> dict:
    """Extract summary from plan files using extract_plan_summary.py."""
    returncode, stdout, stderr = run_command([
        "python3",
        str(script_dir / "extract_plan_summary.py"),
        "--plan-path",
        str(plan_path)
    ])

    if returncode != 0:
        print(f"Error extracting plan summary: {stderr}", file=sys.stderr)
        sys.exit(1)

    return json.loads(stdout)


def get_template(template_type: str, script_dir: Path) -> str:
    """Get PR template using get_pr_template.py."""
    returncode, stdout, stderr = run_command([
        "python3",
        str(script_dir / "get_pr_template.py"),
        "--type",
        template_type
    ])

    if returncode != 0:
        print(f"Error getting template: {stderr}", file=sys.stderr)
        sys.exit(1)

    return stdout


def get_commit_summary(branch: str, base: str, cwd: Path) -> list[str]:
    """Get list of commit messages on branch."""
    returncode, stdout, stderr = run_command([
        "git",
        "log",
        "--oneline",
        f"{base}..{branch}"
    ], cwd)

    if returncode != 0:
        return []

    commits = []
    for line in stdout.strip().split("\n"):
        if line:
            # Remove commit hash, keep message
            parts = line.split(" ", 1)
            if len(parts) > 1:
                commits.append(parts[1])

    return commits


def create_plan_based_pr_body(plan_summary: dict) -> str:
    """Create PR body from plan summary."""
    parts = [f"# {plan_summary['title']}", ""]

    # Add phases summary
    if plan_summary['phases']:
        parts.append("## Summary")
        for phase in plan_summary['phases']:
            parts.append(f"- Implemented Phase {phase['number']}: {phase['name']}")
        parts.append("")

    # Add plan link
    if plan_summary['plan_file']:
        parts.append("## Plan")
        parts.append(f"[Implementation Plan]({plan_summary['plan_file']})")
        parts.append("")

    # Add testing section
    parts.append("## Testing")

    if plan_summary['testing']['automated']:
        parts.append("### Automated")
        for test in plan_summary['testing']['automated']:
            parts.append(f"- [ ] {test}")
        parts.append("")

    if plan_summary['testing']['manual']:
        parts.append("### Manual Verification")
        for check in plan_summary['testing']['manual']:
            parts.append(f"- [ ] {check}")
        parts.append("")

    # Add issue link if available
    if plan_summary['issue_number']:
        parts.append("## Related")
        parts.append(f"Closes #{plan_summary['issue_number']}")
        parts.append("")

    return "\n".join(parts)


def create_generic_pr_body(
    template: str,
    commits: list[str],
    branch: str
) -> str:
    """Create PR body from template and commits."""
    parts = []

    # Add template
    parts.append(template)

    # Add commits if available
    if commits:
        parts.append("")
        parts.append("## Commits")
        for commit in commits:
            parts.append(f"- {commit}")
        parts.append("")

    return "\n".join(parts)


def create_pr(
    title: str,
    body: str,
    branch: str,
    base: str,
    draft: bool = False,
    cwd: Path = None
) -> tuple[bool, str, str]:
    """
    Create PR using gh CLI.

    Returns:
        Tuple of (success, pr_url, error_message)
    """
    cmd = [
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", base,
        "--head", branch
    ]

    if draft:
        cmd.append("--draft")

    returncode, stdout, stderr = run_command(cmd, cwd)

    if returncode != 0:
        return False, "", stderr

    # gh pr create outputs the PR URL
    pr_url = stdout.strip()

    return True, pr_url, ""


def main():
    parser = argparse.ArgumentParser(
        description="Create GitHub pull request using gh CLI"
    )
    parser.add_argument(
        "--branch",
        type=str,
        required=True,
        help="Branch to create PR from"
    )
    parser.add_argument(
        "--base",
        type=str,
        default="main",
        help="Base branch to merge into (default: main)"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        help="Path to plan directory (for plan-based PRs)"
    )
    parser.add_argument(
        "--template",
        type=str,
        choices=["feature", "bugfix", "docs", "refactor", "chore"],
        default="feature",
        help="Template type (default: feature)"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="PR title (optional, extracted from plan if available)"
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create as draft PR"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Repository directory (default: current directory)"
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # Determine PR type and generate body
    if args.plan_path:
        # Plan-based PR
        if not args.plan_path.exists():
            print(f"Error: Plan directory not found: {args.plan_path}", file=sys.stderr)
            sys.exit(1)

        plan_summary = extract_plan_summary(args.plan_path, script_dir)
        pr_title = args.title or plan_summary['title']
        pr_body = create_plan_based_pr_body(plan_summary)
    else:
        # Generic PR with template
        pr_title = args.title or f"Update from {args.branch}"
        template = get_template(args.template, script_dir)
        commits = get_commit_summary(args.branch, args.base, args.directory)
        pr_body = create_generic_pr_body(template, commits, args.branch)

    # Create PR
    success, pr_url, error = create_pr(
        pr_title,
        pr_body,
        args.branch,
        args.base,
        args.draft,
        args.directory
    )

    if success:
        result = {
            "success": True,
            "title": pr_title,
            "url": pr_url,
            "branch": args.branch,
            "base": args.base,
            "draft": args.draft
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        result = {
            "success": False,
            "error": error
        }
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
