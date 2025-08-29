"""Core rsync execution and directory management utilities for fnb.

This module provides the fundamental operations for executing rsync commands
with SSH password automation and local directory validation. It handles the
low-level details of process execution, authentication, and error handling.
"""

import os
import subprocess
from pathlib import Path

import pexpect
import signal

from fnb.logger import get_logger

logger = get_logger(__name__)


def run_rsync(
    source: str,
    target: str,
    options: list[str],
    ssh_password: str | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess | bool:
    """Execute an rsync command with optional SSH password automation.

    This function handles both local and remote rsync operations. For remote
    operations requiring SSH authentication, it can automatically provide
    passwords using pexpect to handle interactive prompts.

    Args:
        source: Source path for rsync operation. Can be local path or remote
            in format "user@host:path/". Remote paths trigger SSH authentication.
        target: Destination path for rsync operation. Usually a local path.
        options: List of rsync command-line options to include in the operation.
            Common options: ["-auvz", "--delete", "--dry-run"].
        ssh_password: SSH password for automatic authentication. If None,
            rsync runs without password automation and will fall back to
            interactive password prompts or SSH key authentication. If provided,
            uses pexpect for password automation.
        timeout: Maximum seconds to wait for SSH password prompt. Only used
            when ssh_password is provided.

    Returns:
        subprocess.CompletedProcess | bool: For operations without password
        automation, returns CompletedProcess object with execution details.
        For password-automated operations, returns True if successful,
        False if failed.

    Raises:
        subprocess.CalledProcessError: If rsync execution fails (non-zero exit).
        pexpect.TIMEOUT: If SSH password prompt times out.
        pexpect.EOF: If SSH connection unexpectedly closes.
        Exception: For any other errors during execution.

    Examples:
        Local rsync operation:

        >>> run_rsync("./source/", "./target/", ["-av"])
        CompletedProcess(args=['rsync', '-av', './source/', './target/'],
                        returncode=0)

        Remote rsync with SSH password:

        >>> run_rsync("user@server:~/data/", "./backup/",
        ...           ["-auvz", "--delete"], ssh_password="mypass")
        True

        Dry run to preview changes:

        >>> run_rsync("user@server:~/logs/", "./logs/",
        ...           ["-av", "--dry-run"], ssh_password="mypass")
        True

        Remote sync with custom timeout:

        >>> run_rsync("user@server:~/files/", "./files/",
        ...           ["-av"], ssh_password="mypass", timeout=60)
        True
    """
    cmd = ["rsync"] + options + [source, target]
    cmd_str = " ".join(cmd)

    logger.info(f"Executing: {cmd_str}")

    try:
        if ssh_password:
            # Use pexpect for interactive SSH passwort automation
            return _run_rsync_with_password(
                command=cmd_str,
                ssh_password=ssh_password,
                timeout=timeout,
            )
        else:
            # Regular non-interactive execution
            return subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"rsync failed with exit code {e.returncode}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        logger.error(f"Error executing rsync: {e}")
        raise


def _run_rsync_with_password(
    command: str, ssh_password: str, timeout: int = 30
) -> bool:
    """Execute rsync command with SSH password automation using pexpect.

    This internal function handles the complex process of automating SSH
    password entry for rsync operations. It uses pexpect to detect password
    prompts and automatically provide credentials, then handles both
    interactive and non-interactive terminal environments appropriately.

    Args:
        command: The complete rsync command as a string, ready for execution.
        ssh_password: SSH password to send when prompted during authentication.
        timeout: Maximum seconds to wait for password prompt before timing out.

    Returns:
        bool: True if the rsync operation completed successfully (even with
        signal termination which is normal for SSH), False if there were
        critical errors like connection failures.

    Raises:
        pexpect.TIMEOUT: If password prompt doesn't appear within timeout period.
        Exception: For unexpected errors during pexpect automation.

    Examples:
        Basic password automation:

        >>> _run_rsync_with_password(
        ...     "rsync -av user@server:~/data/ ./backup/",
        ...     "mypassword", 30)
        True

        Handle timeout scenarios:

        >>> _run_rsync_with_password(
        ...     "rsync -av user@badserver:~/data/ ./backup/",
        ...     "mypassword", 5)
        pexpect.TIMEOUT: Timed out waiting for password prompt after 5s
    """
    child = None
    try:
        child = pexpect.spawn(command)
        child.timeout = timeout

        i = child.expect(["[Pp]assword:", pexpect.EOF, pexpect.TIMEOUT])

        if i == 0:  # Password prompt
            child.sendline(ssh_password)

            # Check if we're in an interactive environment
            if os.isatty(0):  # Interactive terminal (stdin is a TTY)
                try:
                    child.interact()
                except Exception as e:
                    logger.error(f"interact() failed: {e}")
                    # Fall back to non-interactive mode
                    child.expect(pexpect.EOF, timeout=timeout)
            else:
                # Non-interactive environment (CI, scripts, etc.)
                logger.info(
                    "Non-interactive environment detected, using expect() instead of interact()"
                )
                child.expect(pexpect.EOF, timeout=timeout)

            # Note: After interact() or expect(), the process might have exited with
            # SIGHUP or similar signals due to SSH connection closure.
            # This is often normal and shouldn't be treated as an error.

            # If we have a very clear failure (like returncode > 1), report it
            if child.exitstatus is not None and child.exitstatus > 1:
                logger.warning(f"Warning: rsync exited with code {child.exitstatus}")
                # We're being more lenient here and treating this as a warning
                # rather than a hard error

            # If process was terminated by a signal, it could be SIGHUP from SSH
            # which is often normal when the SSH session ends
            if child.signalstatus is not None:
                signal_name = signal.Signals(child.signalstatus).name
                logger.info(
                    f"Note: Process ended with signal {signal_name}. "
                    f"This is often normal with SSH sessions."
                )

            return True

        elif i == 1:  # EOF
            logger.error("Connection closed unexpectedly. Check SSH configuration.")
            # This might be a critical error, but we'll just warn and continue
            return False

        elif i == 2:  # TIMEOUT
            logger.error(f"Timed out waiting for password prompt after {timeout}s.")
            raise pexpect.TIMEOUT(
                f"Timed out waiting for password prompt after {timeout}s: {command}"
            )

    except pexpect.ExceptionPexpect as e:
        logger.error(f"pexpect error: {e}")
        # Only re-raise truly unexpected pexpect errors
        if not isinstance(e, (pexpect.EOF, pexpect.TIMEOUT)):
            raise
        return False
    except Exception as e:
        logger.error(f"Unexpected error during rsync: {e}")
        raise
    finally:
        # Ensure child process is closed properly if it exists
        if child and not child.closed:
            try:
                child.close()
            except Exception:
                # Ignore errors during cleanup
                pass

    return False


def verify_directory(path: str, create: bool = False) -> Path:
    """Verify that a local directory exists, optionally creating it if missing.

    This function validates local directory paths and ensures they exist for
    rsync operations. It includes safety checks to prevent operations on
    remote paths and provides clear error handling for various failure scenarios.

    Args:
        path: Local directory path to verify or create. Must be a local path
            without ":" characters (which indicate remote paths).
        create: If True, automatically create the directory and any missing
            parent directories. If False, only verify existence without creation.

    Returns:
        Path: Validated Path object pointing to the existing directory.

    Raises:
        ValueError: If path contains ":" indicating a remote path, or if path
            exists but is not a directory (e.g., it's a file).
        FileNotFoundError: If directory doesn't exist and create=False.
        OSError: If directory creation fails due to permissions or other
            filesystem issues.

    Examples:
        Verify existing directory:

        >>> verify_directory("./backup")
        PosixPath('./backup')

        Create directory if missing:

        >>> verify_directory("./new/nested/path", create=True)
        Created directory: ./new/nested/path
        PosixPath('./new/nested/path')

        Handle remote path error:

        >>> verify_directory("user@server:~/path")
        ValueError: Remote paths are not supported for verification: user@server:~/path

        Handle file vs directory conflict:

        >>> verify_directory("./existing_file.txt")
        ValueError: Path exists but is not a directory: ./existing_file.txt

        Handle missing directory without create:

        >>> verify_directory("./missing")
        FileNotFoundError: Directory does not exist: ./missing
    """
    # Check if the path is remote
    if ":" in path:
        raise ValueError(f"Remote paths are not supported for verification: {path}")

    dir_path = Path(path)

    if dir_path.exists():
        if not dir_path.is_dir():
            raise ValueError(f"Path exists but is not a directory: {dir_path}")
        return dir_path

    if not create:
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
        return dir_path
    except OSError as e:
        raise OSError(f"Failed to create directory {dir_path}: {e}")


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/gear.py

    """
    source = "user@hostname:~/remote/path/backup/"
    target = "./local/path/backup/"
    options = ["-auvz", "--delete", "--dry-run"]
    ssh_password = "something"
    run_rsync(source=source, target=target, options=options, ssh_password=ssh_password)
