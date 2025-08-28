# FAQ

## General Questions

### What is fnb?

fnb (Fetch'n'Backup) is a simple two-step backup tool that uses rsync for efficient data synchronization. It allows you to:

1. **Fetch** data from remote servers to local storage
2. **Backup** local data to external/cloud storage
3. **Sync** both operations in sequence

### How does fnb work?

fnb uses a configuration-driven approach with TOML files to define backup tasks. Each task specifies source and target locations, rsync options, and other settings.

### What are the main benefits?

- **Simple Configuration**: TOML-based configuration files
- **SSH Automation**: Automatic password handling for remote connections
- **Dry Run Support**: Preview operations before execution
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Reliable**: Built on proven rsync technology

## Installation

### Requirements

- Python 3.12 or higher
- rsync (usually pre-installed on Unix-like systems)

### Quick Installation

```bash
# Install from PyPI
pip install fnb

# Or install from source
git clone https://gitlab.com/qumasan/fnb.git
cd fnb
pip install -e .
```

## Configuration

### Basic Setup

```bash
# Generate initial configuration
fnb init

# Check configuration status
fnb status
```

For detailed configuration options, see the [Configuration Guide](usage/configuration.md).

## Common Issues

### SSH Authentication

**Q: How do I handle SSH passwords?**

A: fnb supports multiple authentication methods:
- SSH key authentication (recommended)
- Password via `.env` file
- Command-line password option

### Path Issues

**Q: Target directory doesn't exist**

A: Use the `--create-dirs` option to automatically create missing directories:

```bash
fnb fetch logs --create-dirs
```

### Permission Errors

**Q: Permission denied errors**

A: Check file permissions and SSH access:
- Verify SSH key permissions (600 for private key)
- Ensure target directories are writable
- Test SSH connection manually first

## Getting Help

- **Documentation**: Complete guides available in this documentation
- **Issues**: Report bugs at [GitLab Issues](https://gitlab.com/qumasan/fnb/-/issues)
- **Commands**: Use `fnb --help` or `fnb COMMAND --help` for built-in help

## Contributing

We welcome contributions! See the [Contributing Guide](development/contributing.md) for details on:
- Setting up development environment
- Code standards and testing
- Submitting pull requests
