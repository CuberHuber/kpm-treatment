<!-- Thank you for contributing to kpm-treatment. -->
<!-- See CONTRIBUTING.md for the rules every change must satisfy. -->

## Summary

<!-- Describe the change in one or two sentences.
     Focus on the why; the diff already covers the what. -->

## Related issue

Closes #

## Local checks

<!-- Tick every box that applies. A pull request that fails any
     of the three CI workflows (Test, Compliance, Pre-commit)
     cannot be merged. -->

- [ ] `uv run pytest --cov=src --cov-report=term-missing`
      (coverage gate is 80%)
- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy src/`
- [ ] `uv run bandit -r src/`
- [ ] `uv run flake8 src/`
- [ ] `uv run pre-commit run --all-files`

## Style and design

- [ ] Every new class is `@final` and immutable
      (`@dataclass(frozen=True)` for value types).
- [ ] Capabilities are exposed through `typing.Protocol`,
      not abstract base classes;
      protocols hold three or four methods at most.
- [ ] No `-er`/`-or` class names;
      protocol names are adjectives.
- [ ] No class exceeds five public methods
      or four constructor parameters.
- [ ] Every function signature is annotated;
      no bare `Any`.
- [ ] Functions raise immediately on invalid state
      and never return `None` to signal failure.

## Tests

- [ ] A change under `src/` ships with the tests that prove it works.
- [ ] A bug fix ships with a regression test
      that fails before the fix and passes after.
- [ ] Tests are marked with `@pytest.mark.unit`
      or `@pytest.mark.integration`,
      and no internal object is mocked.

## Notes for the reviewer

<!-- Anything reviewers should know:
     follow-up work, alternatives considered,
     external dependencies, or deliberate gaps. -->
