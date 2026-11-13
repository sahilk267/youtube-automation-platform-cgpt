# GitHub source sync status

**Target repository:** `sahilk267/youtube-automation-platform-cgpt` (PUBLIC when opened). This document records the planned canonical layout and excludes large/private binaries.

The first complete source import should contain:

- Runtime `app/`, `sql/` (001–012), `tests/`, `tools/`, `requirements.txt`, `configs/`, readable `examples/` scripts and captions.
- Versioned `spec/launch-v3/` and `spec/combined-v3/` specification snapshots. They are **not** runnable apps.
- `research/` platform/120-channel materials and research limitations.
- Readme, agent handoff, architecture, status, security, Windows quickstart, roadmap, recovery notes, CI.

**Omitted intentionally:** local SQLite and user-owned raw source footage, licensed voice weights, OAuth credentials, downloaded copyrighted third-party clips, and generated MP4/PNG demonstration outputs. Regenerate technical demos from `examples/create_*.py` as appropriate. Historic ZIP manifests in `docs/historical/` describe old archives and may reference missing generated files; do **not** run `tools/verify_package.py` against a normalized Git checkout and call missing media a source failure.

**Audit after import:** compare GitHub tree paths with this inventory, run `python -m pytest -q` from fresh clone, inspect actual CI result, and record commit SHA. No docs-only commit should be described as full code sync. A successful remote tree write does not certify target Windows, real model or YouTube provider acceptance.
