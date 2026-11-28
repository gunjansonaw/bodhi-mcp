# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org).

## [Unreleased]

### Added

- Project scaffolding: packaging, CI, contribution guidelines.
- `bodhi_get_update` tool and async Bodhi REST client.
- `bodhi_get_update` validates the alias format before calling Bodhi and returns a
  clear error for malformed aliases.

### Tests

- JSON fixtures shaped like Bodhi API responses (stable, testing, obsolete and Rawhide
  updates) and a shared MockTransport router in `tests/conftest.py`.
