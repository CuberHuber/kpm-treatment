# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**kpm-treatment** — tooling for working with Kaspersky Password Manager (KPM) data/exports.

Language: Python 3.11+ (supports each subsequent major version via CI matrix).

## Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_foo.py

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run linter/formatter
uv run ruff check .
uv run ruff format .

# Run type checker
uv run mypy src/

# Run security scanner
uv run bandit -r src/

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Toolchain

| Tool | Purpose |
|------|---------|
| `uv` | Package and venv management |
| `pytest` | Test runner |
| `ruff` | Linting and formatting (replaces black + isort + flake8) |
| `mypy` | Static type checking |
| `bandit` | Security scanning |
| `pre-commit` | Git hook enforcement |

### pre-commit hooks (`.pre-commit-config.yaml`)

Required hooks: `ruff`, `ruff-format`, `mypy`, `bandit`. Run `pre-commit install` after cloning.

## Code Style

- **PEP 8** + ruff enforcement
- **Type annotations** on all function signatures — no bare `Any`
- **Immutable by default**: prefer `@dataclass(frozen=True)` and `NamedTuple` over mutable classes
- Protocols (`typing.Protocol`) for structural subtyping — no abstract base classes
- Use context managers for all resource acquisition

## Testing

- All tests under `tests/`, mirroring `src/` layout
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`
- No mocking of internal objects — use fakes/test doubles
- Each test exercises one behavior

## GitHub Actions

CI matrix runs on Python **3.11, 3.12, 3.13**. Three workflows:

1. **test** — `pytest --cov` on each matrix version
2. **compliance** — `ruff check`, `ruff format --check`, `mypy`, `bandit`
3. **pre-commit** — `pre-commit run --all-files`

## Elegant Objects Principles

This project follows [Elegant Objects](https://www.elegantobjects.org/) (Yegor Bugayenko):

- **No null** — raise exceptions or use `Optional` explicitly; never return `None` silently
- **No static methods or utility classes** — behaviour belongs inside objects
- **Immutable objects** — never mutate state after construction; return new instances
- **No getters/setters** — objects expose behaviour, not data; method names describe what they do, not what they return
- **No type casting** — design away from `isinstance` checks
- **No implementation inheritance** — compose via `Protocol` and delegation
- **Small interfaces** — no `Protocol` with more than 3–4 methods
- **Constructor does nothing** — `__init__` only assigns; no I/O, no computation, no validation with side effects
- **Fail fast** — raise immediately on invalid state; never swallow exceptions silently
- **Objects represent entities** — not bags of data; a class named `UserData` is a smell
