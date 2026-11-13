# ViralOS M2.3 + M3.1 | Actual engineering contract

**Build date:** 2026-11-12. **Runtime mode:** local-first Windows-compatible CPU architecture. **This is a research/production engineering checkpoint, NOT a finished 12-domain creator platform.**

## What is real and testable

### M2.3: reviewed evidence-to-screen cards

1. Record source with `/api/projects/{pid}/sources`. The record is **owner supplied**, not independently verified by a website fetch. Store a claim linked to its `source_version_id`, and link the exact claim quote to the current script.
2. Verify the full original context yourself, then mark the claim `SUPPORTED`. Mark the supporting evidence edge as reviewed using `POST /api/projects/{pid}/m23/evidence-edges/{edge_id}/review` with reviewer, source-and-locator checked, explanation. This stores an **operator attestation**, not a machine-proven fact.
3. `POST /api/projects/{pid}/m23/evidence-cards` accepts `claim_id`, `source_version_id`, and explicit attribution/rights attestation. It writes a reproducible original **PNG source card** using the verified claim text, source publisher and URL hostname; it does **not** download copyrighted video frames/images.
4. Card's asset ID can be used as `RIGHTS_APPROVED_STILL` or `IMAGE_INSERT` in a typed Studio timeline. The web dashboard can insert the card as an editable image overlay in Studio JSON. The image endpoint exposes only provenance-valid cards in the exact project.
5. The final-video approval fingerprint checks image hashes, source-version hashes, claim status, evidence-edge reviewer and timestamps. If a related claim is changed/reviewed again, the card becomes stale and review/export blocks. Source and screenshot context must still be independently checked by the owner before publishing.

### Optional offline ASR: word-timestamp proposals (NOT true forced alignment)

**Optional installation, not required for normal CPU editor:**

```powershell
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-asr-optional.txt
$env:VIRALOS_FASTER_WHISPER_MODEL_DIR = 'C:\models\a-local-faster-whisper-model'
$env:VIRALOS_WHISPER_MODEL_RIGHTS_OK = '1'
$env:VIRALOS_OFFLINE_ASR_OPT_IN = '1'
```

**The model must already exist on the owner's disk, have an authorized license, and be capable of handling the selected locale.** ViralOS does not download model weights. The adapter accepts only `en` and `hi` in Launch, forces CPU int8, and sets Hugging Face offline environment variables. Real installed-model quality/performance **has not been measured**.

Use an assembled M2.1 Director Studio plan (voice already measured and bound). `POST /api/projects/{pid}/m23/plans/{plan_id}/asr-proposal` generates a candidate word-timestamp JSON with a transcript-match flag. If model output disagrees with recorded narration, it remains a proposal and requires corrected tokens. `POST /api/projects/{pid}/m23/alignment-drafts/{draft_id}/approve` requires the owner to inspect **all** words and timings. Only exact, scene-bounded, non-overlapping corrected timestamps can be bound into the existing M2.2 reviewed word-VTT workflow.

This uses the *faster-whisper* ASR word-timestamp facility, not an external phoneme forced-aligner. It cannot guarantee speech-correct transcript or word alignment by itself. It is not a professional dubbing system.

### Locale review

The existing M2.1 pipeline accepts reviewed original/translated scripts, distinct approved voice assets, and measured per-scene lengths. `GET /api/projects/{pid}/m23/plans/{plan_id}/locale-audit` reports locale mismatches and missing captions. **Translation, localized graphic redesign and proper-name review remain human tasks.** Piper requires an operator-installed, rights-checked language-compatible voice. The optional ASR runtime does not create voice or translate text.

### CPU rendering and production-time measurement

M2 Studio now records actual monotonic `render_wall_seconds` in FFmpeg QC reports. This measures work **on the computer running that specific job** and should not be transferred to the target i7/32 GB machine as an estimate. Real scene cards are letterboxed to preserve the text and attribution instead of cropping supporting evidence.

Run the original illustrative evidence sample:

```powershell
# Only if eSpeak and FFmpeg/FFprobe are installed; no remote source is fetched
& '.\.venv\Scripts\python.exe' examples/create_m23_demo.py
```

The packaged demo `examples/m23_evidence_demo.mp4` is 12 seconds at 540×960 with H.264/AAC and synthetic eSpeak narration. The source is deliberately **fictional and marked DEMO**. Neither facts nor publication rights for any real source are inferred.

### M3.1: separate estimated monetization metrics

YouTube Analytics has distinct scopes for read-only activity and monetary reports. The previous read-only connector **does not** prove revenue access. Authorize monetary reports *only on the owner's Windows device*:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-youtube-optional.txt
& '.\.venv\Scripts\python.exe' tools/connect_youtube_monetary.py `
  --local-channel-id <LOCAL_CHANNEL_ID> `
  --expected-youtube-channel-id <UC_OWNED_CHANNEL_ID> `
  --client-secrets 'C:\path\to\google-desktop-oauth.json'
$env:VIRALOS_ENABLE_MONETARY_SYNC = '1'
```

These commands are user-action only; no credentials are shipped. OAuth secrets stay in an OS credential store through `keyring`. Income API endpoint `POST /api/m31/monetary/sync` requests estimatedRevenue/estimatedAdRevenue, validates exact linked channel and observed dates, stores `YOUTUBE_ANALYTICS_MONETARY_OAUTH` rows separately from owner-entered estimates, and labels them **estimates rather than finalized earnings**. No expenses/profit/tax/currency-conversion are fabricated. `GET /api/m31/channels/{channel_id}/earnings` is safe and offline; if no actual data, it returns empty rows.

### M3.1: scene-level audience learning

YouTube Analytics can return `elapsedVideoTimeRatio`, `audienceWatchRatio` and `relativeRetentionPerformance` for a **specific owned video**. Owner must authorize read-only Analytics using the existing `tools/connect_youtube_readonly.py` and enable `VIRALOS_ENABLE_RETENTION_SYNC=1`. `POST /api/m31/retention/sync` requires an existing `UPLOADED_PRIVATE` video linked to a specific approved final export, exact owner channel and confirmed OAuth credentials; it stores only observed samples. The original timeline's shot durations map sample positions to scenes; per-scene observed first/last values are **descriptive, not proof that a specific scene caused viewer drop-off**. Values above 1 are allowed (rewatches). Empty reports are shown as unavailable, not as zero retention. Stored report: `GET /api/m31/exports/{export_id}/retention`.

### M3.1: crash-safe remote unknown recovery

Prior M3 marks uncertain upload outcomes `REMOTE_UNKNOWN`, never blindly uploads twice. `POST /api/m31/private-upload/intents/{intent_id}/reconcile` is disabled by default. With `VIRALOS_ENABLE_REMOTE_RECONCILE=1`, the owner supplies an existing YouTube video ID after personally inspecting it in YouTube Studio. It then verifies the exact authenticated channel, remote video ID and remote `private` privacy status; only then may it transition to `UPLOADED_PRIVATE`. **The remote MP4 is not cryptographically compared to the local file**; owner attestation remains required.

## Explicit no-network and validation facts

- The code was locally regression-tested in a Linux runtime with FFmpeg and deterministic/mock API responses. No live YouTube OAuth, channel upload, revenue or retention fetch happened in this delivery.
- No local ASR weights are included. The optional faster-whisper runtime is **mock-tested**; no live trained model ran in this delivery.
- No autonomous external-news investigation, broadcast footage rights, full-screen synthetic voice performance, automatic native multilingual dubbing, GPU rendering, or all-12-category creative expertise is claimed.
- Runtime bound to `127.0.0.1`; treat dashboard as a single-user developer tool. Do not expose it on LAN or public Internet. Back up `data/` and `outputs/` locally (no remote backup system included).
- Tests: `python -m pytest -q`; package hashes `python tools/verify_package.py`; JS syntax `node --check app/static/app.js` if Node installed.

## Authoritative external references (verified November 2026)

- YouTube Data API `videos.insert`: https://developers.google.com/youtube/v3/docs/videos/insert
- YouTube `status.privacyStatus` defaults if omitted: https://developers.google.com/youtube/data/reference/rest/v3/videos
- YouTube Analytics `reports.query` scopes: https://developers.google.com/youtube/analytics/reference/reports/query
- Video-level audience retention: https://developers.google.com/youtube/analytics/channel_reports
- WhisperX forced-alignment limitations if considering future genuine forced alignment: https://github.com/m-bain/whisperX
