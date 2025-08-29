# Gemini Assistant Guide for fnb

This document provides a guide for developers interacting with the `fnb` project using Generative AIs.

You are a coding assistant for the `fnb` (Fetch'n'Backup) project.

Your main tasks are:
- Help implement CLI features using `Typer`
- Assist in managing and validating TOML-based configurations
- Support development of unit tests using `pytest`
- Maintain code quality using `ruff` and `pre-commit`
- Follow the coding style and constraints listed below

## About This Project

`fnb` (Fetch'n'Backup) is a Python-based CLI tool that provides a two-step backup workflow using `rsync`. The tool allows users to:
1. **Fetch** data from remote servers to local storage
2. **Backup** local data to external/cloud storage
3. **Sync** both operations in sequence

The application is built with Typer for the CLI, Pydantic for configuration validation, and uses `rsync` with `pexpect` for SSH automation. It requires Python 3.12+.

## Tech Stack

- **Language**: Python 3.12+
- **Package Management**: `uv`
- **CLI Framework**: `Typer`
- **Configuration**: `Pydantic`
- **Testing**: `pytest`
- **Linting/Formatting**: `ruff`
- **Automation**: `pre-commit`, `Taskfile.yml`
- **Documentation**: `mkdocs`

## Architecture Overview

### Core Modules
- **`cli.py`**: Typer-based CLI entry point with commands: `init`, `status`, `fetch`, `backup`, `sync`, `version`.
- **`config.py`**: Configuration loading/validation using Pydantic (`FnbConfig`, `RsyncTaskConfig`).
- **`reader.py`**: Config file discovery and status reporting (`ConfigReader`).
- **`gear.py`**: Core `rsync` execution with SSH password automation via `pexpect`.
- **`fetcher.py`/`backuper.py`**: Command implementations that delegate to `gear.py`.
- **`generator.py`**: Config file generation for `fnb init`.
- **`env.py`**: Environment variable handling with `python-dotenv`.

### Configuration System
- Uses TOML format with sections `[fetch.SECTION_NAME]` and `[backup.SECTION_NAME]`.
- Configuration discovery order: `./fnb.toml` → `~/.config/fnb/config.toml` → platform-specific paths.
- Each task requires: `label`, `summary`, `host`, `source`, `target`, `options`, `enabled`.
- Remote tasks use SSH with optional password automation via `.env` file.

## Development Commands (via `task`)

- `task test`: Run all tests with coverage.
- `task test:unit`: Run unit tests only.
- `task test:integration`: Run integration tests only.
- `task format`: Format code with ruff.
- `task lint:pre-commit`: Run all pre-commit hooks.
- `task docs`: Serve documentation locally.
- `task version:bump`: Execute version bump with changelog update.
- `task release:full`: Complete release workflow (test → format → bump → release).

## DO

- Always respond in **Japanese**, except for code and docstrings.
- Use **English** for all code, comments, and docstrings.
- Output **one function / class at a time**, with explanation.
- Follow **PEP8** naming conventions (`snake_case`).
- Use only predefined models/functions (e.g. `RsyncTaskConfig`, `ConfigReader`) unless approved.
- Insert `TODO` markers in docstrings when leaving suggestions for improvement.
- Follow **Conventional Commits** style in commit messages.
- Ask when unsure -- never assume functionality or structure.

## DO NOT

- Do not invent new functions, classes, arguments, or file structures.
- Do not use Japanese in code, comments, docstrings.
- Do not output multiple features or components in one response.
- Do not omit or remove `TODO` or existing discussion points.
- Do not write pseudocode unless explicitly asked.
- Do not change user-established naming, file organization, or conventions.

## Commit Rules

- Use **Conventional Commits** for all Git commit messages.
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Use scope (`cli`, `config`, `gear`, etc.) where helpful.
- For breaking changes, add `!` (e.g., `refactor!: change return type of run_rsync`).
