-- ViralOS v2.0 canonical initial SQLite schema (design/prototype baseline)
-- Normative: use Alembic versioned migrations for application; do NOT execute DROP/RESET on user data.
-- SQLite 3.38+ expected; FTS5 availability check at install. All timestamps UTC RFC3339 TEXT.
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY, applied_at TEXT NOT NULL, checksum_sha256 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS domains (
  domain_id TEXT PRIMARY KEY CHECK(domain_id IN
    ('newsroom','science','technology','business','gaming','history','space','learning','sports','career','productivity','culture')),
  dossier_path TEXT NOT NULL UNIQUE, enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1))
);
CREATE TABLE IF NOT EXISTS channels (
  channel_id TEXT PRIMARY KEY,
  domain_id TEXT NOT NULL REFERENCES domains(domain_id),
  sport_id TEXT CHECK(sport_id IS NULL OR sport_id IN ('cricket','nfl','mlb','nba','soccer')),
  name TEXT NOT NULL, locale TEXT NOT NULL, market TEXT NOT NULL, timezone TEXT NOT NULL,
  youtube_channel_id TEXT, approval_mode TEXT NOT NULL DEFAULT 'MANUAL'
   CHECK(approval_mode IN ('MANUAL','TRUSTED_LOW_RISK')),
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK(status IN ('DRAFT','ACTIVE','PAUSED')),
  revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>=1),
  voice_profile_id TEXT, risk_policy_id TEXT NOT NULL, content_formats_json TEXT NOT NULL DEFAULT '["SHORT","LONG"]' CHECK(json_valid(content_formats_json)),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  CHECK((domain_id='sports' AND sport_id IS NOT NULL) OR (domain_id<>'sports' AND sport_id IS NULL))
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_channels_youtube_id ON channels(youtube_channel_id) WHERE youtube_channel_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS connectors (
  provider_id TEXT PRIMARY KEY, method TEXT NOT NULL, access_state TEXT NOT NULL,
  terms_uri TEXT, terms_reviewed_at TEXT, quota_remaining INTEGER,
  last_attempt_at TEXT, last_success_at TEXT, last_error TEXT, coverage_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(coverage_json))
);
CREATE TABLE IF NOT EXISTS source_independence_groups (
  independence_group_id TEXT PRIMARY KEY, name TEXT, provenance_explanation TEXT NOT NULL,
  confidence TEXT NOT NULL CHECK(confidence IN ('VERIFIED','POSSIBLE','UNKNOWN')),
  reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS sources (
  source_id TEXT PRIMARY KEY, canonical_url TEXT NOT NULL UNIQUE, original_publisher TEXT,
  source_class TEXT NOT NULL DEFAULT 'UNKNOWN', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_versions (
  source_version_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(source_id), retrieved_at TEXT NOT NULL,
  published_at TEXT, content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),
  raw_relpath TEXT, original_language TEXT, rights_policy_id TEXT NOT NULL,
  access_status TEXT NOT NULL CHECK(access_status IN ('CAPTURED','METADATA_ONLY','RESTRICTED','FAILED')),
  independence_group_id TEXT REFERENCES source_independence_groups(independence_group_id), archive_uri TEXT,
  text_excerpt TEXT, metadata_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(metadata_json)),
  UNIQUE(source_id,content_sha256,retrieved_at)
);
CREATE INDEX IF NOT EXISTS ix_versions_source ON source_versions(source_id,retrieved_at DESC);
CREATE TABLE IF NOT EXISTS source_relations (
  relation_id TEXT PRIMARY KEY, from_source_id TEXT NOT NULL REFERENCES sources(source_id),
  to_source_id TEXT NOT NULL REFERENCES sources(source_id), relation TEXT NOT NULL
   CHECK(relation IN ('REPRINTS','QUOTES','SUMMARIZES','REFERENCES','ORIGINAL_RECORD','UNKNOWN')),
  observed_at TEXT NOT NULL, proof_source_version_id TEXT REFERENCES source_versions(source_version_id)
);
-- Store only excerpts licensed/allowed for local indexing; search index is not evidence of correctness.
CREATE VIRTUAL TABLE IF NOT EXISTS source_excerpt_fts USING fts5(source_version_id UNINDEXED, excerpt, tokenize='unicode61');

CREATE TABLE IF NOT EXISTS topics (
  topic_id TEXT PRIMARY KEY, domain_id TEXT NOT NULL REFERENCES domains(domain_id),
  canonical_key TEXT NOT NULL, first_observed_at TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL DEFAULT 'INSUFFICIENT_DATA'
   CHECK(lifecycle_state IN ('EMERGING','GROWING','PEAKING','DECLINING','INSUFFICIENT_DATA')),
  UNIQUE(domain_id,canonical_key)
);
CREATE TABLE IF NOT EXISTS topic_observations (
  observation_id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topics(topic_id),
  provider_id TEXT NOT NULL REFERENCES connectors(provider_id),
  source_version_id TEXT REFERENCES source_versions(source_version_id),
  external_id TEXT, observed_at TEXT NOT NULL, market TEXT NOT NULL, locale TEXT NOT NULL,
  metric_name TEXT NOT NULL, metric_value REAL, metric_unit TEXT NOT NULL,
  coverage_state TEXT NOT NULL,
  UNIQUE(topic_id,provider_id,external_id,observed_at,metric_name)
);
CREATE INDEX IF NOT EXISTS ix_observations_time ON topic_observations(topic_id,observed_at DESC);

CREATE TABLE IF NOT EXISTS research_plans (
  research_plan_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  topic_id TEXT NOT NULL REFERENCES topics(topic_id), domain_id TEXT NOT NULL REFERENCES domains(domain_id),
  depth TEXT NOT NULL CHECK(depth IN ('QUICK_VERIFIED_BRIEF','DEEP_INVESTIGATION','EXTENDED_FORENSIC')),
  plan_json TEXT NOT NULL CHECK(json_valid(plan_json)),
  status TEXT NOT NULL CHECK(status IN ('DRAFT','RUNNING','SUFFICIENT_FOR_DRAFT','NEEDS_MORE_RESEARCH','BLOCKED_EXTERNAL_SOURCE','HUMAN_ADJUDICATION_REQUIRED')),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_questions (
  question_id TEXT PRIMARY KEY, research_plan_id TEXT NOT NULL REFERENCES research_plans(research_plan_id),
  exact_question TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'OPEN',
  acceptance_evidence_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(acceptance_evidence_json))
);
CREATE TABLE IF NOT EXISTS research_gaps (
  gap_id TEXT PRIMARY KEY, research_plan_id TEXT NOT NULL REFERENCES research_plans(research_plan_id),
  question_id TEXT REFERENCES research_questions(question_id), reason_code TEXT NOT NULL,
  attempts_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(attempts_json)), impact TEXT NOT NULL,
  resolved_at TEXT
);
CREATE TABLE IF NOT EXISTS claims (
  claim_id TEXT PRIMARY KEY, research_plan_id TEXT NOT NULL REFERENCES research_plans(research_plan_id),
  proposition TEXT NOT NULL, claim_type TEXT NOT NULL CHECK(claim_type IN
   ('FACT','QUOTE','POLICY','PREDICTION','OPINION','ALLEGATION','EXPLANATION','SATIRE','HYPOTHESIS')),
  verification_status TEXT NOT NULL DEFAULT 'UNREVIEWED' CHECK(verification_status IN
   ('UNREVIEWED','SUPPORTED','REFUTED','MIXED','UNVERIFIABLE','OUT_OF_CONTEXT','REQUIRES_HUMAN_REVIEW')),
  attributed_to TEXT, scope_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(scope_json)),
  reviewer_id TEXT, review_reason TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_edges (
  evidence_edge_id TEXT PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(claim_id),
  source_version_id TEXT NOT NULL REFERENCES source_versions(source_version_id),
  relation TEXT NOT NULL CHECK(relation IN ('SUPPORTS','REFUTES','CONTEXT','ORIGIN','CORRECTION')),
  locator TEXT NOT NULL, excerpt_or_value TEXT NOT NULL, independence_group_id TEXT REFERENCES source_independence_groups(independence_group_id),
  checked_by TEXT, checked_at TEXT, human_review_required INTEGER NOT NULL DEFAULT 0 CHECK(human_review_required IN (0,1))
);
CREATE INDEX IF NOT EXISTS ix_evidence_claim ON evidence_edges(claim_id);

CREATE TABLE IF NOT EXISTS content_projects (
  project_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  topic_id TEXT NOT NULL REFERENCES topics(topic_id), domain_id TEXT NOT NULL REFERENCES domains(domain_id),
  editorial_angle TEXT NOT NULL, angle_sha256 TEXT NOT NULL CHECK(length(angle_sha256)=64),
  revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>=1), format TEXT NOT NULL CHECK(format IN ('SHORT','LONG')),
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK(status IN
    ('DRAFT','RESEARCHING','SCRIPTING','PRODUCING','QA_REVIEW','APPROVED','EXPORTED','PUBLISHED','BLOCKED','CANCELLED')),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_active_content_angle ON content_projects(channel_id,topic_id,angle_sha256,format)
 WHERE status NOT IN ('CANCELLED');
CREATE TABLE IF NOT EXISTS scripts (
  script_version_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  revision INTEGER NOT NULL CHECK(revision>=1), original_language TEXT NOT NULL,
  script_text TEXT NOT NULL, narrative_plan_json TEXT NOT NULL CHECK(json_valid(narrative_plan_json)),
  content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64), created_at TEXT NOT NULL,
  UNIQUE(project_id,revision)
);
CREATE TABLE IF NOT EXISTS script_claim_links (
  script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
  claim_id TEXT NOT NULL REFERENCES claims(claim_id), span_start INTEGER NOT NULL CHECK(span_start>=0),
  span_end INTEGER NOT NULL CHECK(span_end>=span_start),
  PRIMARY KEY(script_version_id,claim_id,span_start)
);
CREATE TABLE IF NOT EXISTS assets (
  asset_id TEXT PRIMARY KEY, source_version_id TEXT REFERENCES source_versions(source_version_id),
  origin_uri TEXT, sha256 TEXT NOT NULL CHECK(length(sha256)=64), relpath TEXT NOT NULL,
  media_type TEXT NOT NULL, synthetic INTEGER NOT NULL DEFAULT 0 CHECK(synthetic IN (0,1)),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS asset_rights (
  rights_record_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(asset_id),
  holder TEXT, license_name TEXT, evidence_uri TEXT, permitted_uses_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(permitted_uses_json)),
  restrictions_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(restrictions_json)), attribution_required INTEGER NOT NULL DEFAULT 0 CHECK(attribution_required IN (0,1)),
  expires_at TEXT, review_status TEXT NOT NULL CHECK(review_status IN ('UNKNOWN','PENDING_REVIEW','CLEARED','REJECTED','EXPIRED')),
  reviewer_id TEXT, reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS scenes (
  scene_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
  order_index INTEGER NOT NULL CHECK(order_index>=0),
  spec_json TEXT NOT NULL CHECK(json_valid(spec_json)), spec_sha256 TEXT NOT NULL CHECK(length(spec_sha256)=64),
  status TEXT NOT NULL DEFAULT 'DRAFT', UNIQUE(project_id,script_version_id,order_index)
);
CREATE TABLE IF NOT EXISTS scene_assets (
  scene_id TEXT NOT NULL REFERENCES scenes(scene_id),
  asset_id TEXT NOT NULL REFERENCES assets(asset_id), rights_record_id TEXT REFERENCES asset_rights(rights_record_id),
  PRIMARY KEY(scene_id,asset_id)
);
CREATE TABLE IF NOT EXISTS render_attempts (
  render_attempt_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  project_revision INTEGER NOT NULL, manifest_json TEXT NOT NULL CHECK(json_valid(manifest_json)),
  output_relpath TEXT, output_sha256 TEXT, worker_id TEXT, status TEXT NOT NULL,
  started_at TEXT NOT NULL, finished_at TEXT
);
CREATE TABLE IF NOT EXISTS qa_gate_reports (
  gate_report_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  project_revision INTEGER NOT NULL, gate_type TEXT NOT NULL, decision TEXT NOT NULL
  CHECK(decision IN ('PASS','FAIL','REVIEW_REQUIRED','NOT_APPLICABLE')),
  checks_json TEXT NOT NULL CHECK(json_valid(checks_json)), report_sha256 TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
  approval_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  project_revision INTEGER NOT NULL, project_sha256 TEXT NOT NULL, rights_manifest_sha256 TEXT NOT NULL,
  risk_report_sha256 TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT','REQUEST_CHANGES')),
  actor_type TEXT NOT NULL CHECK(actor_type IN ('OWNER','AUTHORIZED_HUMAN_REVIEWER')),
  reviewer_id TEXT NOT NULL, approved_at TEXT NOT NULL, expires_at TEXT
);

CREATE TABLE IF NOT EXISTS channel_accounts (
  account_link_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  provider TEXT NOT NULL DEFAULT 'YOUTUBE', external_account_id TEXT NOT NULL,
  oauth_secret_reference TEXT NOT NULL, scopes_json TEXT NOT NULL CHECK(json_valid(scopes_json)),
  authorized_at TEXT NOT NULL, revoked_at TEXT,
  UNIQUE(channel_id,provider,external_account_id)
);
CREATE TABLE IF NOT EXISTS publication_intents (
  publication_intent_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
  channel_id TEXT NOT NULL REFERENCES channels(channel_id), approval_id TEXT REFERENCES approvals(approval_id),
  project_revision INTEGER NOT NULL, video_sha256 TEXT NOT NULL, title TEXT NOT NULL,
  description TEXT NOT NULL, visibility TEXT NOT NULL CHECK(visibility IN ('PRIVATE','UNLISTED','PUBLIC')),
  contains_synthetic_media INTEGER NOT NULL CHECK(contains_synthetic_media IN (0,1)),
  made_for_kids_reviewed INTEGER NOT NULL DEFAULT 0 CHECK(made_for_kids_reviewed IN (0,1)),
  scheduled_at TEXT, state TEXT NOT NULL DEFAULT 'DRAFT',
  idempotency_key TEXT NOT NULL, created_at TEXT NOT NULL,
  UNIQUE(channel_id,idempotency_key)
);
CREATE TABLE IF NOT EXISTS publications (
  publication_id TEXT PRIMARY KEY, publication_intent_id TEXT NOT NULL UNIQUE REFERENCES publication_intents(publication_intent_id),
  platform TEXT NOT NULL DEFAULT 'YOUTUBE', external_video_id TEXT UNIQUE,
  status TEXT NOT NULL, uploaded_at TEXT, published_at TEXT, observed_at TEXT, last_error_code TEXT
);
CREATE TABLE IF NOT EXISTS analytics_snapshots (
  snapshot_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  publication_id TEXT REFERENCES publications(publication_id), provider TEXT NOT NULL,
  metric_name TEXT NOT NULL, metric_value REAL, unit TEXT NOT NULL,
  window_start TEXT NOT NULL, window_end TEXT NOT NULL, observed_at TEXT NOT NULL,
  availability TEXT NOT NULL CHECK(availability IN ('OBSERVED','NOT_AUTHORIZED','NOT_ELIGIBLE','NOT_AVAILABLE','PENDING')),
  content_format TEXT NOT NULL CHECK(content_format IN ('SHORT','LONG')),
  synthetic_test_fixture INTEGER NOT NULL DEFAULT 0 CHECK(synthetic_test_fixture IN (0,1))
);
CREATE INDEX IF NOT EXISTS ix_analytics_channel_time ON analytics_snapshots(channel_id,window_start,window_end);
CREATE TABLE IF NOT EXISTS experiments (
  experiment_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  hypothesis TEXT NOT NULL, protocol_json TEXT NOT NULL CHECK(json_valid(protocol_json)),
  status TEXT NOT NULL, concluded_at TEXT
);
CREATE TABLE IF NOT EXISTS revenue_entries (
  ledger_entry_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL REFERENCES channels(channel_id),
  period_start TEXT NOT NULL, period_end TEXT NOT NULL,
  currency TEXT NOT NULL CHECK(length(currency)=3), amount_minor_units INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('EARNED_REVENUE','EXPENSE','RESERVE','SAVINGS_TRANSFER','ADJUSTMENT')),
  basis TEXT NOT NULL CHECK(basis IN ('ACTUAL_AUTHORIZED','OWNER_ENTERED_ACTUAL','ESTIMATE_SCENARIO')),
  source_reference TEXT, note TEXT, created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workers (
  worker_id TEXT PRIMARY KEY, provider_type TEXT NOT NULL, capability_json TEXT NOT NULL CHECK(json_valid(capability_json)),
  last_seen_at TEXT NOT NULL, health_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS models (
  model_id TEXT PRIMARY KEY, version_tag TEXT NOT NULL, model_sha256 TEXT NOT NULL CHECK(length(model_sha256)=64),
  metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)), commercial_status TEXT NOT NULL,
  verified_at TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY, channel_id TEXT REFERENCES channels(channel_id), domain_id TEXT NOT NULL REFERENCES domains(domain_id),
  job_type TEXT NOT NULL, input_sha256 TEXT NOT NULL CHECK(length(input_sha256)=64),
  idempotency_key TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 50,
  state TEXT NOT NULL CHECK(state IN
   ('QUEUED','RUNNING','RETRY_WAIT','BLOCKED','WAITING_FOR_APPROVAL','WAITING_FOR_CAPABILITY','SUCCEEDED','FAILED','CANCELLED')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  lease_worker_id TEXT REFERENCES workers(worker_id), lease_expiry_at TEXT, heartbeat_at TEXT,
  next_retry_at TEXT, error_code TEXT, progress_json TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(progress_json)),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(channel_id,job_type,idempotency_key)
);
CREATE INDEX IF NOT EXISTS ix_jobs_schedule ON jobs(state,priority DESC,created_at);
CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_idempotency_global
 ON jobs(COALESCE(channel_id,'GLOBAL'),job_type,idempotency_key);
CREATE TABLE IF NOT EXISTS allowed_job_state_transitions (
  from_state TEXT NOT NULL, to_state TEXT NOT NULL,
  PRIMARY KEY(from_state,to_state)
);
INSERT OR IGNORE INTO allowed_job_state_transitions(from_state,to_state) VALUES
 ('QUEUED','RUNNING'),('QUEUED','CANCELLED'),('QUEUED','BLOCKED'),
 ('RUNNING','SUCCEEDED'),('RUNNING','RETRY_WAIT'),('RUNNING','BLOCKED'),
 ('RUNNING','WAITING_FOR_APPROVAL'),('RUNNING','WAITING_FOR_CAPABILITY'),
 ('RUNNING','FAILED'),('RUNNING','CANCELLED'),
 ('RETRY_WAIT','QUEUED'),('RETRY_WAIT','FAILED'),('RETRY_WAIT','CANCELLED'),
 ('BLOCKED','QUEUED'),('BLOCKED','CANCELLED'),
 ('WAITING_FOR_APPROVAL','QUEUED'),('WAITING_FOR_APPROVAL','CANCELLED'),
 ('WAITING_FOR_CAPABILITY','QUEUED'),('WAITING_FOR_CAPABILITY','CANCELLED'),
 ('FAILED','QUEUED'),('FAILED','CANCELLED');
CREATE TRIGGER IF NOT EXISTS trg_jobs_valid_state_transition
 BEFORE UPDATE OF state ON jobs
 WHEN OLD.state <> NEW.state AND NOT EXISTS (
  SELECT 1 FROM allowed_job_state_transitions
   WHERE from_state=OLD.state AND to_state=NEW.state)
 BEGIN SELECT RAISE(ABORT,'invalid durable job state transition'); END;
CREATE TABLE IF NOT EXISTS job_dependencies (
  job_id TEXT NOT NULL REFERENCES jobs(job_id), depends_on_job_id TEXT NOT NULL REFERENCES jobs(job_id),
  PRIMARY KEY(job_id,depends_on_job_id), CHECK(job_id<>depends_on_job_id)
);
CREATE TABLE IF NOT EXISTS job_attempts (
  attempt_id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(job_id),
  worker_id TEXT REFERENCES workers(worker_id), started_at TEXT NOT NULL,
  finished_at TEXT, outcome TEXT, error_code TEXT, output_sha256 TEXT
);
CREATE TABLE IF NOT EXISTS audit_events (
  event_id TEXT PRIMARY KEY, actor_type TEXT NOT NULL, actor_id TEXT,
  event_type TEXT NOT NULL, resource_type TEXT NOT NULL, resource_id TEXT,
  before_sha256 TEXT, after_sha256 TEXT, reason TEXT, trace_id TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_resource ON audit_events(resource_type,resource_id,created_at);

-- Prevent silent mutation of source-version evidence. Controlled deletion is a separate retention operation.
CREATE TRIGGER IF NOT EXISTS trg_source_versions_immutable
 BEFORE UPDATE ON source_versions
 BEGIN SELECT RAISE(ABORT,'source versions are immutable; insert a new version'); END;
