# Qwen Code Context for EastmoneyTradingLibrary

## Project Overview

This is a Python package named `emta` (EasyMoney Trading Agent). It's an unofficial library intended for interacting with Eastmoney trading services. The project is in early development stages, currently only containing a basic package structure.

### Key Technologies
- **Language**: Python 3.11
- **Dependency Management**: UV (package management and virtual environment)
- **Build System**: Hatchling
- **Testing**: Pytest
- **Code Quality**:
  - Mypy (static type checking)
  - Ruff (linting and formatting)
  - Pre-commit (git hooks)
- **License**: MIT

### Project Structure
```
EastmoneyTradingLibrary/
├── src/emta/           # Main source code package
│   ├── __init__.py     # Package initializer with a hello function
│   └── py.typed        # PEP 561 marker for type hints
├── tests/              # (Planned) Test directory
├── dist/               # Distribution files (built packages)
├── .python-version     # Specifies Python version (3.11)
├── LICENSE             # MIT license file
├── README.md           # Project documentation
├── pyproject.toml      # Project configuration (metadata, dependencies, tools)
└── uv.lock             # UV lock file for dependencies
```

## Building and Running

### Prerequisites
- Python 3.11 (as specified in `.python-version`)
- UV package manager

### Installation
```bash
pip install emta
```

### Development Setup
1. Clone the repository
2. Install dependencies using UV:
   ```bash
   uv sync
   ```

### Running Tests
Tests are written with pytest. Execute them using:
```bash
uv run pytest
```

### Type Checking
Run mypy for static type checking:
```bash
uv run mypy src/
```

### Linting
Check code style with ruff:
```bash
uv run ruff check src/
```

## Development Conventions

### Code Style
- Follow PEP 8 style guide
- Use type hints for all function signatures and variables where possible
- Ruff is configured with specific rules (E, W, F, I, B, C4, UP, ARG001) and ignores (E501, B008, W191, B904)

### Testing
- Use pytest for writing tests
- Place test files in a `tests/` directory (not yet present in current structure)
- Aim for comprehensive test coverage

### Dependency Management
- Runtime dependencies are defined in `pyproject.toml` under `[project.dependencies]`
- Development dependencies are defined in `pyproject.toml` under `[tool.uv.dev-dependencies]`
- Use `uv.lock` to lock dependency versions for reproducible builds

### Versioning
- Follow semantic versioning (currently at 0.4.1)
- Version is specified in `pyproject.toml`

### Commit Hooks
- Pre-commit is configured for git hooks to ensure code quality before commits

## Current Status
The project is in very early development. The main package (`src/emta/`) currently only contains a simple `hello()` function. The planned features include:
- [ ] Login to Eastmoney
- [ ] Modular code structure
- [ ] Error handling
