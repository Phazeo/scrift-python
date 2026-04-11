# Changelog

All notable changes to this project will be documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [SemVer](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

## [0.2.1] - 2026-04-11

### Fixed

- `svg_variants` and `colors` fields on `ServiceResponse` typed correctly as
  `list[SvgVariant] | None` and `list[ServiceColor] | None` (no longer `Any`)
- Client-side validation on `batch()`, `list()`, `get_png()`, `get_webp()` - raises
  `ValueError` before the HTTP call on invalid arguments
- All four resource classes (`CatalogResource`, `SvgResource`, `BrandResource`,
  `RasterResource`) now exported from `scrift.__init__`

### Added

- `SvgVariant` model (`variant: str`, `verified: bool`)
- `ServiceColor` model (`role: str`, `hex: str`, `source: str`)
- ADR-0001 documenting the single-retry-on-429 design decision

## [0.2.0] - 2026-04-08

### Added

- `RasterResource` on the client as `client.raster` with `get_png` and `get_webp`
  (`GET /v1/png/{slug}`, `GET /v1/webp/{slug}`) returning raw image bytes; optional
  `size` and `variant` query parameters
- `RateLimitInfo` (`limit`, `remaining`, `reset_at`) on all JSON response models,
  parsed from `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- `ScriftRateLimitError` (alias `RateLimitError`) with `retry_after: int | None` on
  HTTP 429 after the automatic retry is exhausted
- API key validation accepting `scrf_` + 8+ alphanumeric characters (plus legacy
  `sk_live_` / `sk_test_` and other opaque key shapes)

### Changed

- **Breaking:** `RateLimitError.retry_after` is now `int | None` (was `float | None`)

### Tests

- HTTP tests use `respx` for mocking

## [0.1.0] - 2026-04-08

### Added

- Initial release
- `ScriftClient` with `catalog`, `svg`, and `brand` resources
- `CatalogResource`: `get`, `list`, `batch`, `search`
- `SvgResource`: `get` (returns raw SVG bytes)
- `BrandResource`: `get` by domain
- Pydantic v2 models with camelCase → snake_case field mapping
- Exception hierarchy: `ScriftError`, `AuthenticationError`,
  `NotFoundError`, `RateLimitError`, `ValidationError`, `APIError`
- 429 retry with Retry-After header support
- Full test suite with HTTP mocks
