"""Tests for CatalogResource - get, list, batch, search."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scrift import NotFoundError, Scrift, ValidationError
from tests.conftest import ERROR_NOT_FOUND, ERROR_VALIDATION, SERVICE_JSON

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestCatalogGet:
    def test_returns_service_response(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(json=SERVICE_JSON, url="https://api.scrift.app/v1/catalog/stripe")
        result = client.catalog.get("stripe")
        assert result.slug == "stripe"
        assert result.name == "Stripe"

    def test_snake_case_mapping(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(json=SERVICE_JSON, url="https://api.scrift.app/v1/catalog/stripe")
        result = client.catalog.get("stripe")
        assert result.brand_color == "635BFF"
        assert result.dark_mode_color == "7A73FF"

    def test_css_vars_mapping(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(json=SERVICE_JSON, url="https://api.scrift.app/v1/catalog/stripe")
        result = client.catalog.get("stripe")
        assert result.css is not None
        assert result.css.brand_color == "#635BFF"
        assert result.css.brand_color_dark == "#7A73FF"
        assert result.css.brand_color_contrast == "#FFFFFF"

    def test_not_found_raises(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=404,
            json=ERROR_NOT_FOUND,
            url="https://api.scrift.app/v1/catalog/nonexistent",
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.catalog.get("nonexistent")
        assert exc_info.value.status_code == 404
        assert exc_info.value.error_code == "service_not_found"


class TestCatalogList:
    def test_returns_paginated_list(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        payload = {
            "items": [SERVICE_JSON],
            "total": 1,
            "limit": 50,
            "offset": 0,
        }
        httpx_mock.add_response(
            json=payload, url="https://api.scrift.app/v1/catalog?limit=50&offset=0"
        )
        result = client.catalog.list()
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].slug == "stripe"

    def test_custom_pagination(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        payload = {"items": [], "total": 100, "limit": 10, "offset": 20}
        httpx_mock.add_response(
            json=payload, url="https://api.scrift.app/v1/catalog?limit=10&offset=20"
        )
        result = client.catalog.list(limit=10, offset=20)
        assert result.limit == 10
        assert result.offset == 20


class TestCatalogBatch:
    def test_returns_batch_response(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        payload = {
            "results": {"stripe": SERVICE_JSON, "nonexistent": None},
            "found": 1,
            "notFound": ["nonexistent"],
        }
        httpx_mock.add_response(
            json=payload,
            url="https://api.scrift.app/v1/catalog/batch",
            method="POST",
        )
        result = client.catalog.batch(["stripe", "nonexistent"])
        assert result.found == 1
        assert result.not_found == ["nonexistent"]
        assert result.results["stripe"] is not None
        assert result.results["stripe"].slug == "stripe"
        assert result.results["nonexistent"] is None


class TestCatalogSearch:
    def test_returns_search_response(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        payload = {"matches": [SERVICE_JSON], "query": "stripe", "total": 1}
        httpx_mock.add_response(
            json=payload,
            url="https://api.scrift.app/v1/search?q=stripe",
        )
        result = client.catalog.search("stripe")
        assert result.total == 1
        assert result.query == "stripe"
        assert result.matches[0].slug == "stripe"

    def test_search_with_limit(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        payload = {"matches": [], "query": "st", "total": 0}
        httpx_mock.add_response(
            json=payload,
            url="https://api.scrift.app/v1/search?q=st&limit=5",
        )
        result = client.catalog.search("st", limit=5)
        assert result.total == 0

    def test_validation_error_on_short_query(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=422,
            json=ERROR_VALIDATION,
            url="https://api.scrift.app/v1/search?q=x",
        )
        with pytest.raises(ValidationError) as exc_info:
            client.catalog.search("x")
        assert exc_info.value.status_code == 422
