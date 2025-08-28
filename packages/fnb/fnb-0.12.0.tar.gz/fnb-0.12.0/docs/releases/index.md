# Release Notes

This section contains detailed release notes for fnb versions.

## Recent Releases

- [v0.11.2 - ReadTheDocs Documentation Platform Integration](v0.11.2.md) (2025-08-25)
- [v0.11.1 - Security Documentation Enhancement](v0.11.1.md) (2025-08-24)
- [v0.11.0 - Automated Maintenance & Internationalization](v0.11.0.md) (2025-08-22)

## Release Naming Convention

fnb follows [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

## Release Process

Our release process is automated with:
- **Commitizen**: Automatic version bumping and changelog generation
- **GitLab CI/CD**: Automated testing and deployment
- **TestPyPI**: Automatic test deployment on tag push
- **PyPI**: Manual approval for production deployment

See [Release Management](../development/releasing.md) for detailed workflow.

## Archive

For a complete changelog history, see [CHANGELOG.md](../../CHANGELOG.md).
