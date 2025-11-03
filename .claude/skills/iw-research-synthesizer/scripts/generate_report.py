#!/usr/bin/env python3
"""
Generate research report from gathered findings.

Usage:
    python3 generate_report.py <research-name>

This script provides the framework for report generation. Claude should
perform the actual synthesis and analysis based on the gathered findings.
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import re


def load_research_config(research_name: str) -> dict:
    """
    Load research configuration from .research-config.json.

    Tries multiple locations to find the research directory.

    Args:
        research_name: Name of the research project

    Returns:
        Dictionary with config data or defaults
    """
    # Try default location first
    default_path = Path(".docs/research") / research_name
    config_file = default_path / ".research-config.json"

    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)

    # Try current directory
    local_path = Path.cwd() / research_name
    config_file = local_path / ".research-config.json"

    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)

    # Search parent directories (up to 3 levels)
    for parent in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        search_path = parent / research_name
        config_file = search_path / ".research-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

    # Fallback to default if no config found (backward compatibility)
    return {
        "research_name": research_name,
        "workspace_path": ".docs/research",
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "obsidian_integration": False
    }


def load_file(file_path: Path) -> str:
    """Load file content or return empty string if not found."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extract_research_questions(plan_content: str) -> list:
    """Extract research questions from plan file."""
    questions = []
    lines = plan_content.split('\n')
    in_questions = False

    for line in lines:
        if '## Research Questions' in line:
            in_questions = True
            continue
        elif in_questions and line.startswith('##'):
            break
        elif in_questions and line.strip() and not line.strip().startswith('['):
            # Extract numbered questions or bullet points
            match = re.match(r'^\d+\.\s*(.+)$', line.strip())
            if match:
                questions.append(match.group(1))
            elif line.strip().startswith('-'):
                questions.append(line.strip()[1:].strip())

    return questions


def extract_created_date(plan_content: str) -> str:
    """Extract created date from plan file."""
    for line in plan_content.split('\n'):
        if line.startswith('**Created**:'):
            return line.split(':', 1)[1].strip()
    return "Unknown"


def count_sources_by_type(sources_content: str) -> dict:
    """Count sources by type from sources.md."""
    counts = {
        'papers': 0,
        'code': 0,
        'docs': 0,
        'articles': 0,
        'other': 0
    }

    for line in sources_content.split('\n'):
        if line.startswith('## '):
            source_type = line[3:].split(':')[0].strip().lower()
            if 'paper' in source_type:
                counts['papers'] += 1
            elif 'code' in source_type or 'repo' in source_type:
                counts['code'] += 1
            elif 'doc' in source_type:
                counts['docs'] += 1
            elif 'blog' in source_type or 'article' in source_type:
                counts['articles'] += 1
            else:
                counts['other'] += 1

    return counts


def extract_themes(findings_content: str) -> list:
    """Extract theme names from findings.md."""
    themes = []
    for line in findings_content.split('\n'):
        if line.startswith('## ') and not line.startswith('## Research'):
            theme = line[3:].strip()
            if theme:
                themes.append(theme)
    return themes


def count_findings(findings_content: str) -> int:
    """Count total findings from findings.md."""
    count = 0
    for line in findings_content.split('\n'):
        if line.strip().startswith('- ') and '*(Source:' in line:
            count += 1
    return count


def cleanup_workspace(research_dir: Path, final_report_path: Path, dry_run: bool = False) -> dict:
    """
    Clean up intermediate research files after report is moved.

    Args:
        research_dir: Workspace directory containing intermediate files
        final_report_path: Path where final report was saved
        dry_run: If True, show what would be deleted without deleting

    Returns:
        Dictionary with cleanup results
    """
    files_to_remove = [
        "research-plan.md",
        "sources.md",
        "findings.md",
        ".research-config.json"
    ]

    dirs_to_remove = [
        "assets"
    ]

    removed_files = []
    removed_dirs = []
    errors = []

    # Remove files
    for filename in files_to_remove:
        file_path = research_dir / filename
        if file_path.exists():
            if dry_run:
                print(f"Would remove: {file_path}")
                removed_files.append(str(file_path))
            else:
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                except Exception as e:
                    errors.append(f"Failed to remove {file_path}: {e}")

    # Remove directories
    for dirname in dirs_to_remove:
        dir_path = research_dir / dirname
        if dir_path.exists():
            if dry_run:
                print(f"Would remove: {dir_path}")
                removed_dirs.append(str(dir_path))
            else:
                try:
                    shutil.rmtree(dir_path)
                    removed_dirs.append(str(dir_path))
                except Exception as e:
                    errors.append(f"Failed to remove {dir_path}: {e}")

    # Remove research directory if empty
    if not dry_run:
        try:
            if research_dir.exists() and not any(research_dir.iterdir()):
                research_dir.rmdir()
                removed_dirs.append(str(research_dir))
        except Exception as e:
            # Not empty or can't remove, that's okay
            pass

    return {
        "removed_files": removed_files,
        "removed_dirs": removed_dirs,
        "errors": errors,
        "final_report": str(final_report_path)
    }


def generate_report(research_name: str) -> dict:
    """Generate framework for research report."""
    # Load research config to get workspace location
    config = load_research_config(research_name)
    workspace_path = Path(config["workspace_path"])

    research_dir = workspace_path / research_name

    # Load all research files
    plan = load_file(research_dir / "research-plan.md")
    sources = load_file(research_dir / "sources.md")
    findings = load_file(research_dir / "findings.md")

    # Extract components
    questions = extract_research_questions(plan)
    start_date = extract_created_date(plan)
    themes = extract_themes(findings)
    source_counts = count_sources_by_type(sources)
    findings_count = count_findings(findings)

    # Load template
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "assets" / "report-template.md"
    template = load_file(template_path)

    # Generate report framework
    # Note: Claude should fill in the actual synthesis content
    report = template.replace("{{RESEARCH_NAME}}", research_name)
    report = report.replace("{{START_DATE}}", start_date)
    report = report.replace("{{END_DATE}}", datetime.now().strftime("%Y-%m-%d"))
    report = report.replace("{{GENERATED_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Placeholders for Claude to fill in
    report = report.replace("{{EXECUTIVE_SUMMARY}}",
                           "[Claude should synthesize 2-3 paragraph executive summary here based on findings]")

    questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions)) if questions else "[No questions defined]"
    report = report.replace("{{RESEARCH_QUESTIONS}}", questions_text)

    report = report.replace("{{KEY_FINDINGS}}",
                           f"[Claude should synthesize key findings from themes: {', '.join(themes)}]\n\n" +
                           "[Organize by theme with cross-source analysis]")

    report = report.replace("{{DETAILED_ANALYSIS}}",
                           "[Claude should provide detailed analysis addressing each research question]")

    report = report.replace("{{SOURCES}}",
                           "[Claude should organize sources by type from sources.md]")

    report = report.replace("{{RECOMMENDATIONS}}",
                           "[Claude should generate recommendations based on findings]")

    # Write report framework
    report_file = research_dir / "research-report.md"
    with open(report_file, 'w') as f:
        f.write(report)

    # Calculate statistics
    total_sources = sum(source_counts.values())

    return {
        "report_file": str(report_file),
        "questions_count": len(questions),
        "themes_count": len(themes),
        "findings_count": findings_count,
        "sources_total": total_sources,
        "sources_breakdown": source_counts,
        "word_count": len(report.split())
    }


def main():
    parser = argparse.ArgumentParser(description="Generate research report framework")
    parser.add_argument("research_name", help="Research project name")
    parser.add_argument(
        "--final-path",
        help="Final location for report (prompts if not provided)",
        default=None
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip cleanup of intermediate files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show cleanup actions without executing"
    )

    args = parser.parse_args()

    try:
        result = generate_report(args.research_name)
        report_file = Path(result['report_file'])
        config = load_research_config(args.research_name)
        workspace_path = Path(config["workspace_path"])
        research_dir = workspace_path / args.research_name

        print(f"✅ Research report framework generated!")
        print(f"\nReport: {result['report_file']}")
        print(f"\nStatistics:")
        print(f"- Research questions: {result['questions_count']}")
        print(f"- Themes identified: {result['themes_count']}")
        print(f"- Total findings: {result['findings_count']}")
        print(f"- Sources consulted: {result['sources_total']}", end="")

        breakdown = result['sources_breakdown']
        parts = []
        if breakdown['papers'] > 0:
            parts.append(f"{breakdown['papers']} papers")
        if breakdown['code'] > 0:
            parts.append(f"{breakdown['code']} repos")
        if breakdown['docs'] > 0:
            parts.append(f"{breakdown['docs']} docs")
        if breakdown['articles'] > 0:
            parts.append(f"{breakdown['articles']} articles")
        if breakdown['other'] > 0:
            parts.append(f"{breakdown['other']} other")

        if parts:
            print(f" ({', '.join(parts)})")
        else:
            print()

        print(f"\n⚠️  Note: Claude should now synthesize the actual report content")
        print(f"   The framework has been created with placeholders.")
        print(f"   Review and complete the synthesis manually or via the skill.")

        # Prompt for final location (if not provided via CLI)
        if not args.final_path:
            print(f"\n📋 Workspace: {research_dir}")
            print("\nWhere would you like to save the final report?")
            print("1. Keep in workspace (no move)")
            print("2. Specify custom path")

            choice = input("\nChoice (1-2): ").strip()

            if choice == "2":
                final_path_input = input("Enter final report path: ").strip()
                final_path = Path(final_path_input).expanduser()
            else:
                # Keep in workspace
                final_path = report_file
        else:
            final_path = Path(args.final_path).expanduser()

        # Move report if different location
        moved = False
        if final_path != report_file:
            print(f"\n📦 Moving report to: {final_path}")

            # Create parent directory if needed
            final_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy report to final location
            shutil.copy2(report_file, final_path)

            # Verify copy succeeded
            if final_path.exists():
                print(f"✅ Report saved to: {final_path}")
                moved = True
            else:
                print(f"❌ Failed to move report to: {final_path}")
                print(f"   Report remains in workspace: {report_file}")
                final_path = report_file  # Revert to workspace location

        # Cleanup workspace (only if report was moved successfully and not disabled)
        if moved and not args.no_cleanup:
            print(f"\n🧹 Cleaning up workspace...")
            cleanup_result = cleanup_workspace(research_dir, final_path, dry_run=args.dry_run)

            if cleanup_result["removed_files"]:
                print(f"   Removed {len(cleanup_result['removed_files'])} files")
            if cleanup_result["removed_dirs"]:
                print(f"   Removed {len(cleanup_result['removed_dirs'])} directories")
            if cleanup_result["errors"]:
                print(f"⚠️  Errors during cleanup:")
                for error in cleanup_result["errors"]:
                    print(f"   - {error}")
            else:
                print(f"✅ Workspace cleaned successfully")
        else:
            print(f"\n📁 Research files remain in: {research_dir}")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
