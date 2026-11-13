# CORE-16 — TRANSACTIONS, EXTERNAL SIDE EFFECTS, MIGRATIONS & DISASTER RECOVERY

## Atomic content revision boundary
Revision N tracks: `script_hash`, `source_set_hash`, `rights_set_hash`, `scene_set_hash`, `title_thumbnail_hash`, `risk_report_hash`. A material change to any hash invalidates previously recorded `APPROVE` for release content. Before export/publish compare exactly against approval snapshot and report. Approval always references a specific authorized human actor (not LLM persona).

## Upload state machine
`PREPARED -> AUTH_CHECKED -> SUBMITTED -> CONFIRMED` or `PREPARED/AUTH_CHECKED -> BLOCKED` or `SUBMITTED -> UNKNOWN_REMOTE_STATE -> RECONCILIATION -> CONFIRMED/HOLD_FOR_HUMAN`. Reconciliation must use authorized account and provider-supported listing/status; only remote-confirmed absence *and* recorded safe retry predicate allow another upload. Never treat a timeout as a failed upload or issue blind duplicate `videos.insert`.

## Side effects
All outward uploads, social posts, third-party file deletes, payments, model downloads and external account changes require scoped permission and audit. Automatic publish only for explicitly opted-in low-risk channel policy, matching final hash and current trusted low-risk gate; manual is default. High-risk investigations always need human review. Publish to PRIVATE by default until visibility is separately authorized.

## SQLite + migration
`database/schema.sql` is baseline schema. Apply `database/002_operational_controls.sql` in a transaction after full pre-upgrade backup and checksum; record `schema_migrations` version=2.0.1; if interrupted, fail read-only with diagnostics until integrity checked. No unbounded fallback wiping user data. Never downgrade destructively. Restore test validates DB schema, source SHA256, render objects, secrets and platform references; credentials not copied across machines without explicit relink.

## Idempotency
Use canonical JSON digest of request+resource revision+authorized channel, never just button click count. `same key + different digest` = HTTP 409. Lease expiry of local pure computation permits checkpoint-based rerun; side-effect job on uncertain remote state requires reconciliation. Retried sync should not count duplicate topic observations as new independent evidence.

## Retention & deletion
Research source versions immutable while legally retained; link deletions/corrections as tombstone with audit event. Backups use relative paths and content checksums, no unsafe symlinks. Explicit retention policy and user-controlled deletion for personal data; provider ToS rights for raw ingested copies are not inferred.
