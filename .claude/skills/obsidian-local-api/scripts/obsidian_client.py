#!/usr/bin/env python3
"""
Obsidian Local REST API Client Module

This module provides a base client for interacting with the Obsidian Local REST API.
It handles authentication, connection configuration, and common HTTP operations.

Configuration is loaded from (in order of precedence):
1. Environment variables (OBSIDIAN_API_KEY, OBSIDIAN_HOST, OBSIDIAN_PORT, OBSIDIAN_HTTPS)
2. Project-level config file (.obsidian-api.json)
3. User-level config file (~/.obsidian-api/config.json)
4. Defaults (localhost:27124, HTTPS)

Requires:
    requests library: pip install requests
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import urllib3

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ObsidianClient:
    """Client for interacting with Obsidian Local REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        use_https: Optional[bool] = None
    ):
        """
        Initialize Obsidian API client.

        Args:
            api_key: API key from Obsidian plugin settings
            host: Host address (default: localhost)
            port: Port number (default: 27124 for HTTPS)
            use_https: Use HTTPS (default: True)
        """
        self.api_key = api_key or self._load_config_value("api_key")
        self.host = host if host is not None else self._load_config_value("host", "localhost")
        self.port = port if port is not None else int(self._load_config_value("port", "27124"))
        self.use_https = use_https if use_https is not None else self._load_config_value("https", True)

        # Build base URL
        protocol = "https" if self.use_https else "http"
        self.base_url = f"{protocol}://{self.host}:{self.port}"

        # Setup session
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def _load_config_value(self, key: str, default: Any = None) -> Any:
        """
        Load configuration value from environment or config files.

        Precedence:
        1. Environment variables
        2. Project-level .obsidian-api.json
        3. User-level ~/.obsidian-api/config.json
        4. Default value

        Args:
            key: Configuration key to load
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        # Check environment variables
        env_key = f"OBSIDIAN_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            # Convert string booleans
            if env_value.lower() in ("true", "1", "yes"):
                return True
            elif env_value.lower() in ("false", "0", "no"):
                return False
            return env_value

        # Check project-level config
        project_config = Path.cwd() / ".obsidian-api.json"
        if project_config.exists():
            try:
                with open(project_config, 'r') as f:
                    config = json.load(f)
                    if key in config:
                        return config[key]
            except (json.JSONDecodeError, IOError):
                pass

        # Check user-level config
        user_config = Path.home() / ".obsidian-api" / "config.json"
        if user_config.exists():
            try:
                with open(user_config, 'r') as f:
                    config = json.load(f)
                    if key in config:
                        return config[key]
            except (json.JSONDecodeError, IOError):
                pass

        return default

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Make an HTTP request to the Obsidian API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/vault/note.md")
            data: Request body (string or bytes)
            json_data: JSON request body (dict)
            headers: Additional headers
            params: Query parameters

        Returns:
            Tuple of (success, response_data, error_message)
        """
        url = f"{self.base_url}{endpoint}"

        # Merge headers
        req_headers = {}
        if headers:
            req_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                json=json_data,
                headers=req_headers,
                params=params,
                verify=False,  # Allow self-signed certificates
                timeout=120
            )

            # Check for errors
            if response.status_code >= 400:
                error_msg = self._parse_error(response)
                return False, None, error_msg

            # Parse response
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                try:
                    return True, response.json(), None
                except json.JSONDecodeError:
                    return True, response.text, None
            else:
                return True, response.text, None

        except requests.exceptions.ConnectionError:
            return False, None, (
                "Connection refused. Ensure Obsidian is running with the "
                "Local REST API plugin enabled."
            )
        except requests.exceptions.Timeout:
            return False, None, "Request timed out. Check your network connection."
        except requests.exceptions.RequestException as e:
            return False, None, f"Request failed: {str(e)}"

    def _parse_error(self, response: requests.Response) -> str:
        """
        Parse error response from API.

        Args:
            response: HTTP response object

        Returns:
            Human-readable error message
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            message = error_data.get('message', '')
            error_code = error_data.get('errorCode', '')

            if error_code:
                return f"{message} (Error code: {error_code})"
            return message
        except json.JSONDecodeError:
            pass

        # Generic error messages based on status code
        if status_code == 401:
            return (
                "Authentication failed. Check your API key with: "
                "config_helper.py --show"
            )
        elif status_code == 404:
            return "Note not found. Verify the path is correct relative to vault root."
        elif status_code == 400:
            return f"Bad request: {response.text}"
        elif status_code == 500:
            return "Internal server error in Obsidian API."
        else:
            return f"HTTP {status_code}: {response.text}"

    def get(self, endpoint: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Send GET request.

        Args:
            endpoint: API endpoint
            headers: Optional headers
            params: Optional query parameters

        Returns:
            Tuple of (success, response_data, error_message)
        """
        return self._make_request("GET", endpoint, headers=headers, params=params)

    def post(self, endpoint: str, data: Optional[str] = None, json_data: Optional[Dict] = None, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Send POST request.

        Args:
            endpoint: API endpoint
            data: Request body (string)
            json_data: JSON request body (dict)
            headers: Optional headers
            params: Query parameters

        Returns:
            Tuple of (success, response_data, error_message)
        """
        return self._make_request("POST", endpoint, data=data, json_data=json_data, headers=headers, params=params)

    def put(self, endpoint: str, data: Optional[str] = None, headers: Optional[Dict] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Send PUT request.

        Args:
            endpoint: API endpoint
            data: Request body (string)
            headers: Optional headers

        Returns:
            Tuple of (success, response_data, error_message)
        """
        return self._make_request("PUT", endpoint, data=data, headers=headers)

    def patch(self, endpoint: str, json_data: Dict, headers: Optional[Dict] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Send PATCH request.

        Args:
            endpoint: API endpoint
            json_data: JSON request body (dict)
            headers: Optional headers

        Returns:
            Tuple of (success, response_data, error_message)
        """
        return self._make_request("PATCH", endpoint, json_data=json_data, headers=headers)

    def delete(self, endpoint: str, headers: Optional[Dict] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Send DELETE request.

        Args:
            endpoint: API endpoint
            headers: Optional headers

        Returns:
            Tuple of (success, response_data, error_message)
        """
        return self._make_request("DELETE", endpoint, headers=headers)

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Obsidian API.

        Returns:
            Tuple of (success, message)
        """
        success, data, error = self.get("/")

        if success:
            if isinstance(data, dict):
                version = data.get('versions', {}).get('self', 'unknown')
                return True, f"Connected to Obsidian Local REST API v{version}"
            return True, "Connected to Obsidian Local REST API"
        else:
            return False, error or "Connection failed"

    def _get_vault_path(self) -> Optional[str]:
        """
        Get vault path from config, prompting if not set.

        Returns:
            Vault path or None if user declines
        """
        # Check if already loaded
        vault_path = self._load_config_value("vault_path")

        if vault_path:
            return vault_path

        # Vault path not configured, prompt user
        print("\n" + "=" * 60)
        print("⚠️  Filesystem Fallback Required")
        print("=" * 60)
        print("The Obsidian API operation failed or timed out.")
        print("To continue, please provide your Obsidian vault path.")
        print("This enables direct file access as a fallback.")
        print()
        print("You can find your vault path in Obsidian:")
        print("  Settings → About → Vault folder path")
        print()

        vault_input = input("Enter vault path (or press Enter to cancel): ").strip()

        if not vault_input:
            return None

        vault_path = Path(vault_input).expanduser()

        # Validate path
        if not vault_path.exists():
            print(f"❌ Path does not exist: {vault_path}", file=sys.stderr)
            return None

        if not vault_path.is_dir():
            print(f"❌ Path is not a directory: {vault_path}", file=sys.stderr)
            return None

        # Save to config for future use
        print(f"✅ Vault path validated: {vault_path}")
        print("Saving to configuration...")

        # Load full config
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        from config_helper import load_config, save_config
        config = load_config()
        config['vault_path'] = str(vault_path)

        if save_config(config):
            print("✅ Configuration saved. Future operations will use filesystem fallback automatically.")
            return str(vault_path)
        else:
            print("⚠️  Could not save configuration, but continuing with this session.")
            return str(vault_path)

    def _try_filesystem_fallback(self, operation: str, note_path: str, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """
        Attempt operation via filesystem fallback.

        Args:
            operation: Operation type ('read', 'write', 'append')
            note_path: Note path relative to vault
            **kwargs: Operation-specific arguments

        Returns:
            Tuple of (success, data, error_message)
        """
        vault_path = self._get_vault_path()

        if not vault_path:
            return False, None, "Filesystem fallback requires vault path (operation cancelled by user)"

        try:
            from filesystem_ops import FilesystemOperations
            fs = FilesystemOperations(vault_path)

            if operation == 'read':
                return fs.read_note(note_path)
            elif operation == 'write':
                content = kwargs.get('content', '')
                return fs.write_note(note_path, content)
            elif operation == 'append':
                content = kwargs.get('content', '')
                heading = kwargs.get('heading')
                return fs.append_note(note_path, content, heading)
            else:
                return False, None, f"Unknown operation: {operation}"

        except Exception as e:
            return False, None, f"Filesystem fallback failed: {str(e)}"

    def get_with_fallback(self, note_path: str) -> Tuple[bool, Any, Optional[str]]:
        """
        GET request with filesystem fallback.

        Args:
            note_path: Note path for reading (e.g., "Daily/note.md")

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"
        success, data, error = self.get(endpoint)

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API read failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('read', note_path)

    def put_with_fallback(self, note_path: str, content: str) -> Tuple[bool, Any, Optional[str]]:
        """
        PUT request with filesystem fallback.

        Args:
            note_path: Note path for writing
            content: Note content

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"
        success, data, error = self.put(
            endpoint,
            data=content,
            headers={"Content-Type": "text/markdown"}
        )

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API write failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('write', note_path, content=content)

    def append_with_fallback(self, note_path: str, content: str, heading: Optional[str] = None) -> Tuple[bool, Any, Optional[str]]:
        """
        Append operation with filesystem fallback.

        Args:
            note_path: Note path for appending
            content: Content to append
            heading: Optional heading to insert after

        Returns:
            Tuple of (success, data, error_message)
        """
        # Try API first
        endpoint = f"/vault/{note_path}"

        if heading:
            # Use PATCH for targeted insertion
            success, data, error = self.patch(
                endpoint,
                json_data={"content": content, "heading": heading}
            )
        else:
            # Use POST for simple append
            success, data, error = self.post(
                endpoint,
                data=content,
                headers={"Content-Type": "text/markdown"}
            )

        if success:
            return True, data, None

        # API failed, log and try filesystem
        print(f"ℹ️  API append failed ({error}), trying filesystem fallback...")
        return self._try_filesystem_fallback('append', note_path, content=content, heading=heading)


def get_client() -> ObsidianClient:
    """
    Get a configured Obsidian API client instance.

    Returns:
        ObsidianClient instance with configuration loaded from environment/files
    """
    return ObsidianClient()
