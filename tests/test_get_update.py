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
from bodhi_mcp.server import create_server, validate_alias


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


@pytest.mark.parametrize(
    "alias",
    [
        "",
        "foo-1.2-1.fc44",
        "FEDORA-2026",
        "FEDORA-26-1a2b3c4d5e",
        "FEDORA-2026-1a2b3c4d5",
        "FEDORA-2026-1A2B3C4D5E",
        "fedora-2026-1a2b3c4d5e",
        "FEDORA-2026-1a2b3c4d5e/comments",
        "../releases",
    ],
)
async def test_invalid_alias_is_rejected_without_a_request(server, router, alias):
    with pytest.raises(ToolError, match="Invalid update alias"):
        await call(server, alias)
    assert router.requests == []


@pytest.mark.parametrize(
    "alias",
    [
        "FEDORA-2026-1a2b3c4d5e",
        "FEDORA-EPEL-2025-0f9e8d7c6b",
        "FEDORA-EPEL-NEXT-2024-a1b2c3d4e5",
        "FEDORA-FLATPAK-2025-1234567890",
        "  FEDORA-2026-1a2b3c4d5e  ",
    ],
)
def test_valid_aliases(alias):
    assert validate_alias(alias) == alias.strip()


def test_fixtures_keep_emails_so_stripping_can_be_tested():
    data = load_fixture("update_testing")["update"]
    assert "@" in data["user"]["email"]
    assert all("@" in c["user"]["email"] for c in data["comments"])
