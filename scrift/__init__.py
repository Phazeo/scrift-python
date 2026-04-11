"""Scrift Python SDK - brand assets at your fingertips."""

from scrift._client import ScriftClient as Scrift
from scrift.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ScriftError,
    ScriftRateLimitError,
    ValidationError,
)
from scrift.models import (
    BatchResponse,
    BrandResponse,
    CatalogListResponse,
    CssVars,
    RateLimitInfo,
    SearchResponse,
    ServiceColor,
    ServiceResponse,
    SvgVariant,
)
from scrift.resources.brand import BrandResource
from scrift.resources.catalog import CatalogResource
from scrift.resources.raster import RasterResource
from scrift.resources.svg import SvgResource

__all__ = [
    "APIError",
    "AuthenticationError",
    "BatchResponse",
    "BrandResource",
    "BrandResponse",
    "CatalogListResponse",
    "CatalogResource",
    "CssVars",
    "NotFoundError",
    "RasterResource",
    "RateLimitError",
    "RateLimitInfo",
    "Scrift",
    "ScriftError",
    "ScriftRateLimitError",
    "SearchResponse",
    "ServiceColor",
    "ServiceResponse",
    "SvgResource",
    "SvgVariant",
    "ValidationError",
]

__version__ = "0.2.2"
