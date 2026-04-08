"""Tests for BrandResource - domain lookup."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scrift import NotFoundError, Scrift
from tests.conftest import BRAND_JSON

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestBrandGet:
    def test_returns_brand_response(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            json=BRAND_JSON,
            url="https://api.scrift.app/v1/brand?domain=stripe.com",
        )
        result = client.brand.get("stripe.com")
        assert result.slug == "stripe"
        assert result.name == "Stripe"
        assert result.variants == ["color", "mono", "wordmark"]

    def test_snake_case_mapping(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            json=BRAND_JSON,
            url="https://api.scrift.app/v1/brand?domain=stripe.com",
        )
        result = client.brand.get("stripe.com")
        assert result.brand_color == "635BFF"
        assert result.dark_mode_color == "7A73FF"

    def test_css_vars(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            json=BRAND_JSON,
            url="https://api.scrift.app/v1/brand?domain=stripe.com",
        )
        result = client.brand.get("stripe.com")
        assert result.css is not None
        assert result.css.brand_color == "#635BFF"

    def test_not_found_raises(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=404,
            json={"error": "domain_not_found", "message": "Domain not found"},
            url="https://api.scrift.app/v1/brand?domain=nope.invalid",
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.brand.get("nope.invalid")
        assert exc_info.value.error_code == "domain_not_found"
