#!/usr/bin/env python3
"""
Execute an Obsidian command via API.

This script triggers execution of an Obsidian command. Use list_commands.py
to see available commands and their IDs.

Usage:
    execute_command.py <command-id>

Arguments:
    command-id         Command ID to execute

Options:
    --help            Show this help message

Examples:
    # Toggle bold formatting
    execute_command.py "editor:toggle-bold"

    # Open command palette
    execute_command.py "command-palette:open"

    # Export to PDF (if available)
    execute_command.py "markdown:export-pdf"

Requires:
    - Obsidian running with Local REST API plugin enabled
    - API key configured (use config_helper.py)
"""

import sys
import argparse
from pathlib import Path

# Add script directory to path to import obsidian_client
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from obsidian_client import get_client


def execute_command(command_id: str) -> bool:
    """
    Execute an Obsidian command.

    Args:
        command_id: Command ID to execute

    Returns:
        True if successful, False otherwise
    """
    client = get_client()

    # Execute command via API
    endpoint = f"/commands/{command_id}/"
    success, data, error = client.post(endpoint)

    if success:
        print(f"✅ Command executed: {command_id}")
        if data and isinstance(data, str) and data.strip():
            print(f"Response: {data}")
        return True
    else:
        print(f"❌ Failed to execute command: {error}", file=sys.stderr)
        print(f"\nTip: Use list_commands.py to see available commands", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute an Obsidian command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "editor:toggle-bold"
  %(prog)s "command-palette:open"

Tip: Use list_commands.py to see available commands
        """
    )

    parser.add_argument(
        "command_id",
        help="Command ID to execute (use list_commands.py to see available commands)"
    )

    args = parser.parse_args()

    # Execute command
    success = execute_command(args.command_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
