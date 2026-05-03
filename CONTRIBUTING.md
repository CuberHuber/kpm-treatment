# Contributing to kpm-treatment

Thank you for considering a contribution.
This document covers everything you need
  to land a change in the project.

## Ground rules

The project follows the [Elegant Objects][eo] principles
  enforced by `flake8` with `eo-styleguide`
  (`FIN100`, `PEO*`)
  and the supplemental plugins
  (`flake8-final`,
  `flake8-no-private-methods`,
  `flake8-one-class`,
  `flake8-override`),
  `mypy --strict`,
  `ruff`,
  `bandit`,
  and the [yegor256/skills][y256-skills] Claude Code skills
  declared in [`CLAUDE.md`](CLAUDE.md).
Read [`CLAUDE.md`](CLAUDE.md) before opening a pull request.
Every rule there is enforced by a tool;
  if a tool reports a violation, fix the root cause
  rather than silence the tool.
Contributors are also expected to follow the
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

The non-negotiables in short form:

- Every class is `@final` and immutable
  (`@dataclass(frozen=True)` for value types).
- Capabilities live behind `typing.Protocol`,
  never abstract base classes;
  protocols hold three or four methods at most.
- Every function signature is annotated;
  bare `Any` is rejected.
- A function raises immediately on invalid state
  and never returns `None` to signal failure.
- Class names are nouns
  (no `-er` or `-or` suffixes);
  protocol names are adjectives.
- A class exposes at most five public methods
  and four constructor parameters.

## Development environment

The project uses [uv] for environment management
  and [pre-commit] for git hook enforcement.
After cloning,
  sync the dependencies and install the hooks once:

```bash
uv sync
uv run pre-commit install
```

Python 3.11+;
  CI runs on 3.11, 3.12, and 3.13.

## Local checks

Run every check locally before pushing:

```bash
# Tests with coverage (the project gates at 80%)
uv run pytest --cov=src --cov-report=term-missing

# Linter and formatter
uv run ruff check .
uv run ruff format .

# Static type checker (strict mode)
uv run mypy src/

# Security scanner
uv run bandit -r src/

# Elegant Objects style checker
uv run flake8 src/

# All hooks at once
uv run pre-commit run --all-files
```

A pull request that fails any of the three CI workflows
  (`Test`, `Compliance`, `Pre-commit`)
  cannot be merged.
The `Release` workflow runs separately on `v*` tag push
  and is not gated on pull requests.

## Tests

Every test lives under `tests/`,
  mirroring the `src/` layout.
Mark each test with `@pytest.mark.unit`
  or `@pytest.mark.integration`.
Each test exercises one behaviour.
The project forbids mocking internal objects;
  use fakes or test doubles that satisfy
  the relevant `Protocol` instead.

A change that touches `src/`
  ships with the tests that prove it works;
  a fix for a bug ships with a regression test
  that fails before the fix and passes after.

## Adding a new output format

The format catalogue is open by design;
  adding a target requires three steps.

1. Implement the format under `src/kpm_treatment/formats/`,
   declaring the protocols it satisfies
   (`Exportable`,
   `Lintable` if it can be auto-detected,
   and `Describable`).
   Raise `FormatUnrepresentable` from `of()`
   when a parsed `KpmExport` carries entries the format cannot render,
   rather than dropping records silently.
2. Register it in `DEFAULT_REGISTRY`
   at the bottom of `src/kpm_treatment/formats/registry.py`.
3. Add tests under `tests/test_formats.py`
   covering rendering,
   detection (if `Lintable`),
   and the unrepresentable path.

The architecture section of [`README.md`](README.md)
  walks through the same flow with concrete file references.

## Commit messages

Use the [Conventional Commits][conventional] prefix
  that matches the change:
  `feat`,
  `fix`,
  `perf`,
  `chore`,
  `docs`,
  `refactor`,
  `test`,
  or `ci`.
The first line stays under 72 characters
  and uses the imperative mood
  (`add CSV escape rule`,
  not `added CSV escape rule`).
The recent `git log` shows the project's house style.
The `commit-msg` pre-commit hook
  rejects any other prefix.

## Pull requests

Open a draft pull request as soon as the branch builds locally.
The repository's pull request template lists the checklist
  every reviewer applies before merging.

A pull request that depends on an unreleased external change
  must explain why the change is unavoidable
  and link the upstream issue.

## Releases

Maintainers cut releases by tagging the `main` branch
  with a `v*` tag that matches `project.version` in `pyproject.toml`.
The [`Release` workflow][release-yml]
  rebuilds and tests the package,
  publishes to [PyPI] through trusted publishing,
  and creates a GitHub Release with the artefacts attached.
Contributors do not run the release workflow;
  they bump the version
  and let the maintainer push the tag.

## Reporting a security issue

Do not open a public issue for a vulnerability.
Follow the disclosure process in [`SECURITY.md`](SECURITY.md).

[conventional]: https://www.conventionalcommits.org/
[eo]: https://www.elegantobjects.org/
[pre-commit]: https://pre-commit.com/
[PyPI]: https://pypi.org/project/kpm-treatment/
[release-yml]: .github/workflows/release.yml
[uv]: https://docs.astral.sh/uv/
[y256-skills]: https://github.com/yegor256/skills
