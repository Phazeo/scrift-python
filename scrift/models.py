"""Pydantic v2 models matching real Scrift API response shapes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True, slots=True)
class RateLimitInfo:
    """Rate limit quota from response headers ``X-RateLimit-*``."""

    limit: int | None
    remaining: int | None
    reset_at: int | None  # Unix timestamp


class CssVars(BaseModel):
    """CSS custom properties returned by the API."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    brand_color: str = Field(alias="--brand-color")
    brand_color_dark: str = Field(alias="--brand-color-dark")
    brand_color_contrast: str = Field(alias="--brand-color-contrast")


class ServiceResponse(BaseModel):
    """Single brand/service from the catalog."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: int
    slug: str
    name: str
    brand_color: str | None = Field(None, alias="brandColor")
    dark_mode_color: str | None = Field(None, alias="darkModeColor")
    svg_variants: Any | None = Field(None, alias="svgVariants")
    colors: Any | None = None
    css: CssVars | None = Field(None, alias="_css")
    notice: str | None = Field(None, alias="_notice")
    rate_limit: RateLimitInfo | None = None


class BrandResponse(BaseModel):
    """Response from /v1/brand - includes variant list."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: int
    slug: str
    name: str
    brand_color: str | None = Field(None, alias="brandColor")
    dark_mode_color: str | None = Field(None, alias="darkModeColor")
    variants: list[str] = Field(default_factory=list)
    css: CssVars | None = Field(None, alias="_css")
    notice: str | None = Field(None, alias="_notice")
    rate_limit: RateLimitInfo | None = None


class BatchResponse(BaseModel):
    """Response from POST /v1/catalog/batch."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    results: dict[str, ServiceResponse | None]
    found: int
    not_found: list[str] = Field(default_factory=list, alias="notFound")
    rate_limit: RateLimitInfo | None = None


class SearchResponse(BaseModel):
    """Response from GET /v1/search."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    matches: list[ServiceResponse]
    query: str
    total: int
    rate_limit: RateLimitInfo | None = None


class CatalogListResponse(BaseModel):
    """Paginated catalog list response."""

    model_config = ConfigDict(populate_by_name=True, frozen=True)

    items: list[ServiceResponse]
    total: int
    limit: int
    offset: int
    rate_limit: RateLimitInfo | None = None
