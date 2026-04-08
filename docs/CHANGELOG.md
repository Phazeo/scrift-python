# Changelog

All notable changes to this project will be documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [SemVer](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

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
- Full test suite with pytest-httpx mocks
