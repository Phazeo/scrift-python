"""Tests for SvgResource - raw SVG bytes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from scrift import NotFoundError, Scrift
from tests.conftest import ERROR_NOT_FOUND

if TYPE_CHECKING:
    import respx

SVG_BYTES = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
)


class TestSvgGet:
    def test_returns_svg_bytes(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/svg/stripe").mock(
            return_value=httpx.Response(
                200, content=SVG_BYTES, headers={"Content-Type": "image/svg+xml"}
            )
        )
        result = client.svg.get("stripe")
        assert result == SVG_BYTES
        assert isinstance(result, bytes)

    def test_with_variant(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/svg/stripe?variant=dark").mock(
            return_value=httpx.Response(
                200, content=SVG_BYTES, headers={"Content-Type": "image/svg+xml"}
            )
        )
        result = client.svg.get("stripe", variant="dark")
        assert result == SVG_BYTES

    def test_not_found_raises(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/svg/nonexistent").mock(
            return_value=httpx.Response(404, json=ERROR_NOT_FOUND)
        )
        with pytest.raises(NotFoundError):
            client.svg.get("nonexistent")
