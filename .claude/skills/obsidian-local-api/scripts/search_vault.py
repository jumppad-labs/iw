#!/usr/bin/env python3
"""
Search the Obsidian vault for notes matching a query.

This script performs a simple text search across the vault and displays
matching notes with context.

Usage:
    search_vault.py <query> [options]

Arguments:
    query                  Search query text

Options:
    --context-length N     Number of characters of context (default: 100)
    --help                Show this help message

Examples:
    # Search for "machine learning"
    search_vault.py "machine learning"

    # Search with more context
    search_vault.py "TODO" --context-length 200

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


def search_vault(query: str, context_length: int = 100) -> bool:
    """
    Search vault for notes matching query.

    Args:
        query: Search query text
        context_length: Number of characters of context around matches

    Returns:
        True if successful, False otherwise
    """
    client = get_client()

    # Search via API using query parameters (not JSON body)
    endpoint = "/search/simple"
    success, data, error = client.post(
        endpoint,
        data='',  # Empty body to force POST
        params={
            "query": query,
            "context": context_length
        }
    )

    if not success:
        print(f"❌ Search failed: {error}", file=sys.stderr)
        return False

    # Parse and display results
    if isinstance(data, list):
        if len(data) == 0:
            print(f"No results found for: {query}")
            return True

        print(f"Found {len(data)} notes matching '{query}':\n")

        for result in data:
            filename = result.get('filename', 'unknown')
            matches = result.get('matches', [])

            print(f"📄 {filename}")

            for i, match in enumerate(matches, 1):
                context = match.get('context', '')
                match_info = match.get('match', {})
                start = match_info.get('start', 0)
                end = match_info.get('end', 0)

                # Highlight the match in context (simple approach)
                if start >= 0 and end > start:
                    # Context includes the match, try to highlight it
                    print(f"   Match {i}: ...{context}...")
                else:
                    print(f"   Match {i}: ...{context}...")

            print()  # Blank line between files

        print(f"Total: {len(data)} files with matches")
        return True
    else:
        # Unexpected response format
        print(f"⚠️  Unexpected response format")
        print(data)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search Obsidian vault for notes matching query",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "machine learning"
  %(prog)s "TODO" --context-length 200
        """
    )

    parser.add_argument(
        "query",
        help="Search query text"
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=100,
        help="Number of characters of context around matches (default: 100)"
    )

    args = parser.parse_args()

    # Search vault
    success = search_vault(args.query, args.context_length)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
