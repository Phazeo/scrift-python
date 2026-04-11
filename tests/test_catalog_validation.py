"""Tests for client-side argument validation on CatalogResource."""

from __future__ import annotations

import pytest

from scrift import Scrift


@pytest.fixture
def client() -> Scrift:
    return Scrift(api_key="scrf_testkey123456")


class TestBatchValidation:
    def test_empty_list_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            client.catalog.batch([])

    def test_too_many_slugs_raises(self, client: Scrift) -> None:
        slugs = [f"slug-{i}" for i in range(51)]
        with pytest.raises(ValueError, match="at most 50 slugs, got 51"):
            client.catalog.batch(slugs)

    def test_exactly_50_does_not_raise_validation(self, respx_mock: None, client: Scrift) -> None:
        """50 slugs should pass client validation (server call will fail without mock)."""
        import httpx
        import respx as respx_lib

        payload = {"results": {}, "found": 0, "notFound": []}
        with respx_lib.mock(assert_all_called=False) as router:
            router.post("https://api.scrift.app/v1/catalog/batch").mock(
                return_value=httpx.Response(200, json=payload)
            )
            slugs = [f"slug-{i}" for i in range(50)]
            result = client.catalog.batch(slugs)
            assert result.found == 0

    def test_empty_string_slug_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="non-empty string"):
            client.catalog.batch(["stripe", ""])

    def test_whitespace_only_slug_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="non-empty string"):
            client.catalog.batch(["stripe", "   "])


class TestListValidation:
    def test_limit_zero_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="limit must be >= 1"):
            client.catalog.list(limit=0)

    def test_limit_negative_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="limit must be >= 1"):
            client.catalog.list(limit=-5)

    def test_limit_over_200_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="limit must be <= 200"):
            client.catalog.list(limit=201)

    def test_offset_negative_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="offset must be >= 0"):
            client.catalog.list(offset=-1)
