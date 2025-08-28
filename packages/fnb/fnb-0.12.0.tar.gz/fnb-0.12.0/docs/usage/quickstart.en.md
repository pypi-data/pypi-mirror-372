# Quick Start

Get up and running with fnb in minutes! This guide will walk you through the basic setup and your first backup operations.

## Prerequisites

- Python 3.12 or higher
- rsync (usually pre-installed on Unix-like systems)
- SSH access to remote servers (if needed)

## Installation

### Install from PyPI (Recommended)

```bash
pip install fnb
```

### Verify Installation

```bash
fnb version
```

## Initial Setup

### 1. Generate Configuration

Create your first configuration file:

```bash
fnb init
```

This creates two files:
- `fnb.toml` - Main configuration file
- `.env.plain` - Template for SSH passwords (rename to `.env`)

### 2. Configure SSH Access (Optional)

If you need SSH password authentication, set up the `.env` file:

```bash
# Rename the template
mv .env.plain .env

# Edit the file with your SSH passwords
# SSH_PASSWORD_hostname=your_password
```

**Note**: SSH key authentication is recommended for better security.

## Basic Usage

### Check Configuration Status

```bash
fnb status
```

This shows all configured tasks and their current status.

### Preview Operations (Dry Run)

Always test with dry-run first:

```bash
fnb fetch logs --dry-run
fnb backup logs --dry-run
fnb sync logs --dry-run
```

### Execute Operations

When you're ready, run the actual operations:

```bash
# Fetch data from remote server
fnb fetch logs

# Backup to external storage
fnb backup logs

# Or do both in sequence
fnb sync logs
```

## Example Configuration

Here's a simple configuration for backing up web server logs:

```toml
# fnb.toml
[fetch.weblogs]
label = "weblogs"
summary = "Fetch web server access logs"
host = "admin@webserver.example.com"
source = "/var/log/nginx/"
target = "./backup/weblogs/"
options = ["-auvz", "--delete", "--include=*.log", "--include=**/", "--exclude=*"]
enabled = true

[backup.weblogs]
label = "weblogs"
summary = "Backup web logs to external drive"
host = "none"
source = "./backup/weblogs/"
target = "/mnt/backup-drive/weblogs/"
options = ["-auvz", "--delete", "--progress"]
enabled = true
```

### Using This Configuration

```bash
# Check what will be done
fnb sync weblogs --dry-run

# Execute the complete workflow
fnb sync weblogs

# Create directories if they don't exist
fnb sync weblogs --create-dirs
```

## Common Workflows

### Server Backup Workflow

```bash
# 1. Check current status
fnb status

# 2. Test fetch operation
fnb fetch server-data --dry-run

# 3. Execute fetch
fnb fetch server-data

# 4. Test backup operation
fnb backup server-data --dry-run

# 5. Execute backup
fnb backup server-data
```

### Complete Sync Workflow

```bash
# Test complete pipeline
fnb sync server-data --dry-run

# Execute complete pipeline
fnb sync server-data

# With directory creation
fnb sync server-data --create-dirs
```

### Development Project Backup

```bash
# Generate specific config for projects
fnb init config

# Test project sync
fnb sync project --dry-run

# Execute with SSH password
fnb sync project --ssh-password mypassword
```

## Directory Management

### Auto-Create Directories

Use `--create-dirs` to automatically create missing target directories:

```bash
fnb fetch logs --create-dirs
fnb backup logs --create-dirs
fnb sync logs --create-dirs
```

### Directory Structure

fnb follows this typical structure:

```
project-root/
├── fnb.toml          # Main configuration
├── .env              # SSH passwords (optional)
└── backup/           # Local backup staging area
    ├── logs/         # Fetched logs
    ├── database/     # Database backups
    └── configs/      # Configuration files
```

## Configuration Tips

### 1. Start Simple

Begin with basic configurations and add complexity gradually:

```toml
[fetch.simple]
label = "simple"
summary = "Simple fetch example"
host = "user@server"
source = "~/documents/"
target = "./backup/docs/"
options = ["-av"]
enabled = true
```

### 2. Use Dry Run

Always test new configurations with `--dry-run` first.

### 3. Incremental Setup

Add one task at a time and test thoroughly before adding more.

### 4. Monitor Progress

Use the `--progress` option for large transfers:

```toml
options = ["-auvz", "--progress"]
```

## Troubleshooting

### Common Issues

**Config file not found:**
```bash
fnb init  # Create initial config
```

**SSH connection failed:**
```bash
# Test SSH manually first
ssh user@hostname

# Use SSH password option
fnb fetch logs --ssh-password mypass
```

**Directory doesn't exist:**
```bash
fnb fetch logs --create-dirs
```

**Permission denied:**
- Check SSH key permissions (should be 600)
- Verify target directory permissions
- Ensure user has access to source directories

### Getting Help

```bash
# General help
fnb --help

# Command-specific help
fnb fetch --help
fnb backup --help
fnb sync --help
```

## Next Steps

Now that you have fnb running:

1. **[Configuration Guide](configuration.md)** - Learn advanced configuration options
2. **[Commands Reference](commands.md)** - Complete command documentation
3. **[Examples](examples.md)** - Real-world usage scenarios
4. **[FAQ](../faq.md)** - Common questions and solutions

## Quick Reference

```bash
# Essential commands
fnb init                    # Generate config
fnb status                  # Show config status
fnb fetch LABEL            # Fetch from remote
fnb backup LABEL           # Backup locally
fnb sync LABEL             # Fetch + backup
fnb COMMAND --dry-run      # Preview operation
fnb COMMAND --create-dirs  # Auto-create directories
fnb COMMAND --help         # Get help
```

You're now ready to use fnb for your backup workflows!
