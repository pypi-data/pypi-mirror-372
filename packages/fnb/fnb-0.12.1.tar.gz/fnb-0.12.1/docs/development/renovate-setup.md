# Renovate Setup Guide

This document explains how to set up Renovate for automated dependency management in the fnb project.

## Overview

Renovate is configured to automatically update dependencies and create merge requests for:
- Python package dependencies
- Development tool dependencies
- Documentation dependencies
- Security vulnerability fixes

## Configuration

The project includes a `renovate.json` configuration file with the following features:

### Scheduling
- **Weekly updates**: Monday before 6am JST
- **Monthly lock file maintenance**: First day of each month
- **Security updates**: Immediate processing

### Grouping Strategy
- **Python production dependencies**: Core runtime packages
- **Python dev dependencies**: Testing and development tools
- **Documentation dependencies**: MkDocs and related packages
- **Testing dependencies**: pytest and coverage tools

### Auto-merge Rules
- **Patch updates**: Automatically merged for stable packages (typer, pydantic, etc.)
- **Major updates**: Require manual review
- **Security updates**: High priority with immediate notification

## GitLab Integration

### Step 1: Enable Renovate in GitLab

1. Go to your GitLab project settings
2. Navigate to **Integrations**
3. Search for **Renovate**
4. Enable the integration
5. Configure webhook URL (if using self-hosted Renovate)

### Step 2: Configure Renovate App (GitLab.com)

If using GitLab.com:

1. Visit [Renovate GitLab App](https://gitlab.com/renovate-bot/renovate)
2. Install the app for your project
3. Grant necessary permissions:
   - Read repository contents
   - Create merge requests
   - Update repository settings

### Step 3: Verify Configuration

After setup, Renovate will:
1. Scan your `pyproject.toml` for dependencies
2. Create an initial "Configure Renovate" MR
3. Start creating dependency update MRs based on schedule

## Testing Locally

Use the provided Taskfile tasks to simulate Renovate locally:

```bash
# Update all dependencies
task deps:update

# Test with updated dependencies
task deps:test

# Check for security vulnerabilities
task deps:security
```

## CI/CD Integration

The project includes a special `renovate-test` job that runs enhanced testing for Renovate MRs:

- Comprehensive unit test suite
- Package integrity validation
- Installation testing from built wheel
- Command-line interface verification

## Monitoring and Maintenance

### Renovate Dashboard

Monitor Renovate activity at:
- **GitLab**: Project → Merge Requests → Filter by "renovate" label
- **Renovate Dashboard**: `https://app.renovatebot.com/dashboard`

### Manual Intervention

Sometimes manual intervention is needed:
- **Merge conflicts**: Renovate will rebase automatically
- **Failed tests**: Review and fix compatibility issues
- **Major updates**: Evaluate breaking changes carefully

## Configuration Customization

The `renovate.json` file can be customized for:

### Package-specific rules
```json
{
  "packageRules": [
    {
      "matchPackageNames": ["specific-package"],
      "schedule": ["after 10pm on sunday"],
      "automerge": false
    }
  ]
}
```

### Ignore specific packages
```json
{
  "ignoreDeps": ["package-to-ignore"]
}
```

### Custom commit messages
```json
{
  "commitMessagePrefix": "⬆️ ",
  "semanticCommits": "enabled"
}
```

## Security Considerations

### Automated Security Updates

- **High priority**: Security updates are processed immediately
- **Auto-merge**: Critical patches are auto-merged after CI passes
- **Notification**: Security updates include detailed vulnerability info

### Token Management

- **GitLab tokens**: Renovate uses GitLab's built-in authentication
- **Registry access**: No additional tokens needed for PyPI packages
- **Permissions**: Minimal required permissions for security

### Review Process

1. **Automated checks**: CI/CD runs full test suite
2. **Security scanning**: Automated vulnerability assessment
3. **Manual review**: Major updates require human approval
4. **Rollback plan**: Easy revert via GitLab MR interface

## Troubleshooting

### Common Issues

**Renovate not creating MRs:**
- Check repository permissions
- Verify `renovate.json` syntax with JSON Schema
- Review Renovate logs in GitLab CI

**CI failures on Renovate MRs:**
- Check compatibility with updated dependencies
- Review test failures and adapt code if needed
- Use `task deps:test` to reproduce locally

**Too many MRs created:**
- Adjust `prConcurrentLimit` in configuration
- Group related dependencies together
- Modify scheduling to reduce frequency

### Getting Help

- **Renovate Documentation**: [docs.renovatebot.com](https://docs.renovatebot.com/)
- **GitLab Integration**: [GitLab Renovate docs](https://docs.gitlab.com/ee/user/project/integrations/renovate.html)
- **Community Support**: [GitHub Discussions](https://github.com/renovatebot/renovate/discussions)

## Maintenance Schedule

### Weekly Tasks (Automated)
- Dependency updates via Renovate MRs
- Security vulnerability scanning
- Automated testing of updates

### Monthly Tasks (Semi-automated)
- Lock file maintenance
- Review major version updates
- Update Renovate configuration if needed

### Quarterly Tasks (Manual)
- Review dependency strategy
- Update grouping rules
- Evaluate new packages for auto-merge

This setup ensures fnb dependencies stay current while maintaining stability and security.
