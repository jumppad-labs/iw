#!/usr/bin/env python3
"""
Workflow Version Checker

Compares local workflow version with latest GitHub version.
Returns exit codes indicating update status.

Usage:
    python3 check_version.py [--local-version VERSION] [--remote-version VERSION]

Exit codes:
    0 - No update needed (up to date)
    1 - Update available
    2 - Unable to determine (error or missing version file)
"""

import argparse
import sys
from pathlib import Path


def read_local_version() -> str:
    """
    Read local VERSION file.

    Checks user-level installation first, then project-level.

    Returns:
        Version string, or None if not found
    """
    # Try user-level first
    user_version = Path.home() / ".claude" / "skills" / "iw-install" / "VERSION"
    if user_version.exists():
        return user_version.read_text().strip()

    # Try project-level
    project_version = Path(".claude") / "skills" / "iw-install" / "VERSION"
    if project_version.exists():
        return project_version.read_text().strip()

    return None


def compare_versions(local: str, remote: str) -> int:
    """
    Compare semantic versions.

    Uses simple version comparison. For production use, consider
    using packaging.version for more robust comparison.

    Args:
        local: Local version string (e.g., "1.0.0")
        remote: Remote version string (e.g., "1.1.0")

    Returns:
        -1 if remote is newer
        0 if versions are equal
        1 if local is newer
    """
    try:
        # Parse semantic versions (MAJOR.MINOR.PATCH)
        local_parts = [int(x) for x in local.split(".")]
        remote_parts = [int(x) for x in remote.split(".")]

        # Pad shorter version with zeros
        while len(local_parts) < 3:
            local_parts.append(0)
        while len(remote_parts) < 3:
            remote_parts.append(0)

        # Compare
        if remote_parts > local_parts:
            return -1  # Remote is newer
        elif remote_parts < local_parts:
            return 1  # Local is newer
        else:
            return 0  # Same version

    except (ValueError, AttributeError) as e:
        print(f"Error parsing versions: {e}", file=sys.stderr)
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check workflow version for updates"
    )
    parser.add_argument(
        "--local-version",
        help="Local version (defaults to reading from VERSION file)",
    )
    parser.add_argument(
        "--remote-version",
        help="Remote version (normally fetched via WebFetch)",
    )

    args = parser.parse_args()

    # Get local version
    local_version = args.local_version or read_local_version()

    if not local_version:
        print("No local VERSION file found.", file=sys.stderr)
        print("Run /iw-install to install workflow with version tracking.")
        sys.exit(2)  # Unable to determine

    print(f"Local version: {local_version}")

    # Get remote version
    remote_version = args.remote_version

    if not remote_version:
        print("Remote version not provided.", file=sys.stderr)
        print("This script requires --remote-version for comparison.")
        print("Claude will fetch this using WebFetch tool.")
        sys.exit(2)  # Unable to determine

    print(f"Remote version: {remote_version}")

    # Compare versions
    result = compare_versions(local_version, remote_version)

    if result is None:
        print("Unable to compare versions (invalid format)", file=sys.stderr)
        sys.exit(2)

    if result < 0:
        print(f"✨ Update available: {local_version} → {remote_version}")
        sys.exit(1)  # Update available
    elif result == 0:
        print(f"✓ Up to date (v{local_version})")
        sys.exit(0)  # No update needed
    else:
        print(f"ℹ️  Local version is newer (v{local_version} > v{remote_version})")
        print("You may be running a development version.")
        sys.exit(0)  # No update needed


if __name__ == "__main__":
    main()
