#!/usr/bin/env python3
"""
Hook script to load the iw-workflow skill at session start.

Provides context about the project workflow and documentation structure.
"""

# Configure UTF-8 encoding for Windows
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    """Print workflow guidance."""
    print("Loading workflow guidance...")
    print()
    print("Documentation Structure:")
    print("- CLAUDE.md: General Go development standards")
    print("- .docs/knowledge/: Jumppad-specific technical knowledge")
    print("- workflow skill: Process and methodology (auto-loaded)")
    print()
    print("Use /iw-plan for complex features, /iw-implement to execute plans.")
    print("See the workflow skill for full details on the planning and implementation process.")
    print()


if __name__ == "__main__":
    main()
