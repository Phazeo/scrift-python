"""Scrift Python SDK - brand assets at your fingertips."""

from scrift._client import ScriftClient as Scrift
from scrift.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ScriftError,
    ValidationError,
)
from scrift.models import (
    BatchResponse,
    BrandResponse,
    CatalogListResponse,
    CssVars,
    SearchResponse,
    ServiceResponse,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "BatchResponse",
    "BrandResponse",
    "CatalogListResponse",
    "CssVars",
    "NotFoundError",
    "RateLimitError",
    "Scrift",
    "ScriftError",
    "SearchResponse",
    "ServiceResponse",
    "ValidationError",
]

__version__ = "0.1.0"
