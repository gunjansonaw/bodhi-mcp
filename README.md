# bodhi-mcp

[![Tests](https://github.com/gunjansonaw/bodhi-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/gunjansonaw/bodhi-mcp/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Read-only [MCP](https://modelcontextprotocol.io) server for Fedora's
[Bodhi](https://bodhi.fedoraproject.org) update system. It lets an AI assistant
answer questions such as "is my update in stable yet?", "why is it blocked?" or
"which update contains this build?".

It is designed to work alongside two existing servers:

| Server | Covers |
|---|---|
| [koji-mcp](https://github.com/echevemaster/koji-mcp) | Koji builds, tasks and failure diagnosis |
| [logdetective-mcp](https://github.com/fedora-copr/logdetective-mcp) | Build log analysis |
| **bodhi-mcp** | Bodhi updates, karma, gating results and releases |

> **Status:** early development (0.1.0 not yet released).

## Scope

- Anonymous, read-only calls to Bodhi's public REST API. No login and no write actions.
- Gentle on Fedora infrastructure: an identifying user agent, one request at a
  time, short timeouts and caching.
- Email addresses returned by Bodhi are never included in tool output.

## Tools

| Tool | Status | Answers |
|---|---|---|
| `bodhi_get_update` | in progress | One update: status, request, release, builds, link |
| `bodhi_list_updates` | planned | Updates for a package, release or status |
| `bodhi_find_update_for_build` | planned | Which update contains a Koji build (NVR) |
| `bodhi_get_test_results` | planned | Gating decision and required tests |
| `bodhi_list_releases` | planned | Active releases and their karma and testing rules |

## Usage

Requires [uv](https://docs.astral.sh/uv/). From a clone:

```
claude mcp add bodhi --scope user -- uv --directory /path/to/bodhi-mcp run bodhi-mcp
```

## Design notes

**Why httpx instead of the `bodhi-client` bindings?** bodhi-mcp only makes
anonymous GET requests. The official bindings are the better choice for write
operations, since they handle login, CSRF tokens and validation, but they bring
in `koji` and Kerberos dependencies that are heavy for read-only use, especially
on macOS and Windows. If write tools are ever added, those calls will move to the
bindings. All Bodhi calls live in `BodhiClient` (`src/bodhi_mcp/client.py`), so
switching touches one module.

## Development

```
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Tests run offline against recorded responses; they never call the live Bodhi
server. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
