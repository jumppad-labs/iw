#!/usr/bin/env python3
"""
Generate research report from gathered findings.

Usage:
    python3 generate_report.py <research-name>

This script provides the framework for report generation. Claude should
perform the actual synthesis and analysis based on the gathered findings.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import re


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


def generate_report(research_name: str) -> dict:
    """Generate framework for research report."""
    research_dir = Path(".docs/research") / research_name

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

    args = parser.parse_args()

    try:
        result = generate_report(args.research_name)
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

        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
