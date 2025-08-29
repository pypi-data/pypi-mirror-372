# fnb Installation Guide

This document provides comprehensive installation instructions for fnb (Fetch'n'Backup).

## System Requirements

### Required
- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, Linux (OS Independent)
- **rsync**: Available locally or on remote servers

### Recommended
- **Package Manager**: uv (fast) or pip
- **Terminal**: UTF-8 compatible terminal emulator
- **SSH**: For remote server access

## Installation Methods

### 1. From PyPI (Recommended)

#### Using pip
```bash
# Basic installation
pip install fnb

# User installation
pip install --user fnb

# Upgrade to latest version
pip install --upgrade fnb
```

#### Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install fnb
uv pip install fnb

# Add to project
uv add fnb
```

#### Using pipx (Application Isolation)
```bash
# Install pipx if not already installed
pip install pipx

# Install fnb in isolated environment
pipx install fnb
```

### 2. From Source

#### Development Installation
```bash
# Clone repository
git clone https://gitlab.com/qumasan/fnb.git
cd fnb

# Using uv (recommended)
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -e .

# Using traditional pip
python -m venv venv
source venv/bin/activate    # Linux/macOS
# or venv\Scripts\activate    # Windows
pip install -e .
```

#### Build and Install
```bash
git clone https://gitlab.com/qumasan/fnb.git
cd fnb

# Build using uv
uv build
pip install dist/fnb-*.whl

# Or using hatchling directly
pip install build
python -m build
pip install dist/fnb-*.whl
```

## Platform-Specific Setup

### Windows

#### Prerequisites
```powershell
# Check Python 3.12+ installation
python --version

# If Python not found:
# Install Python 3.12+ from Microsoft Store or python.org
```

#### Installation Steps
```powershell
# Run in PowerShell or Command Prompt
pip install fnb

# Verify installation
fnb version
```

#### rsync Setup (Windows)
```powershell
# Using WSL2
wsl --install
wsl
sudo apt update && sudo apt install rsync

# Or using MSYS2/Cygwin
# Install from https://www.msys2.org/
```

### macOS

#### Using Homebrew
```bash
# Install Python via Homebrew (recommended)
brew install python@3.12

# Install fnb
pip3 install fnb

# rsync is usually pre-installed
rsync --version
```

#### Using pyenv
```bash
# Install Python via pyenv
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0

# Install fnb
pip install fnb
```

### Linux

#### Ubuntu/Debian
```bash
# Install Python 3.12+
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# Install fnb
pip3 install fnb

# Install rsync (usually pre-installed)
sudo apt install rsync
```

#### CentOS/RHEL/Rocky Linux
```bash
# Install Python 3.12+
sudo dnf install python3.12 python3-pip

# Install fnb
pip3 install fnb

# Install rsync
sudo dnf install rsync
```

#### Arch Linux
```bash
# Install Python
sudo pacman -S python python-pip

# Install fnb
pip install fnb

# Install rsync
sudo pacman -S rsync
```

## Verify Installation

Confirm successful installation:

```bash
# Check version
fnb version

# Display help
fnb --help

# Initialize config file (functionality test)
fnb init --help
```

## Dependencies

fnb depends on the following Python packages:

```
pexpect>=4.9.0      # SSH automation
platformdirs>=4.3.8 # Platform-specific paths
pydantic>=2.11.7    # Configuration validation
python-dotenv>=1.0.1 # Environment variables
toml>=0.10.2        # Configuration files
typer>=0.14.2       # CLI framework
```

These are automatically installed.

## Troubleshooting

### Common Issues and Solutions

#### 1. Python Version Error
```
ERROR: fnb requires Python 3.12 or higher
```

**Solution:**
```bash
# Check current version
python --version

# Install Python 3.12+:
# - Windows: Microsoft Store or python.org
# - macOS: brew install python@3.12
# - Linux: Install python3.12 via package manager
```

#### 2. pip Installation Error
```
ERROR: Could not find a version that satisfies the requirement fnb
```

**Solution:**
```bash
# Update pip to latest version
pip install --upgrade pip

# Direct install from PyPI
pip install --index-url https://pypi.org/simple/ fnb
```

#### 3. Permission Error (Linux/macOS)
```
ERROR: Permission denied
```

**Solution:**
```bash
# Install in user environment
pip install --user fnb

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install fnb
```

#### 4. rsync Not Found
```
ERROR: rsync command not found
```

**Solution:**
```bash
# Linux
sudo apt install rsync  # Ubuntu/Debian
sudo dnf install rsync  # CentOS/RHEL

# macOS (usually pre-installed)
brew install rsync  # if latest version needed

# Windows
# Use WSL, MSYS2, or Cygwin
```

#### 5. pexpect Error on Windows (Development)
```
ERROR: pexpect is not supported on Windows
```

**Solution:**
Windows has limited SSH password automation:
```bash
# Use WSL2 (recommended)
wsl
pip install fnb

# Or manual SSH password entry
# pexpect functionality will be disabled
```

### Log Inspection

If issues persist:

```bash
# Verbose installation
pip install -v fnb

# Python environment info
python -m pip show fnb
python -c "import sys; print(sys.path)"

# Check config file locations
fnb status
```

## Upgrade

Upgrade existing fnb to latest version:

```bash
# Using pip
pip install --upgrade fnb

# Using uv
uv pip install --upgrade fnb

# Using pipx
pipx upgrade fnb
```

## Uninstall

Complete removal of fnb:

```bash
# Uninstall package
pip uninstall fnb

# Remove config files (optional)
# Linux/macOS
rm -rf ~/.config/fnb/
rm -f ./fnb.toml
rm -f ./.env

# Windows
# Delete %LOCALAPPDATA%\fnb\ folder
# Delete fnb.toml and .env files
```

## Next Steps

After successful installation:

- **Quick Start**: See [Quick Start Guide](usage/quickstart.en.md)
- **Configuration**: Learn about [Configuration](usage/configuration.en.md) (coming soon)
- **Usage**: Read [Command Reference](usage/commands.en.md) (coming soon)

## Support

For installation issues or support:

- **Issue Tracker**: https://gitlab.com/qumasan/fnb/-/issues
- **Documentation**: https://qumasan.gitlab.io/fnb/
- **Repository**: https://gitlab.com/qumasan/fnb

When creating a new issue, please include:
- OS and version
- Python version (`python --version`)
- Complete error message
- Installation method used
