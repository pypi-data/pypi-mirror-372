# Contributing Guide

Thank you for your interest in contributing to the fnb project! This guide explains how to contribute to the project effectively.

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://gitlab.com/qumasan/fnb.git
cd fnb
```

### 2. Development Environment Setup

```bash
# Setup virtual environment using uv
uv venv

# Install in development mode with all dependencies
uv pip install -e .

# Install development dependencies
uv sync --all-extras
```

### 3. Verify Installation

```bash
# Run tests to ensure everything is working
task test:unit

# Check code formatting
task lint

# Build documentation
task docs:build
```

## Coding Standards

### Code Style

- Python 3.12+ features and syntax
- Follow [PEP 8](https://peps.python.org/pep-0008/) coding style
- Use type hints for type-safe code
- Write comprehensive docstrings (Google style)
- Maintain sufficient test coverage (target: 85%+)

### Formatting and Linting

We use `ruff` for code formatting and linting:

```bash
# Format code automatically
task lint

# Run pre-commit hooks (includes formatting, linting, tests)
task lint:pre-commit

# Check code quality manually
uv run ruff check src tests
uv run ruff format src tests
```

### Documentation

- Use Google-style docstrings for all functions and classes
- Include examples in docstrings where helpful
- Update relevant documentation when adding features
- Write clear commit messages following [Conventional Commits](https://conventionalcommits.org/)

## Development Workflow

### 1. Issue-Driven Development

- Check existing issues before starting work
- Create an issue for new features or bugs
- Link pull requests to relevant issues
- Use GitLab's issue templates when available

### 2. Branching Strategy

```bash
# Create feature branch from main
git checkout -b feature/your-feature-name

# Work on your changes
# ... make changes ...

# Run tests and formatting
task test:ci

# Commit with conventional commit format
git commit -m "feat: add new backup validation feature"

# Push and create merge request
git push origin feature/your-feature-name
```

### 3. Merge Request Guidelines

- Use descriptive titles and descriptions
- Include issue references (e.g., "Closes #123")
- Ensure all CI checks pass
- Add/update tests for new functionality
- Update documentation as needed
- Request review from maintainers

## Testing

### Test Structure

```
tests/
├── unit/          # Fast unit tests (target: <2s execution)
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_fetcher.py
│   └── ...
├── integration/   # Integration tests (slower, more comprehensive)
│   └── test_integration.py
└── fixtures/      # Test fixtures and utilities
    └── ...
```

### Running Tests

```bash
# Run all tests
task test

# Run only unit tests (fast)
task test:unit

# Run only integration tests
task test:integration

# Run tests with coverage report
uv run pytest --cov=fnb --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_cli.py

# Run specific test
uv run pytest tests/unit/test_cli.py::test_version_command
```

### Writing Tests

- Write tests for new features and bug fixes
- Follow the existing test patterns
- Use descriptive test function names
- Include both positive and negative test cases
- Mock external dependencies (SSH, filesystem operations)

Example test:

```python
def test_config_validation_success():
    """Test successful configuration validation."""
    config_data = {
        "fetch": {
            "test_task": {
                "label": "test",
                "summary": "Test task",
                "host": "user@host",
                "source": "/remote/path/",
                "target": "./local/path/",
                "options": ["-av"],
                "enabled": True
            }
        }
    }

    config = FnbConfig.model_validate(config_data)
    assert len(config.fetch) == 1
    assert config.fetch["test_task"].label == "test"
```

## Documentation

### Building Documentation

```bash
# Serve documentation locally
task docs

# Build static documentation
task docs:build

# The documentation will be available at http://localhost:8000
```

### Documentation Structure

```
docs/
├── index.{en,ja}.md           # Home page
├── installation.{en,ja}.md    # Installation guide
├── usage/                     # User guides
│   ├── quickstart.{en,ja}.md
│   ├── commands.{en,ja}.md
│   └── ...
├── development/               # Developer documentation
│   ├── contributing.{en,ja}.md
│   └── releasing.{en,ja}.md
└── references/                # API and technical references
    ├── api.{en,ja}.md
    └── ...
```

### Writing Documentation

- Write in clear, concise English
- Include practical examples
- Use consistent terminology
- Update both English and Japanese versions when possible
- Test all code examples

## Version Management and Releases

### Version Bumping

We use `commitizen` for version management:

```bash
# Preview version bump
task bump-dry

# Execute version bump and update changelog
task bump

# Create GitLab release
task release
```

### Release Process

1. Ensure all tests pass: `task test:ci`
2. Update version and changelog: `task bump`
3. Create GitLab release: `task release`
4. Deploy to PyPI (maintainers only): `task publish:prod`

## GitLab Workflow

### Using GitLab CLI (glab)

```bash
# View issues
glab issue list

# Create merge request
glab mr create --title "feat: add new feature" --description "Closes #123"

# View merge request status
glab mr status

# Check CI pipeline
glab ci status
```

### Issue Templates

Use the provided issue templates for:
- Bug reports
- Feature requests
- Documentation improvements
- Performance issues

## Code Review Guidelines

### For Contributors

- Keep changes focused and atomic
- Write clear commit messages
- Include tests for new functionality
- Update documentation as needed
- Respond to review comments promptly

### For Reviewers

- Focus on code quality, not personal preferences
- Provide constructive feedback
- Test the changes if needed
- Check that CI passes
- Verify documentation is updated

## Common Development Tasks

### Adding a New CLI Command

1. Add command function in `src/fnb/cli.py`
2. Add business logic in appropriate module
3. Write comprehensive tests
4. Update documentation
5. Add usage examples

### Adding Configuration Options

1. Update Pydantic models in `src/fnb/config.py`
2. Add validation logic
3. Update configuration documentation
4. Add tests for validation scenarios
5. Update example configurations

### Fixing Bugs

1. Create a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Add regression test if needed
5. Update documentation if behavior changed

## Getting Help

### Communication Channels

- GitLab Issues: Technical discussions and bug reports
- GitLab Merge Requests: Code review discussions
- Documentation: In-code docstrings and docs/ directory

### Resources

- [fnb Documentation](https://qumasan.gitlab.io/fnb/)
- [GitLab Project](https://gitlab.com/qumasan/fnb)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes and changelogs
- Project documentation

Thank you for contributing to fnb! Your contributions help make backup workflows easier and more reliable for everyone.
