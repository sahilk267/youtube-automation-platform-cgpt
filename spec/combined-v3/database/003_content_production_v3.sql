-- v3.0 additive reference migration; apply only with versioned migration runner and verified backup.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS creative_briefs (
 brief_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id),
 domain_id TEXT NOT NULL REFERENCES domains(domain_id),
 contract_version TEXT NOT NULL CHECK(contract_version='3.0.0'),
 brief_json TEXT NOT NULL CHECK(json_valid(brief_json)),
 brief_sha256 TEXT NOT NULL CHECK(length(brief_sha256)=64),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','EVIDENCE_LOCKED','BLOCKED','APPROVED_FOR_STORY')),
 created_at TEXT NOT NULL, UNIQUE(project_id,brief_sha256)
);
CREATE TABLE IF NOT EXISTS creative_story_versions (
 story_id TEXT PRIMARY KEY, brief_id TEXT NOT NULL REFERENCES creative_briefs(brief_id),
 research_revision_sha256 TEXT NOT NULL CHECK(length(research_revision_sha256)=64),
 beat_graph_json TEXT NOT NULL CHECK(json_valid(beat_graph_json)),
 duration_ms INTEGER NOT NULL CHECK(duration_ms>0),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','FACT_REVIEWED','BLOCKED')), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS creative_shot_plans (
 shot_plan_id TEXT PRIMARY KEY, story_id TEXT NOT NULL REFERENCES creative_story_versions(story_id),
 shot_plan_json TEXT NOT NULL CHECK(json_valid(shot_plan_json)),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','RIGHTS_REVIEWED','BLOCKED')), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS creative_locale_variants (
 variant_id TEXT PRIMARY KEY, story_id TEXT NOT NULL REFERENCES creative_story_versions(story_id),
 locale TEXT NOT NULL, source_claim_sha256 TEXT NOT NULL CHECK(length(source_claim_sha256)=64),
 variant_json TEXT NOT NULL CHECK(json_valid(variant_json)),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','BLOCKED','QC_REQUIRED','APPROVED')),created_at TEXT NOT NULL,
 UNIQUE(story_id,locale,source_claim_sha256)
);
CREATE TABLE IF NOT EXISTS creative_timeline_versions (
 timeline_id TEXT PRIMARY KEY, story_id TEXT NOT NULL REFERENCES creative_story_versions(story_id),
 variant_id TEXT REFERENCES creative_locale_variants(variant_id),
 locale TEXT NOT NULL, timeline_json TEXT NOT NULL CHECK(json_valid(timeline_json)),
 render_graph_sha256 TEXT NOT NULL CHECK(length(render_graph_sha256)=64),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','QC_PENDING','QC_PASS','BLOCKED','APPROVED')),
 created_at TEXT NOT NULL, UNIQUE(story_id,locale,render_graph_sha256)
);
CREATE TABLE IF NOT EXISTS creative_quality_reports (
 report_id TEXT PRIMARY KEY, timeline_id TEXT NOT NULL REFERENCES creative_timeline_versions(timeline_id),
 report_json TEXT NOT NULL CHECK(json_valid(report_json)),
 reviewed_revision_sha256 TEXT NOT NULL CHECK(length(reviewed_revision_sha256)=64),
 human_watchthrough TEXT NOT NULL CHECK(human_watchthrough IN ('NOT_DONE','APPROVED','REJECTED')),
 final_status TEXT NOT NULL CHECK(final_status IN ('PASS','FAIL','REVIEW_REQUIRED')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS creative_rights_source_clip_maps (
 clip_map_id TEXT PRIMARY KEY, story_id TEXT NOT NULL REFERENCES creative_story_versions(story_id),
 source_url TEXT NOT NULL, rights_decision_id TEXT,
 clip_map_json TEXT NOT NULL CHECK(json_valid(clip_map_json)),
 legal_status TEXT NOT NULL CHECK(legal_status IN ('PENDING','APPROVED','REJECTED')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS creative_asset_dependencies (
 dependency_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES content_projects(project_id),
 parent_artifact_id TEXT NOT NULL, child_artifact_id TEXT NOT NULL,
 dependency_kind TEXT NOT NULL CHECK(dependency_kind IN ('CLAIM','RIGHTS','AUDIO','OVERLAY','VISUAL','LOCALE','TIMELINE','PUBLISH_APPROVAL')),
 parent_sha256 TEXT NOT NULL CHECK(length(parent_sha256)=64),
 invalidated_at TEXT, reason TEXT, UNIQUE(parent_artifact_id,child_artifact_id,dependency_kind)
);
CREATE INDEX IF NOT EXISTS idx_creative_story_brief ON creative_story_versions(brief_id);
CREATE INDEX IF NOT EXISTS idx_creative_variant_story ON creative_locale_variants(story_id);
CREATE INDEX IF NOT EXISTS idx_creative_timeline_story ON creative_timeline_versions(story_id,locale);
CREATE INDEX IF NOT EXISTS idx_creative_dependencies_parent ON creative_asset_dependencies(parent_artifact_id);
