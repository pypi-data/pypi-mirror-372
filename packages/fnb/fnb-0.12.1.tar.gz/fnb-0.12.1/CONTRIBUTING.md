# Contributing to fnb

Thank you for your interest in contributing to fnb (Fetch'n'Backup)! This guide provides everything you need to know to contribute effectively to the project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Code Standards](#code-standards)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Development Environment Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- GitLab CLI (`glab`) for issue and MR management

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://gitlab.com/qumasan/fnb.git
   cd fnb
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   uv venv

   # Install in development mode
   uv pip install -e .

   # Verify installation
   uv run fnb --help
   ```

3. **Install development dependencies**
   ```bash
   # Development tools are included in pyproject.toml
   # All dependencies are automatically installed with the above command
   ```

### Using Git Worktree for Branch Development

For isolated branch development, use git worktree to avoid conflicts:

```bash
# Check available branches
git branch -a

# Create worktree for feature branch
git worktree add ../worktrees/<feature-branch-name> -b <feature-branch-name>

# Work in isolated environment
cd ../worktrees/<feature-branch-name>
uv venv
uv pip install -e .

# After development, clean up
cd ../../fnb
git worktree remove ../worktrees/<feature-branch-name>
```

## Code Standards

### Python Standards

- **Python Version**: 3.12+ required
- **Code Style**: Follow PEP 8 (enforced by ruff)
- **Line Length**: 88 characters (configured in pyproject.toml)
- **Type Hints**: Required for all functions and methods
- **Docstrings**: Google-style docstrings for all public APIs

### Code Quality Tools

The project uses several automated tools for code quality:

```bash
# Format code
task lint

# Run pre-commit hooks
task lint:pre-commit

# Check types (if applicable)
# Type checking is handled by Pydantic models and function signatures
```

### Configuration

All tool configurations are in `pyproject.toml`:
- **ruff**: Linting and formatting
- **pytest**: Test configuration
- **commitizen**: Version management
- **hatch**: Build system

## Development Workflow

### Task Management with Taskfile

Use the `task` command for all development operations:

```bash
# Core development tasks
task test              # Run all tests with coverage
task test:unit         # Run unit tests only (fast)
task test:integration  # Run integration tests only
task test:ci           # Simulate CI pipeline locally
task lint              # Format code with ruff
task docs              # Serve documentation locally

# Version management
task version           # Preview version bump
task version:bump      # Execute version bump
task release           # Create GitLab release
task release:full      # Complete release workflow
```

### GitLab Issue-Driven Development

1. **Find or create an issue**
   ```bash
   # List open issues
   glab issue list

   # Create new issue
   glab issue create --title "feat: description" --label "enhancement"
   ```

2. **Create feature branch**
   ```bash
   # Use descriptive branch names
   git worktree add ../worktrees/feat-new-feature -b feat-new-feature
   ```

3. **Development cycle**
   ```bash
   # Make changes
   # Run tests frequently
   task test:unit

   # Format code before commit
   task lint

   # Run pre-commit hooks
   task lint:pre-commit
   ```

4. **Create merge request**
   ```bash
   # Create MR with issue reference
   glab mr create --title "feat: description" --description "Closes #<issue-number>"
   ```

## Testing

### Test Structure

- **Unit Tests**: `tests/unit/` (124 tests, ~1.65s execution)
- **Integration Tests**: `tests/integration/` (23 tests, ~3.25s execution)
- **Test Coverage**: Target 83%+ (currently 87%)

### Running Tests

```bash
# Run all tests
task test

# Run specific test categories
task test:unit         # Fast unit tests
task test:integration  # Comprehensive integration tests

# Run specific test files
uv run pytest tests/unit/test_specific.py

# Run with coverage report
uv run pytest --cov=fnb --cov-report=html
```

### Test Coverage Requirements

- **Minimum Coverage**: 83% overall
- **High-Priority Modules**:
  - cli.py, generator.py, reader.py: 85%+
  - gear.py, fetcher.py, backuper.py: 80%+

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies appropriately

## Documentation

### Documentation Structure

- **MkDocs Site**: Comprehensive user and developer documentation
- **API Documentation**: Auto-generated from docstrings
- **README.md**: Quick start and basic usage
- **INSTALLATION.md**: Detailed installation guide

### Building Documentation

```bash
# Serve documentation locally
task docs

# Build static documentation
task docs:build
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Update relevant documentation with code changes
- Follow existing documentation structure

## Submitting Changes

### Commit Message Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat(backup): add progress display for large transfers
fix(gear): resolve SSH connection timeout issue
docs(contributing): update development workflow
test(cli): add error scenario coverage
```

### Pull Request Process

1. **Ensure code quality**
   ```bash
   # Run complete CI pipeline locally
   task test:ci
   ```

2. **Create descriptive MR**
   - Clear title following conventional commits
   - Detailed description of changes
   - Reference related issues with "Closes #<issue-number>"

3. **MR Requirements**
   - All tests passing
   - Code coverage maintained
   - Documentation updated if needed
   - Pre-commit hooks passing

4. **Review Process**
   - Address reviewer feedback
   - Update MR as needed
   - Maintain clean commit history

## Release Process

### Version Management

The project uses semantic versioning with automated changelog generation:

```bash
# Preview version changes
task version

# Execute version bump
task version:bump

# Create GitLab release
task release

# Complete release workflow
task release:full
```

### PyPI Deployment

```bash
# Deploy to TestPyPI
task publish:test

# Deploy to production PyPI
task publish:prod

# Verify deployment
VERSION=x.y.z task verify:testpypi
```

### Automated Workflows

- **TestPyPI**: Automatic deployment on tag push
- **GitLab CI**: Automated testing and quality checks
- **Version Bumping**: Automated changelog and version updates

## Getting Help

### Resources

- **Documentation**: https://qumasan.gitlab.io/fnb/
- **Issue Tracker**: https://gitlab.com/qumasan/fnb/-/issues
- **Merge Requests**: https://gitlab.com/qumasan/fnb/-/merge_requests

### Support Channels

- Create an issue for bugs or feature requests
- Use discussions for questions and community support
- Check existing documentation and issues before creating new ones

### Contributing Guidelines

- **Be Respectful**: Follow the code of conduct
- **Be Clear**: Provide detailed descriptions and examples
- **Be Patient**: Allow time for review and feedback
- **Be Collaborative**: Work with maintainers and other contributors

## Project Maintainers

For questions about contribution guidelines or project direction, please reach out through GitLab issues or discussions.

---

Thank you for contributing to fnb! Your efforts help make this project better for everyone.
