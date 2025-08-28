## 0.12.0 (2025-08-28)

### Feat

- **logging**: display log file location on startup
- **logging**: optimize log file handling and configuration
- **logging**: complete stdout/stderr separation for user output
- **logging**: add CLI log level control to all commands
- **logging**: replace print with loguru in env.py
- **logging**: replace print with loguru in config.py
- **logging**: replace print with loguru in gear.py and backuper.py
- **logging**: replace print with loguru in reader.py + fix tests
- **logging**: replace print with loguru in fetcher.py + fix tests
- **logging**: add loguru dependency and logger module
- **mypy**: integrate mypy type checking into pre-commit workflow

### Fix

- **test**: update unit tests for loguru output changes
- **mypy**: limit mypy pre-commit hook to src/ directory only
- **types**: add type ignore for typer decorators in cli.py
- **types**: fix no-any-return type errors and improve mypy config
- **types**: fix type errors and update mypy config
- **docs**: add footer navigation links

### Refactor

- **reader**: separate user output from internal logging

## 0.11.2 (2025-08-25)

### Fix

- add ReadTheDocs-compatible optional dependencies

## 0.11.1 (2025-08-24)

### Fix

- **docs**: improve release notes formatting and update PyPI link

## 0.11.0 (2025-08-22)

### Feat

- **ci**: implement self-hosted Renovate via GitLab CI/CD
- **deps**: implement comprehensive Renovate setup for automated dependency management
- **ci**: add Renovate-specific test job for dependency updates
- **docs**: complete Phase 6 - build process optimization and API refinement
- **docs**: complete Phase 4 - quality improvement and content enhancement
- **docs**: complete Phase 2 - create comprehensive English documentation
- **docs**: configure mkdocs-static-i18n with English as default language
- add mkdocs-static-i18n dependency for multilingual documentation
- implement comprehensive API auto-extraction with mkdocstrings
- add comprehensive release management documentation to MkDocs
- update installation.ja.md with comprehensive installation guide
- integrate comprehensive installation guide into docs/installation.en.md
- add English placeholder pages and multilingual navigation
- update mkdocs.yml navigation for Japanese suffixed files
- rename markdown files with Japanese suffix (.ja.md)

### Fix

- **ci**: resolve Renovate job pipeline failures
- **test**: update test expectation for ConfigKind validation error
- update internal markdown links to use .ja.md suffix

### Refactor

- separate completed tasks from TODO.md to DONE.md

## 0.10.0 (2025-08-21)

### 🚀 Major Features

- **Automated TestPyPI Deployment**: Implement automatic TestPyPI deployment on tag push (issue#17)
  - Reduces manual work in release workflow
  - CI time increase minimal (~30 seconds)
  - Maintains safety with manual PyPI production approval

### 🔧 Enhanced Development Experience

- **Enhanced TestPyPI Verification**: Add comprehensive verification task with detailed checks
  - Requires explicit VERSION parameter to prevent errors
  - Includes module import testing for package integrity
  - Provides clear guidance for PyPI production deployment
  - Usage: `VERSION=x.y.z task verify:testpypi`

### 🐛 Fixes

- **Parameter Handling**: Correct VERSION parameter handling in verify:testpypi task
  - Switch from CLI_ARGS to environment variable approach
  - Fix precondition checks for better error handling

### 📋 Release Workflow Improvements

**New Automated Release Process**:
```bash
task release:full  →  [Auto TestPyPI]  →  Verify  →  [Manual PyPI]
```

- TestPyPI deployment now fully automated on tag push
- PyPI production deployment remains manual for safety
- Comprehensive verification tools available locally

### Refactor

- complete Phase 5 - testing and validation
- complete Phase 4 - configuration updates for new test structure
- update Taskfile.yml test tasks for new directory structure
- update pytest configuration for new test structure
- complete Phase 3 - move test_integration.py to tests/integration/
- complete Phase 2 - move remaining test files to tests/unit/
- move test_fixtures.py to tests/unit/ directory
- move test_generator.py to tests/unit/ directory
- move test_env.py to tests/unit/ directory
- move test_config.py to tests/unit/ directory

## 0.9.0 (2025-08-21)

### Feat

- add deploy stages for TestPyPI and PyPI
- add build stage for package creation in CI/CD
- add CI/CD and integration testing tasks to Taskfile
- add version management tasks to Taskfile

### Refactor

- reorganize Taskfile with improved naming and structure
- remove go-task-bin dependency from CI/CD
- remove redundant CI jobs for pipeline efficiency
- modernize GitLab CI/CD syntax from only to rules
- remove obsolete sandbox task from Taskfile

## 0.8.0 (2025-08-20)

### Feat

- complete PyPI metadata configuration

## 0.7.0 (2025-08-20)

### Feat

- add PyPI/TestPyPI publish tasks to Taskfile

### Fix

- remove duplicate file inclusion in wheel build

## 0.6.1 (2025-08-20)

### Fix

- handle pexpect.interact() failure in non-interactive environments

## 0.6.0 (2025-08-20)

### Feat

- add manual test Taskfile for controlled server testing
- add tests/manual/ to .gitignore
- remove integration tests directory

## 0.5.0 (2025-08-19)

### Feat

- **task**: add GitLab repository and pages navigation tasks
- **fnb**: rename project from rfb to fnb (fetch and backup)

### Fix

- **integration**: resolve failing tests and achieve 100% success rate
- **tests**: resolve environment variable interference between test modules
- **env**: correct environment variable prefix from RFB_ to FNB_
- **test**: improve testing of sys.exit in generator

### Refactor

- finalize rfb to fnb rename across all modules
- **reader**: update ConfigReader to use FnbConfig and fnb path
- **config**: rename RfbConfig to FnbConfig throughout codebase
- **fnb**: rename all references from rfb to fnb

## 0.4.1 (2025-07-25)

### Fix

- **task**: added Taskfile

## 0.4.0 (2025-05-07)

### Feat

- **init**: include timestamped header comment in generated files

### Fix

- **env.sampl**: fixed the instruction to run dotenvx

## 0.3.1 (2025-04-21)

### Fix

- **cli**: changed sync options default
- **gear**: make SSH error handling more flexible for common signals

### Refactor

- **config**: migrate to platformdirs for XDG compliant paths
- **paths**: ensure consistent use of Path objects
- improve type annotations consistency and standardize docstrings

## 0.3.0 (2025-04-18)

### Feat

- **auth**: implement SSH password retrieval from environment variables
- **config**: add .env file support for SSH password management
- **cli**: fixed default options to production mode
- **config**: add embedded config template in assets directory
- **gear**: add verify_directory function
- **cli**: added rfb version to show version number

### Refactor

- **create_dirs**: replace ensure_directory_exists with verify_directory

## 0.2.0 (2025-04-17)

### Feat

- **cli**: add ssh-password option to fetch command
- **status**: feat: improve status display with proper rsync paths
- **gear**: feat: add directory existence verification before rsync operations
- **cli**: Implement robust sync command for combined fetch and backup
- **cli**: add status command to display configuration state
- **cli**: implement `rfb init` command for config generation
- **init**: add config file generator module
- **backup**: implement backup logic with rsync
- **fetch**: implement fetch logic with rsync and optional SSH password
- **cli**: implement fetch command using ConfigReader
- **cli**: add base CLI with fetch/backup/sync commands
- **core**: implement fetcher and backuper logic with label support
- **gear**: add rsync utility with optional password automation
- **cli**: implement initial CLI entry point using Typer
- **config**: implement config loader with support for .env, XDG paths, and file merging
- **rfb**: Initial commit

### Fix

- **reader**: fix: preserve tilde and original path format in status display
- **init**: temporal fix
- **pyproject.toml**: updated project information

### Refactor

- **gear**: Refactor gear.py for better password handling and readability
- **config**: split config model and reader logic into separate classes
