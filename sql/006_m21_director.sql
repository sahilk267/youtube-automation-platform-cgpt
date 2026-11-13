-- M2.1: script-derived editorial drafts, locally supplied measured voice segments.
-- Existing 001-005 definitions and hashes are immutable.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m21_director_drafts (
 draft_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 project_revision INTEGER NOT NULL,
 locale TEXT NOT NULL,
 source_text_sha256 TEXT NOT NULL CHECK(length(source_text_sha256)=64),
 segments_json TEXT NOT NULL CHECK(json_valid(segments_json)),
 visual_policy TEXT NOT NULL,
 translation_review TEXT NOT NULL CHECK(translation_review IN ('SOURCE_LANGUAGE','OWNER_REVIEWED_TRANSLATION')),
 draft_sha256 TEXT NOT NULL UNIQUE,
 status TEXT NOT NULL CHECK(status IN ('DRAFT','ASSEMBLED')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS m21_voice_segments (
 draft_id TEXT NOT NULL REFERENCES m21_director_drafts(draft_id) ON DELETE CASCADE,
 segment_index INTEGER NOT NULL CHECK(segment_index>=0),
 asset_relpath TEXT NOT NULL,
 audio_sha256 TEXT NOT NULL CHECK(length(audio_sha256)=64),
 sample_rate INTEGER NOT NULL CHECK(sample_rate=16000),
 sample_frames INTEGER NOT NULL CHECK(sample_frames>0),
 source_kind TEXT NOT NULL CHECK(source_kind IN ('OWNER_RECORDED_WAV','OPT_IN_LOCAL_PIPER')),
 uploaded_at TEXT NOT NULL,
 PRIMARY KEY(draft_id,segment_index)
);
CREATE TABLE IF NOT EXISTS m21_plan_audio (
 plan_id TEXT PRIMARY KEY REFERENCES m2_studio_plans(plan_id) ON DELETE CASCADE,
 draft_id TEXT NOT NULL REFERENCES m21_director_drafts(draft_id),
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 voice_relpath TEXT NOT NULL,
 voice_sha256 TEXT NOT NULL CHECK(length(voice_sha256)=64),
 audio_segments_sha256 TEXT NOT NULL CHECK(length(audio_segments_sha256)=64),
 duration_ms INTEGER NOT NULL CHECK(duration_ms>0),
 alignment_provenance TEXT NOT NULL CHECK(alignment_provenance='MEASURED_PER_SEGMENT_NOT_WORD_LEVEL'),
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_m21_drafts_project ON m21_director_drafts(project_id,created_at);
