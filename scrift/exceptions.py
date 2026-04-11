"""Scrift SDK exceptions - one mapping location for all API errors."""

from __future__ import annotations


class ScriftError(Exception):
    """Base exception for all Scrift API errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )


class AuthenticationError(ScriftError):
    """Raised on 401 - invalid or missing API key."""


class NotFoundError(ScriftError):
    """Raised on 404 - resource does not exist."""


class ScriftRateLimitError(ScriftError):
    """Raised on 429 - rate limit exceeded after automatic retry is exhausted.

    ``retry_after`` is seconds to wait from the ``Retry-After`` header, or
    ``None`` if the header was absent or unparsable.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, error_code=error_code)
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r}, "
            f"retry_after={self.retry_after!r})"
        )


# Backward-compatible alias (v0.1.0 name).
RateLimitError = ScriftRateLimitError


class ValidationError(ScriftError):
    """Raised on 422 - request validation failed."""


class APIError(ScriftError):
    """Raised for any other non-success status code."""
