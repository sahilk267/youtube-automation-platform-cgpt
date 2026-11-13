-- Additive M1–M3 migration. No alteration of canonical v3 columns.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m1_project_sources (
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 source_version_id TEXT NOT NULL REFERENCES source_versions(source_version_id),
 bound_at TEXT NOT NULL,
 PRIMARY KEY(project_id, source_version_id)
);
CREATE TABLE IF NOT EXISTS m1_source_feeds (
 feed_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 feed_url TEXT NOT NULL,
 title TEXT NOT NULL,
 imported_at TEXT NOT NULL,
 entries_json TEXT NOT NULL CHECK(json_valid(entries_json)),
 source_status TEXT NOT NULL CHECK(source_status IN ('OWNER_SUPPLIED_XML','FETCHED_FROM_APPROVED_FEED')),
 UNIQUE(project_id,feed_url,imported_at)
);
CREATE TABLE IF NOT EXISTS m2_story_plans (
 story_plan_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 plan_json TEXT NOT NULL CHECK(json_valid(plan_json)),
 fingerprint TEXT NOT NULL CHECK(length(fingerprint)=64),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','QC_REQUIRED','BLOCKED')),
 created_at TEXT NOT NULL,
 UNIQUE(project_id,fingerprint)
);
CREATE TABLE IF NOT EXISTS m2_locale_edits (
 locale_edit_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 locale TEXT NOT NULL,
 localized_scenes_json TEXT NOT NULL CHECK(json_valid(localized_scenes_json)),
 owner_checked INTEGER NOT NULL DEFAULT 0 CHECK(owner_checked IN (0,1)),
 content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),
 created_at TEXT NOT NULL,
 UNIQUE(project_id,script_version_id,locale)
);
CREATE TABLE IF NOT EXISTS m3_review_records (
 review_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 render_attempt_id TEXT NOT NULL REFERENCES render_attempts(render_attempt_id),
 fingerprint TEXT NOT NULL CHECK(length(fingerprint)=64),
 rights_attested INTEGER NOT NULL CHECK(rights_attested IN (0,1)),
 claims_attested INTEGER NOT NULL CHECK(claims_attested IN (0,1)),
 watched_full_video INTEGER NOT NULL CHECK(watched_full_video IN (0,1)),
 reviewer TEXT NOT NULL,
 notes TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('APPROVED','REJECTED')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS m3_exports (
 export_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id),
 render_attempt_id TEXT NOT NULL REFERENCES render_attempts(render_attempt_id),
 review_id TEXT NOT NULL REFERENCES m3_review_records(review_id),
 video_sha256 TEXT NOT NULL CHECK(length(video_sha256)=64),
 export_relpath TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('REVIEW_ONLY','READY_FOR_MANUAL_UPLOAD','INVALIDATED')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS m3_analytics_imports (
 import_id TEXT PRIMARY KEY,
 channel_id TEXT NOT NULL REFERENCES channels(channel_id),
 report_date TEXT NOT NULL,
 format TEXT NOT NULL CHECK(format IN ('SHORT','LONG','ALL')),
 views INTEGER NOT NULL CHECK(views>=0),
 watch_hours REAL CHECK(watch_hours IS NULL OR watch_hours>=0),
 subscribers_gained INTEGER CHECK(subscribers_gained IS NULL OR subscribers_gained>=0),
 estimated_revenue REAL CHECK(estimated_revenue IS NULL OR estimated_revenue>=0),
 revenue_currency TEXT,
 provenance TEXT NOT NULL CHECK(provenance IN ('OWNER_ENTERED_NOT_VERIFIED','AUTHORIZED_API')),
 created_at TEXT NOT NULL,
 UNIQUE(channel_id,report_date,format,provenance)
);
CREATE TABLE IF NOT EXISTS m3_youtube_uploads (
 upload_id TEXT PRIMARY KEY,
 export_id TEXT NOT NULL UNIQUE REFERENCES m3_exports(export_id),
 owner_approved INTEGER NOT NULL CHECK(owner_approved=1),
 video_id TEXT UNIQUE,
 state TEXT NOT NULL CHECK(state IN ('PREPARED','IN_FLIGHT','REMOTE_UNKNOWN','UPLOADED_PRIVATE','FAILED')),
 error TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_m1_ps_project ON m1_project_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_m3_reviews_project ON m3_review_records(project_id,created_at);

CREATE TABLE IF NOT EXISTS m2_voice_provenance (
 project_id TEXT PRIMARY KEY REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 script_sha256 TEXT NOT NULL CHECK(length(script_sha256)=64),
 voice_source TEXT NOT NULL CHECK(voice_source IN ('OPT_IN_LOCAL_PIPER')),
 generated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS m3_youtube_accounts (
 local_channel_id TEXT PRIMARY KEY REFERENCES channels(channel_id) ON DELETE CASCADE,
 remote_channel_id TEXT NOT NULL,
 remote_title TEXT NOT NULL,
 connected_at TEXT NOT NULL,
 verification TEXT NOT NULL CHECK(verification='OAUTH_CHANNELS_MINE'),
 oauth_scope_text TEXT NOT NULL
);
