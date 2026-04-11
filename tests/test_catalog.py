"""Tests for CatalogResource - get, list, batch, search."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from scrift import NotFoundError, Scrift, ValidationError
from tests.conftest import (
    ERROR_NOT_FOUND,
    ERROR_VALIDATION,
    RATE_HEADERS,
    SERVICE_JSON,
)

if TYPE_CHECKING:
    import respx


class TestCatalogGet:
    def test_returns_service_response(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(200, json=SERVICE_JSON)
        )
        result = client.catalog.get("stripe")
        assert result.slug == "stripe"
        assert result.name == "Stripe"

    def test_snake_case_mapping(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(200, json=SERVICE_JSON)
        )
        result = client.catalog.get("stripe")
        assert result.brand_color == "635BFF"
        assert result.dark_mode_color == "7A73FF"

    def test_css_vars_mapping(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(200, json=SERVICE_JSON, headers=RATE_HEADERS)
        )
        result = client.catalog.get("stripe")
        assert result.css is not None
        assert result.css.brand_color == "#635BFF"
        assert result.css.brand_color_dark == "#7A73FF"
        assert result.css.brand_color_contrast == "#FFFFFF"
        assert result.rate_limit is not None
        assert result.rate_limit.limit == 1000
        assert result.rate_limit.remaining == 42
        assert result.rate_limit.reset_at == 1712592000

    def test_not_found_raises(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/nonexistent").mock(
            return_value=httpx.Response(404, json=ERROR_NOT_FOUND)
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.catalog.get("nonexistent")
        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == "service_not_found"


class TestCatalogList:
    def test_returns_paginated_list(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        payload = {
            "items": [SERVICE_JSON],
            "total": 1,
            "limit": 50,
            "offset": 0,
        }
        respx_mock.get("https://api.scrift.app/v1/catalog?limit=50&offset=0").mock(
            return_value=httpx.Response(200, json=payload, headers=RATE_HEADERS)
        )
        result = client.catalog.list()
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].slug == "stripe"
        assert result.rate_limit is not None
        assert result.items[0].rate_limit == result.rate_limit

    def test_custom_pagination(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        payload = {"items": [], "total": 100, "limit": 10, "offset": 20}
        respx_mock.get("https://api.scrift.app/v1/catalog?limit=10&offset=20").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = client.catalog.list(limit=10, offset=20)
        assert result.limit == 10
        assert result.offset == 20


class TestCatalogBatch:
    def test_returns_batch_response(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        payload = {
            "results": {"stripe": SERVICE_JSON, "nonexistent": None},
            "found": 1,
            "notFound": ["nonexistent"],
        }
        respx_mock.post("https://api.scrift.app/v1/catalog/batch").mock(
            return_value=httpx.Response(200, json=payload, headers=RATE_HEADERS)
        )
        result = client.catalog.batch(["stripe", "nonexistent"])
        assert result.found == 1
        assert result.not_found == ["nonexistent"]
        assert result.results["stripe"] is not None
        assert result.results["stripe"].slug == "stripe"
        assert result.results["nonexistent"] is None
        assert result.rate_limit is not None
        assert result.results["stripe"] is not None
        assert result.results["stripe"].rate_limit == result.rate_limit


class TestCatalogSearch:
    def test_returns_search_response(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        payload = {"matches": [SERVICE_JSON], "query": "stripe", "total": 1}
        respx_mock.get("https://api.scrift.app/v1/search?q=stripe").mock(
            return_value=httpx.Response(200, json=payload, headers=RATE_HEADERS)
        )
        result = client.catalog.search("stripe")
        assert result.total == 1
        assert result.query == "stripe"
        assert result.matches[0].slug == "stripe"
        assert result.rate_limit is not None
        assert result.matches[0].rate_limit == result.rate_limit

    def test_search_with_limit(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        payload = {"matches": [], "query": "st", "total": 0}
        respx_mock.get("https://api.scrift.app/v1/search?q=st&limit=5").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = client.catalog.search("st", limit=5)
        assert result.total == 0

    def test_validation_error_on_short_query(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/search?q=x").mock(
            return_value=httpx.Response(422, json=ERROR_VALIDATION)
        )
        with pytest.raises(ValidationError) as exc_info:
            client.catalog.search("x")
        assert exc_info.value.status_code == 422
