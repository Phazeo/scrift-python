"""Shared fixtures for Scrift SDK tests."""

from __future__ import annotations

import pytest

from scrift import Scrift


@pytest.fixture
def client(httpx_mock) -> Scrift:  # type: ignore[type-arg]
    """Pre-configured Scrift client pointing at the mock transport."""
    return Scrift(api_key="sk_test_abc123")


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
