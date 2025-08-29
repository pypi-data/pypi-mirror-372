"""Fetch operations for fnb (Fetch'n'Backup) tool.

This module handles remote-to-local fetch operations using rsync with SSH
authentication. Provides reliable data transfer from remote servers to local
storage with comprehensive error handling.

Key features:
- Remote server → Local directory transfer
- Uses rsync via gear.run_rsync for reliable copying
- SSH-based transfer with optional password automation
- Reads configuration from [fetch.LABEL] sections in config.toml

Separated from backuper.py for clarity and future extensibility:
    - Adding delay or throttling between fetches
    - Supporting different types of remote automation
    - Custom handling for partial/incremental fetch
"""

import subprocess

from fnb.config import RsyncTaskConfig
from fnb.env import get_ssh_password
from fnb.gear import run_rsync, verify_directory
from fnb.logger import get_logger

logger = get_logger(__name__)


def run(
    task: RsyncTaskConfig,
    dry_run: bool = False,
    ssh_password: str | None = None,
    create_dirs: bool = False,
) -> bool:
    """Execute a fetch operation to download data from remote server to local storage.

    Performs an rsync-based fetch operation that downloads data from a remote server
    to local storage. Handles SSH authentication, directory validation, and provides
    comprehensive error handling for various failure scenarios.

    Args:
        task: The fetch task configuration defining source, target, and options.
            Must be a valid RsyncTaskConfig with appropriate fetch settings.
        dry_run: If True, performs a preview run showing what would be transferred
            without actually moving files. Automatically adds --dry-run to rsync options.
        ssh_password: SSH password for remote authentication. If None, attempts to
            retrieve password from environment variables based on task host. If no
            password is found, falls back to interactive password prompts. For local
            tasks (host="none"), this parameter is ignored with a warning.
        create_dirs: If True, automatically creates the target directory if it doesn't
            exist. If False, the operation fails if the target directory is missing.

    Returns:
        bool: True if the fetch operation completed successfully, False if there
        were recoverable errors like directory issues.

    Raises:
        ValueError: If task is None or contains invalid configuration.
        FileNotFoundError: If target directory doesn't exist and create_dirs=False,
            or if configuration references non-existent paths.
        subprocess.CalledProcessError: If the rsync command execution fails with
            a non-zero exit code, indicating transfer errors.
        Exception: For unexpected errors during SSH authentication, network issues,
            or other system-level failures.

    Examples:
        Basic fetch operation:

        >>> task = RsyncTaskConfig(
        ...     label="logs", host="user@server", source="~/logs/",
        ...     target="./backup/logs/", options=["-av"], enabled=True
        ... )
        >>> result = run(task)
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        Fetch completed successfully: logs
        >>> result
        True

        Dry run to preview changes:

        >>> result = run(task, dry_run=True)
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        (DRY RUN - no files will be modified)
        Fetch completed successfully: logs
        >>> result
        True

        Fetch with automatic directory creation:

        >>> result = run(task, create_dirs=True)
        Created directory: ./backup/logs
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        >>> result
        True

        Fetch with SSH password override:

        >>> result = run(task, ssh_password="mypassword")
        Using SSH password from command line for host: user@server
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        >>> result
        True

        Handle missing target directory:

        >>> result = run(task, create_dirs=False)  # target doesn't exist
        Target directory error: Directory does not exist: ./backup/logs
        >>> result
        False
    """
    if task is None:
        raise ValueError("Task cannot be None")

    if not task.is_remote:
        if ssh_password:
            logger.warning("SSH password provided for local task, ignoring")
        ssh_password = None
    elif ssh_password is None and task.is_remote:
        # Try to get the password from environment variables
        ssh_password = get_ssh_password(task.host)
        if ssh_password:
            logger.info(f"Using SSH password from environment for host: {task.host}")

    source = task.rsync_source
    target = task.rsync_target
    options = task.options.copy()

    if dry_run and "--dry-run" not in options:
        options.append("--dry-run")

    try:
        print(f"Fetching {task.label}")  # User-facing output
        logger.debug(f"Fetching {task.label} from {source} to {target}")
        if dry_run:
            print("(DRY RUN - no files will be modified)")  # User-facing output

        # For fetch, we only need to verify the target directory exists
        # Target is always local in fetch operations
        try:
            verify_directory(target, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Target directory error: {e}")
            return False

        run_rsync(
            source=source,
            target=target,
            options=options,
            ssh_password=ssh_password,
        )

        print(f"Fetch completed successfully: {task.label}")  # User-facing output
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Fetch failed with error code {e.returncode}: {task.label}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        logger.error(f"Fetch failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/fetcher.py

    """
    from pathlib import Path

    from fnb.reader import ConfigReader

    config_path = Path("examples/config.toml")
    reader = ConfigReader(config_path)
    task = reader.config.get_task_by_label("fetch", "logs")
    if task:
        run(task=task, dry_run=True, ssh_password=None, create_dirs=False)
