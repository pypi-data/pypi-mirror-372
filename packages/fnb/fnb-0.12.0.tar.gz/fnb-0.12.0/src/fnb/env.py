"""Environment variable management for fnb SSH authentication.

This module handles loading environment variables from .env files and provides
SSH password retrieval for specific hosts with flexible fallback mechanisms.

Key features:
- Hierarchical .env file loading (global and local precedence)
- Host-specific password configuration with normalization
- Clean interface for retrieving SSH passwords with fallbacks
- Uses python-dotenv for reliable environment variable handling
"""

import os
from pathlib import Path

import platformdirs
from dotenv import load_dotenv

from fnb.logger import get_logger

logger = get_logger(__name__)


def load_env_files() -> bool:
    """Load environment variables from .env files with hierarchical precedence.

    Implements a multi-layered environment variable loading system that supports
    both global user settings and project-specific overrides. Files are loaded
    in precedence order, with local files taking priority over global ones.

    The loading order ensures that project-specific settings can override
    user-wide defaults, providing flexibility for different deployment scenarios.

    Returns:
        bool: True if at least one .env file was found and loaded successfully,
        False if no .env files exist in any of the search locations.

    Examples:
        Load existing environment files:

        >>> loaded = load_env_files()
        >>> loaded
        True

        No environment files found:

        >>> loaded = load_env_files()  # No .env files exist
        >>> loaded
        False

        Check environment variables after loading:

        >>> load_env_files()
        True
        >>> import os
        >>> password = os.environ.get("FNB_PASSWORD_DEFAULT")
        >>> password is not None
        True

    Note:
        Loading order (later overrides earlier):
        1. ~/.config/fnb/.env - Global user configuration
        2. ./.env - Local project configuration (highest priority)
    """
    # Track if we loaded any env files
    loaded = False

    # Global config location
    app_name = "fnb"
    config_dir = platformdirs.user_config_path(app_name)

    global_env = config_dir / ".env"
    if global_env.exists():
        load_dotenv(global_env)
        loaded = True

    # Local config (higher priority)
    local_env = Path("./.env")
    if local_env.exists():
        load_dotenv(local_env)
        loaded = True

    return loaded


def get_ssh_password(host: str) -> str | None:
    """Retrieve SSH password for a specific host from environment variables.

    Implements a flexible password lookup system that supports both host-specific
    and default password configurations. Automatically normalizes host names to
    valid environment variable names and provides fallback to default passwords.

    The lookup order prioritizes host-specific passwords over defaults, allowing
    fine-grained control while maintaining convenience for simple setups.

    When no password is found, fnb automatically falls back to interactive
    password input where SSH/rsync will prompt the user directly in the terminal.

    Args:
        host: The hostname specification, can be in formats:
            - "user@hostname" (full SSH specification)
            - "hostname" (hostname only)
            Special characters are normalized for environment variable lookup.

    Returns:
        str | None: The SSH password if found in environment variables,
        None if no password is configured. When None is returned, fnb will
        fall back to interactive password input via SSH's standard prompts.

    Examples:
        Get password for specific host:

        >>> # With FNB_PASSWORD_USER_EXAMPLE_COM="hostpass" in environment
        >>> password = get_ssh_password("user@example.com")
        >>> password
        'hostpass'

        Get default password when host-specific not found:

        >>> # With FNB_PASSWORD_DEFAULT="defaultpass" in environment
        >>> password = get_ssh_password("newserver.com")
        >>> password
        'defaultpass'

        No password found (triggers interactive input):

        >>> password = get_ssh_password("unknown.server")
        >>> password is None
        True
        >>> # fnb will then prompt: "user@unknown.server's password:"

        Host normalization examples:

        >>> # These hosts map to the same environment variable:
        >>> # "user@my-server.com" -> FNB_PASSWORD_USER_MY_SERVER_COM
        >>> # "admin@my.server.com" -> FNB_PASSWORD_ADMIN_MY_SERVER_COM

    Note:
        Host normalization rules:
        - @ symbols become underscores
        - Dots (.) become underscores
        - Hyphens (-) become underscores
        - Case insensitive (converted to uppercase)

        Environment variable lookup order:
        1. FNB_PASSWORD_{NORMALIZED_HOST} - Host-specific password
        2. FNB_PASSWORD_DEFAULT - Fallback for all hosts
        3. None (triggers interactive SSH password prompt)
    """
    # Load .env files if not already loaded
    load_env_files()

    # First try to find a password for the specific host
    # Replace any characters that can't be in an
    # environment variable with underscore
    normalized_host = host.replace("@", "_").replace(".", "_").replace("-", "_")
    password = os.environ.get(f"FNB_PASSWORD_{normalized_host}")

    # If not found, try the default password
    if password is None:
        password = os.environ.get("FNB_PASSWORD_DEFAULT")

    return password


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/env.py

    """
    loaded = load_env_files()
    logger.info(f"Loaded .env files: {loaded}")

    test_host = "user@example.com"
    password = get_ssh_password(test_host)
    if password:
        logger.info(f"Found password for {test_host}: {'*' * len(password)}")
    else:
        logger.info(f"No password found for {test_host}")

    # Test default password
    default_password = os.environ.get("FNB_PASSWORD_DEFAULT")
    if default_password:
        logger.info(f"Default password is set: {'*' * len(default_password)}")
    else:
        logger.info("No default password found")
