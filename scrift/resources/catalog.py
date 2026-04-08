"""Catalog resource - list, get, batch, search."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrift.models import BatchResponse, CatalogListResponse, SearchResponse, ServiceResponse

if TYPE_CHECKING:
    import builtins

    from scrift._http import HttpClient


class CatalogResource:
    """Operations on /v1/catalog and /v1/search."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, slug: str) -> ServiceResponse:
        """Get a single brand by slug."""
        response = self._http.get(f"/v1/catalog/{slug}")
        return ServiceResponse.model_validate(response.json())

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> CatalogListResponse:
        """List catalog entries with pagination."""
        params: dict[str, object] = {"limit": limit, "offset": offset}
        response = self._http.get("/v1/catalog", params=params)
        return CatalogListResponse.model_validate(response.json())

    def batch(self, slugs: builtins.list[str]) -> BatchResponse:
        """Look up multiple brands by slug (max 50)."""
        response = self._http.post("/v1/catalog/batch", json={"slugs": slugs})
        return BatchResponse.model_validate(response.json())

    def search(
        self,
        query: str,
        *,
        limit: int | None = None,
    ) -> SearchResponse:
        """Search the catalog by name."""
        params: dict[str, object] = {"q": query}
        if limit is not None:
            params["limit"] = limit
        response = self._http.get("/v1/search", params=params)
        return SearchResponse.model_validate(response.json())
