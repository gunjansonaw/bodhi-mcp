# Test fixtures

JSON bodies shaped like real Bodhi REST API responses, used by the offline tests.

| File | Endpoint | What it covers |
| --- | --- | --- |
| `update_stable.json` | `GET /updates/FEDORA-2025-7c1d4e8f2a` | stable critpath security update |
| `update_testing.json` | `GET /updates/FEDORA-2025-b3e90a1c55` | testing update with negative karma and failed gating |
| `update_obsolete.json` | `GET /updates/FEDORA-2025-4f2a6d9b01` | update obsoleted by a newer build |
| `update_rawhide.json` | `GET /updates/FEDORA-2026-e5c2a7b913` | automatic Rawhide update |

These files are currently schema-based: they follow the field names and shapes of
Bodhi's API but were written by hand, because the development environment could not
reach bodhi.fedoraproject.org. User and comment objects deliberately keep their
`email` fields so tests can prove the tools strip them.

To replace one with a real capture, keep the file name and run, for example:

```sh
curl -s https://bodhi.fedoraproject.org/updates/<alias> | python3 -m json.tool > tests/fixtures/update_stable.json
```

Then update the alias constants in `tests/conftest.py` to match.
