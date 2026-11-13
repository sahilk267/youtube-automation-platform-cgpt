-- M2.2: additive, final-render review and explicit owner-reviewed word timing.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m22_word_alignments (
 alignment_id TEXT PRIMARY KEY,
 plan_id TEXT NOT NULL REFERENCES m2_studio_plans(plan_id) ON DELETE CASCADE,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 voice_sha256 TEXT NOT NULL CHECK(length(voice_sha256)=64),
 plan_sha256 TEXT NOT NULL CHECK(length(plan_sha256)=64),
 words_json TEXT NOT NULL CHECK(json_valid(words_json)),
 provenance TEXT NOT NULL CHECK(provenance IN ('OWNER_TIMED_REVIEWED','EXTERNAL_ALIGNER_OWNER_REVIEWED')),
 submitted_at TEXT NOT NULL,
 UNIQUE(plan_id,voice_sha256,plan_sha256)
);
CREATE TABLE IF NOT EXISTS m22_studio_reviews (
 review_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 preview_render_id TEXT NOT NULL REFERENCES m2_studio_renders(studio_render_id),
 plan_id TEXT NOT NULL REFERENCES m2_studio_plans(plan_id),
 fingerprint TEXT NOT NULL CHECK(length(fingerprint)=64),
 reviewer TEXT NOT NULL,
 watched_full_video INTEGER NOT NULL CHECK(watched_full_video=1),
 original_or_rights_reviewed INTEGER NOT NULL CHECK(original_or_rights_reviewed=1),
 facts_sources_reviewed INTEGER NOT NULL CHECK(facts_sources_reviewed=1),
 narration_and_captions_reviewed INTEGER NOT NULL CHECK(narration_and_captions_reviewed=1),
 notes TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status='OWNER_APPROVED_FOR_FINAL_EXPORT'),
 created_at TEXT NOT NULL,
 UNIQUE(preview_render_id,fingerprint)
);
CREATE TABLE IF NOT EXISTS m22_final_exports (
 export_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 plan_id TEXT NOT NULL REFERENCES m2_studio_plans(plan_id),
 review_id TEXT NOT NULL UNIQUE REFERENCES m22_studio_reviews(review_id),
 fingerprint TEXT NOT NULL CHECK(length(fingerprint)=64),
 file_relpath TEXT NOT NULL,
 file_sha256 TEXT NOT NULL CHECK(length(file_sha256)=64),
 report_json TEXT NOT NULL CHECK(json_valid(report_json)),
 manifest_json TEXT NOT NULL CHECK(json_valid(manifest_json)),
 status TEXT NOT NULL CHECK(status IN ('OWNER_APPROVED_FINAL_EXPORT','INVALIDATED')),
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_m22_exports_project ON m22_final_exports(project_id,created_at);
