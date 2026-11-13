-- Distinct authenticated monetary estimates; do not merge with operator-entered analytics.
-- Revenue OAuth metadata is NOT upload scope authorization.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m31_monetary_daily (
 snapshot_id TEXT PRIMARY KEY,
 local_channel_id TEXT NOT NULL REFERENCES channels(channel_id) ON DELETE CASCADE,
 remote_channel_id TEXT NOT NULL,
 report_date TEXT NOT NULL,
 currency TEXT NOT NULL CHECK(length(currency)=3),
 estimated_revenue REAL NOT NULL CHECK(estimated_revenue>=0),
 estimated_ad_revenue REAL NOT NULL CHECK(estimated_ad_revenue>=0),
 source TEXT NOT NULL CHECK(source='YOUTUBE_ANALYTICS_MONETARY_OAUTH'),
 retrieved_at TEXT NOT NULL,
 response_digest TEXT NOT NULL CHECK(length(response_digest)=64),
 UNIQUE(local_channel_id,report_date,currency)
);
CREATE INDEX IF NOT EXISTS idx_m31_monetary ON m31_monetary_daily(local_channel_id,report_date);
CREATE TABLE IF NOT EXISTS m31_retention_snapshots (
 snapshot_id TEXT PRIMARY KEY,
 export_id TEXT NOT NULL REFERENCES m22_final_exports(export_id) ON DELETE CASCADE,
 remote_video_id TEXT NOT NULL,
 start_date TEXT NOT NULL,
 end_date TEXT NOT NULL,
 raw_json TEXT NOT NULL CHECK(json_valid(raw_json)),
 scene_json TEXT NOT NULL CHECK(json_valid(scene_json)),
 source TEXT NOT NULL CHECK(source='OWNER_AUTHORIZED_YOUTUBE_ANALYTICS'),
 retrieved_at TEXT NOT NULL,
 UNIQUE(export_id,start_date,end_date)
);

CREATE TABLE IF NOT EXISTS m31_monetary_accounts (
 local_channel_id TEXT PRIMARY KEY REFERENCES channels(channel_id) ON DELETE CASCADE,
 remote_channel_id TEXT NOT NULL,
 remote_title TEXT NOT NULL,
 verified_at TEXT NOT NULL,
 scopes_json TEXT NOT NULL CHECK(json_valid(scopes_json))
);
