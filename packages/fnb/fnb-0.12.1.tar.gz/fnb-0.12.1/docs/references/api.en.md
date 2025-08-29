# API Reference

This page explains fnb's internal APIs and class structure.
Use this reference when extending fnb or using it from other projects.

## Package Overview

fnb consists of the following modules:

- **cli**: CLI entry point (Typer-based)
- **config**: Configuration models (Pydantic-based)
- **reader**: Configuration file loading and discovery
- **gear**: rsync execution engine (SSH automation with pexpect)
- **fetcher**: Remote fetch operations
- **backuper**: Local backup operations
- **generator**: Configuration file generation
- **env**: Environment variable handling

## Configuration Management

### config module

::: fnb.config

## Configuration File Loading

### reader module

::: fnb.reader

## rsync Execution Engine

### gear module

::: fnb.gear

## Fetch Operations

### fetcher module

::: fnb.fetcher

## Backup Operations

### backuper module

::: fnb.backuper

## Configuration File Generation

### generator module

::: fnb.generator

## CLI Interface

### cli module

::: fnb.cli

## Environment Variable Handling

### env module

::: fnb.env

## Usage Examples

### Basic Programmatic Usage

```python
from pathlib import Path
from fnb.reader import ConfigReader
from fnb.fetcher import run as run_fetch
from fnb.backuper import run as run_backup

# Load configuration
reader = ConfigReader(Path("./config.toml"))

# Get tasks
fetch_task = reader.config.get_task_by_label("fetch", "docs")
backup_task = reader.config.get_task_by_label("backup", "docs")

# Execute fetch
if fetch_task and fetch_task.enabled:
    print(f"Fetching {fetch_task.label}...")
    run_fetch(fetch_task, dry_run=False)

# Execute backup
if backup_task and backup_task.enabled:
    print(f"Backing up {backup_task.label}...")
    run_backup(backup_task, dry_run=False)
```

### Custom Configuration Extension

```python
from typing import Optional
from pydantic import Field
from fnb.config import RsyncTaskConfig

class ExtendedTaskConfig(RsyncTaskConfig):
    """Extended task configuration with notification options"""
    notify_email: Optional[str] = Field(None, description="Email address for completion notifications")
    notify_on_error: bool = Field(True, description="Whether to send notifications on error")
    retention_days: Optional[int] = Field(None, description="Number of days to retain backups")
```

### Batch Processing Example

```python
from fnb.reader import ConfigReader
from fnb.fetcher import run as run_fetch
from fnb.backuper import run as run_backup

def run_all_tasks(config_path: str, dry_run: bool = True):
    """Execute all tasks sequentially"""
    reader = ConfigReader(config_path)

    # Execute all fetch tasks
    for task in reader.config.get_enabled_tasks("fetch"):
        print(f"Fetching: {task.label}")
        run_fetch(task, dry_run=dry_run)

    # Execute all backup tasks
    for task in reader.config.get_enabled_tasks("backup"):
        print(f"Backing up: {task.label}")
        run_backup(task, dry_run=dry_run)
```
