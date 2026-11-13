# CORE-02 — Data Model, Migrations, Retention and Provenance

## 2.1 Canonical entity graph

`Channel` -> `Topic` (selected idea) -> `ResearchPlan` -> `Source` -> immutable `SourceVersion` -> `Claim` -> `EvidenceEdge` -> `ScriptVersion` -> `SceneSpec` -> `Asset`/`AssetRight` -> `RenderAttempt` -> `QAGate` -> `Approval` -> `PublicationIntent`/`Publication` -> `AnalyticsSnapshot` -> `Experiment` -> `RevenueEntry`.

A shared event has its own topic and research sources, but output is **channel-specific**. Do not mix facts about different sports seasons, countries or language editions. Store source/original language and translation as distinct versions, with explicit alignment and editorial review.

## 2.2 Storage ownership

- SQLite stores IDs, metadata, hashes, edges, state, currency minor units, review records and artifact paths.
- Content-addressed file store retains retrieved bytes and generated media with digest and license metadata; can be cleaned by tracked references, **not** arbitrary disk deletion.
- SQLite FTS5 contains source excerpts/transcripts for retrieval; no full copyrighted material ingestion unless terms/license permit; retention policy respected.
- Auth/refresh tokens remain in OS protected secrets store keyed by channel and scope, not SQLite plaintext. DB stores only opaque token reference and provider/account scope metadata.
- Immutable audit events record actor, timestamp, reason, before/after hashes; they do not contain raw API tokens or source-protection details.

## 2.3 Versioning and invalidation

New source fetch with different bytes -> new SourceVersion. If a correction, retraction or changed score affects a referenced Claim, find all downstream scripts, charts, thumbnails, videos and scheduled publications. Mark `NEEDS_REVIEW` and regenerate dependent scenes; do not edit prior published record as if never aired. Signed approvals reference `(project_id, revision_hash, risk_summary_hash, rights_manifest_hash)`.

## 2.4 Migration policy

- `backend/migrations` has numbered, transactional, reviewed schema migrations. No table recreate/data loss without backup/restore and explicit owner approval.
- `sqlite3.pragma_integrity_check` and FK check before/after migrations.
- Migrations applied once with schema version record; failure restores backup snapshot.
- Ultimate data additions are additive; future PostgreSQL adapter must preserve UUIDs, timestamps, source hashes and currency minor units.
- FTS schema is a rebuildable materialized index; rebuild from source versions when necessary.

## 2.5 Caching, reproducibility and lifetime

Each external retrieval caches bytes, HTTP metadata when permitted, content hash, capture date and source-specific expiry; access errors retained. A generated script references exact source versions so it can be re-audited even if web pages change. Reproducible AI generation records model file digest, backend version, seed (when applicable), parameters, hardware class, prompt compile version, and source/script revision; results may still vary across nondeterministic hardware kernels.

Retention defaults (local project policy, overridable): keep project records and source citations until owner deletion or rights-required removal; use 30-day rotating debug logs, 90-day failed temp render cleanup only when unreferenced, and explicit review before deleting generated video assets. Do not retain private content longer than permitted by source terms. Media source copies can be disabled if licensing forbids local archive; preserve metadata/citation instead.

## 2.6 Security and backup

Daily backup suggestion, manual backup action and pre-migration verified backup; keep database and content-addressed file inventory consistent in snapshot. Backups encrypted when containing private work; test restore into clean workspace and verify source hashes plus application restart. Failure to restore cannot be reported as 'backup success'. Implement disaster recovery runbook and storage-exhaustion pause.

## 2.7 Memory and learning

Domain memories are retrieval datasets, not hidden prompts that silently alter truth. Store dataset version, evaluation date, originating sources, provenance, expiration and channel scope. Audiences learn from authenticated analytics only; do not push unreviewed creator style imitation or fabricated claims into evergreen knowledge base. Corrections invalidate learned claims but can retain incident records for retrospective audit.

## 2.8 SQLite baseline limitations

Single writer policy, bounded queue length, FTS tokenization limits for regional scripts, backups, and disk free preflight. Large concurrent SaaS traffic requires separately planned DB migration; do not fake distributed leases over an unsynchronized SQLite file share.
