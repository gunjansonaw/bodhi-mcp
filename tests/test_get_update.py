import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from bodhi_mcp.client import BodhiClient
from bodhi_mcp.server import create_server

FIXTURE = {
    "update": {
        "alias": "FEDORA-2026-1a2b3c4d5e",
        "title": "foo-1.2-1.fc44",
        "status": "testing",
        "request": "stable",
        "type": "bugfix",
        "critpath": False,
        "stable_karma": 3,
        "release": {"name": "F44"},
        "builds": [{"nvr": "foo-1.2-1.fc44"}],
        "url": "https://bodhi.fedoraproject.org/updates/FEDORA-2026-1a2b3c4d5e",
    }
}


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/updates/FEDORA-2026-1a2b3c4d5e":
        assert request.headers["User-Agent"].startswith("bodhi-mcp/")
        return httpx.Response(200, json=FIXTURE)
    return httpx.Response(404, json={"status": "error"})


@pytest.fixture
def server():
    return create_server(BodhiClient(transport=httpx.MockTransport(handler)))


async def test_get_update(server):
    result = await server.call_tool("bodhi_get_update", {"alias": "FEDORA-2026-1a2b3c4d5e"})
    text = str(result)
    assert "testing" in text and "foo-1.2-1.fc44" in text


async def test_unknown_update(server):
    with pytest.raises(ToolError):
        await server.call_tool("bodhi_get_update", {"alias": "FEDORA-2026-0000000000"})
