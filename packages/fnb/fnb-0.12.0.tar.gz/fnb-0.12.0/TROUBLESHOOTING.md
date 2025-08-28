# Troubleshooting Guide

This document provides solutions for common issues encountered while developing, building, or using fnb (Fetch'n'Backup).

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Runtime Errors](#runtime-errors)
- [Build and Development Issues](#build-and-development-issues)
- [PyPI Deployment Problems](#pypi-deployment-problems)
- [SSH and Authentication Issues](#ssh-and-authentication-issues)
- [Performance and Network Issues](#performance-and-network-issues)
- [Testing Issues](#testing-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Compatibility

**Problem**: Installation fails with Python version errors
```
ERROR: This package requires Python 3.12+
```

**Solution**:
```bash
# Check current Python version
python --version

# Install and use Python 3.12+ with uv
uv python install 3.12
uv python pin 3.12

# Create virtual environment with specific Python version
uv venv --python 3.12

# Or specify Python version directly
uv venv --python python3.12

# Verify Python version in virtual environment
uv run python --version
```

### uv Package Manager Issues

**Problem**: `uv` command not found
```
command not found: uv
```

**Solution**:
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using Homebrew (macOS)
brew install uv

# Verify installation
uv --version
```

### Virtual Environment Issues

**Problem**: Dependencies not found or conflicting versions
```
ModuleNotFoundError: No module named 'fnb'
```

**Solution**:
```bash
# Recreate virtual environment with correct Python version
rm -rf .venv
uv venv --python 3.12

# Reinstall dependencies
uv pip install -e .

# Verify installation
uv run fnb --help
```

### Permission Errors

**Problem**: Permission denied during installation
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Use virtual environment (recommended)
uv venv --python 3.12
uv pip install -e .

# Or install with user flag
pip install --user fnb

# Check permissions
ls -la ~/.local/bin/
```

## Configuration Problems

### Config File Not Found

**Problem**: No configuration file found
```
❌ No config file found. Run 'fnb init' to create one.
```

**Solution**:
```bash
# Create new configuration
uv run fnb init

# Or manually create in expected location
mkdir -p ~/.config/fnb
cp examples/config.toml ~/.config/fnb/config.toml

# Check config file locations
uv run fnb status
```

### Invalid TOML Syntax

**Problem**: Configuration file parsing errors
```
Invalid TOML in config file: Expected '=' after key
```

**Solution**:
```bash
# Validate TOML syntax
uv run python -c "import tomllib; tomllib.loads(open('fnb.toml').read())"

# Common TOML syntax issues:
# 1. Missing quotes around strings with spaces
label = "My Backup Task"  # ✓ Correct
label = My Backup Task    # ✗ Wrong

# 2. Incorrect array syntax
options = ["-av", "--delete"]  # ✓ Correct
options = -av --delete         # ✗ Wrong

# 3. Missing section headers
[fetch.task1]  # ✓ Correct section header
task1          # ✗ Missing section
```

### Configuration Validation Errors

**Problem**: Configuration schema validation fails
```
Configuration validation failed: Field required
```

**Solution**:
```bash
# Check required fields
cat > fnb.toml << EOF
[fetch.example]
label = "Example Task"
summary = "Example fetch task"
host = "example.com"
source = "/remote/path"
target = "/local/path"
options = ["-av"]
enabled = true
EOF

# Validate configuration
uv run fnb status

# Check example configuration
cat examples/config.toml
```

## Runtime Errors

### Task Not Found

**Problem**: Specified task doesn't exist
```
❌ Error: Task 'nonexistent' not found in fetch tasks
```

**Solution**:
```bash
# List available tasks
uv run fnb status

# Check task names in config file
grep -A1 "^\[fetch\." fnb.toml
grep -A1 "^\[backup\." fnb.toml

# Verify task label matches command
uv run fnb fetch task_name  # task_name must match [fetch.task_name]
```

### Directory Creation Errors

**Problem**: Target directories don't exist
```
FileNotFoundError: Target directory doesn't exist
```

**Solution**:
```bash
# Use create-dirs option
uv run fnb fetch task_name --create-dirs
uv run fnb backup task_name --create-dirs

# Or manually create directories
mkdir -p /path/to/target/directory

# Check directory permissions
ls -ld /path/to/target/
```

### rsync Command Failures

**Problem**: rsync execution fails
```
rsync: failed to connect to server
```

**Solution**:
```bash
# Test rsync manually
rsync -av user@host:/remote/path /local/path

# Check common issues:
# 1. Incorrect host or path
# 2. SSH key authentication
# 3. Network connectivity
# 4. rsync not installed on remote

# Use dry-run for testing
uv run fnb fetch task_name --dry-run
```

## Build and Development Issues

### Test Failures

**Problem**: Tests fail during development
```
FAILED tests/unit/test_module.py::test_function
```

**Solution**:
```bash
# Run tests with verbose output
task test:unit -v

# Run specific test file
uv run pytest tests/unit/test_module.py -v

# Check test coverage
task test
open htmlcov/index.html

# Common test issues:
# 1. Missing test fixtures
# 2. Incorrect mock setup
# 3. Environment-dependent tests
```

### Code Formatting Issues

**Problem**: Pre-commit hooks fail
```
ruff format failed
```

**Solution**:
```bash
# Format code automatically
task lint

# Check formatting without changes
task lint:check

# Fix specific files
uv run ruff format src/fnb/module.py

# Configure editor for auto-formatting
# VS Code: settings.json
{
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### Import and Module Issues

**Problem**: Import errors during development
```
ModuleNotFoundError: No module named 'fnb'
```

**Solution**:
```bash
# Install in editable mode
uv pip install -e .

# Check Python path
uv run python -c "import sys; print(sys.path)"

# Verify package structure
ls -la src/fnb/
cat src/fnb/__init__.py

# Use absolute imports
from fnb.config import FnbConfig  # ✓ Correct
from config import FnbConfig      # ✗ Wrong
```

## PyPI Deployment Problems

### Authentication Failures

**Problem**: PyPI upload authentication fails
```
HTTP Error 403: Invalid or non-existent authentication information
```

**Solution**:
```bash
# Check API token configuration
echo $PYPI_API_TOKEN
echo $TESTPYPI_API_TOKEN

# Recreate API tokens
# 1. Visit https://pypi.org/manage/account/token/
# 2. Create new token with project scope
# 3. Update .env file
echo "PYPI_API_TOKEN=pypi-your-new-token" >> .env

# Test with TestPyPI first
task publish:test
```

### Build Failures

**Problem**: Package build fails
```
ERROR: Failed building wheel for fnb
```

**Solution**:
```bash
# Check build configuration
uv build --verbose

# Common build issues:
# 1. Missing files in pyproject.toml
# 2. Incorrect version format
# 3. Missing dependencies

# Verify package metadata
cat pyproject.toml

# Check version consistency
grep version pyproject.toml
grep __version__ src/fnb/__init__.py

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
uv build
```

### Version Conflicts

**Problem**: Version already exists on PyPI
```
HTTP Error 400: File already exists
```

**Solution**:
```bash
# Bump version
task version:bump

# Or manually increment
# Edit pyproject.toml and src/fnb/__init__.py

# Check current version
cat pyproject.toml | grep version
uv run python -c "import fnb; print(fnb.__version__)"

# Test upload to TestPyPI first
task publish:test
```

### Package Verification Failures

**Problem**: TestPyPI verification fails
```
ERROR: No matching distribution found for fnb==x.y.z
```

**Solution**:
```bash
# Wait for package propagation (5-10 minutes)
sleep 300

# Check package on TestPyPI
open https://test.pypi.org/project/fnb/

# Verify package contents
uv run python -c "
import tarfile
import zipfile
# Check dist/ contents
"

# Manual verification
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           fnb==x.y.z
```

## SSH and Authentication Issues

### SSH Connection Failures

**Problem**: SSH authentication fails
```
pexpect.TIMEOUT: SSH connection timeout
```

**Solution**:
```bash
# Test SSH connection manually
ssh user@hostname

# Check SSH key setup
ssh-add -l
cat ~/.ssh/config

# Use SSH agent
eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa

# Configure SSH for non-interactive use
cat >> ~/.ssh/config << EOF
Host hostname
    HostName hostname
    User username
    IdentityFile ~/.ssh/id_rsa
    PasswordAuthentication no
EOF
```

### Password Authentication Issues

**Problem**: SSH password prompts not handled
```
pexpect.EOF: SSH connection unexpectedly closed
```

**Solution**:
```bash
# Set up .env file for password authentication
echo "HOSTNAME_PASSWORD=your_password" >> .env

# Or use SSH keys (recommended)
ssh-copy-id user@hostname

# Test without password
ssh -o PasswordAuthentication=no user@hostname

# Check pexpect interaction
uv run fnb fetch task_name --dry-run  # Test without actual transfer
```

### Host Key Verification

**Problem**: SSH host key verification fails
```
Host key verification failed
```

**Solution**:
```bash
# Add host to known_hosts
ssh-keyscan hostname >> ~/.ssh/known_hosts

# Or temporarily disable host key checking (less secure)
ssh -o StrictHostKeyChecking=no user@hostname

# Update SSH config
cat >> ~/.ssh/config << EOF
Host hostname
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
```

## Performance and Network Issues

### Slow Transfer Speeds

**Problem**: File transfers are slower than expected

**Solution**:
```bash
# Optimize rsync options
options = [
    "-av",
    "--compress",
    "--compress-level=6",
    "--partial",
    "--progress"
]

# Use parallel transfers (if available)
options = ["-av", "--parallel=4"]

# Adjust SSH compression
options = ["-av", "-e", "ssh -C"]

# Monitor network usage
iotop
nethogs
```

### Large File Handling

**Problem**: Transfers fail with large files
```
rsync: error in rsync protocol data stream
```

**Solution**:
```bash
# Use partial transfers
options = ["-av", "--partial", "--partial-dir=.rsync-partial"]

# Increase timeout values
options = ["-av", "--timeout=3600"]

# Use checksum verification
options = ["-av", "--checksum"]

# Split large transfers
# Create multiple tasks for different subdirectories
```

### Network Interruption Recovery

**Problem**: Transfers fail due to network issues

**Solution**:
```bash
# Enable resume capability
options = ["-av", "--partial", "--append", "--progress"]

# Use persistent connections
options = ["-av", "-e", "ssh -o ControlMaster=auto -o ControlPath=/tmp/ssh-%r@%h:%p"]

# Implement retry logic
for i in {1..3}; do
    uv run fnb fetch task_name && break
    echo "Retry $i failed, waiting..."
    sleep 60
done
```

## Testing Issues

### Test Environment Setup

**Problem**: Tests fail in CI or different environments

**Solution**:
```bash
# Use test fixtures properly
# Check tests/conftest.py for available fixtures

# Isolate test dependencies
uv run pytest tests/unit/ --no-cov  # Skip coverage for debugging

# Run integration tests separately
task test:integration

# Check test configuration
cat pyproject.toml | grep -A10 pytest
```

### Mock and Fixture Issues

**Problem**: Mocking doesn't work correctly

**Solution**:
```bash
# Use proper mock paths
# Mock at the point of import, not definition
@patch('fnb.cli.run_rsync')  # ✓ Correct
@patch('fnb.gear.run_rsync')  # ✗ Wrong if imported in cli

# Check fixture scope
# Use appropriate scope: function, class, module, session

# Debug test isolation
uv run pytest tests/unit/test_module.py::test_function -v -s
```

### Coverage Issues

**Problem**: Test coverage drops unexpectedly

**Solution**:
```bash
# Generate detailed coverage report
task test
open htmlcov/index.html

# Find uncovered lines
uv run pytest --cov=fnb --cov-report=term-missing

# Exclude test-only code from coverage
# Add to pyproject.toml:
[tool.coverage.run]
omit = ["tests/*", "*/test_*"]
```

## Getting Help

### Debug Information Collection

When reporting issues, include:

```bash
# System information
uname -a
uv run python --version
uv --version

# Package version
uv run fnb version

# Configuration check
uv run fnb status

# Environment variables
env | grep -i fnb
env | grep -i python

# Recent logs (if applicable)
journalctl -u your-service --since "1 hour ago"
```

### Log Analysis

```bash
# Enable verbose output
uv run fnb fetch task_name --verbose

# Use dry-run for debugging
uv run fnb fetch task_name --dry-run

# Check rsync logs
rsync -av --verbose --dry-run user@host:/path /local/path
```

### Common Diagnostic Commands

```bash
# Test basic functionality
uv run fnb --help
uv run fnb version
uv run fnb init --help

# Check configuration
uv run fnb status

# Test network connectivity
ping hostname
telnet hostname 22
ssh -v user@hostname

# Verify permissions
ls -la ~/.config/fnb/
ls -la /target/directory/
```

### Support Resources

- **Issue Tracker**: https://gitlab.com/qumasan/fnb/-/issues
- **Documentation**: https://qumasan.gitlab.io/fnb/
- **Repository**: https://gitlab.com/qumasan/fnb
- **Contributing Guide**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Release Guide**: [RELEASING.md](./RELEASING.md)

### Creating Effective Bug Reports

When creating an issue, include:

1. **Environment Details**
   - OS and version
   - Python version (`uv run python --version`)
   - fnb version (`uv run fnb version`)
   - Installation method

2. **Reproduction Steps**
   - Exact commands used
   - Configuration file (with sensitive data removed)
   - Expected vs actual behavior

3. **Error Messages**
   - Complete error output
   - Stack traces
   - Log files

4. **Additional Context**
   - Network configuration
   - SSH setup
   - Recent changes

### Quick Fixes Checklist

Before reporting an issue, try:

- [ ] Update to latest version: `uv pip install --upgrade fnb`
- [ ] Recreate virtual environment: `rm -rf .venv && uv venv --python 3.12 && uv pip install -e .`
- [ ] Check configuration: `uv run fnb status`
- [ ] Test with dry-run: `uv run fnb fetch task_name --dry-run`
- [ ] Verify network connectivity: `ping hostname`
- [ ] Check SSH access: `ssh user@hostname`
- [ ] Review recent changes to configuration or environment

---

**Last Updated**: 2025-08-21 (v0.10.0)
**Document Version**: 1.0.0
