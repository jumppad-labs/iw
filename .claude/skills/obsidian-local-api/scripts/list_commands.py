#!/usr/bin/env python3
"""
List available Obsidian commands that can be executed via API.

This script retrieves and displays all commands available in Obsidian,
optionally filtering by keyword.

Usage:
    list_commands.py [options]

Options:
    --filter TEXT      Filter commands by keyword (case-insensitive)
    --help            Show this help message

Examples:
    # List all commands
    list_commands.py

    # Filter for export commands
    list_commands.py --filter "export"

    # Filter for editor commands
    list_commands.py --filter "editor"

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


def list_commands(filter_text: str = None) -> bool:
    """
    List available Obsidian commands.

    Args:
        filter_text: Optional filter keyword

    Returns:
        True if successful, False otherwise
    """
    client = get_client()

    # List commands via API
    endpoint = "/commands/"
    success, data, error = client.get(endpoint)

    if not success:
        print(f"❌ Failed to list commands: {error}", file=sys.stderr)
        return False

    # Parse and display commands
    if isinstance(data, dict) and 'commands' in data:
        commands = data['commands']

        # Apply filter if specified
        if filter_text:
            filter_lower = filter_text.lower()
            commands = [
                cmd for cmd in commands
                if filter_lower in cmd.get('id', '').lower()
                or filter_lower in cmd.get('name', '').lower()
            ]

        if len(commands) == 0:
            if filter_text:
                print(f"No commands found matching: {filter_text}")
            else:
                print("No commands available")
            return True

        print(f"Available commands ({len(commands)}):\n")

        # Display commands in a formatted table
        for cmd in commands:
            cmd_id = cmd.get('id', 'unknown')
            cmd_name = cmd.get('name', 'Unknown')
            print(f"  {cmd_id}")
            print(f"    {cmd_name}\n")

        return True
    else:
        print(f"⚠️  Unexpected response format")
        print(data)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="List available Obsidian commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --filter "export"
  %(prog)s --filter "editor"
        """
    )

    parser.add_argument(
        "--filter",
        help="Filter commands by keyword (case-insensitive)"
    )

    args = parser.parse_args()

    # List commands
    success = list_commands(args.filter)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
