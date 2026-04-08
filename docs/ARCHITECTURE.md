# SDK Architecture

## Overview

The Scrift Python SDK targets **Python 3.13+**. It is a thin, typed HTTP client over the Scrift REST API.
It follows the same resource-oriented pattern used by Anthropic, Stripe, and
OpenAI's Python SDKs - the gold standard for Python API clients in 2026.

## Layer structure

```
scrift/
├── _client.py          # Entry point - ScriftClient instantiation
├── _http.py            # HTTP transport - auth, retries, error mapping
├── models.py           # Pydantic v2 response models (camelCase → snake_case)
├── exceptions.py       # Exception hierarchy
└── resources/
    ├── catalog.py      # CatalogResource - get, list, batch, search
    ├── svg.py          # SvgResource - get (returns raw bytes)
    └── brand.py        # BrandResource - get by domain
```

## Dependency direction

```
_client.py
└── resources/      (resources know about _http and models)
    └── _http.py    (http knows about exceptions only)
        └── exceptions.py
```

Dependencies point inward only. Resources never import each other.
`_http.py` never imports resources. `models.py` has zero imports from
this package - pure Pydantic.

## Adding a new endpoint

1. Backend ships the new route first
2. Add response model to `models.py`
3. Add method to the relevant resource file in `resources/`
4. Add tests in `tests/`
5. Never touch `_client.py` or `_http.py` for new features

New top-level resource (e.g. webhooks):

1. Create `resources/webhooks.py`
2. Add `self.webhooks = WebhooksResource(self._http)` in `_client.py`
3. Export from `__init__.py`

## HTTP layer

- httpx sync client (async client planned for v2)
- 30s default timeout, configurable
- X-API-Key injected on every request
- User-Agent: scrift-python/{version}
- Retry once on 429 with Retry-After respect
- No retry on other 4xx - fail fast

## Models

All API responses use camelCase. SDK models expose snake_case via Pydantic
field aliases. `model_config = ConfigDict(populate_by_name=True)` on every
model allows construction by either name.

## Versioning

Follows semantic versioning (SemVer):

- PATCH: bug fixes, no API changes
- MINOR: new methods, backward compatible
- MAJOR: breaking changes (rename, remove, signature change)

Never make breaking changes in a minor or patch release.
