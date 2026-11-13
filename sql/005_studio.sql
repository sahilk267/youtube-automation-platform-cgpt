-- M2 CPU Studio: isolated, additive to M0-M3. Does not change legacy SceneSpec.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m2_studio_assets (
 asset_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 kind TEXT NOT NULL CHECK(kind IN ('STILL','MUSIC')),
 local_relpath TEXT NOT NULL,
 origin TEXT NOT NULL,
 license_note TEXT NOT NULL,
 rights_attested INTEGER NOT NULL CHECK(rights_attested=1),
 content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),
 mime TEXT NOT NULL,
 duration_ms INTEGER,
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_studio_assets_project ON m2_studio_assets(project_id);
CREATE TABLE IF NOT EXISTS m2_studio_plans (
 plan_id TEXT PRIMARY KEY,
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 script_version_id TEXT NOT NULL REFERENCES scripts(script_version_id),
 project_revision INTEGER NOT NULL,
 locale TEXT NOT NULL,
 plan_json TEXT NOT NULL CHECK(json_valid(plan_json)),
 plan_sha256 TEXT NOT NULL CHECK(length(plan_sha256)=64),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','NEEDS_AUDIO_QC','BLOCKED')),
 created_at TEXT NOT NULL,
 UNIQUE(project_id,plan_sha256)
);
CREATE INDEX IF NOT EXISTS idx_studio_plans_project ON m2_studio_plans(project_id,created_at);
CREATE TABLE IF NOT EXISTS m2_studio_renders (
 studio_render_id TEXT PRIMARY KEY,
 plan_id TEXT NOT NULL REFERENCES m2_studio_plans(plan_id),
 project_id TEXT NOT NULL REFERENCES content_projects(project_id) ON DELETE CASCADE,
 job_id TEXT NOT NULL UNIQUE REFERENCES jobs(job_id),
 output_relpath TEXT NOT NULL,
 output_sha256 TEXT NOT NULL CHECK(length(output_sha256)=64),
 quality_report_json TEXT NOT NULL CHECK(json_valid(quality_report_json)),
 render_manifest_json TEXT NOT NULL CHECK(json_valid(render_manifest_json)),
 status TEXT NOT NULL CHECK(status='TECHNICAL_STUDIO_PREVIEW'),
 created_at TEXT NOT NULL
);
