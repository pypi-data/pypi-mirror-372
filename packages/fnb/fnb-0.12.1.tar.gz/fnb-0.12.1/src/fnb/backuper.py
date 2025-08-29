"""Backup operations for fnb (Fetch'n'Backup) tool.

This module handles local-to-external backup operations using rsync.
Supports backing up to cloud storage, NAS devices, or external drives.

Key features:
- Local directory → External storage transfer
- Uses rsync via gear.run_rsync for reliable copying
- Reads configuration from [backup.LABEL] sections in config.toml
- Supports various external destinations (OneDrive, NAS, etc.)

Separated from fetcher.py to allow for future specialization:
    - Adding snapshot-style folder naming (e.g., YYYY-MM-DD/)
    - Cloud API integration or notifications
    - Verification or checksum logic post-backup
"""

import subprocess

from fnb.config import RsyncTaskConfig
from fnb.gear import run_rsync, verify_directory
from fnb.logger import get_logger

logger = get_logger(__name__)


def run(
    task: RsyncTaskConfig, dry_run: bool = False, create_dirs: bool = False
) -> bool:
    """Execute a backup operation to copy local data to external storage destinations.

    Performs an rsync-based backup operation that copies data from local storage to
    external destinations like cloud storage, NAS devices, or external drives. Validates
    both source and target directories and provides comprehensive error handling.

    Args:
        task: The backup task configuration defining source, target, and rsync options.
            Must be a valid RsyncTaskConfig configured for backup operations.
        dry_run: If True, performs a preview run showing what would be transferred
            without actually moving files. Automatically adds --dry-run to rsync options.
        create_dirs: If True, automatically creates both source and target directories
            if they don't exist. If False, the operation fails if either directory is missing.

    Returns:
        bool: True if the backup operation completed successfully, False if there
        were recoverable errors like directory access issues.

    Raises:
        ValueError: If task is None or contains invalid configuration.
        FileNotFoundError: If source or target directories don't exist and create_dirs=False,
            or if configuration references non-existent paths.
        subprocess.CalledProcessError: If the rsync command execution fails with
            a non-zero exit code, indicating transfer or permission errors.
        Exception: For unexpected errors during file system operations, permission
            issues, or other system-level failures.

    Examples:
        Basic backup operation:

        >>> task = RsyncTaskConfig(
        ...     label="documents", host="none", source="./documents/",
        ...     target="/mnt/backup/documents/", options=["-av"], enabled=True
        ... )
        >>> result = run(task)
        Backing up documents from ./documents/ to /mnt/backup/documents/
        Backup completed successfully: documents
        >>> result
        True

        Dry run to preview changes:

        >>> result = run(task, dry_run=True)
        Backing up documents from ./documents/ to /mnt/backup/documents/
        (DRY RUN - no files will be modified)
        Backup completed successfully: documents
        >>> result
        True

        Backup with automatic directory creation:

        >>> result = run(task, create_dirs=True)
        Created directory: ./documents
        Created directory: /mnt/backup/documents
        Backing up documents from ./documents/ to /mnt/backup/documents/
        >>> result
        True

        Handle missing source directory:

        >>> result = run(task, create_dirs=False)  # source doesn't exist
        Source directory error: Directory does not exist: ./documents
        >>> result
        False

        Handle missing target directory:

        >>> result = run(task, create_dirs=False)  # target doesn't exist
        Target directory error: Directory does not exist: /mnt/backup/documents
        >>> result
        False

        Backup with rsync options:

        >>> task.options = ["-av", "--delete", "--exclude=*.tmp"]
        >>> result = run(task)
        Backing up documents from ./documents/ to /mnt/backup/documents/
        >>> result
        True
    """
    if task is None:
        raise ValueError("Task cannot be None")

    source = task.rsync_source
    target = task.rsync_target
    options = task.options.copy()

    if dry_run and "--dry-run" not in options:
        options.append("--dry-run")

    try:
        print(f"Backing up {task.label}")  # User-facing output
        logger.debug(f"Backing up {task.label} from {source} to {target}")
        if dry_run:
            print("(DRY RUN - no files will be modified)")  # User-facing output

        # Ensure source directory exists (for backup, source is always local)
        try:
            verify_directory(source, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Source directory error: {e}")
            return False

        # Ensure target directory exists (for backup, source is always local)
        try:
            verify_directory(target, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Target directory error: {e}")
            return False

        run_rsync(source=source, target=target, options=options, ssh_password=None)

        print(f"Backup completed successfully: {task.label}")  # User-facing output
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed with error code {e.returncode}: {task.label}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        logger.error(f"Backup failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/backuper.py

    """
    from pathlib import Path

    from fnb.reader import ConfigReader

    config_path = Path("examples/config.toml")
    reader = ConfigReader(config_path)
    task = reader.config.get_task_by_label("backup", "logs")
    if task:
        run(task=task, dry_run=True, create_dirs=False)
