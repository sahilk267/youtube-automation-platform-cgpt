-- M2.3 additive release: ASR proposals are NEVER equivalent to owner-approved word timings.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m23_alignment_drafts (
 draft_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 plan_id TEXT NOT NULL REFERENCES m2_studio_plans(plan_id),
 plan_sha256 TEXT NOT NULL CHECK(length(plan_sha256)=64),
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 voice_sha256 TEXT NOT NULL CHECK(length(voice_sha256)=64),
 asr_model_label TEXT NOT NULL,
 language TEXT NOT NULL,
 candidate_json TEXT NOT NULL CHECK(json_valid(candidate_json)),
 transcript_matches INTEGER NOT NULL CHECK(transcript_matches IN (0,1)),
 status TEXT NOT NULL CHECK(status IN ('REVIEW_REQUIRED','OWNER_APPROVED','SUPERSEDED')),
 created_at TEXT NOT NULL,
 reviewed_at TEXT,
 UNIQUE(plan_id,voice_sha256,plan_sha256)
);
CREATE TABLE IF NOT EXISTS m23_evidence_cards (
 card_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 claim_id TEXT NOT NULL REFERENCES claims(claim_id),
 source_version_id TEXT NOT NULL REFERENCES source_versions(source_version_id),
 asset_id TEXT NOT NULL UNIQUE REFERENCES m2_studio_assets(asset_id),
 claim_updated_at TEXT NOT NULL,
 source_content_sha256 TEXT NOT NULL CHECK(length(source_content_sha256)=64),
 provenance_json TEXT NOT NULL CHECK(json_valid(provenance_json)),
 created_at TEXT NOT NULL,
 UNIQUE(project_id,claim_id,source_version_id)
);
