-- M3: private-only upload intent. No secret tokens stored in SQLite.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m3_upload_accounts (
 local_channel_id TEXT PRIMARY KEY REFERENCES channels(channel_id) ON DELETE CASCADE,
 remote_channel_id TEXT NOT NULL,
 remote_title TEXT NOT NULL,
 verified_at TEXT NOT NULL,
 scopes_json TEXT NOT NULL CHECK(json_valid(scopes_json))
);
CREATE TABLE IF NOT EXISTS m3_private_upload_intents (
 intent_id TEXT PRIMARY KEY,
 export_id TEXT NOT NULL UNIQUE REFERENCES m22_final_exports(export_id),
 local_channel_id TEXT NOT NULL REFERENCES channels(channel_id),
 remote_channel_id TEXT NOT NULL,
 title TEXT NOT NULL,
 description TEXT NOT NULL,
 tags_json TEXT NOT NULL CHECK(json_valid(tags_json)),
 altered_content INTEGER NOT NULL CHECK(altered_content IN (0,1)),
 made_for_kids INTEGER NOT NULL CHECK(made_for_kids IN (0,1)),
 owner_confirmed INTEGER NOT NULL CHECK(owner_confirmed=1),
 privacy_status TEXT NOT NULL DEFAULT 'private' CHECK(privacy_status='private'),
 state TEXT NOT NULL CHECK(state IN ('PREPARED','IN_FLIGHT','REMOTE_UNKNOWN','UPLOADED_PRIVATE','FAILED_SAFE')),
 remote_video_id TEXT UNIQUE,
 receipt_json TEXT,
 last_error TEXT,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_m3_private_intents_channel ON m3_private_upload_intents(local_channel_id,created_at);
