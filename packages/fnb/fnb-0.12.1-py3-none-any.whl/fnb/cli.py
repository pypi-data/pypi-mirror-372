"""Command-line interface entry point for the fnb (Fetch'n'Backup) tool.

This script defines the main CLI commands using Typer framework, providing
a user-friendly interface for backup workflow operations.

Available commands:
- `fetch`: Pull data from remote server to local storage
- `backup`: Push local data to cloud or external backup destinations
- `sync`: Run both fetch and backup operations sequentially
- `status`: Show the current status of all configured tasks
- `init`: Generate initial configuration files (.toml, .env)

Each command delegates to its corresponding module:
- fetch   -> fnb.fetcher
- backup  -> fnb.backuper
- status  -> fnb.reader
- init    -> fnb.generator

Shared options include:
- `--config`: Path to config file (default: auto-detect)
- `--dry-run`: Preview without making changes
- `--ssh-password`: For remote SSH login if required

Configuration is defined in a `config.toml` file, which can be initialized with:
    fnb init

To expose this CLI as a `fnb` command, set up `project.scripts` in pyproject.toml.
"""

from pathlib import Path

import typer

from fnb import __version__
from fnb import backuper, fetcher, generator
from fnb.reader import ConfigReader
from fnb.logger import configure_logger


app = typer.Typer(help="fnb - Fetch'n'Backup")


def setup_logging(
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging (same as --log-level DEBUG)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Enable quiet mode (same as --log-level WARNING)"
    ),
) -> str:
    """Setup logging configuration based on command line arguments.

    Args:
        log_level: Explicit log level
        verbose: Enable verbose mode (DEBUG level)
        quiet: Enable quiet mode (WARNING level)

    Returns:
        The effective log level that was set
    """
    # Determine effective log level
    if verbose:
        effective_level = "DEBUG"
    elif quiet:
        effective_level = "WARNING"
    else:
        effective_level = log_level.upper()

    # Configure loguru
    configure_logger(level=effective_level, enable_file_logging=True)

    return effective_level


@app.command()
def version() -> None:
    """Display the current version of fnb (Fetch'n'Backup) tool.

    This command shows the installed version number of the fnb CLI tool.
    Useful for troubleshooting, compatibility checking, and support requests.

    Returns:
        None: Prints version information to stdout and exits.

    Examples:
        Display current version:

        >>> fnb version
        fnb version 0.10.0
    """
    typer.echo(f"fnb version {__version__}")


@app.command()
def init(
    kind: str = typer.Argument(
        "all", help="Kind of configuration file to generate (all, config, env)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing file without confirmation"
    ),
) -> None:
    """Generate default configuration files for fnb in the current directory.

    Creates template configuration files to help users get started with fnb.
    By default, generates both fnb.toml (task configuration) and .env.plain
    (SSH password template). Individual file types can be specified.

    Args:
        kind: Type of configuration file to generate. Options:
            - "all": Generate both config.toml and .env files (default)
            - "config": Generate only fnb.toml configuration file
            - "env": Generate only .env.plain environment file
        force: If True, overwrite existing files without user confirmation.
            If False, prompts before overwriting existing files.

    Returns:
        None: Creates files in current directory and prints status messages.

    Raises:
        ValueError: If invalid kind argument is provided.
        typer.Exit: If file creation fails or user cancels overwrite.

    Examples:
        Generate all configuration files:

        >>> fnb init
        ✅ Created ./fnb.toml from template.
        ✅ Created ./.env.plain from template.

        Generate only the main config file:

        >>> fnb init config
        ✅ Created ./fnb.toml from template.

        Force overwrite existing files:

        >>> fnb init --force
        ✅ Created ./fnb.toml from template.
        ✅ Created ./.env.plain from template.
    """
    try:
        # Convert str to ConfigKind and delegate to generator module
        config_kind = generator.ConfigKind(kind.lower())
        generator.run(kind=config_kind, force=force)
    except ValueError as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def status(
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging (same as --log-level DEBUG)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Enable quiet mode (same as --log-level WARNING)"
    ),
) -> None:
    """Display a summary of all enabled fetch and backup tasks from configuration.

    Reads the fnb configuration file and displays an organized summary of all
    enabled tasks, showing source and target paths for both fetch and backup
    operations. Also validates that target directories exist locally.

    Args:
        config: Path to configuration file. If None, auto-detects config file
            by searching in standard locations:
            - ./fnb.toml (current directory)
            - ./config.toml
            - ~/.config/fnb/config.toml (user config directory)

    Returns:
        None: Prints task summary to stdout.

    Raises:
        typer.Exit: If no config file found or configuration is invalid.
        FileNotFoundError: If specified config file doesn't exist.
        ValueError: If config file contains invalid TOML or schema errors.

    Examples:
        Show status with auto-detected config:

        >>> fnb status
        📄 Config file: ./fnb.toml

        📦 Fetch Tasks (remote → local):
         ✅ logs: user@server:~/logs/ → ./backup/logs/

        💾 Backup Tasks (local → external):
         ✅ logs: ./backup/logs/ → /mnt/external/backup/

        Use specific config file:

        >>> fnb status --config /path/to/custom.toml
        📄 Config file: /path/to/custom.toml
        ...
    """
    # Setup logging first
    setup_logging(log_level=log_level, verbose=verbose, quiet=quiet)

    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        reader.print_status()
    except FileNotFoundError:
        typer.echo("❌ No config file found. Run 'fnb init' to create one.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def fetch(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    ssh_password: str | None = typer.Option(
        None,
        "--ssh-password",
        "-p",
        help="Password for SSH authentication (overrides .env)",
    ),
    config: str = typer.Option(
        "./fnb.toml", "--config", "-c", help="Path to config file"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging (same as --log-level DEBUG)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Enable quiet mode (same as --log-level WARNING)"
    ),
) -> None:
    """Fetch data from a remote server to local storage using rsync.

    Executes a fetch operation based on the task configuration defined in the
    config file. The fetch operation downloads data from a remote server to
    local storage using rsync with SSH authentication.

    Args:
        label: Task label that identifies the fetch configuration in the
            [fetch.LABEL] section of the config file.
        dry_run: If True, preview the rsync operation without actually
            transferring files. Shows what would be done.
        create_dirs: If True, automatically create the target directory
            if it doesn't exist. If False, operation fails if target missing.
        ssh_password: SSH password for remote authentication. If provided,
            overrides any password defined in .env files. If None, attempts
            to use password from environment variables.
        config: Path to the configuration file containing task definitions.
            Defaults to "./fnb.toml" in current directory.

    Returns:
        None: Executes rsync operation and prints status messages.

    Raises:
        typer.Exit: If operation fails due to:
            - Task label not found in configuration
            - Configuration file not found or invalid
            - Target directory doesn't exist and create_dirs=False
            - rsync command execution failure
            - SSH authentication failure

    Examples:
        Fetch logs from remote server:

        >>> fnb fetch logs
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        Fetch completed successfully: logs

        Preview fetch operation without transferring files:

        >>> fnb fetch logs --dry-run
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        (DRY RUN - no files will be modified)

        Fetch with SSH password and auto-create directories:

        >>> fnb fetch logs --ssh-password mypass --create-dirs
        Using SSH password from command line for host: user@server
        Created directory: ./backup/logs
        Fetching logs from user@server:~/logs/ to ./backup/logs/

        Use custom config file:

        >>> fnb fetch logs --config /path/to/custom.toml
        ...
    """
    # Setup logging first
    setup_logging(log_level=log_level, verbose=verbose, quiet=quiet)

    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        task = reader.config.get_task_by_label("fetch", label)

        if task is None:
            typer.echo(f"❌ Label not found: {label}")
            raise typer.Exit(1)

        fetcher.run(
            task,
            dry_run=dry_run,
            ssh_password=ssh_password,
            create_dirs=create_dirs,
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def backup(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    config: str = typer.Option(
        "./fnb.toml", "--config", "-c", help="Path to config file"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging (same as --log-level DEBUG)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Enable quiet mode (same as --log-level WARNING)"
    ),
) -> None:
    """Backup local data to external storage or cloud destinations using rsync.

    Executes a backup operation based on the task configuration defined in the
    config file. The backup operation copies data from local storage to external
    destinations like cloud storage, NAS, or external drives using rsync.

    Args:
        label: Task label that identifies the backup configuration in the
            [backup.LABEL] section of the config file.
        dry_run: If True, preview the rsync operation without actually
            transferring files. Shows what would be done.
        create_dirs: If True, automatically create source and target directories
            if they don't exist. If False, operation fails if directories missing.
        config: Path to the configuration file containing task definitions.
            Defaults to "./fnb.toml" in current directory.

    Returns:
        None: Executes rsync operation and prints status messages.

    Raises:
        typer.Exit: If operation fails due to:
            - Task label not found in configuration
            - Configuration file not found or invalid
            - Source or target directories don't exist and create_dirs=False
            - rsync command execution failure
            - Insufficient permissions for target location

    Examples:
        Backup logs to external storage:

        >>> fnb backup logs
        Backing up logs from ./backup/logs/ to /mnt/external/backup/
        Backup completed successfully: logs

        Preview backup operation without transferring files:

        >>> fnb backup logs --dry-run
        Backing up logs from ./backup/logs/ to /mnt/external/backup/
        (DRY RUN - no files will be modified)

        Backup with auto-create directories:

        >>> fnb backup logs --create-dirs
        Created directory: ./backup/logs
        Created directory: /mnt/external/backup
        Backing up logs from ./backup/logs/ to /mnt/external/backup/

        Use custom config file:

        >>> fnb backup logs --config /path/to/custom.toml
        ...
    """
    # Setup logging first
    setup_logging(log_level=log_level, verbose=verbose, quiet=quiet)

    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)
        task = reader.config.get_task_by_label("backup", label)

        if task is None:
            typer.echo(f"❌ Label not found: {label}")
            raise typer.Exit(1)

        backuper.run(
            task,
            dry_run=dry_run,
            create_dirs=create_dirs,
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def sync(
    label: str,
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        "-f",
        help="Force create target directory if it doesn't exist",
    ),
    ssh_password: str | None = typer.Option(
        None,
        "--ssh-password",
        "-p",
        help="Password for SSH authentication (overrides .env)",
    ),
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging (same as --log-level DEBUG)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Enable quiet mode (same as --log-level WARNING)"
    ),
) -> None:
    """Execute both fetch and backup operations sequentially for a given label.

    This is a convenience command that runs both fetch (remote → local) and
    backup (local → external) operations in sequence for the same label.
    This provides a complete data pipeline from remote source to backup destination.

    Args:
        label: Task label that identifies both fetch and backup configurations.
            Must exist in both [fetch.LABEL] and [backup.LABEL] sections.
        dry_run: If True, preview both operations without actually transferring
            files. Shows what would be done for both fetch and backup.
        create_dirs: If True, automatically create directories for both
            operations if they don't exist.
        ssh_password: SSH password for remote authentication during fetch.
            Only used for the fetch operation, not backup.
        config: Path to the configuration file. If None, auto-detects config
            file by searching standard locations.

    Returns:
        None: Executes both operations and prints status messages.

    Raises:
        typer.Exit: If either operation fails due to:
            - Task label not found in fetch or backup configuration
            - Configuration file issues
            - Directory access problems
            - rsync execution failures

    Examples:
        Sync logs from remote to backup:

        >>> fnb sync logs
        📦 Fetch logs from user@server:~/logs/ → ./backup/logs/
        Fetching logs from user@server:~/logs/ to ./backup/logs/
        Fetch completed successfully: logs
        💾 Backup logs from ./backup/logs/ → /mnt/external/backup/
        Backing up logs from ./backup/logs/ to /mnt/external/backup/
        Backup completed successfully: logs

        ✅ Sync operation completed for 'logs'

        Preview complete sync pipeline:

        >>> fnb sync logs --dry-run
        📦 Fetch logs from user@server:~/logs/ → ./backup/logs/
        (DRY RUN - no files will be modified)
        💾 Backup logs from ./backup/logs/ → /mnt/external/backup/
        (DRY RUN - no files will be modified)

        ✅ Sync preview completed for 'logs'

        Sync with SSH authentication and directory creation:

        >>> fnb sync logs --ssh-password mypass --create-dirs
        📦 Fetch logs from user@server:~/logs/ → ./backup/logs/
        Using SSH password from command line for host: user@server
        Created directory: ./backup/logs
        💾 Backup logs from ./backup/logs/ → /mnt/external/backup/
        Created directory: /mnt/external/backup

        ✅ Sync operation completed for 'logs'
    """
    # Setup logging first
    setup_logging(log_level=log_level, verbose=verbose, quiet=quiet)

    try:
        config_path = Path(config) if config else None
        reader = ConfigReader(config_path)

        # Get fetch task
        fetch_task = reader.config.get_task_by_label("fetch", label)
        if fetch_task and fetch_task.enabled:
            typer.echo(f"📦 Fetch {label} from {fetch_task.host} → {fetch_task.target}")
            fetcher.run(
                fetch_task,
                dry_run=dry_run,
                ssh_password=ssh_password,
                create_dirs=create_dirs,
            )
        else:
            typer.echo(f"⚠️  Skipping fetch: no enabled task found for label '{label}'")

        # Get backup task
        backup_task = reader.config.get_task_by_label("backup", label)
        if backup_task and backup_task.enabled:
            typer.echo(
                f"💾 Backup {label} from {backup_task.source} → {backup_task.target}"
            )
            backuper.run(
                backup_task,
                dry_run=dry_run,
                create_dirs=create_dirs,
            )
        else:
            typer.echo(f"⚠️  Skipping backup: no enabled task found for label '{label}'")

        typer.echo(
            f"\n✅ Sync {'preview' if dry_run else 'operation'} completed for '{label}'"
        )

    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        typer.echo("Use --create-dirs option to create missing directories.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
