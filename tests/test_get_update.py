import httpx
import pytest
from conftest import (
    OBSOLETE_ALIAS,
    RAWHIDE_ALIAS,
    STABLE_ALIAS,
    TESTING_ALIAS,
    Router,
    load_fixture,
)
from mcp.server.mcpserver.exceptions import ToolError

from bodhi_mcp.client import BodhiClient
from bodhi_mcp.server import create_server


async def call(server, alias: str) -> str:
    return str(await server.call_tool("bodhi_get_update", {"alias": alias}))


@pytest.mark.parametrize(
    ("alias", "status", "nvr"),
    [
        (STABLE_ALIAS, "stable", "python3.13-3.13.9-1.fc42"),
        (TESTING_ALIAS, "testing", "systemd-257.10-1.fc43"),
        (OBSOLETE_ALIAS, "obsolete", "firefox-144.0-1.fc43"),
        (RAWHIDE_ALIAS, "stable", "rust-1.91.0-1.fc46"),
    ],
)
async def test_get_update_from_fixtures(server, alias, status, nvr):
    text = await call(server, alias)
    assert alias in text
    assert f"status: {status}" in text
    assert nvr in text


async def test_get_update_sends_user_agent(server, router):
    await call(server, STABLE_ALIAS)
    request = router.requests[-1]
    assert request.url.path == f"/updates/{STABLE_ALIAS}"
    assert request.headers["User-Agent"].startswith("bodhi-mcp/")


async def test_unknown_update(server):
    with pytest.raises(ToolError, match="Not found"):
        await call(server, "FEDORA-2026-0000000000")


async def test_server_error_is_a_tool_error():
    router = Router({f"/updates/{STABLE_ALIAS}": lambda _: httpx.Response(503)})
    server = create_server(BodhiClient(transport=router.transport()))
    with pytest.raises(ToolError, match="HTTP 503"):
        await call(server, STABLE_ALIAS)


def test_fixtures_keep_emails_so_stripping_can_be_tested():
    data = load_fixture("update_testing")["update"]
    assert "@" in data["user"]["email"]
    assert all("@" in c["user"]["email"] for c in data["comments"])
