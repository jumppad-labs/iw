#!/usr/bin/env python3
"""
Create phase commit for completed implementation phase.

Creates a git commit for a completed phase with proper message format
including plan reference and issue number.

Usage:
    python3 create_phase_commit.py --phase <number> --plan-path <plan-directory> [--worktree <path>]

Output:
    JSON with commit hash, message, and stats
"""

import argparse
import json
import re
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


def extract_phase_info(plan_path: Path, phase_number: int) -> dict:
    """
    Extract phase name and details from plan files.

    Returns dict with:
        - phase_name: str
        - phase_description: str (if available)
    """
    # Find plan file
    plan_files = list(plan_path.glob("*-plan.md"))
    if not plan_files:
        return {"phase_name": f"Phase {phase_number}", "phase_description": ""}

    plan_file = plan_files[0]
    content = plan_file.read_text()
    lines = content.split("\n")

    phase_name = f"Phase {phase_number}"
    phase_description = ""

    # Look for phase header
    phase_pattern = re.compile(rf"^###+\s+Phase\s+{phase_number}:\s+(.+)$")

    in_phase = False
    for i, line in enumerate(lines):
        match = phase_pattern.match(line)
        if match:
            phase_name = match.group(1).strip()
            in_phase = True
            # Try to extract description from next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                desc_line = lines[j].strip()
                if desc_line and not desc_line.startswith("#") and not desc_line.startswith("-"):
                    phase_description = desc_line
                    break
            break

    return {
        "phase_name": phase_name,
        "phase_description": phase_description
    }


def extract_issue_number(plan_path: Path) -> int | None:
    """Extract issue number from plan path."""
    match = re.search(r'/issues/(\d+)/', str(plan_path))
    if match:
        return int(match.group(1))

    for file_path in plan_path.glob("*-plan.md"):
        match = re.match(r'(\d+)-', file_path.name)
        if match:
            return int(match.group(1))

    return None


def create_commit_message(
    phase_number: int,
    phase_info: dict,
    plan_path: Path,
    issue_number: int | None
) -> str:
    """Generate commit message for phase."""
    phase_name = phase_info["phase_name"]
    phase_desc = phase_info["phase_description"]

    message_parts = [
        f"Phase {phase_number}: {phase_name}",
        ""
    ]

    if phase_desc:
        message_parts.append(phase_desc)
        message_parts.append("")

    # Add plan reference
    message_parts.append(f"Plan: {plan_path}")

    # Add issue reference if available
    if issue_number:
        message_parts.append(f"Issue: #{issue_number}")

    return "\n".join(message_parts)


def create_commit(worktree_path: Path, commit_message: str) -> tuple[bool, dict, str]:
    """
    Create git commit in the repository.

    Returns:
        Tuple of (success, commit_info, error_message)
    """
    # Stage all changes
    returncode, stdout, stderr = run_git_command(
        ["git", "add", "-A"],
        worktree_path
    )
    if returncode != 0:
        return False, {}, f"Failed to stage changes: {stderr}"

    # Check if there are changes to commit
    returncode, stdout, stderr = run_git_command(
        ["git", "diff", "--cached", "--quiet"],
        worktree_path
    )
    if returncode == 0:
        # No changes to commit
        return False, {}, "No changes to commit"

    # Create commit
    returncode, stdout, stderr = run_git_command(
        ["git", "commit", "-m", commit_message],
        worktree_path
    )
    if returncode != 0:
        return False, {}, f"Failed to create commit: {stderr}"

    # Get commit hash
    returncode, commit_hash, _ = run_git_command(
        ["git", "rev-parse", "HEAD"],
        worktree_path
    )
    commit_hash = commit_hash.strip()

    # Get commit stats
    returncode, stats, _ = run_git_command(
        ["git", "show", "--stat", "--oneline", commit_hash],
        worktree_path
    )

    return True, {
        "commit_hash": commit_hash,
        "commit_message": commit_message,
        "stats": stats.strip()
    }, ""


def main():
    parser = argparse.ArgumentParser(
        description="Create phase commit for implementation"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        help="Phase number"
    )
    parser.add_argument(
        "--plan-path",
        type=Path,
        required=True,
        help="Path to the plan directory"
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=Path.cwd(),
        help="Worktree path (default: current directory)"
    )

    args = parser.parse_args()

    if not args.plan_path.exists():
        print(json.dumps({
            "success": False,
            "error": f"Plan directory not found: {args.plan_path}"
        }), file=sys.stderr)
        sys.exit(1)

    # Extract phase info from plan
    phase_info = extract_phase_info(args.plan_path, args.phase)
    issue_number = extract_issue_number(args.plan_path)

    # Generate commit message
    commit_message = create_commit_message(
        args.phase,
        phase_info,
        args.plan_path,
        issue_number
    )

    # Create commit
    success, commit_info, error = create_commit(args.worktree, commit_message)

    if success:
        result = {
            "success": True,
            "phase": args.phase,
            **commit_info
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        result = {
            "success": False,
            "error": error,
            "phase": args.phase
        }
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
