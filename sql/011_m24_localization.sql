-- M2.4: immutable project-bound localization with separate WAV assets and previews.
-- No automatic translation, cloning or video publication.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m24_variants (
 variant_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 source_script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 source_script_sha256 TEXT NOT NULL CHECK(length(source_script_sha256)=64),
 project_revision INTEGER NOT NULL,
 locale TEXT NOT NULL CHECK(locale IN ('en-US','hi-IN')),
 reviewed_text TEXT NOT NULL,
 reviewed_text_sha256 TEXT NOT NULL CHECK(length(reviewed_text_sha256)=64),
 reviewer TEXT NOT NULL,
 regional_notes TEXT NOT NULL,
 segment_json TEXT NOT NULL CHECK(json_valid(segment_json)),
 state TEXT NOT NULL CHECK(state IN ('DRAFT','RENDERED')),
 created_at TEXT NOT NULL,
 UNIQUE(project_id,source_script_version_id,locale,reviewed_text_sha256)
);
CREATE TABLE IF NOT EXISTS m24_pronunciation (
 variant_id TEXT NOT NULL REFERENCES m24_variants(variant_id) ON DELETE CASCADE,
 written TEXT NOT NULL,
 speak_as TEXT NOT NULL,
 reviewed_by TEXT NOT NULL,
 PRIMARY KEY (variant_id,written)
);
CREATE TABLE IF NOT EXISTS m24_voices (
 variant_id TEXT NOT NULL REFERENCES m24_variants(variant_id) ON DELETE CASCADE,
 segment_index INTEGER NOT NULL CHECK(segment_index>=0),
 file_relpath TEXT NOT NULL,
 file_sha256 TEXT NOT NULL CHECK(length(file_sha256)=64),
 sample_frames INTEGER NOT NULL CHECK(sample_frames>0),
 source_kind TEXT NOT NULL CHECK(source_kind IN ('OWNER_RECORDED_WAV','OPT_IN_LOCAL_PIPER')),
 created_at TEXT NOT NULL,
 PRIMARY KEY(variant_id,segment_index)
);
CREATE TABLE IF NOT EXISTS m24_previews (
 preview_id TEXT PRIMARY KEY,
 variant_id TEXT NOT NULL UNIQUE REFERENCES m24_variants(variant_id),
 file_relpath TEXT NOT NULL,
 file_sha256 TEXT NOT NULL CHECK(length(file_sha256)=64),
 narration_sha256 TEXT NOT NULL CHECK(length(narration_sha256)=64),
 input_fingerprint TEXT NOT NULL CHECK(length(input_fingerprint)=64),
 plan_json TEXT NOT NULL CHECK(json_valid(plan_json)),
 qc_json TEXT NOT NULL CHECK(json_valid(qc_json)),
 created_at TEXT NOT NULL
);
