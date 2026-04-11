"""Brand resource - look up a brand by domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrift._responses import brand_response_from_http

if TYPE_CHECKING:
    from scrift._http import HttpClient
    from scrift.models import BrandResponse


class BrandResource:
    """Operations on /v1/brand."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, domain: str) -> BrandResponse:
        """Look up a brand by its website domain."""
        response = self._http.get("/v1/brand", params={"domain": domain})
        return brand_response_from_http(response)
