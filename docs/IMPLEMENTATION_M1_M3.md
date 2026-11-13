# ViralOS Launch – M1/M2/M3 engineering increment (2026-11-12)

**Status:** runnable assisted development workbench, NOT a production-ready YouTube creation agent. It extends M0 without removing the Launch v3 canonical source specification. The master specification and implemented source are deliberately separate. No GPU is required for baseline operation.

## What's actually implemented

| Milestone | Working now | Not complete / not claimed |
| --- | --- | --- |
| M1 Research | Project-bound source version links, owner-pasted RSS/Atom parser, optional **explicit allowlisted** HTTPS feed fetch with permission flag, source coverage & missing evidence report, cross-project contamination guard | Auto article retrieval, full original source validation, independent multilingual corroboration, LLM research/trend discovery, live cricket/NFL data licensing |
| M2 Creative | Deterministic scene timing/beat plan, original CPU pitch/gridiron-like slides, optional owner WAV & preconfigured local Piper voice, editable locale-on-screen-text variants, storyboard-timed SRT exports, FFmpeg MP4 technical preview, checks for stale generated voice | Professional scene-compositing editor, word-level voice alignment, automatic translation and dubbed soundtracks, licensed b-roll, cinematic image/video gen, full watch-through by software |
| M3 Publishing & Learning | Human full-watch/claims/rights attestations, content/revision fingerprint and stale approval block, **private review ZIP**, explicitly labeled owner-entered metrics, optional Google **read-only Analytics OAuth** with OS keyring and account identity check | Uploads to YouTube, automatic monetization, independently verified revenue, published title/thumbnail experiment, official multi-language audio upload, professional final release QA |

**No platform uploads are possible:** POST `/api/youtube/upload` returns HTTP 403. This is intentional; the available render is watermarked `TECHNICAL PREVIEW / NOT PUBLISH READY`. The private review ZIP must not be confused with a final upload package.

## Windows setup

1. Install Python 3.12 and FFmpeg/FFprobe, all available on PATH. Local SSD recommended. Use `cmd /c where ffmpeg` to verify. No NVIDIA driver required.
2. Extract ZIP; in PowerShell from project root run `powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1`. The script installs the `requirements.txt` package set and starts local service. Alternatively:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

3. Open `http://127.0.0.1:8000`. Work through channel > project > source > claim > script > scenes > optional voice. Then audit sources, compile story plan, review SRT, queue CPU preview, record human review and download private ZIP.
4. Scripts, source text and screen overlays are entered by the operator. No AI silently writes factual sports commentary. A claim marked SUPPORTED means **owner attestation**, not machine proof.
5. Output files and DB are stored on the host locally (`data/`, `outputs/`). Back up both; they are not synced automatically. The app is one-user, localhost-only; never expose this server to the internet.

## Optional offline Piper TTS

Install Piper independently, obtain a voice model you have permission to use, and configure:

```powershell
$env:VIRALOS_PIPER_EXE="C:\\Tools\\piper\\piper.exe"
$env:VIRALOS_PIPER_MODEL="C:\\Tools\\piper\\voice.onnx"
$env:VIRALOS_PIPER_MODEL_RIGHTS_OK="1"
```

Then after saving a script call `POST /api/projects/{project_id}/voice/opt-in-piper` from the local API docs. Listen to the generated WAV and verify proper names. Caption timings are still **scene estimates, not word-aligned subtitles**. Piper is **not bundled**; installation/model license and runtime have not been verified on the user's Windows machine.

## Optional approved feed collection

Create a local JSON file like `configs/approved_feeds.example.json`, but replace placeholder URL with an explicitly vetted official RSS URL and set `permission_reviewed=true` only after access/terms checks. Set environment variable `VIRALOS_APPROVED_FEEDS_FILE` to its absolute path **before startup**. No default feed is fetched; unconfigured network access stays off. The backend checks HTTPS URL, port, DNS globals, no redirects, max 256 KiB, max 20 items; DNS preflight alone is not robust network sandboxing, so only trusted owner-configured feed URLs belong in this list. RSS titles are **leads**, never independent fact verification.

## Optional authorized YouTube Analytics – READ ONLY

The owner must have an enabled Google Cloud YouTube Data and YouTube Analytics API project and an OAuth **Desktop App** client. Install separate opt-in dependencies with `pip install -r requirements-youtube-optional.txt`. They are not in the baseline. Use Windows Credential Manager via `keyring` (no plaintext fallback):

```powershell
.\.venv\Scripts\python.exe -m tools.connect_youtube_readonly --local-channel-id LOCAL_UUID --expected-youtube-channel-id UCxxxxxxxx --client-secrets "C:\\Secure\\client_secret.json"
```

The app verifies exact owned YouTube channel ID from `channels.list(mine=true)`, then stores tokens in the OS keyring. A user-initiated POST `/api/youtube/analytics/sync` with JSON `{"local_channel_id":"LOCAL_UUID","start_date":"2026-11-01","end_date":"2026-11-07"}` fetches a day-level report via Analytics API and stores only observed metrics. The connection is **read-only**, cannot upload videos, and does not request monetary metrics. No live account or external API was available in the development environment, so this OAuth integration is **implemented but not live-validated**. Tokens, quota access and account permissions may fail; errors do not fabricate values.

## More important safe behavior

- `m1_project_sources` prevents accidental citation source linkage between projects; pre-M1 sources must be explicitly re-bound if historical project association cannot be established.
- Manual RSS XML forbids DTD and external entity declarations and does not fetch remote content.
- Creative timing includes `spoken_segment=NOT_ALIGNED`, and time-based captions are **not** a substitute for actual transcript alignment.
- Revision, status, claim and locale fingerprint changes invalidate reviews. Stale Piper narration cannot be queued after script revision.
- Reused sports highlights cannot be passed as original work merely by recording a new AI voice. This version provides original diagrams only; no third-party video downloader or watermark remover.
- Read-only analytics reports use returned **column names**, not assumed column index order. Revenue remains missing unless owner explicitly supplies figures (provenance displayed).
- SQLite WAL, local bind, owner control are not remote/SaaS security. OAuth/YouTube is opt-in and needs credential-store/Windows validation.

## How to test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

19 automated checks ran successfully in the isolated Linux development environment, covering migration and basic APIs, FFmpeg preview, source-boundary tests, XML negative input, deterministic scene/caption timeline, owner-localization, stale plan detection, review and export, owner-observed metrics, blocked upload, optional-source/TTS fail-closed and Google Analytics response normalization. This is **not** proof of Windows compatibility or professional YouTube-quality videos.

## Pending prioritized acceptance gates

1. M1: vetted official sports-data sources and license, reproducible claim verification, source independence graph, history and multilingual claims, actual trend observation samples.
2. M2: domain-specific full professional render timeline (text/video/image layers, overlays, sound mix, synchronized voice), real Piper Windows bench, captions timing audit, localization human QA, visual quality human reviews.
3. M3: final release-quality render, owner's explicit rights/legal approval, verified YouTube OAuth account matching, safe remote upload/reconciliation, real Analytics read-only smoke test, corrections and withdrawals.
4. M4: production durability (recover RUNNING jobs after crash, account separation, backup/restore automated tests, security hardening) and monitored GPU provider adapters.

Treat this incremental codebase as an honest, testable checkpoint for the larger Launch and Ultimate v3 roadmap, not as completion of all 12 domain OSs.
