#!/usr/bin/env python3
"""
Initialize a new research project directory structure.

Usage:
    python3 init_research.py <research-name>

Creates:
    .docs/research/<research-name>/
    ├── research-plan.md       # Research scope and objectives
    ├── sources.md             # Collected sources with excerpts
    ├── findings.md            # Organized findings by theme
    ├── research-report.md     # Final synthesized report (generated)
    └── assets/                # Supporting files (PDFs, images, etc.)
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")) -> dict:
    """Create research directory structure."""
    research_dir = base_path / research_name
    created_date = datetime.now().strftime("%Y-%m-%d")

    # Create directories
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "assets").mkdir(exist_ok=True)

    # Load template from assets
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "assets" / "research-plan-template.md"

    if template_path.exists():
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Replace placeholders
        populated_content = template_content.replace("{{RESEARCH_NAME}}", research_name)
        populated_content = populated_content.replace("{{CREATED_DATE}}", created_date)
        populated_content = populated_content.replace("{{UPDATED_DATE}}", created_date)

        # Write research-plan.md
        plan_file = research_dir / "research-plan.md"
        with open(plan_file, 'w') as f:
            f.write(populated_content)

    # Create empty sources.md
    sources_file = research_dir / "sources.md"
    with open(sources_file, 'w') as f:
        f.write(f"# Sources for {research_name}\n\n")
        f.write(f"**Last Updated**: {created_date}\n\n")

    # Create empty findings.md
    findings_file = research_dir / "findings.md"
    with open(findings_file, 'w') as f:
        f.write(f"# Research Findings: {research_name}\n\n")
        f.write(f"**Last Updated**: {created_date}\n\n")

    return {
        "research_dir": str(research_dir),
        "research_name": research_name,
        "created_date": created_date
    }

def main():
    parser = argparse.ArgumentParser(description="Initialize research project structure")
    parser.add_argument("research_name", help="Name of the research project")
    args = parser.parse_args()

    try:
        result = create_research_structure(args.research_name)
        print(f"✅ Research project initialized: {result['research_dir']}")
        print("\nNext steps:")
        print("1. Use /research-plan to define research scope")
        print("2. Use /research-execute to gather information")
        print("3. Use /research-synthesize to generate report")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
