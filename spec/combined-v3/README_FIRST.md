# ViralOS COMBINED v3.0 — READ FIRST

**Type: specification package, not executable ViralOS software.**

**Use case:** creator-owned YouTube channels; initial machine Intel i7 8th generation, 32GB RAM, **no dedicated GPU**; future CUDA RTX 3090 24GB / RTX A6000 48GB / stronger GPU; CPU/GPU/Hybrid/Auto workers. Do not assume user has GPU or a paid subscription. No guaranteed YouTube income or monetization.

**Scope:** One monorepo migration path from Launch to all 12 domains; production, evidence, source, rights, rendering, publishing and compute services stay shared; feature flags never imply completed engines.

**This archive is self-contained and independent.** Do NOT unzip Launch, Ultimate and Combined on top of each other; they are edition views of one future codebase. Combined is for long-term implementation; Launch for CPU-first milestone; Ultimate for full domain coverage.

## Agent reading order (DO NOT SKIP)
1. `AGENT_START_HERE.md` then `SPEC_PRECEDENCE.md`.
2. `core/21_EVIDENCE_TO_SCREEN_V3.md` through `core/26_CREATIVE_CONTRACT_MAPPING.md` (new production authority).
3. Original `core/00`–`core/20` and selected `projects/` (research, infrastructure, jobs, rights, publishing).
4. `configs/creative_operation_registry_v3.json`, `configs/creative_profile_matrix_v3.json`; corresponding `creative/directors/` and `creative/formats/`.
5. Strict `contracts/v3/*.schema.json`, `contracts/v3/CREATIVE_API_SUPPLEMENT.md` and additive `database/003_content_production_v3.sql`.
6. `research/` desk benchmark + ADR-001 (research evidence, not observed 600-video analysis), `tests/`, `OPEN_DECISIONS.md`.
7. Execute `python tools/validate_pack.py` then `python tools/validate_v3.py` after `pip install jsonschema PyYAML`. Both are specification validators ONLY.

## Publication/rights non-negotiables
Use original diagrams, authentic owned footage, licensed assets, sources and clear fact labels. Unknown rights, consequential allegations or video without full owner preview -> blocked. YouTube in-app Remix/Green Screen is not an unrestricted source-download/reupload license. Do not infer private competitor CTR/retention/RPM. No invented YouTube API for alternate audio tracks.

**Versioning:** v2 `contract_version=2.0.0` remains compatible for old core records; new production artifacts carry `contract_version=3.0.0`. Do not mutate stored v2 SourceVersion/SceneSpec: create versioned derivatives and migration.

## Completion truthfulness
`SPECIFIED` means written. `CODED` means real code. `INTEGRATION_TESTED` means actual working interactions. `HARDWARE_VERIFIED` means real Windows CPU/GPU test. `HUMAN_VIDEO_ACCEPTED` means full final file reviewed. This ZIP is ONLY **SPECIFIED**, with structural validation of schemas/docs/migration/fixtures. No final videos are supplied and no actual uploads have been performed.
