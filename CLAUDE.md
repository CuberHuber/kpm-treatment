# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

**kpm-treatment** — tooling for working with Kaspersky Password Manager (KPM) data/exports.

Language: Python 3.11+; CI runs on 3.11, 3.12, and 3.13.

## Commands

```bash
# Install dependencies and the git hooks
uv sync
uv run pre-commit install

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

# Run EO style checker (FIN100: @final, PEO*: EO principles)
uv run flake8 src/

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Toolchain

| Tool | Purpose |
|------|---------|
| `uv` | Package and venv management |
| `pytest` | Test runner |
| `ruff` | Linting and formatting (replaces black and isort; flake8 still runs separately for EO codes) |
| `mypy` | Static type checking |
| `bandit` | Security scanning |
| `flake8` + `eo-styleguide` | EO principle enforcement (`FIN100`, `PEO*` codes), plus `flake8-final`, `flake8-no-private-methods`, `flake8-one-class`, `flake8-override` |
| `pre-commit` | Git hook enforcement |

### pre-commit hooks (`.pre-commit-config.yaml`)

The configured hooks fall into three groups.
File hygiene runs `trailing-whitespace`, `end-of-file-fixer`,
  `check-yaml`, and `check-added-large-files`.
Style and analysis run `ruff` (with `--fix`),
  `ruff-format`, `mypy`, `bandit`,
  and `flake8` with the EO plugin set.
Commit-message validation runs `conventional-pre-commit`
  on the `commit-msg` stage,
  accepting `feat`, `fix`, `perf`, `chore`,
  `docs`, `refactor`, `test`, and `ci`.
Run `uv run pre-commit install` after cloning
  to wire every group into git.

## Code style

Every rule is enforced by `ruff`, `mypy`, `bandit`,
  or `flake8` (eo-styleguide).
Fix the root cause; never silence a tool.

### Immutability

Every class is `@final`.
Never mutate state; return a new instance instead.

### Protocols, not inheritance

Describe capabilities with `typing.Protocol`.
Keep each `Protocol` to three or four methods.
No abstract base classes.

```python
class Parseable(Protocol):
    def export(self) -> KpmExport: ...
```

### Type annotations

Annotate every function signature.
Never use bare `Any`.

```python
# correct
def field(self, name: str) -> str: ...

# wrong
def field(self, name): ...
```

### Fail fast

Raise immediately on invalid state.
Never return `None` to signal failure; never swallow exceptions.

```python
def field(self, name: str) -> str:
    ...
    raise ValueError(
        f"Required field '{name}' missing in block:\n{self._raw}"
    )
```

### Resource acquisition

Use context managers for every resource.

```python
with open(path, encoding="utf-8") as fh:
    text = fh.read()
```

## Testing

- All tests under `tests/`, mirroring `src/` layout
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`
- No mocking of internal objects — use fakes/test doubles
- Each test exercises one behaviour

## GitHub Actions

CI matrix runs on Python **3.11, 3.12, 3.13**. Four workflows:

1. **Test** — `pytest --cov` on each matrix version
2. **Compliance** — `ruff check`, `ruff format --check`, `mypy`, `bandit`
3. **Pre-commit** — `pre-commit run --all-files`
4. **Release** — runs on `v*` tag push; rebuilds, publishes to PyPI via Trusted Publishing, and creates a GitHub Release

## Elegant Objects principles

This project follows [Elegant Objects](https://www.elegantobjects.org/) (Yegor Bugayenko):

- **No null** — raise exceptions immediately; never return `None` silently to signal failure
- **No static methods or utility classes** — behaviour belongs inside objects
- **Immutable objects** — never mutate state after construction; return new instances
- **No getters/setters** — objects expose behaviour, not data; method names describe what they do, not what they return
- **No type casting** — design away from `isinstance` checks
- **No implementation inheritance** — compose via `Protocol` and delegation
- **Small interfaces** — no `Protocol` with more than 3–4 methods
- **Constructor does nothing** — `__init__` only assigns; no I/O, no computation, no validation with side effects
- **Fail fast** — raise immediately on invalid state; never swallow exceptions silently
- **Objects represent entities** — not bags of data; a class named `UserData` is a smell

### Naming

- **No `-er`/`-or` class names** — a class name must be a noun representing an entity, not a "doer". Use `KpmText` not `KpmTextParser`; `Export` not `Exporter`. If tempted to add `-er`/`-or`, reconsider what entity the object represents.
- **Protocol names are adjectives** — Protocols describe capabilities: `Parseable`, `Exportable`, `Readable` — never `Parser`, `Reader`, `Exporter`.
- **Method names are verbs describing what the object does** — not what the method returns. Prefer `export()`, `fetch()`, `render()` over `getExport()`, `getData()`.

### Responsibilities

- **Max 5 public methods per class** — more signals too many responsibilities; split the class.
- **Max 4 constructor parameters** — if more are needed, compose objects or introduce an intermediate value object.

## Skills

This project mandates the [yegor256/skills][y256-skills] Claude Code skills.
Invoke the matching skill **before** starting each task below —
  no exceptions.

**fix-broken-build** — invoke whenever a build is broken:
  failing tests, linters, type checks,
  or any check that blocks a clean full build.

**explain-architecture** — invoke when writing, editing,
  or reviewing the architecture section of `README.md`.

**analyze-argumentation-flow** — invoke when reviewing English prose
  in design documents, README sections, ADRs,
  or any text that defends a thesis.

**format-plain-text** — invoke whenever creating or editing `.md`,
  `.tex`, or `.txt` files;
  apply to all prose outside fenced code blocks.

**rewrite-prose** — invoke when writing or polishing wording
  in `.md`, `.tex`, or `.txt` files,
  and in English embedded in source code:
  comments, docstrings, log messages, error messages,
  and user-facing strings.

[y256-skills]: https://github.com/yegor256/skills
