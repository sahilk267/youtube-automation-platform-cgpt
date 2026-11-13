# ViralOS Launch M2 — CPU Studio v0.3 (engineering checkpoint)

**Scope:** Additive implementation to existing M0/M1/M3 app. **Not full cinematic AI/video production and not approved for public YouTube publishing.** This release deliberately does not change the canonical `spec/ViralOS_Launch_v3/` archive.

## What actually works

- Pydantic-validated studio video plan with 2–12 shots; each shot 1.2–12 s, 90 s total max, first HOOK and final PAYOFF/CTA.
- Shot visual types: original cricket/NFL diagram, original solid graphics, or user-uploaded and owner-attested PNG/JPEG still. No third-party broadcast clip ingestion.
- Independent timed text overlays (LABEL/STAT/CALLOUT) plus owner-approved still IMAGE_INSERT overlays, timed within each shot with fade/slide entrance and exit; same-anchor overlaps rejected.
- Optional globally timed **owner-authored** caption cues; non-overlap and duration bounds checked. This is **not** word-accurate forced alignment.
- Pre-existing owner narration WAV (upload using project Voice form) with strict duration matching (±450 ms). Optional WAV music with explicit origin/license/owner rights attestation, mixed at conservative 0.08 gain under narration. No automatic music discovery or license clearance.
- CPU-only Python/Pillow frame compositor streams RGB frames to FFmpeg H.264 (20 fps; Short 540×960; Long 960×540), then adds AAC audio if present. Font resolution uses installed system fonts (no font bundles).
- Persistent SQLite migration 005, plan hash, asset integrity hashes, durable queue (interrupted renders can be manually retried from the beginning), stale/duplicate detection, render artifact/manifest/technical QC report.
- Local web dashboard: edit plan JSON, upload optional still/music, queue/render, preview, technical QC.
- Negative tests for missing rights, wrong project assets, overlapping captions, stale voice/job, invalid timing and narration duration.

## Running on Windows (i7 8th Gen, 32GB RAM, no GPU)

1. Install Python 3.12, FFmpeg and FFprobe on PATH; ensure a Unicode-capable Hindi/English font such as Nirmala UI is installed. Check `python --version`, `ffmpeg -version`, `ffprobe -version`.
2. Extract ZIP preserving directory structure; from project root run `powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1`.
3. Open `http://127.0.0.1:8000` and create channel → project → **manual script**. Optionally add source/claim records. Studio plans require a current script.
4. In **M2 Studio Director**, load sample and edit JSON. Set shot timings, text and overlays. To add a timed supporting image, use an overlay with `style: "IMAGE_INSERT"`, `image_asset_id` from your STILL upload, `text` as visible origin/context label, and an owner-selected time/anchor. Every explicit factual claim must be linked to a claim in the current script; no automatic verification.
5. To use licensed still/audio, complete the relevant upload form; paste returned `asset_id` into `shots[].visual.asset_id` or `music_asset_id`.
6. For narration, upload an owned/authorized WAV into existing Voice form, with duration matching entire video within ±0.45 s. For separate locales, localize `headline`, `overlays`, `captions`, use a matching language narration and attest review.
7. Save plan, queue, render next; preview MP4 and examine QC report. No YouTube publishing endpoint has been enabled.
8. Run `python -m pytest -q`, check `/health` and `/api/studio/capabilities`; a real Windows smoke test on your machine is still pending.

## API overview

| Route | Purpose |
|---|---|
| GET `/api/studio/capabilities` | Honest feature availability |
| GET `/api/projects/{id}/studio/example` | Editable typed plan example |
| POST `/api/projects/{id}/studio/assets/still` | Multipart image + origin + license_note + rights_attested |
| POST `/api/projects/{id}/studio/assets/music` | Multipart WAV + origin + license_note + rights_attested |
| GET `/api/projects/{id}/studio/assets` | Local project assets only |
| POST `/api/projects/{id}/studio/plans` | Validate and persist typed plan; invalidate old review by project revision |
| GET `/api/projects/{id}/studio/plan` | Latest plan |
| POST `/api/projects/{id}/studio/queue` | Idempotently queue current plan+script+media hash |
| POST `/api/studio/run-next` | Synchronous local worker (development-only) |
| GET `/api/studio/reports/{id}` | Persisted technical QC + manifest |
| GET `/api/studio/previews/{id}` | Local MP4 technical preview |

Sample plan shape:

```json
{
  "locale":"en-US", "locale_reviewed":false, "music_asset_id":null,
  "shots":[
    {"role":"HOOK","duration_ms":3000,"headline":"Why did the formation change?","visual":{"kind":"ORIGINAL_DIAGRAM"},"claim_ids":[],"overlays":[{"text":"Look at the position","start_ms":200,"end_ms":2400,"anchor":"CENTER","style":"CALLOUT"}]},
    {"role":"PAYOFF","duration_ms":3000,"headline":"The open lane is the key","visual":{"kind":"ORIGINAL_DIAGRAM"},"claim_ids":[],"overlays":[{"text":"Original tactical illustration","start_ms":250,"end_ms":2450,"anchor":"CENTER","style":"STAT"}]}
  ],
  "captions":[], "captions_provenance":"NOT_PROVIDED"
}
```

## Limits and necessary next iterations

- This is **original diagram + timed layer generation**, not photorealistic video generation or footage-aware editing. No green-screen remix tool or third-party clip downloader.
- No automatic fact verification: owner-supplied claims/reviews remain manual attestations; script facts and visual diagrams must be checked by humans.
- No automatic translation, speech transcription, speech-to-word alignment, lip sync or native voice-language evaluation. Locale-specific script and captions are provided by the operator.
- The sample visualizer shows *illustrative* field placements, **not actual game data** or footage. Any numerical stat shown is authored, not validated by renderer.
- Rights/license records are owner attestations, not independent legal clearance. The application does not guarantee YouTube Partner Program monetization, fair use or absence of Content ID matches.
- Ingestion, voice detection and FFprobe QC cannot judge creative excellence, scientific accuracy or human audible speech. Low-energy WAV triggers an explicit warning.
- Runtime may be slow on CPU; per-job rendering uses a synchronous local worker and has not been throughput-benchmarked on i7 8th-gen Windows.
- `ViralOS Launch v3` specification remains source of truth for longer-term requirements; this M2 slice is an isolated additive implementation. Future migration must retain engine/source IDs and avoid duplicate publishing implementations.

## Release gate

All automated tests pass in build environment, but **Windows device test, independent legal review, fully watched representative video, factual editing review, speaking-audio assessment and audience trials are missing.** Status remains `TECHNICAL_STUDIO_PREVIEW`, `publish_ready=false`.
