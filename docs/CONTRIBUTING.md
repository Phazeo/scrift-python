# Contributing to scrift-python

Thank you for your interest in contributing. This document covers
everything you need to get started.

## Prerequisites

- Python 3.13+
- uv (https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/scrift/scrift-python.git
cd scrift-python
uv sync --all-extras
```

## Project structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full layer breakdown.

## Making changes

### Adding a new endpoint

1. Add the response model to `scrift/models.py`
2. Add the method to the relevant file in `scrift/resources/`
3. Add tests in `tests/` - both happy path and error cases
4. Update the method reference table in `README.md`

### Adding a new resource

1. Create `scrift/resources/{name}.py`
2. Register it in `scrift/_client.py`: `self.{name} = {Name}Resource(self._http)`
3. Export from `scrift/__init__.py`
4. Add tests in `tests/test_{name}.py`

### Never do this

- Do not add business logic to `_http.py` - it is transport only
- Do not make real HTTP calls in tests - use respx mocks
- Do not break existing method signatures without a major version bump
- Do not add dependencies without discussion

## Running tests

```bash
uv run pytest tests/ --cov=scrift --cov-report=term-missing -v
```

## Quality gates (all must pass before submitting a PR)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy scrift/
uv run pytest tests/ --cov=scrift --cov-report=term-missing --cov-fail-under=85 -v
```

## Submitting a PR

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes and ensure all quality gates pass
4. Open a PR against `main` with a clear description
5. A maintainer will review within a few days

## Releasing

Releases are published to PyPI automatically via GitHub Actions using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — no API
token is stored anywhere.

### Who can release

Only maintainers with push access to `Phazeo/scrift-python` can trigger
a release. All releases require manual approval in the `pypi` GitHub
environment before publishing.

### Release process

1. Ensure all changes are merged to `main` and CI is green
2. Bump the version in `pyproject.toml` and `scrift/__init__.py`
3. Update `docs/CHANGELOG.md` with the new version entry
4. Commit: `git commit -m "chore: bump version to vX.Y.Z"`
5. Push to main: `git push origin main`
6. Tag the release: `git tag vX.Y.Z && git push origin vX.Y.Z`
7. GitHub Actions triggers automatically — go to the Actions tab
8. Review and approve the `pypi` environment deployment
9. Verify on PyPI: `pip install scrift==X.Y.Z`

### Version format

Follows [Semantic Versioning](https://semver.org/):

- Patch `0.2.x` — bug fixes, non-breaking improvements
- Minor `0.x.0` — new features, backward compatible
- Major `x.0.0` — breaking API changes

## Reporting bugs

Open a GitHub issue with:

- Python version
- SDK version (`pip show scrift`)
- Minimal reproduction code
- Expected vs actual behaviour

## Questions

Email hello@phazeo.com or open a GitHub discussion.
