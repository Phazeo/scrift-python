"""ScriftClient - main entry point for the SDK."""

from __future__ import annotations

import warnings

from scrift._http import HttpClient
from scrift.resources.brand import BrandResource
from scrift.resources.catalog import CatalogResource
from scrift.resources.svg import SvgResource


class ScriftClient:
    """Synchronous client for the Scrift brand-asset API.

    Usage::

        from scrift import Scrift

        client = Scrift(api_key="sk_live_...")
        brand = client.catalog.get("stripe")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        from scrift._http import _DEFAULT_BASE_URL, _DEFAULT_TIMEOUT

        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url if base_url is not None else _DEFAULT_BASE_URL,
            timeout=timeout if timeout is not None else _DEFAULT_TIMEOUT,
        )
        self._closed = False
        self.catalog = CatalogResource(self._http)
        self.svg = SvgResource(self._http)
        self.brand = BrandResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()
        self._closed = True

    def __enter__(self) -> ScriftClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def __del__(self) -> None:
        if not self._closed:
            warnings.warn(
                "Unclosed ScriftClient. Use 'with Scrift(...) as client:' "
                "or call 'client.close()' explicitly.",
                ResourceWarning,
                stacklevel=1,
            )
