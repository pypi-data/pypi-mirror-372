# Release Management Guide

This document provides comprehensive instructions for releasing fnb (Fetch'n'Backup) to PyPI, including version management, testing procedures, and deployment workflows.

## Table of Contents

- [Release Overview](#release-overview)
- [Prerequisites](#prerequisites)
- [Version Management](#version-management)
- [Release Workflows](#release-workflows)
- [PyPI Deployment](#pypi-deployment)
- [Testing and Verification](#testing-and-verification)
- [Troubleshooting](#troubleshooting)
- [Automated CI/CD](#automated-cicd)

## Release Overview

The fnb project uses semantic versioning with automated workflows for:
- **Version Management**: Automated with commitizen
- **Testing**: Unit and integration tests with 87% coverage
- **Building**: Using uv build system with hatchling backend
- **Deployment**: TestPyPI for testing, PyPI for production
- **Documentation**: Automated changelog generation

### Release Types

- **Patch Release** (0.10.1): Bug fixes and minor improvements
- **Minor Release** (0.11.0): New features, backward compatible
- **Major Release** (1.0.0): Breaking changes (when ready)

## Prerequisites

### Environment Setup

1. **Development Environment**
   ```bash
   # Ensure clean working directory
   git status

   # Update to latest main branch
   git checkout main
   git pull origin main
   ```

2. **Required Tools**
   - Python 3.12+
   - uv package manager
   - GitLab CLI (`glab`)
   - Task runner (`task`)

3. **API Tokens Configuration**

   Create `.env` file in project root:
   ```bash
   # PyPI Production API Token
   PYPI_API_TOKEN=pypi-your-production-token-here

   # TestPyPI API Token
   TESTPYPI_API_TOKEN=pypi-your-testpypi-token-here
   ```

   **⚠️ Security Note**: Never commit API tokens to version control. Add `.env` to `.gitignore`.

### API Token Setup

1. **PyPI Production Token**
   - Visit https://pypi.org/manage/account/token/
   - Create token with scope limited to `fnb` project
   - Add to `.env` as `PYPI_API_TOKEN`

2. **TestPyPI Token**
   - Visit https://test.pypi.org/manage/account/token/
   - Create token with scope limited to `fnb` project
   - Add to `.env` as `TESTPYPI_API_TOKEN`

## Version Management

### Automated Version Bumping

The project uses [commitizen](https://commitizen-tools.github.io/commitizen/) for automated version management:

```bash
# Preview version changes (dry run)
task version

# Execute version bump with changelog update
task version:bump
```

### Manual Version Configuration

Files automatically updated during version bump:
- `pyproject.toml:version`
- `src/fnb/__init__.py:__version__`
- `CHANGELOG.md` (conventional commits)

### Version Scheme

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.10.0"
tag_format = "$version"
version_scheme = "semver"
update_changelog_on_bump = true
major_version_zero = true
```

## Release Workflows

### 1. Quick Release (Recommended)

Complete automated workflow for most releases:

```bash
# Complete release workflow (test → format → bump → release)
task release:full
```

This command performs:
1. Runs all tests including integration tests
2. Formats code with ruff
3. Runs pre-commit hooks
4. Bumps version and updates changelog
5. Creates GitLab release with tags

### 2. Step-by-Step Release

For more control over the release process:

```bash
# Step 1: Run comprehensive tests
task test

# Step 2: Format code and run quality checks
task lint
task lint:pre-commit

# Step 3: Preview version changes
task version

# Step 4: Bump version
task version:bump

# Step 5: Create GitLab release
task release
```

### 3. Development Testing Workflow

Before creating a release, test the complete CI pipeline locally:

```bash
# Simulate complete CI pipeline
task test:ci

# This runs:
# - Unit tests with coverage
# - Code formatting checks
# - Pre-commit hooks
```

## PyPI Deployment

### TestPyPI Deployment (Recommended First)

Always test deployment to TestPyPI before production:

```bash
# Deploy to TestPyPI
task publish:test
```

### Production PyPI Deployment

After successful TestPyPI verification:

```bash
# Deploy to production PyPI
task publish:prod
```

### Deployment Process Details

Both deployment commands perform:
1. **Build**: `uv build` creates wheel and source distribution
2. **Upload**: `uv publish` uploads to respective PyPI repository
3. **Validation**: Automatic package validation by PyPI

## Testing and Verification

### TestPyPI Verification

After TestPyPI deployment, verify the package:

```bash
# Verify specific version (replace x.y.z with actual version)
VERSION=x.y.z task verify:testpypi
```

The verification process:
1. Creates isolated test environment in `/tmp/fnb-test`
2. Installs package from TestPyPI
3. Tests core functionality:
   - `fnb version` command
   - `fnb --help` command
   - `fnb init --help` command
   - Module import verification
4. Reports verification status

### Manual Verification

You can also verify manually:

```bash
# Create test environment
cd /tmp
python3 -m venv test-fnb
source test-fnb/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           fnb==x.y.z

# Test basic functionality
fnb --help
fnb version
fnb init --help

# Cleanup
deactivate
rm -rf test-fnb
```

### Production Verification

After PyPI deployment, verify with:

```bash
# Install from production PyPI
pip install fnb==x.y.z

# Test functionality
fnb --help
fnb version
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build environment
   uv build --verbose

   # Common fixes:
   # - Update pyproject.toml metadata
   # - Check version consistency
   # - Verify dependency specifications
   ```

2. **Upload Failures**
   ```bash
   # Check API token validity
   echo $PYPI_API_TOKEN
   echo $TESTPYPI_API_TOKEN

   # Verify token permissions in PyPI account settings
   ```

3. **Version Conflicts**
   ```bash
   # Check current version
   cat pyproject.toml | grep version
   cat src/fnb/__init__.py | grep __version__

   # Force version consistency
   task version:bump
   ```

4. **Test Failures**
   ```bash
   # Run tests with verbose output
   task test:unit -v

   # Check coverage report
   open htmlcov/index.html
   ```

### Recovery Procedures

1. **Failed Release Recovery**
   ```bash
   # If release failed after version bump
   git reset --hard HEAD~1  # Reset to before version bump

   # Or fix issues and retry
   task release
   ```

2. **PyPI Upload Failure Recovery**
   ```bash
   # Delete failed packages (if possible)
   # Fix issues in code/configuration
   # Increment version and retry
   task version:bump
   task publish:test  # Always test first
   ```

## Automated CI/CD

### GitLab CI Integration

The project includes automated workflows:

1. **Automatic TestPyPI Deployment**
   - Triggered on git tag push
   - Runs complete test suite
   - Deploys to TestPyPI automatically

2. **Manual Production Deployment**
   - Use `task publish:prod` after TestPyPI verification
   - Requires manual execution for safety

### CI Configuration

GitLab CI automatically:
- Runs unit and integration tests
- Checks code formatting
- Validates package metadata
- Deploys to TestPyPI on tag creation

## Release Checklist

### Pre-Release

- [ ] All tests passing (`task test`)
- [ ] Code formatted (`task lint`)
- [ ] Pre-commit hooks pass (`task lint:pre-commit`)
- [ ] Documentation updated
- [ ] CHANGELOG.md reviewed
- [ ] API tokens configured in `.env`

### Release Process

- [ ] Version bumped (`task version:bump`)
- [ ] GitLab release created (`task release`)
- [ ] TestPyPI deployment successful (`task publish:test`)
- [ ] TestPyPI verification passed (`VERSION=x.y.z task verify:testpypi`)
- [ ] Production PyPI deployment (`task publish:prod`)
- [ ] Production verification completed

### Post-Release

- [ ] Release announcement (if needed)
- [ ] Documentation site updated
- [ ] Issue tracker updated
- [ ] Next development cycle planned

## Release Schedule

### Regular Releases

- **Patch Releases**: As needed for bug fixes
- **Minor Releases**: Monthly or when feature-complete
- **Major Releases**: When breaking changes are necessary

### Emergency Releases

For critical security or functionality issues:
1. Create hotfix branch
2. Implement minimal fix
3. Fast-track testing and review
4. Emergency release deployment

## Best Practices

### Development

- Use conventional commits for automatic changelog generation
- Maintain high test coverage (target: 87%+)
- Test all changes in TestPyPI before production
- Review changelogs before release

### Security

- Never commit API tokens
- Use minimal-scope API tokens
- Regularly rotate API tokens
- Monitor release notifications

### Documentation

- Update documentation with releases
- Maintain accurate installation instructions
- Document breaking changes clearly
- Provide migration guides for major releases

## Support and Contact

For release-related issues:
- **Bug Reports**: https://gitlab.com/qumasan/fnb/-/issues
- **Documentation**: https://qumasan.gitlab.io/fnb/
- **Merge Requests**: https://gitlab.com/qumasan/fnb/-/merge_requests

---

**Last Updated**: 2025-08-21 (v0.10.0)
**Document Version**: 1.0.0
