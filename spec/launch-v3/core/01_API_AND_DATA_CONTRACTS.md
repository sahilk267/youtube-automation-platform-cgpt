# CORE-01 — API, Identity, Persistence and Contract Semantics

## 1.1 Common envelope

Every API response returns `request_id`, `contract_version`, `data` and optionally `pagination`; errors return `code`, `message`, `details`, `retryable`, `correlation_id`. No bare invented success fields. UUIDs are immutable. Every serialized artifact tracks `schema_version`, creator/worker, timestamp and digest. `GET /health` is allowed without account connection and must report `database, job_queue, ffmpeg, model_optional, youtube_optional, storage_free_bytes` accurately.

## 1.2 Routes and verbs (minimum stable API)

| Route | Method | Input -> output | Guard |
|---|---|---|---|
| `/api/v1/channels` | GET, POST | ChannelProfile create/list | Validate locale, domain, ownership |
| `/api/v1/channels/{id}` | GET, PATCH | Versioned ChannelProfile | Optimistic concurrency, audit |
| `/api/v1/connectors` | GET | Connector health/rights/quota | Never claim unsupported integration |
| `/api/v1/connectors/{id}/sync` | POST | SourceSyncRequest -> job_id | Provider ToS, quota, consent |
| `/api/v1/topics` | GET | Topic observation cards | Show provenance and stale flag |
| `/api/v1/topics/{id}/research` | POST | ResearchPlan -> job_id | No automatic final claim assertions |
| `/api/v1/research/{id}` | GET | Plan, gaps, sources, claims | Explicit current state |
| `/api/v1/sources/{id}/versions` | GET | Version hashes, retrievals | Immutable bytes |
| `/api/v1/projects` | POST, GET | ContentProject create/list | Channel and topic linked |
| `/api/v1/projects/{id}/script` | POST, GET | ScriptVersion -> job_id/version | Provenance gate |
| `/api/v1/projects/{id}/storyboard` | POST, GET | SceneSpec[] | Asset rights and accuracy metadata |
| `/api/v1/projects/{id}/render` | POST | RenderRequest -> job_id | Capability, rights and asset checks |
| `/api/v1/projects/{id}/qa` | POST | QAGateReport -> job_id | Same verified project revision |
| `/api/v1/projects/{id}/approvals` | POST | ApprovalDecision -> review record | User actor and snapshot hash |
| `/api/v1/projects/{id}/export` | POST | ExportJob -> artifact manifest | Allowed even if YouTube disconnected, subject to safety labels |
| `/api/v1/projects/{id}/publish` | POST | PublicationIntent -> job_id | Requires explicit approval, valid OAuth |
| `/api/v1/publications/{id}` | GET | Reconciled platform publication status | Never fabricate platform_id |
| `/api/v1/analytics/sync` | POST | Authorized window -> job_id | OAuth scope + quotas |
| `/api/v1/analytics/snapshots` | GET | Observed data, missing dimensions | No predictions mixed |
| `/api/v1/ledger` | GET, POST | Ledger actual entries/imports | Actual vs estimate fields separated |
| `/api/v1/jobs/{id}` | GET | State, progress, error, attempts | Honest telemetry |
| `/api/v1/jobs/{id}/cancel` | POST | Cancel request -> state | Safe cancellation |
| `/api/v1/workers` | GET | Capabilities and availability | No decorative GPU state |
| `/api/v1/settings/compute` | PATCH | Auto/CPU/CUDA/Hybrid preference | Validated availability |

API request payloads and response objects SHALL be typed from canonical schemas, with strict field validation and documented pagination. Routes listed here are normative minimum; implementing `GET/POST/PATCH` as appropriate is permitted only when documented with contract tests.

## 1.3 Identity and key rules

- `channel_id` UUID: profile ID distinct from YouTube channel external ID.
- `domain_id` strict enum from registry. `sport_id` sports plugin config (`cricket`, `nfl`, `mlb`, `nba`, `soccer`), not extra domain ID.
- `source_id` UUID for canonical logical URL/document; `source_version_id` UUID for retrieval content hash and capture timestamp.
- `topic_id` UUID; observations immutable and time-indexed. One topic can contain many observations and claims.
- `project_id` UUID; derived shot/render/publish attempts must reference explicit script/version hashes.
- `publication_id` local UUID; external YouTube video ID is nullable until confirmed from authorized API.
- `worker_id` persistent capability identifier; `model_id` version/hash/license metadata record.
- Idempotency key scope `(operation_name, channel_id, key)` unique. If same key used with different request hash, reject HTTP 409, not silently reuse.

## 1.4 Local paths and media object store

User content saved as `workspace/projects/<project_uuid>/<revision>/...`; immutable source downloads stored by SHA-256 relative path (`sources/sha256/<hex>`) with metadata in DB. Quarantine unknown media until MIME probing, size limits and safe decoder handling. Never trust external filename/path; normalize to workspace and block traversal, symlinks that escape workspace, path prefixes and internal/private-network fetch URLs.

## 1.5 Revision semantics

Every project modification increments `revision`. Output assets remember revision and `input_digest`. If claims, transcript, script, rights record, scene or title materially change after approval, approval becomes invalid and downstream publication moves to `NEEDS_REAPPROVAL`. A content project can have many render attempts; only one approved output artifact revision can be active per publication intent. Existing YouTube publication cannot be 'rolled back' locally: create correction/replacement request with explicit owner decision.

## 1.6 Database boundaries

`database/schema.sql` is a **starting schema for the local platform**, not a completed multi-tenant SaaS schema. All app writes are transactions; use FK constraints ON and WAL; SQLite busy_timeout and one writer queue. FTS indexes are secondary search indexes; primary data is normalized. Do not use full-text search relevance scores as evidence confidence.

## 1.7 Explicit anti-duplication keys

`source_version` unique by source+hash+captured window; `topic_observation` unique provider + external event ID + timestamp where external IDs exist; `content_project` unique channel+topic+editorial_angle hash for an active version; `publication` unique channel+content revision+platform+purpose. Duplicate ingestions merge source references but never erase provenance. Upload retries reconcile known remote IDs before issuing another videos.insert.

## 1.8 Validation/error examples

- Unknown domain -> `INVALID_DOMAIN` 422.
- Incompatible SceneSpec major version -> `CONTRACT_VERSION_UNSUPPORTED` 422.
- Reused idempotency key with different payload -> `IDEMPOTENCY_CONFLICT` 409.
- No source/invalid citation -> `EVIDENCE_INCOMPLETE` 409.
- Missing legal permission for asset -> `RIGHTS_UNRESOLVED` 409.
- Missing authorized account -> `AUTH_REQUIRED` 401/403 as appropriate.
- CPU selected, GPU-only render -> `WAITING_FOR_CAPABILITY` job state and explanation; no fake success.
