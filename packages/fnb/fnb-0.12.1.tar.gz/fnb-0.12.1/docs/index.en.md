# fnb — Fetch'n'Backup

**Simple two-step backup tool with rsync**

fnb is a command-line tool that simplifies backup workflows by providing a structured approach to data synchronization using rsync. Whether you need to fetch data from remote servers or backup local data to external storage, fnb makes it easy with configuration-driven automation.

## Key Features

### 🔄 **Two-Step Workflow**
1. **Fetch**: Pull data from remote servers to local storage
2. **Backup**: Push local data to external/cloud destinations
3. **Sync**: Execute both steps in sequence

### ⚙️ **Configuration-Driven**
- TOML-based configuration files
- Task-based organization
- Environment variable support
- Auto-discovery of config files

### 🔐 **SSH Automation**
- Automatic SSH password handling
- Support for key-based authentication
- Secure credential management
- Interactive and non-interactive modes

### 🛡️ **Safe Operations**
- Dry-run mode for all operations
- Directory existence validation
- Comprehensive error handling
- Progress tracking and logging

## Quick Start

### 1. Install fnb

```bash
pip install fnb
```

### 2. Generate Configuration

```bash
fnb init
```

### 3. Configure Tasks

Edit the generated `fnb.toml` file to define your backup tasks:

```toml
[fetch.logs]
label = "logs"
summary = "Fetch application logs"
host = "user@server.com"
source = "/var/log/app/"
target = "./backup/logs/"
options = ["-auvz", "--delete"]
enabled = true

[backup.logs]
label = "logs"
summary = "Backup logs to external storage"
host = "none"
source = "./backup/logs/"
target = "/mnt/external/logs/"
options = ["-auvz", "--delete"]
enabled = true
```

### 4. Run Backup Operations

```bash
# Check configuration
fnb status

# Fetch from remote
fnb fetch logs

# Backup to external storage
fnb backup logs

# Or do both in sequence
fnb sync logs
```

## Use Cases

### 🌐 **Server Backup**
- Web server content and logs
- Database dumps and configurations
- Application data and media files

### 💼 **Personal Data**
- Documents and photos
- Development projects
- System configurations

### 🏢 **Enterprise**
- Multi-server infrastructure
- Compliance and archival
- Disaster recovery preparation

## Why fnb?

- **Simple**: Easy configuration with TOML files
- **Reliable**: Built on proven rsync technology
- **Flexible**: Supports various backup scenarios
- **Secure**: SSH automation with credential management
- **Cross-platform**: Works on Linux, macOS, and Windows

## Get Started

- **[Installation Guide](installation.md)**: Detailed setup instructions
- **[Quick Start](usage/quickstart.md)**: Get up and running quickly
- **[Configuration](usage/configuration.md)**: Complete configuration reference
- **[Commands](usage/commands.md)**: Full command-line reference

## Community & Support

- **Documentation**: Comprehensive guides and examples
- **Issues**: [GitLab Issues](https://gitlab.com/qumasan/fnb/-/issues) for bug reports
- **Contributing**: See our [Contributing Guide](development/contributing.md)

---

**fnb** — Making backup workflows simple and reliable.
