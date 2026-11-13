-- ViralOS additive operational migration v2.1 (schema migrations version 2.0.1).
-- Apply AFTER canonical schema.sql in a single BEGIN IMMEDIATE transaction; inspect integrity and back up first.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS connector_qualification (
 qualification_id TEXT PRIMARY KEY, provider_id TEXT NOT NULL, provider_terms_uri TEXT,
 checked_at TEXT NOT NULL, result TEXT NOT NULL CHECK(result IN ('ALLOWED','RESTRICTED','AUTH_MISSING','UNKNOWN','EXPIRED')),
 scopes_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(scopes_json)),
 proof_sha256 TEXT, reviewer TEXT, note TEXT
);
CREATE INDEX IF NOT EXISTS idx_connector_qualification_provider ON connector_qualification(provider_id,checked_at);
CREATE TABLE IF NOT EXISTS research_attempts (
 attempt_id TEXT PRIMARY KEY, research_plan_id TEXT NOT NULL REFERENCES research_plans(research_plan_id),
 provider_id TEXT NOT NULL, query_hash TEXT NOT NULL, attempted_at TEXT NOT NULL,
 result_state TEXT NOT NULL CHECK(result_state IN ('OK','EMPTY','ERROR','RESTRICTED','QUOTA','STALE')),
 result_count INTEGER NOT NULL DEFAULT 0 CHECK(result_count>=0),
 detail_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(detail_json))
);
CREATE TABLE IF NOT EXISTS operation_artifacts (
 artifact_id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(job_id),
 artifact_type TEXT NOT NULL, sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 relative_path TEXT NOT NULL, contract_version TEXT NOT NULL, provenance_json TEXT NOT NULL CHECK(json_valid(provenance_json)),
 created_at TEXT NOT NULL, UNIQUE(job_id,artifact_type,sha256)
);
CREATE TABLE IF NOT EXISTS outbound_action_intents (
 intent_id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(job_id),
 channel_id TEXT REFERENCES channels(channel_id), action_type TEXT NOT NULL,
 payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256)=64),
 idempotency_key TEXT NOT NULL, remote_ref TEXT,
 status TEXT NOT NULL CHECK(status IN ('PREPARED','AUTH_CHECKED','SUBMITTED','UNKNOWN_REMOTE_STATE','RECONCILING','CONFIRMED','BLOCKED','HOLD_FOR_HUMAN')),
 review_ref TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 UNIQUE(channel_id,action_type,idempotency_key)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_outbound_action_idem_global
 ON outbound_action_intents(COALESCE(channel_id,'GLOBAL'),action_type,idempotency_key);
CREATE TABLE IF NOT EXISTS outbound_reconciliation_events (
 event_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL REFERENCES outbound_action_intents(intent_id),
 remote_state TEXT NOT NULL, decision TEXT NOT NULL, observed_at TEXT NOT NULL,
 evidence_sha256 TEXT, actor_id TEXT, note TEXT
);
CREATE TABLE IF NOT EXISTS review_revision_snapshots (
 review_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
 revision INTEGER NOT NULL, script_sha256 TEXT NOT NULL, sources_sha256 TEXT NOT NULL,
 rights_sha256 TEXT NOT NULL, scenes_sha256 TEXT NOT NULL, packaging_sha256 TEXT NOT NULL,
 risk_sha256 TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('APPROVED','REJECTED','CHANGES_REQUIRED')),
 human_actor_id TEXT NOT NULL, reviewed_at TEXT NOT NULL, revoked_at TEXT
);
CREATE TABLE IF NOT EXISTS model_execution_audit (
 inference_id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(job_id), model_id TEXT REFERENCES models(model_id),
 input_sha256 TEXT NOT NULL, output_sha256 TEXT, mode TEXT NOT NULL,
 measured_ram_peak_bytes INTEGER, measured_vram_peak_bytes INTEGER,
 started_at TEXT NOT NULL, ended_at TEXT, outcome TEXT NOT NULL,
 licensing_review_ref TEXT
);
CREATE TABLE IF NOT EXISTS research_coverage_reports (
 coverage_id TEXT PRIMARY KEY, research_plan_id TEXT NOT NULL REFERENCES research_plans(research_plan_id),
 report_json TEXT NOT NULL CHECK(json_valid(report_json)),
 report_sha256 TEXT NOT NULL CHECK(length(report_sha256)=64), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS compatibility_migrations (
 migration_id TEXT PRIMARY KEY, from_profile TEXT NOT NULL, to_profile TEXT NOT NULL,
 old_schema_version TEXT NOT NULL, new_schema_version TEXT NOT NULL,
 workspace_sha256 TEXT, started_at TEXT NOT NULL, finished_at TEXT,
 result TEXT NOT NULL CHECK(result IN ('STARTED','COMMITTED','FAILED','RESTORED'))
);
-- State transitions of external actions are application guarded and must be logged atomically.
