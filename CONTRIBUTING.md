# Contributing to bodhi-mcp

Thanks for your interest. Issues and pull requests are welcome.

## Workflow

1. Open an issue first for anything bigger than a small fix.
2. Branch from `main` using a prefix: `feat/`, `fix/`, `docs/`, `test/`, `ci/` or `chore/`.
3. Keep pull requests small and focused on one change.
4. Make sure CI passes. `main` only receives changes through reviewed pull requests.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org):

```
feat(client): add retries for timeouts and 5xx responses

Explain what changed and why, wrapped at 72 characters.

Signed-off-by: Your Name <you@example.com>
```

Every commit must be signed off (`git commit -s`), certifying the
[Developer Certificate of Origin](https://developercertificate.org).

## Checks

```
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

- Tests must not call the live Bodhi server. Use recorded fixtures with
  `httpx.MockTransport`.
- New behaviour needs tests.
- Tool output must never include email addresses.

## Scope

bodhi-mcp is read-only by design. Proposals for write actions (submitting
updates, karma, waivers) should start as an issue for discussion.
