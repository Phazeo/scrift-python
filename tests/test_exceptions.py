"""Tests for HTTP error mapping and 429 retry logic."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import httpx
import pytest

from scrift import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    Scrift,
    ScriftError,
    ScriftRateLimitError,
    ValidationError,
)
from tests.conftest import ERROR_AUTH, ERROR_RATE_LIMIT, SERVICE_JSON

if TYPE_CHECKING:
    import respx


class TestExceptionHierarchy:
    def test_all_inherit_from_scrift_error(self) -> None:
        assert issubclass(AuthenticationError, ScriftError)
        assert issubclass(NotFoundError, ScriftError)
        assert issubclass(ScriftRateLimitError, ScriftError)
        assert issubclass(RateLimitError, ScriftError)
        assert RateLimitError is ScriftRateLimitError
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

    def test_rate_limit_repr_includes_retry(self) -> None:
        err = ScriftRateLimitError("slow down", status_code=429, error_code="rl", retry_after=12)
        assert "12" in repr(err)


class TestErrorMapping:
    def test_401_raises_authentication_error(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(401, json=ERROR_AUTH)
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "invalid_api_key"

    def test_500_raises_api_error(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(
                500, json={"error": "internal_error", "message": "Something broke"}
            )
        )
        with pytest.raises(APIError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 500

    def test_non_json_error_body(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(502, content=b"Bad Gateway")
        )
        with pytest.raises(APIError) as exc_info:
            client.catalog.get("stripe")
        assert exc_info.value.status_code == 502
        assert "502" in exc_info.value.message


class TestRateLimitRetry:
    def test_retries_on_429_then_succeeds(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "0"}),
                httpx.Response(200, json=SERVICE_JSON),
            ]
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            result = client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(0.0)
        assert result.slug == "stripe"

    def test_raises_after_retry_still_429(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "0"}),
                httpx.Response(429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "5"}),
            ]
        )
        with patch("scrift._http.time.sleep"):
            with pytest.raises(ScriftRateLimitError) as exc_info:
                client.catalog.get("stripe")
            assert exc_info.value.retry_after == 5

    def test_429_retry_after_capped_at_30s(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "120"}),
                httpx.Response(200, json=SERVICE_JSON),
            ]
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(30.0)

    def test_429_without_retry_after_header(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(429, json=ERROR_RATE_LIMIT),
                httpx.Response(200, json=SERVICE_JSON),
            ]
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            result = client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(1.0)
        assert result.slug == "stripe"

    def test_malformed_retry_after_sleep_uses_default(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(
                    429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "not-a-number"}
                ),
                httpx.Response(200, json=SERVICE_JSON),
            ]
        )
        with patch("scrift._http.time.sleep") as mock_sleep:
            client.catalog.get("stripe")
            mock_sleep.assert_called_once_with(1.0)

    def test_final_429_malformed_retry_after_exception_field(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            side_effect=[
                httpx.Response(429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "0"}),
                httpx.Response(
                    429, json=ERROR_RATE_LIMIT, headers={"Retry-After": "not-a-number"}
                ),
            ]
        )
        with patch("scrift._http.time.sleep"):
            with pytest.raises(ScriftRateLimitError) as exc_info:
                client.catalog.get("stripe")
            assert exc_info.value.retry_after is None


class TestContextManager:
    def test_client_as_context_manager(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("https://api.scrift.app/v1/catalog/stripe").mock(
            return_value=httpx.Response(200, json=SERVICE_JSON)
        )
        with Scrift(api_key="scrf_testkey123456") as client:
            result = client.catalog.get("stripe")
            assert result.slug == "stripe"

    def test_unclosed_client_warns(self, respx_mock: respx.MockRouter) -> None:
        import warnings

        client = Scrift(api_key="scrf_testkey123456")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            assert len(w) == 1
            assert issubclass(w[0].category, ResourceWarning)
            assert "Unclosed" in str(w[0].message)
        client.close()

    def test_closed_client_no_warning(self, respx_mock: respx.MockRouter) -> None:
        import warnings

        client = Scrift(api_key="scrf_testkey123456")
        client.close()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            assert len(w) == 0
