-- M3.2: non-destructive acceptance checkpoints. No bearer tokens / OAuth secrets stored.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS m32_acceptance_checks (
 check_id TEXT PRIMARY KEY,
 export_id TEXT NOT NULL REFERENCES m22_final_exports(export_id),
 local_channel_id TEXT NOT NULL REFERENCES channels(channel_id),
 remote_channel_id TEXT,
 mode TEXT NOT NULL CHECK(mode IN ('OFFLINE','OWNER_AUTHORIZED_READ_ONLY')),
 report_json TEXT NOT NULL CHECK(json_valid(report_json)),
 status TEXT NOT NULL CHECK(status IN ('BLOCKED','LOCAL_READY','REMOTE_CHANNEL_VERIFIED')),
 created_at TEXT NOT NULL
);
