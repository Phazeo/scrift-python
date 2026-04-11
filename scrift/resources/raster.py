"""PNG and WebP raster endpoints - raw image bytes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrift._http import HttpClient

_VALID_RASTER_SIZES: frozenset[int] = frozenset({32, 64, 128, 256, 512})


def _validate_raster_args(slug: str, size: int | None) -> None:
    if not slug or not slug.strip():
        msg = "slug must be a non-empty string"
        raise ValueError(msg)
    if size is not None and size not in _VALID_RASTER_SIZES:
        msg = f"size must be one of {sorted(_VALID_RASTER_SIZES)}, got {size}"
        raise ValueError(msg)


class RasterResource:
    """Operations on /v1/png and /v1/webp."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_png(
        self,
        slug: str,
        *,
        size: int | None = None,
        variant: str | None = None,
    ) -> bytes:
        """Fetch PNG bytes for *slug* (``GET /v1/png/{slug}``).

        Allowed ``size`` values: 32, 64, 128, 256, 512.
        """
        _validate_raster_args(slug, size)
        params = _raster_params(size, variant)
        response = self._http.get(f"/v1/png/{slug}", params=params)
        return response.content

    def get_webp(
        self,
        slug: str,
        *,
        size: int | None = None,
        variant: str | None = None,
    ) -> bytes:
        """Fetch WebP bytes for *slug* (``GET /v1/webp/{slug}``)."""
        _validate_raster_args(slug, size)
        params = _raster_params(size, variant)
        response = self._http.get(f"/v1/webp/{slug}", params=params)
        return response.content


def _raster_params(size: int | None, variant: str | None) -> dict[str, Any] | None:
    p: dict[str, Any] = {}
    if size is not None:
        p["size"] = size
    if variant is not None:
        p["variant"] = variant
    return p or None
