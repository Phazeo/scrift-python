"""Low-level HTTP transport - auth injection, error mapping, retry on 429."""

from __future__ import annotations

import time
from typing import Any, NoReturn

import httpx

from scrift.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ScriftError,
    ScriftRateLimitError,
    ValidationError,
)

_DEFAULT_BASE_URL = "https://api.scrift.app"
_DEFAULT_TIMEOUT = 30.0
_MAX_RETRY_AFTER_SECONDS = 30.0


def _get_version() -> str:
    from scrift import __version__

    return __version__


class HttpClient:
    """Thin wrapper around ``httpx.Client`` with auth, error mapping, and 429 retry."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": f"scrift-python/{_get_version()}",
            },
        )

    # -- public request helpers ------------------------------------------------

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        json: Any | None = None,
    ) -> httpx.Response:
        return self._request("POST", path, json=json)

    # -- internals -------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        response = self._client.request(method, path, params=params, json=json)

        if response.status_code == 429:
            retry_after = _parse_retry_after_seconds(response)
            delay = (
                min(float(retry_after), _MAX_RETRY_AFTER_SECONDS)
                if retry_after is not None
                else 1.0
            )
            time.sleep(delay)
            response = self._client.request(method, path, params=params, json=json)

        if response.is_success:
            return response

        _raise_for_status(response)

    def close(self) -> None:
        self._client.close()


def _parse_retry_after_seconds(response: httpx.Response) -> float | None:
    header = response.headers.get("Retry-After")
    if header is None:
        return None
    try:
        return float(header)
    except (ValueError, TypeError):
        return None


def _retry_after_int(response: httpx.Response) -> int | None:
    raw = _parse_retry_after_seconds(response)
    if raw is None:
        return None
    return int(raw)


def _raise_for_status(response: httpx.Response) -> NoReturn:
    """Map HTTP status to the appropriate ScriftError subclass."""
    status = response.status_code
    error_code: str | None = None
    message: str = f"HTTP {status}"

    try:
        body = response.json()
        error_code = body.get("error")
        message = body.get("message", message)
    except (ValueError, UnicodeDecodeError):
        pass

    exc_cls: type[ScriftError]
    if status == 401:
        exc_cls = AuthenticationError
    elif status == 404:
        exc_cls = NotFoundError
    elif status == 422:
        exc_cls = ValidationError
    elif status == 429:
        raise ScriftRateLimitError(
            message,
            status_code=status,
            error_code=error_code,
            retry_after=_retry_after_int(response),
        )
    else:
        exc_cls = APIError

    raise exc_cls(message, status_code=status, error_code=error_code)
