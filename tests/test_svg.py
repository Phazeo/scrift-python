"""Tests for SvgResource - raw SVG bytes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scrift import NotFoundError, Scrift
from tests.conftest import ERROR_NOT_FOUND

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

SVG_BYTES = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
)


class TestSvgGet:
    def test_returns_svg_bytes(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            content=SVG_BYTES,
            headers={"Content-Type": "image/svg+xml"},
            url="https://api.scrift.app/v1/svg/stripe",
        )
        result = client.svg.get("stripe")
        assert result == SVG_BYTES
        assert isinstance(result, bytes)

    def test_with_variant(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            content=SVG_BYTES,
            headers={"Content-Type": "image/svg+xml"},
            url="https://api.scrift.app/v1/svg/stripe?variant=dark",
        )
        result = client.svg.get("stripe", variant="dark")
        assert result == SVG_BYTES

    def test_not_found_raises(self, httpx_mock: HTTPXMock, client: Scrift) -> None:
        httpx_mock.add_response(
            status_code=404,
            json=ERROR_NOT_FOUND,
            url="https://api.scrift.app/v1/svg/nonexistent",
        )
        with pytest.raises(NotFoundError):
            client.svg.get("nonexistent")
