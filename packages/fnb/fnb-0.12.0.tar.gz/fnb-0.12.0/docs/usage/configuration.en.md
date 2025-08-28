# Configuration

fnb uses [TOML](https://toml.io) format configuration files. The main configuration file is `fnb.toml` or `config.toml`.

## Configuration File Priority

Configuration files are searched in the following order (highest priority first):

1. `./fnb.toml` - Project-local configuration
2. `~/.config/fnb/config.toml` - Global user configuration (XDG compliant)
3. `C:\Users\username\AppData\Local\fnb\config.toml` - Windows user configuration
4. `./config/*.toml` - Split/merged configurations (for development/operations)

## Basic Structure

The configuration file consists of two main sections: `fetch` and `backup`:

```toml
[fetch.label_name]
# Remote-to-local fetch configuration

[backup.label_name]
# Local-to-external backup configuration
```

## Configuration Fields

Each section contains the following fields:

| Field | Description | Example |
|---|---|---|
| `label` | Unique task identifier | `"logs"` |
| `summary` | Brief task description | `"Fetch logs from server"` |
| `host` | Remote hostname, or `"none"` for local operations | `"user@remote-host"` |
| `source` | rsync source path | `"~/path/to/source/"` |
| `target` | rsync target path | `"./local/backup/path/"` |
| `options` | Array of rsync options | `["-auvz", "--delete"]` |
| `enabled` | Whether the task is active | `true` or `false` |

## Complete Configuration Example

```toml
# Fetch configuration - from remote to local
[fetch.logs]
label = "logs"
summary = "Fetch application logs from production server"
host = "admin@prod-server.example.com"
source = "/var/log/myapp/"
target = "./backup/logs/"
options = ["-auvz", "--delete", "--exclude=*.tmp"]
enabled = true

[fetch.database]
label = "database"
summary = "Fetch database dumps"
host = "admin@db-server.example.com"
source = "/backups/database/"
target = "./backup/db/"
options = ["-auvz", "--progress"]
enabled = true

# Backup configuration - from local to external
[backup.logs]
label = "logs"
summary = "Backup logs to external storage"
host = "none"
source = "./backup/logs/"
target = "/mnt/external/logs/"
options = ["-auvz", "--delete"]
enabled = true

[backup.database]
label = "database"
summary = "Backup database to cloud storage"
host = "none"
source = "./backup/db/"
target = "/mnt/cloud/database/"
options = ["-auvz", "--progress"]
enabled = false
```

## Path Configuration

### Remote Paths

For `fetch` tasks, use SSH-style paths:

```toml
host = "user@hostname"
source = "/absolute/path/" or "~/relative/path/"
target = "./local/path/"
```

### Local Paths

For `backup` tasks, use local filesystem paths:

```toml
host = "none"
source = "./local/source/"
target = "/absolute/target/path/" or "./relative/target/"
```

### Environment Variables

Paths support environment variable expansion:

```toml
source = "$HOME/documents/"
target = "${BACKUP_DIR}/documents/"
```

## rsync Options

Common rsync options and their purposes:

| Option | Description |
|---|---|
| `-a` | Archive mode (preserves permissions, timestamps, symbolic links) |
| `-v` | Verbose output |
| `-z` | Compress during transfer |
| `-u` | Skip files that are newer on the receiver |
| `--delete` | Delete extraneous files from destination |
| `--progress` | Show progress during transfer |
| `--exclude=PATTERN` | Exclude files matching pattern |
| `--dry-run` | Show what would be done without making changes |

### Examples

```toml
# Basic synchronization
options = ["-auvz"]

# Synchronization with deletion and progress
options = ["-auvz", "--delete", "--progress"]

# Exclude temporary and cache files
options = ["-auvz", "--exclude=*.tmp", "--exclude=cache/"]

# Bandwidth-limited transfer
options = ["-auvz", "--bwlimit=1000"]
```

## SSH Configuration

### Password Authentication

Create a `.env` file for SSH passwords:

```bash
# .env
SSH_PASSWORD_prod_server=your_secure_password
SSH_PASSWORD_db_server=another_password
```

Environment variable format: `SSH_PASSWORD_<hostname_normalized>`

### Key-based Authentication

For better security, use SSH key authentication:

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to remote server
ssh-copy-id user@hostname
```

## Task Labels

Labels must be:
- Unique within each section (`fetch` or `backup`)
- Alphanumeric characters and underscores only
- Used for command-line operations: `fnb fetch logs`

## Validation Rules

fnb validates configuration files and will report errors for:

- Missing required fields
- Invalid TOML syntax
- Duplicate labels within sections
- Invalid rsync options
- Malformed host specifications

## Advanced Configuration

### Multiple Environments

Use separate configuration files for different environments:

```bash
# Development
fnb --config config/dev.toml fetch logs

# Production
fnb --config config/prod.toml fetch logs
```

### Configuration Templates

Generate configuration templates:

```bash
# Generate complete configuration
fnb init

# Generate only config file
fnb init config

# Generate only environment file
fnb init env
```

### Config File Discovery

fnb automatically discovers configuration files in this order:

1. `--config` command line option
2. `./fnb.toml` in current directory
3. `./config.toml` in current directory
4. `./config/*.toml` files
5. User configuration directory based on OS

Run `fnb status` to see which configuration file is being used.

## Troubleshooting

### Common Issues

1. **Config file not found**: Run `fnb init` to create initial configuration
2. **Invalid TOML syntax**: Check for missing quotes, brackets, or commas
3. **Task not found**: Verify label matches configuration exactly
4. **Permission denied**: Check SSH credentials and file permissions
5. **Path not found**: Verify source and target paths exist

### Debugging

Use `--dry-run` to preview operations:

```bash
fnb fetch logs --dry-run
fnb backup logs --dry-run
```

Check configuration status:

```bash
fnb status
```

For detailed examples, see the [Examples Guide](examples.md).
