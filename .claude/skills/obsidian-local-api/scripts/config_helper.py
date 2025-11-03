#!/usr/bin/env python3
"""
Interactive configuration helper for Obsidian API credentials.

This script helps configure API credentials for accessing Obsidian Local REST API.
It can display current configuration, set individual values, or run interactive setup.

Configuration is stored in ~/.obsidian-api/config.json by default.

Usage:
    config_helper.py [options]

Options:
    --show              Show current configuration
    --set-key KEY       Set API key
    --set-host HOST     Set host address (default: localhost)
    --set-port PORT     Set port number (default: 27124)
    --test              Test connection to Obsidian API
    --help             Show this help message

Examples:
    # Interactive setup
    config_helper.py

    # Set API key
    config_helper.py --set-key "abc123xyz456"

    # Set custom host and port
    config_helper.py --set-host "192.168.1.100" --set-port 27124

    # Show current configuration
    config_helper.py --show

    # Test connection
    config_helper.py --test

Requires:
    - Obsidian running with Local REST API plugin enabled
"""

import sys
import json
import getpass
from pathlib import Path

# Add script directory to path to import obsidian_client
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from obsidian_client import ObsidianClient


CONFIG_DIR = Path.home() / ".obsidian-api"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Write config file with restrictive permissions
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        # Set file permissions to user-only read/write (600)
        CONFIG_FILE.chmod(0o600)

        return True
    except IOError as e:
        print(f"❌ Failed to save configuration: {e}", file=sys.stderr)
        return False


def show_config():
    """Display current configuration."""
    config = load_config()

    if not config:
        print("No configuration found.")
        print(f"Configuration file: {CONFIG_FILE}")
        return

    print("Current configuration:")
    print(f"  Config file: {CONFIG_FILE}\n")

    # Display config values, masking API key
    for key, value in config.items():
        if key == "api_key" and value:
            # Mask API key, show only first/last few chars
            masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "****"
            print(f"  {key}: {masked}")
        elif key == "vault_path" and value:
            print(f"  {key}: {value}")
            # Check if path exists
            vault_exists = Path(value).exists()
            print(f"    Status: {'✅ Exists' if vault_exists else '❌ Not found'}")
        else:
            print(f"  {key}: {value}")


def set_config_value(key: str, value: str):
    """
    Set a configuration value.

    Args:
        key: Configuration key
        value: Configuration value
    """
    config = load_config()
    config[key] = value

    if save_config(config):
        print(f"✅ Configuration updated: {key}")
    else:
        sys.exit(1)


def test_connection():
    """Test connection to Obsidian API."""
    print("Testing connection to Obsidian API...")

    client = ObsidianClient()

    # Check if API key is configured
    if not client.api_key:
        print("❌ No API key configured", file=sys.stderr)
        print("\nRun config_helper.py to set up API key", file=sys.stderr)
        sys.exit(1)

    success, message = client.test_connection()

    if success:
        print(f"✅ {message}")
        print(f"\nConnection details:")
        print(f"  Host: {client.host}")
        print(f"  Port: {client.port}")
        print(f"  Protocol: {'HTTPS' if client.use_https else 'HTTP'}")
    else:
        print(f"❌ {message}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("  1. Ensure Obsidian is running", file=sys.stderr)
        print("  2. Verify Local REST API plugin is enabled", file=sys.stderr)
        print("  3. Check API key is correct (found in plugin settings)", file=sys.stderr)
        sys.exit(1)


def interactive_setup():
    """Run interactive configuration setup."""
    print("Obsidian API Configuration Setup")
    print("=" * 50)
    print()

    config = load_config()

    # API Key
    current_key = config.get('api_key', '')
    if current_key:
        masked = current_key[:4] + "*" * 8 + current_key[-4:] if len(current_key) > 8 else "****"
        print(f"Current API key: {masked}")

    print("\nAPI Key can be found in Obsidian:")
    print("  Settings → Community Plugins → Local REST API → Copy API Key")
    api_key = input("\nEnter API key (or press Enter to keep current): ").strip()
    if api_key:
        config['api_key'] = api_key

    # Host
    current_host = config.get('host', 'localhost')
    host = input(f"\nEnter host (default: {current_host}): ").strip()
    if host:
        config['host'] = host
    elif 'host' not in config:
        config['host'] = 'localhost'

    # Port
    current_port = config.get('port', 27124)
    port_input = input(f"\nEnter port (default: {current_port}): ").strip()
    if port_input:
        try:
            config['port'] = int(port_input)
        except ValueError:
            print("Invalid port number, using default: 27124")
            config['port'] = 27124
    elif 'port' not in config:
        config['port'] = 27124

    # HTTPS
    current_https = config.get('https', True)
    https_input = input(f"\nUse HTTPS? (default: {'yes' if current_https else 'no'}): ").strip().lower()
    if https_input in ('yes', 'y', 'true', '1'):
        config['https'] = True
    elif https_input in ('no', 'n', 'false', '0'):
        config['https'] = False
    elif 'https' not in config:
        config['https'] = True

    # Vault Path (for filesystem fallback)
    print("\n" + "=" * 50)
    print("Vault Path Configuration (Optional)")
    print("=" * 50)
    print("The vault path enables filesystem fallback when API operations fail.")
    print("This is useful for large files that exceed API timeouts.")

    current_vault = config.get('vault_path', '')
    if current_vault:
        print(f"\nCurrent vault path: {current_vault}")

    # Attempt auto-detection from API
    vault_suggestion = None
    if config.get('api_key'):
        print("\nAttempting to detect vault path from API...")
        try:
            client = ObsidianClient(api_key=config.get('api_key'))
            # Try to get vault info from API (if endpoint exists)
            success, data, error = client.get("/vault/")
            if success and isinstance(data, dict):
                vault_suggestion = data.get('vault_path') or data.get('path')
                if vault_suggestion:
                    print(f"✅ Detected vault path: {vault_suggestion}")
        except Exception as e:
            print(f"⚠️  Could not detect vault path: {e}")

    # Prompt for vault path
    prompt_text = "\nEnter vault path"
    if vault_suggestion:
        prompt_text += f" (or press Enter for detected: {vault_suggestion})"
    elif current_vault:
        prompt_text += " (or press Enter to keep current)"
    else:
        prompt_text += " (or press Enter to skip)"
    prompt_text += ": "

    vault_input = input(prompt_text).strip()
    if vault_input:
        # User provided path
        vault_path = Path(vault_input).expanduser()
        if vault_path.exists() and vault_path.is_dir():
            config['vault_path'] = str(vault_path)
            print(f"✅ Vault path set to: {vault_path}")
        else:
            print(f"⚠️  Warning: Path does not exist or is not a directory: {vault_path}")
            print(f"   You can update this later with: --set-vault-path")
            config['vault_path'] = str(vault_path)
    elif vault_suggestion and not current_vault:
        # Use detected path
        config['vault_path'] = vault_suggestion
        print(f"✅ Using detected vault path: {vault_suggestion}")
    elif not current_vault:
        print("ℹ️  Vault path not configured. Filesystem fallback will prompt when needed.")

    # Save configuration
    print()
    if save_config(config):
        print(f"✅ Configuration saved to: {CONFIG_FILE}")

        # Test connection
        print()
        test_input = input("Test connection now? (yes/no): ").strip().lower()
        if test_input in ('yes', 'y'):
            print()
            test_connection()
    else:
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure Obsidian API credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Interactive setup
  %(prog)s --show                       # Show current config
  %(prog)s --set-key "abc123"           # Set API key
  %(prog)s --test                       # Test connection
        """
    )

    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--set-key", metavar="KEY", help="Set API key")
    parser.add_argument("--set-host", metavar="HOST", help="Set host address")
    parser.add_argument("--set-port", metavar="PORT", type=int, help="Set port number")
    parser.add_argument("--set-vault-path", metavar="PATH", help="Set vault path for filesystem fallback")
    parser.add_argument("--test", action="store_true", help="Test connection")

    args = parser.parse_args()

    # Handle options
    if args.show:
        show_config()
    elif args.set_key:
        set_config_value("api_key", args.set_key)
    elif args.set_host:
        set_config_value("host", args.set_host)
    elif args.set_port:
        set_config_value("port", args.set_port)
    elif args.set_vault_path:
        # Validate vault path before saving
        vault_path = Path(args.set_vault_path).expanduser()
        if vault_path.exists() and vault_path.is_dir():
            set_config_value("vault_path", str(vault_path))
            print(f"✅ Vault path set to: {vault_path}")
        else:
            print(f"❌ Invalid vault path: {vault_path}", file=sys.stderr)
            print(f"   Path must exist and be a directory", file=sys.stderr)
            sys.exit(1)
    elif args.test:
        test_connection()
    else:
        # No options provided, run interactive setup
        interactive_setup()


if __name__ == "__main__":
    main()
