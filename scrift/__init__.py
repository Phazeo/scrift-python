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
    ServiceResponse,
)
from scrift.resources.raster import RasterResource

__all__ = [
    "APIError",
    "AuthenticationError",
    "BatchResponse",
    "BrandResponse",
    "CatalogListResponse",
    "CssVars",
    "NotFoundError",
    "RateLimitError",
    "RasterResource",
    "RateLimitInfo",
    "Scrift",
    "ScriftError",
    "ScriftRateLimitError",
    "SearchResponse",
    "ServiceResponse",
    "ValidationError",
]

__version__ = "0.2.0"
