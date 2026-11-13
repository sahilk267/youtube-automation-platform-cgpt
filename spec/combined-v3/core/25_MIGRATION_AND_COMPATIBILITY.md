# CORE-25 — Migration, Profiles, Security, Status and Implementation Gates (v3.0 NORMATIVE)

## Version hierarchy
1. Law, live platform/rights/source access and actual owner approvals govern external actions.
2. `SPEC_PRECEDENCE.md`, `configs/default_policy.json`, v3 core documents (`core/21`–`core/25`) and strict v3 schemas govern new creative behavior.
3. v2.1 existing core, JSON schemas and SQL remain authoritative for research/YouTube/compute where v3 does not supersede them. v3 extends, never blindly overwrites.
4. Domain audiovisual directors are policy adapters; their format preferences cannot violate shared evidence, rights or local capability gates.
5. Examples and competitor benchmarks are illustrative unless fixture source + human observation validates them.

## SceneSpec migration
`ScriptVersion` + `NarrativePlan` (v2) -> immutable `CreativeBrief` + `TimedBeatGraph` (v3); `SceneSpec` (v2) -> one or more typed `ShotPlan` entries, with speech and overlays separated; `RenderManifest` (v2) points to `VideoTimeline` hash/locale and exact media. v2 `audio_mix`/`subtitle_policy` generic fields are **legacy optional metadata**, not executable controls. Do not accept arbitrary dicts as production engine configuration. Persist old records unmodified and create v3 derivatives with parent hash. The `database/003_content_production_v3.sql` migration is additive; it is a reference migration—not proof of running app compatibility. Run backup and migration integration tests before adopting.

## Profiles and permission defaults
- LAUNCH: enable sports, optionally technology; no extra domains automatically turned on. CPU-only by default, manual-publication-only until owner gives bounded authorization.
- ULTIMATE: all 12 documented; actually enabled domain must pass its own golden media tests; until then show NOT_IMPLEMENTED or BETA, not expert badge.
- COMBINED: identical codebase + release profiles, not third fork; official development baseline for incremental rollout.
- Each external-source operation has access terms and recorded connector status. AI cannot invent third-party rights, YouTube API endpoints or subscriber/watch-time data.

## Production readiness ladder
SPECIFIED (documents/contracts) -> CODED (running implementation) -> UNIT_TESTED -> INTEGRATION_TESTED -> HARDWARE_VERIFIED -> HUMAN_VIDEO_ACCEPTED -> RELEASED. Keep state and evidence per operation, category, format and locale. A script or archive integrity PASS only proves its own checks, never video quality.

## Invalidating changes
Upstream changes to a claim, license, quote/transcript, audio file, on-screen text, source link or visual scene that materially affects meaning must invalidate dependant rendered artifacts and publication approvals. Outbound upload retries must use existing durable intent/reconciliation from v2 CORE-16; never create new duplicate upload code. Unavailable data is not zero, and GPU-only operation is not CPU-capable by declaration.

## Scope change policy
Any new feature requires `V3-REQ-###`, a canonical owner, typed contract, algorithm, negative fixture, release flag and human acceptance criterion. Unknown decisions are listed in `OPEN_DECISIONS.md` with default HOLD/SAFE_FALLBACK. Agent is forbidden from interpreting vague feature names as complete.
