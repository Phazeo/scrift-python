"""Tests for RasterResource (PNG / WebP)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    import respx

    from scrift import Scrift

PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
WEBP_BYTES = b"RIFF\x00\x00\x00\x00WEBP"


class TestRasterPng:
    def test_get_png_minimal(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/png/stripe").mock(
            return_value=httpx.Response(
                200, content=PNG_BYTES, headers={"Content-Type": "image/png"}
            )
        )
        assert client.raster.get_png("stripe") == PNG_BYTES

    def test_get_png_with_size_and_variant(
        self, respx_mock: respx.MockRouter, client: Scrift
    ) -> None:
        respx_mock.get("https://api.scrift.app/v1/png/stripe?size=256&variant=color").mock(
            return_value=httpx.Response(
                200, content=PNG_BYTES, headers={"Content-Type": "image/png"}
            )
        )
        out = client.raster.get_png("stripe", size=256, variant="color")
        assert out == PNG_BYTES


class TestRasterWebp:
    def test_get_webp(self, respx_mock: respx.MockRouter, client: Scrift) -> None:
        respx_mock.get("https://api.scrift.app/v1/webp/github?size=64").mock(
            return_value=httpx.Response(
                200, content=WEBP_BYTES, headers={"Content-Type": "image/webp"}
            )
        )
        assert client.raster.get_webp("github", size=64) == WEBP_BYTES
