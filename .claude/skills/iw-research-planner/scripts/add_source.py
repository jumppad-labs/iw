#!/usr/bin/env python3
"""Add a source to the research sources list."""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def add_source(research_name: str, source_url: str, source_type: str, notes: str = ""):
    """Add source to sources.md file."""
    research_dir = Path(".docs/research") / research_name
    sources_file = research_dir / "sources.md"

    # Create sources.md if it doesn't exist
    if not sources_file.exists():
        with open(sources_file, 'w') as f:
            f.write(f"# Sources for {research_name}\n\n")
            f.write("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n")

    # Append source
    with open(sources_file, 'a') as f:
        f.write(f"\n## {source_type}: {source_url}\n")
        f.write(f"**Added**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        if notes:
            f.write(f"**Notes**: {notes}\n")
        f.write("\n")

    print(f"✅ Source added to {sources_file}")


def main():
    parser = argparse.ArgumentParser(description="Add source to research")
    parser.add_argument("research_name", help="Research project name")
    parser.add_argument("source_url", help="Source URL or reference")
    parser.add_argument("source_type", help="Type: paper, code, docs, blog, book")
    parser.add_argument("--notes", default="", help="Additional notes")

    args = parser.parse_args()
    add_source(args.research_name, args.source_url, args.source_type, args.notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
