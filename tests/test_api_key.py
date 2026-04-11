"""API key validation."""

from __future__ import annotations

import pytest

from scrift import Scrift


@pytest.mark.parametrize(
    "key",
    [
        "scrf_testkey123456",
        "scrf_int_internal0001",
        "opaque_legacy_key_value_12345",
    ],
)
def test_accepts_allowed_key_shapes(key: str) -> None:
    c = Scrift(api_key=key)
    c.close()


@pytest.mark.parametrize(
    "key",
    [
        "",
        "scrf_short",
        "bad",
        "!!!",
        "scrf_int_!!!",
    ],
)
def test_rejects_invalid_keys(key: str) -> None:
    with pytest.raises(ValueError, match="Invalid API key"):
        Scrift(api_key=key)
