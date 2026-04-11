"""Edge cases for rate-limit header parsing on JSON responses."""

from __future__ import annotations

import httpx

from scrift._responses import service_response_from_http
from tests.conftest import SERVICE_JSON


def test_non_numeric_ratelimit_limit_ignored_per_field() -> None:
    r = httpx.Response(
        200,
        json=SERVICE_JSON,
        headers={
            "X-RateLimit-Limit": "unlimited",
            "X-RateLimit-Remaining": "10",
        },
    )
    out = service_response_from_http(r)
    assert out.rate_limit is not None
    assert out.rate_limit.limit is None
    assert out.rate_limit.remaining == 10
