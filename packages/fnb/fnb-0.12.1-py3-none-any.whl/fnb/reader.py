"""Configuration file discovery and loading for fnb.

This module handles the discovery, loading, and validation of fnb configuration
files from multiple standard locations. It provides comprehensive error handling
and environment variable expansion for configuration values.
"""

import os
import tomllib
from pathlib import Path
from typing import Any

import platformdirs

from fnb.config import FnbConfig
from fnb.gear import verify_directory
from fnb.logger import get_logger

logger = get_logger(__name__)


class ConfigReader:
    """Configuration file reader and validator for fnb tasks.

    This class handles the discovery, loading, and validation of fnb configuration
    files. It supports automatic config file detection across standard locations
    and provides comprehensive error handling for configuration issues.

    Attributes:
        config_path: Path to the loaded configuration file.
        config: Validated FnbConfig object containing all task configurations.
    """

    def __init__(self, config_path: Path | None = None):
        """Initialize a ConfigReader with automatic config discovery.

        Loads and validates an fnb configuration file, either from the specified
        path or by searching standard locations. Automatically expands environment
        variables in configuration values.

        Args:
            config_path: Explicit path to config file. If None, auto-detects by
                searching in order: ./fnb.toml, ./config.toml, config/*.toml,
                ~/.config/fnb/config.toml, ~/.config/fnb/*.toml

        Raises:
            FileNotFoundError: If no config file found in any search location.
            ValueError: If config file contains invalid TOML syntax or doesn't
                match the expected schema for fnb configurations.

        Examples:
            Load config with auto-detection:

            >>> reader = ConfigReader()
            >>> print(reader.config_path)  # doctest output
            ./fnb.toml

            Load specific config file:

            >>> reader = ConfigReader(Path("/path/to/custom.toml"))
            >>> len(reader.config.fetch)
            3

            Handle missing config file:

            >>> reader = ConfigReader(Path("/nonexistent.toml"))
            FileNotFoundError: Config file not found: /nonexistent.toml
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_file(self.config_path)
        self._expand_env_vars()

    def _load_file(self, path: Path) -> FnbConfig:
        """Load a TOML config file and convert to FnbConfig.

        Args:
            path (Path): Path to the config file.

        Returns:
            FnbConfig: The parsed config.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file is invalid TOML or doesn't match the expected schema.

        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            with path.open("rb") as f:
                raw_data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML in config file {path}: {e}")
        except Exception as e:
            raise ValueError(f"Error reading config file {path}: {e}")

        try:
            return FnbConfig.model_validate(raw_data)  # type: ignore[no-any-return]
        except Exception as e:
            raise ValueError(f"Invalid config schema in {path}: {e}")

    def _get_default_config_path(self) -> Path:
        """Discover config file by searching standard locations in priority order.

        Implements fnb's config file discovery algorithm, searching multiple
        locations in order of priority: current directory, user config directory,
        and glob patterns for flexible config organization.

        Returns:
            Path: Path to the first config file found in the search order.

        Raises:
            FileNotFoundError: If no config file exists in any of the standard
                locations. Error message includes all searched paths.

        Examples:
            Successful discovery:

            >>> reader = ConfigReader()
            >>> path = reader._get_default_config_path()
            >>> print(path)  # doctest output
            ./fnb.toml

            Search order when no local config exists:

            # Searches: ./fnb.toml, ./config.toml, ./config/*.toml,
            # ~/.config/fnb/config.toml, ~/.config/fnb/*.toml
        """
        app_name = "fnb"
        config_dir = platformdirs.user_config_path(app_name)
        candidates = [
            Path("./fnb.toml"),
            Path("./config.toml"),
            *sorted(Path("./config/").glob("*.toml")),
            config_dir / "config.toml",
            *sorted(config_dir.glob("*.toml")),
        ]

        for path in candidates:
            if path.exists():
                return path  # type: ignore[no-any-return]

        # Build a more helpful error message
        searched_paths = "\n - ".join([str(p) for p in candidates])
        raise FileNotFoundError(
            f"No config file found in expected locations:\n - {searched_paths}\n"
            "Run 'fnb init' to create one in the current directory."
        )

    def _expand_env_vars(self) -> None:
        """Expand environment variables in path strings within the config."""

        def expand(obj: Any) -> Any:
            """Recursively expand env vars in strings or collections."""
            if isinstance(obj, str):
                # Expand environment variables
                return os.path.expandvars(obj)
            elif isinstance(obj, list):
                return [expand(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: expand(v) for k, v in obj.items()}
            else:
                return obj

        for section in ("fetch", "backup"):
            section_data = getattr(self.config, section)
            for key, task in section_data.items():
                updated = task.model_dump()
                expanded = expand(updated)
                section_data[key] = task.model_validate(expanded)

    def print_status(self, check_dirs: bool = True) -> None:
        """Display a comprehensive status summary of all configured tasks.

        Prints an organized overview of both fetch and backup tasks, showing
        source/target paths, enabled status, and directory existence checks.
        This provides users with a complete picture of their fnb configuration.

        Args:
            check_dirs: If True, validates that local target directories exist
                and reports their status. Remote paths are skipped from validation.

        Returns:
            None: Prints formatted status information to stdout.

        Examples:
            Basic status display:

            >>> reader = ConfigReader()
            >>> reader.print_status()
            📄 Config file: ./fnb.toml

            📦 Fetch Tasks (remote → local):
             ✅ logs: user@server:~/logs/ → ./backup/logs/
                📁 Target for logs exists: ./backup/logs

            💾 Backup Tasks (local → external):
             ✅ logs: ./backup/logs/ → /mnt/external/backup/
                📁 Target for logs exists: /mnt/external/backup

            Status without directory checking:

            >>> reader.print_status(check_dirs=False)
            📄 Config file: ./fnb.toml

            📦 Fetch Tasks (remote → local):
             ✅ logs: user@server:~/logs/ → ./backup/logs/

            💾 Backup Tasks (local → external):
             ✅ logs: ./backup/logs/ → /mnt/external/backup/
        """
        print(f"📄 Config file: {self.config_path}")

        self._print_fetch_tasks(check_dirs)
        self._print_backup_tasks(check_dirs)

        print("")  # Add final empty line

    def _print_fetch_tasks(self, check_dirs: bool) -> None:
        """Print status of fetch tasks.

        Args:
            check_dirs (bool): If True, check if directories exist.
        """
        print("\n📦 Fetch Tasks (remote → local):")
        fetch_tasks = self.config.get_enabled_tasks("fetch")
        if not fetch_tasks:
            print(" ❌ No enabled fetch tasks")
            return

        for task in fetch_tasks:
            print(f" ✅ {task.label}: {task.rsync_source} → {task.rsync_target}")

            # Check if target directory exists (local paths only)
            if check_dirs and ":" not in task.rsync_target:  # Local paths only
                self._check_directory(task.rsync_target, f"Target for {task.label}")

    def _print_backup_tasks(self, check_dirs: bool) -> None:
        """Print status of backup tasks.

        Args:
            check_dirs (bool): If True, check if directories exist.
        """
        print("\n💾 Backup Tasks (local → external):")
        backup_tasks = self.config.get_enabled_tasks("backup")
        if not backup_tasks:
            print(" ❌ No enabled backup tasks")
            return

        for task in backup_tasks:
            print(f" ✅ {task.label}: {task.rsync_source} → {task.rsync_target}")

            # Check if target directory exists (local paths only)
            if check_dirs and ":" not in task.rsync_target:  # Local paths only
                self._check_directory(task.rsync_target, f"Target for {task.label}")

    def _check_directory(self, path: str, label: str) -> None:
        """Check if a directory exists and print status.

        Args:
            path (str): Path to check
            label (str): Label to display in output
        """
        try:
            dir_path = verify_directory(path)
            print(f"    📁 {label} exists: {dir_path}")
        except FileNotFoundError:
            print(f"    ⚠️  {label} does not exist: {path}")
        except ValueError as e:
            print(f"    ⚠️  {label} issue: {e}")


if __name__ == "__main__":
    """Self test.

    $ uv run python src/fnb/reader.py

    """
    reader = ConfigReader()
    config = reader.config

    logger.info("📦 Enabled Fetch Tasks:")
    for task in config.get_enabled_tasks("fetch"):
        logger.info(f" - {task.label}: {task.source} → {task.target}")

    logger.info("\n💾 Enabled Backup Tasks:")
    for task in config.get_enabled_tasks("backup"):
        logger.info(f" - {task.label}: {task.source} → {task.target}")

    reader.print_status()
