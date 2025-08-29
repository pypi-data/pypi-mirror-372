# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bear Utils is a comprehensive Python utility library (Python 3.12+) that provides modular components for common programming tasks including caching, database management, logging, file handling, CLI tools, GUI utilities, and more. The project uses modern Python tooling with `uv` for dependency management and `nox` for automation.

## Development Commands

### Core Development Tasks
```bash
# Install dependencies (development setup)
uv sync

# Run tests
uv run pytest
# OR using nox
nox -s tests

# Run specific test
uv run pytest tests/path/to/test_file.py::test_function

# Lint and format code (auto-fix)
nox -s ruff_fix
# OR manually
uv run ruff check . --fix --config config/ruff.toml
uv run ruff format . --config config/ruff.toml

# Lint check only (CI-style, no changes)
nox -s ruff_check

# Type checking
nox -s pyright
# OR manually
uv run pyright

# Run tests with coverage
nox -s coverage
```

### Build and Release
```bash
# Build the package
uv build

# Run all quality checks
nox -t lint
nox -t typecheck
```

## Architecture

### Project Structure
- **Core Package**: `src/bear_utils/` - Main library code organized into domain-specific modules
- **Internal Package**: `src/bear_utils/_internal/` - Implementation details and CLI entry point  
- **CLI Entry Point**: `bear_utils._internal.cli:main` - Main CLI interface
- **Module Entry**: `python -m bear_utils` - Alternative execution method

### Key Modules
- `cache/` - Disk caching with diskcache
- `database/` - SQLAlchemy integration and utilities
- `logger_manager/` - Enhanced console logging with Rich
- `time/` - Time handling and measurement tools
- `files/` - File handling abstractions for different formats
- `cli/` - Command-line utilities and prompt helpers
- `gui/` - PyQt6-based desktop utilities (optional dependency)
- `graphics/` - Image processing and color gradient utilities
- `events/` - Pub/sub event system with async support
- `config/` - Configuration management with Pydantic
- `constants/` - Project-wide constants and enums

### Dependencies
- **Required**: SQLAlchemy, Rich, Pydantic, Typer, FastAPI, PIL, diskcache, etc.
- **Optional**: PyQt6 for GUI functionality (`pip install bear-utils[gui]`)
- **Development**: Ruff (linting), Pyright (typing), pytest (testing), nox (automation)

## Configuration Files

- `config/ruff.toml` - Ruff linting and formatting configuration
- `pyproject.toml` - Project metadata, dependencies, and tool configurations
- `noxfile.py` - Automation tasks for development workflow
- Pytest configuration embedded in `pyproject.toml`

## Code Conventions

- **Target Python**: 3.13+ (line-length: 120 characters)
- **Type Hints**: Comprehensive typing required, use modern types (`list` not `List`)
- **Documentation**: Google-style docstrings
- **Import Style**: Absolute imports preferred, organized by isort
- **Error Handling**: Specific exceptions preferred over broad catches

## Testing

- Framework: pytest with async support
- Location: `tests/` directory 
- Run with: `uv run pytest`
- Special markers: `@pytest.mark.visual` for visual verification tests
- Coverage reporting available via `nox -s coverage`

## Notable Patterns

- **Modular Design**: Each utility module is self-contained
- **Optional Dependencies**: GUI features require explicit installation  
- **Event-Driven**: Supports both sync and async event handlers
- **Configuration Management**: Pydantic-based settings with flexible sources
- **Dynamic Versioning**: Git-based semantic versioning via uv-dynamic-versioning
