"""Tests for HTTP error mapping and 429 retry logic."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from scrift import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    Scrift,
    ScriftError,
    ValidationError,
)
from tests.conftest import ERROR_AUTH, ERROR_RATE_LIMIT, SERVICE_JSON

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestExceptionHierarchy:
    def test_all_inherit_from_scrift_error(self) -> None:
        assert issubclass(AuthenticationError, ScriftError)
        assert issubclass(NotFoundError, ScriftError)
        assert issubclass(RateLimitError, ScriftError)
        assert issubclass(ValidationError, ScriftError)
        assert issubclass(APIError, ScriftError)

    def test_scrift_error_attributes(self) -> None:
        err = ScriftError("test", status_code=500, error_code="internal_error")
        assert err.message == "test"
        assert err.status_code == 500
        assert err.error_code == "internal_error"
        assert str(err) == "test"

    def test_scrift_error_repr(self) -> None:
        err = ScriftError("oops", status_code=400, error_code="bad_request")
        assert "ScriftError" in repr(err)
        assert "400" in repr(err)


class TestErrorMapping:
    def test_401_raises_authentication_error(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=401,
            json=ERROR_AUTH,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "invalid_api_key"

    def test_500_raises_api_error(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=500,
            json={"error": "internal_error", "message": "Something broke"},
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with pytest.raises(APIError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 500

    def test_non_json_error_body(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=502,
            content=b"Bad Gateway",
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with pytest.raises(APIError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 502
        assert "502" in exc_info.value.message


class TestRateLimitRetry:
    def test_retries_on_429_then_succeeds(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=429,
            json=ERROR_RATE_LIMIT,
            headers={"Retry-After": "0"},
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        httpx_mock.add_response(
            json=SERVICE_JSON,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            result = client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(0.0)
        assert result.slug == "stripe"

    def test_raises_after_retry_still_429(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=429,
            json=ERROR_RATE_LIMIT,
            headers={"Retry-After": "0"},
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        httpx_mock.add_response(
            status_code=429,
            json=ERROR_RATE_LIMIT,
            headers={"Retry-After": "5"},
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with patch("scrift._http.time.sleep"):
            with pytest.raises(RateLimitError) as exc_info:
                client.catalog.get("stripe")
            assert exc_info.value.retry_after == 5.0

    def test_429_retry_after_capped_at_30s(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=429,
            json=ERROR_RATE_LIMIT,
            headers={"Retry-After": "120"},
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        httpx_mock.add_response(
            json=SERVICE_JSON,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(30.0)

    def test_429_without_retry_after_header(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=429,
            json=ERROR_RATE_LIMIT,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        httpx_mock.add_response(
            json=SERVICE_JSON,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            result = client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(1.0)
        assert result.slug == "stripe"


class TestContextManager:
    def test_client_as_context_manager(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json=SERVICE_JSON,
            url="https://api.scrift.app/v1/catalog/stripe",
        )
        with Scrift(api_key="sk_test_abc123") as client:
            result = client.catalog.get("stripe")
            assert result.slug == "stripe"

    def test_unclosed_client_warns(self, httpx_mock: HTTPXMock) -> None:
        import warnings

        client = Scrift(api_key="sk_test_abc123")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            assert len(w) == 1
            assert issubclass(w[0].category, ResourceWarning)
            assert "Unclosed" in str(w[0].message)
        client.close()

    def test_closed_client_no_warning(self, httpx_mock: HTTPXMock) -> None:
        import warnings

        client = Scrift(api_key="sk_test_abc123")
        client.close()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            assert len(w) == 0
