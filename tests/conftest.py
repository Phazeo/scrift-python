"""Shared fixtures for Scrift SDK tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx

from scrift import Scrift

if TYPE_CHECKING:
    from collections.abc import Iterator

# Test-only API key shape (matches scrf_ + 8+ alnum).
TEST_API_KEY = "scrf_testkey123456"


@pytest.fixture
def client() -> Scrift:
    """Pre-configured Scrift client; register routes with respx in each test."""
    return Scrift(api_key=TEST_API_KEY)


@pytest.fixture
def respx_mock() -> Iterator[respx.MockRouter]:
    """Active respx router for the duration of a test."""
    with respx.mock(assert_all_called=False) as router:
        yield router


# -- reusable response payloads -----------------------------------------------

SERVICE_JSON = {
    "id": 1,
    "slug": "stripe",
    "name": "Stripe",
    "brandColor": "635BFF",
    "darkModeColor": "7A73FF",
    "svgVariants": None,
    "colors": None,
    "_css": {
        "--brand-color": "#635BFF",
        "--brand-color-dark": "#7A73FF",
        "--brand-color-contrast": "#FFFFFF",
    },
    "_notice": "Provided by Scrift",
}

SERVICE_JSON_WITH_VARIANTS = {
    **SERVICE_JSON,
    "svgVariants": [
        {"variant": "mono", "verified": True},
        {"variant": "color", "verified": False},
    ],
    "colors": [
        {"role": "primary", "hex": "#635BFF", "source": "official"},
        {"role": "on-dark", "hex": "#7A73FF", "source": "community"},
    ],
}

BRAND_JSON = {
    "id": 1,
    "slug": "stripe",
    "name": "Stripe",
    "brandColor": "635BFF",
    "darkModeColor": "7A73FF",
    "variants": ["color", "mono", "wordmark"],
    "_css": {
        "--brand-color": "#635BFF",
        "--brand-color-dark": "#7A73FF",
        "--brand-color-contrast": "#FFFFFF",
    },
    "_notice": "Provided by Scrift",
}

ERROR_NOT_FOUND = {"error": "service_not_found", "message": "Service not found"}
ERROR_AUTH = {"error": "invalid_api_key", "message": "Invalid API key"}
ERROR_RATE_LIMIT = {"error": "rate_limit_exceeded", "message": "Too many requests"}
ERROR_VALIDATION = {"error": "query_too_short", "message": "Query must be at least 2 characters"}

RATE_HEADERS = {
    "X-RateLimit-Limit": "1000",
    "X-RateLimit-Remaining": "42",
    "X-RateLimit-Reset": "1712592000",
}
