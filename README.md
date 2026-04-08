# scrift

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python SDK for the [Scrift](https://scrift.app) brand asset API. Fetch brand colours, SVG logos, and metadata for thousands of companies - one API call at a time.

## Installation

```bash
pip install scrift
```

## Quick start

```python
from scrift import Scrift

with Scrift(api_key="sk_live_...") as client:
    # Look up a single brand
    brand = client.catalog.get("stripe")
    print(brand.name, brand.brand_color)  # Stripe 635BFF

    # List the catalog
    page = client.catalog.list(limit=10)
    for item in page.items:
        print(item.slug)

    # Batch lookup (up to 50 slugs)
    batch = client.catalog.batch(["stripe", "github", "vercel"])
    print(batch.found, batch.not_found)

    # Search by name
    results = client.catalog.search("stripe")
    for match in results.matches:
        print(match.slug, match.name)

    # Fetch an SVG logo
    svg_bytes = client.svg.get("stripe", variant="dark")

    # Look up a brand by domain
    info = client.brand.get("stripe.com")
    print(info.variants)  # ['color', 'mono', 'wordmark']
```

## Method reference

| Method | Description |
|---|---|
| `client.catalog.get(slug)` | Single brand by slug |
| `client.catalog.list(limit=, offset=)` | Paginated catalog list |
| `client.catalog.batch(slugs)` | Batch lookup (max 50) |
| `client.catalog.search(query, limit=)` | Search by name (min 2 chars) |
| `client.svg.get(slug, variant=)` | Raw SVG bytes |
| `client.brand.get(domain)` | Brand lookup by domain |

### SVG variants

`mono`, `color`, `dark`, `light`, `wordmark`, `icon`

### Error handling

```python
from scrift import Scrift, NotFoundError, RateLimitError

with Scrift(api_key="sk_live_...") as client:
    try:
        brand = client.catalog.get("nonexistent")
    except NotFoundError as e:
        print(e.error_code)  # service_not_found
    except RateLimitError as e:
        print(f"Retry after {e.retry_after}s")
```

All exceptions inherit from `ScriftError` and carry `status_code`, `error_code`, and `message`.

| Exception | HTTP status |
|---|---|
| `AuthenticationError` | 401 |
| `NotFoundError` | 404 |
| `ValidationError` | 422 |
| `RateLimitError` | 429 (auto-retries once, capped at 30s) |
| `APIError` | everything else |

## Links

- [Scrift](https://scrift.app)
- [API Documentation](https://scrift.app/docs)

## License

MIT
