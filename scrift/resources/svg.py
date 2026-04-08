"""SVG resource - fetch raw SVG bytes for a brand."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrift._http import HttpClient


class SvgResource:
    """Operations on /v1/svg."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(
        self,
        slug: str,
        *,
        variant: str | None = None,
    ) -> bytes:
        """Fetch raw SVG bytes for *slug*.

        Returns the response body as ``bytes``.
        """
        params: dict[str, object] = {}
        if variant is not None:
            params["variant"] = variant
        response = self._http.get(f"/v1/svg/{slug}", params=params or None)
        return response.content
