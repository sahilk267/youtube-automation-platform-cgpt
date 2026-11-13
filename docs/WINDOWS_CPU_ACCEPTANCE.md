# ViralOS Windows CPU-only acceptance and private recovery (Issue #4)

**What this proves:** an operator can reproduce environment diagnostics, original FFmpeg 9:16 / 16:9 technical rendering, and recover canonical SQLite data from a private backup while invalidating previously approved exports. **What it does not prove:** that the owner's 8th-gen i7 is fast enough, natural Hindi/English voices, forced alignment, real YouTube authorization, media-rights compliance, or video production quality. Owner Windows acceptance remains open until the actual machine is tested and a private signed-off report is stored locally.

## 1. Clean Windows 10/11 setup (no paid services)

Install Git, Python **3.12 64-bit** and FFmpeg with both `ffmpeg.exe` and `ffprobe.exe` on PATH. Clone the repository. Open PowerShell in its root:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe tools/owner_acceptance.py preflight
```

Optional: for **sampled process peak RAM**, install `psutil` in this local venv (no model download):

```powershell
& .\.venv\Scripts\python.exe -m pip install "psutil>=5.9,<8"
```

The preflight report shows Python / OS / FFmpeg / required modules and marks `owner_i7_windows_hardware_verified: false` by design. Confirm CPU family and total RAM in Windows Task Manager separately. No credentials or private project metrics are sent anywhere.

## 2. Synthetic CPU benchmark (no borrowed footage)

```powershell
& .\.venv\Scripts\python.exe tools/owner_acceptance.py benchmark --duration 3 --report "$HOME\ViralOSPrivateBackups\benchmark.json"
& .\.venv\Scripts\python.exe -m pytest -q
powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
```

The benchmark encodes original generated video plus audio in **540x960 and 960x540 H.264/AAC**, verifies both streams using FFprobe, and measures encode wall time. CPU RAM is sampled only when optional psutil is present; a missing measurement is `null`, not a fabricated value. The smoke outputs are discarded after validation. Production rendering, UI fonts, sound and professional quality still require an actual human watch-through. The local app listens on `127.0.0.1:8000` by default. Do not expose the dashboard to the public Internet.

**Record privately:** machine CPU, RAM, Windows build, Python, FFmpeg, video duration/encode wall seconds, optional sampled RSS, UI screenshots showing Hindi glyphs/safe margins, actual audio check, render failures and voice-model license details (if tested). Only publish redacted summaries. Before deciding the PC is accepted, render both a real original 9:16 and 16:9 storyboard, watch the full video and note manual editing effort.

## 3. Private SQLite backup (the application may be running)

Use SQLite's online backup API instead of copying a live WAL database. The command backs up **the database only**, not original media, voice files, cached model files, FFmpeg outputs, system keyring or OAuth credentials.

```powershell
& .\.venv\Scripts\python.exe tools/owner_acceptance.py backup
```

Default storage is `$HOME\ViralOSPrivateBackups`. The command refuses to save inside the public Git repository. Store the resulting `.sqlite3` and `.manifest.json` **together** on encrypted owner-managed storage, preferably with an off-machine private copy. Database data may be private even if this repo is public. Do not commit either file, paste contents into a chat, or upload them to GitHub Issues.

## 4. Verify and restore into a fresh local profile

**Stop ViralOS before restoring**. Never overwrite an existing DB or its `-wal`/`-shm` sidecar. Choose a different, nonexistent target name.

```powershell
& .\.venv\Scripts\python.exe tools/owner_acceptance.py verify --manifest "$HOME\ViralOSPrivateBackups\viralos-REPLACE.sqlite3.manifest.json"
& .\.venv\Scripts\python.exe tools/owner_acceptance.py restore --manifest "$HOME\ViralOSPrivateBackups\viralos-REPLACE.sqlite3.manifest.json" --target "$HOME\ViralOSRecovery\viralos-restored.db"
$env:VIRALOS_DB = "$HOME\ViralOSRecovery\viralos-restored.db"
& .\.venv\Scripts\python.exe tools/check_environment.py
```

The restore verifies backup SHA-256, SQLite integrity, foreign keys and exact migration checksums. It preserves historical human-review records for audit but **invalidates final export approvals**, blocks already-invalidated download/re-export reuse and changes any `IN_FLIGHT` private upload to `REMOTE_UNKNOWN` (manual channel reconciliation required; do not auto retry). An actual successful remote upload remains historically recorded rather than incorrectly assumed missing. All local media paths require revalidation; no media is restored automatically.

If the current software has different migration files, use the matching historical Git commit to verify/migrate a **separate restored copy**. Never alter applied SQL migration files or overwrite the live database to force acceptance.

## 5. Acceptance criteria and safety cases

| Gate | Expected result | Where verified |
|---|---|---|
| Preflight | Missing FFmpeg or Python packages explicitly BLOCKED | Offline Python test + owner run |
| 9:16 and 16:9 | Real H.264 and AAC streams, wall time recorded | FFmpeg test + owner run |
| RAM | Sampled RSS only if psutil is installed; else `null` | Code + report |
| Online SQLite backup | Consistent snapshot even with WAL mode | SQLite unit/integration test |
| Corrupted/tampered backup | Refuse restore before target creation | Negative test |
| Existing target/WAL file | Refuse overwrite | Negative test |
| DB migration integrity | Canonical SQL checksums verified | Negative test |
| Old final approvals | INVALIDATED on restore | Test, human re-review needed |
| Remote upload ambiguity | Mark `REMOTE_UNKNOWN`, no blind retry | SQL test + existing upload tests |
| Voice/GPU/owned Google | Remains unverified without owner access | Pending |

**Do not put secrets in reports**. This is not a replacement for full media backups, Windows-specific end-to-end acceptance, or independently audited legal clearance.