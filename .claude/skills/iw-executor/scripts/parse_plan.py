#!/usr/bin/env python3
"""
Parse implementation plan files and extract structure.

Extracts phases, tasks, file references, and progress status from
plan files created by iw-planner.

Usage:
    python3 parse_plan.py <plan-directory>

Returns JSON with:
    - phases: List of phases with names and task counts
    - tasks: List of all tasks with status, file references, effort
    - progress: Overall completion statistics
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def find_plan_files(plan_dir: Path) -> Dict[str, Path]:
    """Find the four plan files in the directory."""
    files = {}

    for file_path in plan_dir.glob("*-plan.md"):
        files["plan"] = file_path
    for file_path in plan_dir.glob("*-tasks.md"):
        files["tasks"] = file_path
    for file_path in plan_dir.glob("*-context.md"):
        files["context"] = file_path
    for file_path in plan_dir.glob("*-research.md"):
        files["research"] = file_path

    return files


def parse_tasks_file(tasks_path: Path) -> List[Dict[str, Any]]:
    """Parse tasks.md and extract task information."""
    tasks = []
    current_phase = None

    content = tasks_path.read_text()
    lines = content.split("\n")

    for line in lines:
        # Check for phase headers (## Phase N: Name)
        phase_match = re.match(r"^##\s+Phase\s+(\d+):\s+(.+)$", line)
        if phase_match:
            phase_num = int(phase_match.group(1))
            phase_name = phase_match.group(2).strip()
            current_phase = {"number": phase_num, "name": phase_name}
            continue

        # Check for task items (- [ ] or - [x] ...)
        task_match = re.match(r"^-\s+\[([ x])\]\s+(.+)$", line)
        if task_match:
            is_done = task_match.group(1) == "x"
            task_line = task_match.group(2).strip()

            # Parse task details: description - file - effort - dependencies
            parts = [p.strip() for p in task_line.split(" - ")]

            task = {
                "description": parts[0] if len(parts) > 0 else "",
                "file": parts[1] if len(parts) > 1 else "",
                "effort": parts[2] if len(parts) > 2 else "",
                "dependencies": parts[3] if len(parts) > 3 else "",
                "status": "done" if is_done else "pending",
                "phase": current_phase
            }
            tasks.append(task)

    return tasks


def parse_plan_phases(plan_path: Path) -> List[Dict[str, Any]]:
    """Parse plan.md and extract phase information."""
    phases = []

    content = plan_path.read_text()
    lines = content.split("\n")

    for line in lines:
        # Look for phase headers in plan.md
        # Common patterns: "## Phase 1: Name" or "### Phase 1: Name"
        phase_match = re.match(r"^###+\s+Phase\s+(\d+):\s+(.+)$", line)
        if phase_match:
            phase_num = int(phase_match.group(1))
            phase_name = phase_match.group(2).strip()
            phases.append({"number": phase_num, "name": phase_name})

    return phases


def extract_success_criteria(plan_path: Path) -> Dict[str, List[str]]:
    """Extract success criteria from plan.md."""
    criteria = {"automated": [], "manual": []}

    content = plan_path.read_text()
    lines = content.split("\n")

    in_automated = False
    in_manual = False

    for line in lines:
        # Check for section headers
        if "Automated Verification" in line or "automated verification" in line.lower():
            in_automated = True
            in_manual = False
            continue
        elif "Manual Verification" in line or "manual verification" in line.lower():
            in_manual = True
            in_automated = False
            continue
        elif line.startswith("#"):
            # New section, reset flags
            in_automated = False
            in_manual = False
            continue

        # Extract list items
        if line.strip().startswith("-") or line.strip().startswith("*"):
            item = line.strip()[1:].strip()
            if in_automated:
                criteria["automated"].append(item)
            elif in_manual:
                criteria["manual"].append(item)

    return criteria


def main():
    parser = argparse.ArgumentParser(
        description="Parse implementation plan files and extract structure"
    )
    parser.add_argument(
        "plan_dir",
        type=Path,
        help="Path to the plan directory"
    )

    args = parser.parse_args()

    if not args.plan_dir.exists():
        print(f"Error: Plan directory not found: {args.plan_dir}", file=sys.stderr)
        sys.exit(1)

    # Find plan files
    plan_files = find_plan_files(args.plan_dir)

    if "plan" not in plan_files:
        print(f"Error: No *-plan.md file found in {args.plan_dir}", file=sys.stderr)
        sys.exit(1)

    if "tasks" not in plan_files:
        print(f"Error: No *-tasks.md file found in {args.plan_dir}", file=sys.stderr)
        sys.exit(1)

    # Parse files
    tasks = parse_tasks_file(plan_files["tasks"]) if "tasks" in plan_files else []
    phases = parse_plan_phases(plan_files["plan"]) if "plan" in plan_files else []
    success_criteria = extract_success_criteria(plan_files["plan"]) if "plan" in plan_files else {}

    # Calculate progress
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["status"] == "done")

    # Organize tasks by phase
    phases_with_tasks = []
    for phase in phases:
        phase_tasks = [t for t in tasks if t["phase"] and t["phase"]["number"] == phase["number"]]
        phase_completed = sum(1 for t in phase_tasks if t["status"] == "done")

        phases_with_tasks.append({
            "number": phase["number"],
            "name": phase["name"],
            "total_tasks": len(phase_tasks),
            "completed_tasks": phase_completed,
            "tasks": phase_tasks
        })

    # Build result
    result = {
        "plan_directory": str(args.plan_dir),
        "files": {k: str(v) for k, v in plan_files.items()},
        "phases": phases_with_tasks,
        "all_tasks": tasks,
        "success_criteria": success_criteria,
        "progress": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "remaining_tasks": total_tasks - completed_tasks,
            "completion_percentage": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        }
    }

    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
