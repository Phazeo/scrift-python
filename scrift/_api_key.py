"""API key format validation (X-API-Key)."""

from __future__ import annotations

import re

_SCRF_INTERNAL = re.compile(r"^scrf_int_[A-Za-z0-9]+$")
_SCRF_CUSTOMER = re.compile(r"^scrf_[A-Za-z0-9]{8,}$")
_OPAQUE_LEGACY = re.compile(r"^[A-Za-z0-9_.\-]{8,}$")


def validate_api_key(key: str) -> None:
    """Raise ValueError if *key* is not an allowed API key shape."""
    if not key:
        msg = "Invalid API key format. Expected scrf_ + 8+ alphanumeric characters."
        raise ValueError(msg)

    if key.startswith("scrf_int_"):
        if _SCRF_INTERNAL.fullmatch(key):
            return
        msg = "Invalid API key format. Malformed scrf_int_* internal key."
        raise ValueError(msg)

    if key.startswith("scrf_"):
        if _SCRF_CUSTOMER.fullmatch(key):
            return
        msg = (
            "Invalid API key format. Expected scrf_ + 8+ alphanumeric characters "
            "(or scrf_int_* for internal keys)."
        )
        raise ValueError(msg)

    if _OPAQUE_LEGACY.fullmatch(key):
        return

    msg = "Invalid API key format. Expected scrf_ + 8+ alphanumeric characters."
    raise ValueError(msg)
