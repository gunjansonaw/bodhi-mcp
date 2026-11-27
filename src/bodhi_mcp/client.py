"""Small read-only client for Bodhi's REST API."""

from __future__ import annotations

from typing import Any

import httpx

from bodhi_mcp import __version__

BODHI_URL = "https://bodhi.fedoraproject.org"
USER_AGENT = f"bodhi-mcp/{__version__} (+https://github.com/gunjansonaw/bodhi-mcp)"


class BodhiError(Exception):
    """Bodhi returned an error or could not be reached."""


class BodhiClient:
    """Async client for the read-only parts of Bodhi's REST API.

    All HTTP access to Bodhi goes through this class, so tools never build
    requests themselves.
    """

    def __init__(
        self, base_url: str = BODHI_URL, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=30.0,
            transport=transport,
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET a Bodhi API path and return the decoded JSON body.

        Raises:
            BodhiError: if Bodhi cannot be reached or returns an error status.
        """
        try:
            response = await self._http.get(path, params=params)
        except httpx.HTTPError as exc:
            raise BodhiError(f"Could not reach Bodhi: {exc}") from exc
        if response.status_code == 404:
            raise BodhiError(f"Not found in Bodhi: {path}")
        if response.status_code >= 400:
            raise BodhiError(f"Bodhi returned HTTP {response.status_code} for {path}")
        return response.json()
