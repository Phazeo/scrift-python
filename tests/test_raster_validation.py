"""Tests for client-side argument validation on RasterResource."""

from __future__ import annotations

import pytest

from scrift import Scrift


@pytest.fixture
def client() -> Scrift:
    return Scrift(api_key="scrf_testkey123456")


class TestRasterPngValidation:
    def test_empty_slug_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="slug must be a non-empty string"):
            client.raster.get_png("")

    def test_whitespace_slug_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="slug must be a non-empty string"):
            client.raster.get_png("   ")

    def test_invalid_size_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match=r"size must be one of \[32, 64, 128, 256, 512\]"):
            client.raster.get_png("stripe", size=100)

    def test_valid_sizes_pass_validation(self, client: Scrift) -> None:
        """All valid sizes should pass client validation."""
        import httpx
        import respx

        png_bytes = b"\x89PNG\r\n"
        for size in (32, 64, 128, 256, 512):
            with respx.mock(assert_all_called=False) as router:
                router.get(f"https://api.scrift.app/v1/png/stripe?size={size}").mock(
                    return_value=httpx.Response(200, content=png_bytes)
                )
                result = client.raster.get_png("stripe", size=size)
                assert result == png_bytes

    def test_size_none_passes(self, client: Scrift) -> None:
        """size=None (default) should not raise."""
        import httpx
        import respx

        with respx.mock(assert_all_called=False) as router:
            router.get("https://api.scrift.app/v1/png/stripe").mock(
                return_value=httpx.Response(200, content=b"\x89PNG")
            )
            client.raster.get_png("stripe")


class TestRasterWebpValidation:
    def test_empty_slug_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match="slug must be a non-empty string"):
            client.raster.get_webp("")

    def test_invalid_size_raises(self, client: Scrift) -> None:
        with pytest.raises(ValueError, match=r"size must be one of \[32, 64, 128, 256, 512\]"):
            client.raster.get_webp("stripe", size=99)
