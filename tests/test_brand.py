"""Tests for BrandResource - domain lookup."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from scrift import NotFoundError, Scrift
from tests.conftest import BRAND_JSON, RATE_HEADERS

if TYPE_CHECKING:
    import respx


class TestBrandGet:
    def test_returns_brand_response(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/brand?domain=stripe.com").mock(
            return_value=httpx.Response(200, json=BRAND_JSON, headers=RATE_HEADERS)
        )
        result = client.brand.get("stripe.com")
        assert result.slug == "stripe"
        assert result.name == "Stripe"
        assert result.variants == ["color", "mono", "wordmark"]
        assert result.rate_limit is not None
        assert result.rate_limit.limit == 1000

    def test_snake_case_mapping(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/brand?domain=stripe.com").mock(
            return_value=httpx.Response(200, json=BRAND_JSON)
        )
        result = client.brand.get("stripe.com")
        assert result.brand_color == "635BFF"
        assert result.dark_mode_color == "7A73FF"

    def test_css_vars(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/brand?domain=stripe.com").mock(
            return_value=httpx.Response(200, json=BRAND_JSON)
        )
        result = client.brand.get("stripe.com")
        assert result.css is not None
        assert result.css.brand_color == "#635BFF"

    def test_not_found_raises(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/brand?domain=nope.invalid").mock(
            return_value=httpx.Response(
                404, json={"error": "domain_not_found", "message": "Domain not found"}
            )
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.brand.get("nope.invalid")
        assert exc_info.value.error_code == "domain_not_found"
