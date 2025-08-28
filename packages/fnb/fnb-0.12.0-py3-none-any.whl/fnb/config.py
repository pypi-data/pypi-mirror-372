"""Configuration data models and validation for fnb (Fetch'n'Backup).

This module defines Pydantic models for representing and validating fnb task
configurations. It provides the core data structures used throughout the
application for managing fetch and backup operations.
"""

import tomllib
from pathlib import Path
from typing import Literal, Any

from pydantic import BaseModel

from fnb.logger import get_logger

logger = get_logger(__name__)


class RsyncTaskConfig(BaseModel):
    """Configuration model for a single rsync task in fnb.

    This Pydantic model represents a single task configuration that defines
    how data should be transferred using rsync. Tasks can be either fetch
    (remote → local) or backup (local → external) operations.

    The model provides validation for all configuration fields and computed
    properties to generate properly formatted rsync source/target paths.

    Attributes:
        label: Unique identifier for the task within its category (fetch/backup).
            Used to reference the task from CLI commands.
        summary: Human-readable description of what this task does.
            Displayed in status reports and helps document the task purpose.
        host: Remote host specification. Format "user@hostname" for remote
            operations, or "none" for local-only operations.
        source: Source path for the rsync operation. Can be absolute or relative.
            For remote tasks, this is the path on the remote host.
        target: Target path for the rsync operation. Can be absolute or relative.
            For fetch tasks, this is typically a local path.
        options: List of rsync command-line options to include in the operation.
            Common options: ["-auvz", "--delete", "--exclude=pattern"].
        enabled: Whether this task is active and should be executed.
            Disabled tasks are ignored by all operations.

    Examples:
        Remote fetch task configuration:

        >>> task = RsyncTaskConfig(
        ...     label="logs",
        ...     summary="Download server logs",
        ...     host="user@server.example.com",
        ...     source="~/logs/",
        ...     target="./backup/logs/",
        ...     options=["-auvz", "--delete"],
        ...     enabled=True
        ... )
        >>> task.is_remote
        True
        >>> task.rsync_source
        'user@server.example.com:~/logs/'

        Local backup task configuration:

        >>> task = RsyncTaskConfig(
        ...     label="documents",
        ...     summary="Backup documents to external drive",
        ...     host="none",
        ...     source="./documents/",
        ...     target="/mnt/backup/documents/",
        ...     options=["-av", "--exclude=*.tmp"],
        ...     enabled=True
        ... )
        >>> task.is_remote
        False
        >>> task.rsync_source
        './documents/'
    """

    label: str
    summary: str
    host: str
    source: str
    target: str
    options: list[str]
    enabled: bool = True

    @property
    def is_remote(self) -> bool:
        """Determine if this task requires remote SSH connections.

        Checks the host field to determine whether this task involves remote
        operations that require SSH authentication and network connectivity.

        Returns:
            bool: True if the task involves a remote host (host != "none"),
            False for local-only operations.

        Examples:
            Remote task detection:

            >>> task = RsyncTaskConfig(host="user@server.com", ...)
            >>> task.is_remote
            True

            Local task detection:

            >>> task = RsyncTaskConfig(host="none", ...)
            >>> task.is_remote
            False

            Case insensitive:

            >>> task = RsyncTaskConfig(host="NONE", ...)
            >>> task.is_remote
            False
        """
        return self.host.lower() != "none"

    @property
    def rsync_source(self) -> str:
        """Generate properly formatted rsync source path.

        Creates the source path string in the format expected by rsync,
        automatically prefixing with host information for remote operations.

        Returns:
            str: For remote tasks, returns "host:source". For local tasks,
            returns source path unchanged.

        Examples:
            Remote task source formatting:

            >>> task = RsyncTaskConfig(
            ...     host="user@server.com", source="~/data/", ...
            ... )
            >>> task.rsync_source
            'user@server.com:~/data/'

            Local task source (no formatting):

            >>> task = RsyncTaskConfig(
            ...     host="none", source="./local/data/", ...
            ... )
            >>> task.rsync_source
            './local/data/'
        """
        return f"{self.host}:{self.source}" if self.is_remote else self.source

    @property
    def rsync_target(self) -> str:
        """Get the target path for rsync operations.

        Returns the target path as configured, without modification.
        For fnb's typical usage patterns, targets are usually local paths.

        Returns:
            str: The target path exactly as configured in the task.

        Examples:
            Local target path:

            >>> task = RsyncTaskConfig(target="./backup/data/", ...)
            >>> task.rsync_target
            './backup/data/'

            Absolute target path:

            >>> task = RsyncTaskConfig(target="/mnt/backup/data/", ...)
            >>> task.rsync_target
            '/mnt/backup/data/'
        """
        return self.target


class FnbConfig(BaseModel):
    """Main configuration container for fnb (Fetch'n'Backup) applications.

    This Pydantic model represents the complete configuration structure for fnb,
    containing all fetch and backup task definitions. It provides methods to
    query and filter tasks based on various criteria.

    The configuration typically maps to a TOML file structure with [fetch.label]
    and [backup.label] sections, where each section defines a single task.

    Attributes:
        fetch: Dictionary mapping task labels to fetch task configurations.
            Keys are task labels, values are RsyncTaskConfig objects.
        backup: Dictionary mapping task labels to backup task configurations.
            Keys are task labels, values are RsyncTaskConfig objects.

    Examples:
        Basic configuration structure:

        >>> config = FnbConfig(
        ...     fetch={
        ...         "logs": RsyncTaskConfig(
        ...             label="logs", host="user@server", source="~/logs/",
        ...             target="./backup/logs/", options=["-av"], enabled=True
        ...         )
        ...     },
        ...     backup={
        ...         "logs": RsyncTaskConfig(
        ...             label="logs", host="none", source="./backup/logs/",
        ...             target="/mnt/backup/", options=["-av"], enabled=True
        ...         )
        ...     }
        ... )
        >>> len(config.fetch)
        1
        >>> len(config.backup)
        1

        Query enabled tasks:

        >>> enabled_fetch = config.get_enabled_tasks("fetch")
        >>> len(enabled_fetch)
        1

        Find task by label:

        >>> task = config.get_task_by_label("fetch", "logs")
        >>> task.label
        'logs'
    """

    fetch: dict[str, RsyncTaskConfig] = {}
    backup: dict[str, RsyncTaskConfig] = {}

    def get_enabled_tasks(
        self, kind: Literal["fetch", "backup"]
    ) -> list[RsyncTaskConfig]:
        """Retrieve all enabled tasks of the specified type.

        Filters the task configurations to return only those marked as enabled,
        which are the tasks that should be executed by fnb operations.

        Args:
            kind: Type of tasks to retrieve, either "fetch" or "backup".

        Returns:
            list[RsyncTaskConfig]: List of enabled task configurations.
            Empty list if no enabled tasks of the specified kind exist.

        Examples:
            Get enabled fetch tasks:

            >>> config = FnbConfig(fetch={"task1": RsyncTaskConfig(..., enabled=True)})
            >>> tasks = config.get_enabled_tasks("fetch")
            >>> len(tasks)
            1

            No enabled tasks:

            >>> config = FnbConfig(fetch={"task1": RsyncTaskConfig(..., enabled=False)})
            >>> tasks = config.get_enabled_tasks("fetch")
            >>> len(tasks)
            0
        """
        tasks: dict[str, RsyncTaskConfig] = getattr(self, kind)
        return [task for task in tasks.values() if task.enabled]

    def get_task_by_label(
        self, kind: Literal["fetch", "backup"], label: str
    ) -> RsyncTaskConfig | None:
        """Find a specific task by its label within a task category.

        Searches through tasks of the specified kind to find one with the
        matching label. Labels are unique within each category (fetch/backup)
        but can be reused across categories.

        Args:
            kind: Category of task to search ("fetch" or "backup").
            label: The task label to search for. Case-sensitive.

        Returns:
            RsyncTaskConfig | None: The matching task configuration if found,
            None if no task with the specified label exists in the category.

        Examples:
            Find existing task:

            >>> config = FnbConfig(
            ...     fetch={"logs": RsyncTaskConfig(label="logs", ...)}
            ... )
            >>> task = config.get_task_by_label("fetch", "logs")
            >>> task.label
            'logs'

            Task not found:

            >>> task = config.get_task_by_label("fetch", "nonexistent")
            >>> task is None
            True

            Same label in different categories:

            >>> config = FnbConfig(
            ...     fetch={"data": RsyncTaskConfig(label="data", ...)},
            ...     backup={"data": RsyncTaskConfig(label="data", ...)}
            ... )
            >>> fetch_task = config.get_task_by_label("fetch", "data")
            >>> backup_task = config.get_task_by_label("backup", "data")
            >>> fetch_task is not backup_task
            True
        """
        tasks = getattr(self, kind)
        for task in tasks.values():
            if task.label == label:
                return task  # type: ignore[no-any-return]
        return None


def load_config(path: Path) -> FnbConfig:
    """Load and validate fnb configuration from a TOML file.

    Reads a TOML configuration file and converts it into a validated FnbConfig
    object. Performs comprehensive validation of the file format, syntax, and
    schema compliance to ensure the configuration is usable by fnb operations.

    Args:
        path: Path to the TOML configuration file to load. Must be readable
            and contain valid TOML syntax with fnb-compatible structure.

    Returns:
        FnbConfig: Validated configuration object containing all task definitions
        parsed from the TOML file.

    Raises:
        FileNotFoundError: If the specified configuration file doesn't exist
            or cannot be accessed.
        ValueError: If the file contains invalid TOML syntax, or if the content
            doesn't match the expected fnb configuration schema.
        Exception: For other file system errors during reading or unexpected
            parsing failures.

    Examples:
        Load valid configuration:

        >>> config = load_config(Path("./fnb.toml"))
        >>> len(config.fetch)
        2
        >>> len(config.backup)
        1

        Handle missing file:

        >>> config = load_config(Path("./missing.toml"))
        FileNotFoundError: Configuration file not found at ./missing.toml

        Handle invalid TOML:

        >>> # File contains: [fetch.task1 label = "missing quote
        >>> config = load_config(Path("./bad.toml"))
        ValueError: Invalid TOML file at ./bad.toml: Expected '"' at line 1 col 45

        Handle schema validation error:

        >>> # File missing required 'source' field
        >>> config = load_config(Path("./incomplete.toml"))
        ValueError: Configuration validation failed: Field required: source
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {path}")

    try:
        with path.open("rb") as f:
            data: dict[str, Any] = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML file at {path}: {e}")
    except Exception as e:
        raise Exception(f"Error reading configuration file at {path}: {e}")

    try:
        return FnbConfig.model_validate(data)  # type: ignore[no-any-return]
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


if __name__ == "__main__":
    """Self test

    $ uv run python src/fnb/config.py

    """
    config = load_config(Path("examples/config.toml"))

    logger.info("\nEnabled Fetch Tasks:")
    for task in config.get_enabled_tasks("fetch"):
        logger.info(f" - {task.label}: {task.source} -> {task.target}")

    logger.info("\nEnabled Backup Tasks:")
    for task in config.get_enabled_tasks("backup"):
        logger.info(f" - {task.label}: {task.source} -> {task.target}")
