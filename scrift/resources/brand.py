"""Brand resource - look up a brand by domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrift.models import BrandResponse

if TYPE_CHECKING:
    from scrift._http import HttpClient


class BrandResource:
    """Operations on /v1/brand."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, domain: str) -> BrandResponse:
        """Look up a brand by its website domain."""
        response = self._http.get("/v1/brand", params={"domain": domain})
        return BrandResponse.model_validate(response.json())
