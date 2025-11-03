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

    # Create directories
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "assets").mkdir(exist_ok=True)

    # Create template files from assets
    # (Templates will be created in Phase 1.3)

    return {
        "research_dir": str(research_dir),
        "research_name": research_name,
        "created_date": datetime.now().strftime("%Y-%m-%d")
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
