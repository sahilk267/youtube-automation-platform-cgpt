# ViralOS v3.0 — CODING AGENT IMPLEMENTATION BOOTSTRAP

1. Treat this ZIP as specification, NOT an existing application. Inventory any separately provided repository before modifying files. Never claim working code from these Markdown documents.
2. Run `python tools/validate_pack.py` and `python tools/validate_v3.py`; record errors. If dependency `jsonschema` missing, install in an isolated env or report blocker; don't treat skipped validation as PASS.
3. Read `SPEC_PRECEDENCE.md`, `OPEN_DECISIONS.md`, `core/21`–`core/26`, `configs/creative_operation_registry_v3.json`, selected domain/format directors, and corresponding existing v2 research/rights/job/API specs.
4. Use **one modular monolith** (FastAPI + React browser dashboard + SQLite/FTS5 + durable local workers); external queue/cloud/SaaS not mandatory. Preserve `project_id`, `channel_id`, source/claim IDs and storage migration history.
5. Implement data models from `contracts/v3/` and migrations from `database/003_content_production_v3.sql` as additive revisions. Test on a **copy** of populated v2 database; do not reset user data.
6. First build one **actual playable CPU-only original video** with source claim traceability, voice, overlays, captions, scene motion, full human watch-through and FFmpeg manifest. Then verify cricket/NFL differences; Technology is optional. Release cannot claim expert-level merely because schemas pass.
7. Implement reactions only with explicit owner/rights modes and substantive new commentary; third-party unknown footage may be researched but not automatically included. GPU image/video provider stays disabled until hardware/model/license capability tests pass.
8. Locale strategy: master verified facts + independently checked audio, native-script text, overlays, timing, metadata. Studio-only extra language audio is manual; do not implement imaginary API routes.
9. Reuse canonical v2 outbound upload intents and OAuth with approval; no duplicate publisher; manual private export always possible without credentials. Never auto-publish high-risk material.
10. Report each change: file paths, schema IDs, evidence inputs, unit/integration/hardware tests, errors, mock-only tests, human-approval state, unresolved decisions and exact next allowed step. Never silently fabricate source, video output, metrics, rights or code.

**Implement launch-first even for Ultimate/Combined.** A domain reaches release only after distinct factual + creative golden videos and reviewer signoff; quality cannot be guaranteed by prompt text. Treat creator benchmarks as hypotheses until real video/timecode observations exist.
