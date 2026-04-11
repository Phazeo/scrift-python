"""Attach JSON models to HTTP responses (body + X-RateLimit-* headers)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrift.models import (
    BatchResponse,
    BrandResponse,
    CatalogListResponse,
    RateLimitInfo,
    SearchResponse,
    ServiceResponse,
)

if TYPE_CHECKING:
    import httpx


def _rate_limit_from_headers(headers: httpx.Headers) -> RateLimitInfo | None:
    limit = _header_int(headers, "x-ratelimit-limit")
    remaining = _header_int(headers, "x-ratelimit-remaining")
    reset_at = _header_int(headers, "x-ratelimit-reset")
    if limit is None and remaining is None and reset_at is None:
        return None
    return RateLimitInfo(limit=limit, remaining=remaining, reset_at=reset_at)


def _header_int(headers: httpx.Headers, name: str) -> int | None:
    raw = headers.get(name)
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def service_response_from_http(response: httpx.Response) -> ServiceResponse:
    obj = ServiceResponse.model_validate(response.json())
    return obj.model_copy(update={"rate_limit": _rate_limit_from_headers(response.headers)})


def brand_response_from_http(response: httpx.Response) -> BrandResponse:
    obj = BrandResponse.model_validate(response.json())
    return obj.model_copy(update={"rate_limit": _rate_limit_from_headers(response.headers)})


def batch_response_from_http(response: httpx.Response) -> BatchResponse:
    obj = BatchResponse.model_validate(response.json())
    rl = _rate_limit_from_headers(response.headers)
    merged = {
        slug: (svc.model_copy(update={"rate_limit": rl}) if svc is not None else None)
        for slug, svc in obj.results.items()
    }
    return obj.model_copy(update={"rate_limit": rl, "results": merged})


def catalog_list_response_from_http(response: httpx.Response) -> CatalogListResponse:
    obj = CatalogListResponse.model_validate(response.json())
    rl = _rate_limit_from_headers(response.headers)
    items = [item.model_copy(update={"rate_limit": rl}) for item in obj.items]
    return obj.model_copy(update={"rate_limit": rl, "items": items})


def search_response_from_http(response: httpx.Response) -> SearchResponse:
    obj = SearchResponse.model_validate(response.json())
    rl = _rate_limit_from_headers(response.headers)
    matches = [m.model_copy(update={"rate_limit": rl}) for m in obj.matches]
    return obj.model_copy(update={"rate_limit": rl, "matches": matches})
