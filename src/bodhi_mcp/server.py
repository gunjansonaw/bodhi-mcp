"""bodhi-mcp: read-only access to Fedora's Bodhi update system."""

from __future__ import annotations

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from bodhi_mcp.client import BodhiClient, BodhiError

READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)

INSTRUCTIONS = """\
Read-only access to Fedora's Bodhi update system.
Updates are identified by alias, e.g. FEDORA-2026-1a2b3c4d5e.
Koji build details belong to koji-mcp; Bodhi only knows builds by NVR.
"""


def create_server(client: BodhiClient) -> MCPServer:
    """Build the MCP server and register its tools against ``client``."""
    mcp = MCPServer("bodhi_mcp", instructions=INSTRUCTIONS)

    @mcp.tool(annotations=READ_ONLY, structured_output=False)
    async def bodhi_get_update(
        alias: Annotated[str, Field(description="Update alias, e.g. 'FEDORA-2026-1a2b3c4d5e'.")],
    ) -> str:
        """Get one Bodhi update: status, pending request, release, builds (NVRs) and link."""
        try:
            data = await client.get(f"/updates/{alias}")
        except BodhiError as exc:
            raise ToolError(f"{exc}. Check the alias format FEDORA-YYYY-xxxxxxxxxx.") from exc
        update = data["update"]
        builds = ", ".join(b["nvr"] for b in update.get("builds", []))
        return "\n".join(
            [
                f"# {update.get('title', alias)}",
                f"- alias: {update['alias']}",
                f"- release: {update.get('release', {}).get('name')}",
                f"- status: {update.get('status')} (request: {update.get('request')})",
                f"- type: {update.get('type')}, critpath: {update.get('critpath')}",
                f"- stable_karma: {update.get('stable_karma')}",
                f"- builds: {builds}",
                f"- url: {update.get('url')}",
            ]
        )

    return mcp


def main() -> None:
    """Run the server over stdio. Entry point for the ``bodhi-mcp`` command."""
    create_server(BodhiClient()).run("stdio")
