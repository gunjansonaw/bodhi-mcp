"""Shared test helpers: load JSON fixtures and route MockTransport requests to them."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

from bodhi_mcp.client import BodhiClient
from bodhi_mcp.server import create_server

FIXTURES = Path(__file__).parent / "fixtures"

STABLE_ALIAS = "FEDORA-2025-7c1d4e8f2a"
TESTING_ALIAS = "FEDORA-2025-b3e90a1c55"
OBSOLETE_ALIAS = "FEDORA-2025-4f2a6d9b01"
RAWHIDE_ALIAS = "FEDORA-2026-e5c2a7b913"

Route = dict[str, Any] | Callable[[httpx.Request], httpx.Response]


def load_fixture(name: str) -> dict[str, Any]:
    """Return the decoded JSON of ``tests/fixtures/<name>.json``."""
    return json.loads((FIXTURES / f"{name}.json").read_text())


class Router:
    """A MockTransport handler that maps request paths to fixtures or callables.

    Unknown paths get Bodhi's 404 error body. Every request is recorded in
    ``self.requests`` so tests can assert on what was sent.
    """

    def __init__(self, routes: dict[str, Route] | None = None) -> None:
        self.routes: dict[str, Route] = dict(routes or {})
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        route = self.routes.get(request.url.path)
        if route is None:
            return httpx.Response(
                404, json={"status": "error", "errors": [{"description": "Invalid update id"}]}
            )
        if callable(route):
            return route(request)
        return httpx.Response(200, json=route)

    def transport(self) -> httpx.MockTransport:
        """Wrap this router in an ``httpx.MockTransport``."""
        return httpx.MockTransport(self)


def update_routes() -> dict[str, Route]:
    """Routes serving every single-update fixture at ``/updates/{alias}``."""
    routes: dict[str, Route] = {}
    for name in ("update_stable", "update_testing", "update_obsolete", "update_rawhide"):
        data = load_fixture(name)
        routes[f"/updates/{data['update']['alias']}"] = data
    return routes


@pytest.fixture
def router() -> Router:
    """A router preloaded with all single-update fixtures."""
    return Router(update_routes())


@pytest.fixture
def server(router: Router):
    """An MCP server whose Bodhi client talks only to ``router``."""
    return create_server(BodhiClient(transport=router.transport()))
