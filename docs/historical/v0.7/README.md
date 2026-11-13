# ViralOS Launch M0–M3 + M2.4 / M3.2 v0.7 — CPU Development Checkpoint

This ZIP contains **runnable Python/FastAPI application code** plus the canonical Launch v3 specification snapshot, Windows scripts, optional research and narration connectors, a diagnostic dashboard, SQL migrations, private export workflow and tests.

**This is an honest engineering checkpoint, not a complete AI autopublisher or professional video studio.** The exact capabilities, limitations, Windows instructions and opt-in Google Analytics setup are in [docs/IMPLEMENTATION_M1_M3.md](docs/IMPLEMENTATION_M1_M3.md).

Quick start (Windows, Python 3.12, FFmpeg installed):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
```

Open http://127.0.0.1:8000 . Python API docs: http://127.0.0.1:8000/docs .

Modules: `app/main.py` legacy working M0 workflow; `app/expansion.py` new M1/M2/M3 endpoints; `app/intelligence.py` bounded feed/claim/timeline logic; `app/source_connectors.py` explicit approved RSS fetch; `app/tts.py` optional Piper; `app/youtube_analytics.py` optional read-only OAuth/Analytics; `app/renderer.py` original CPU technical render. `sql/004_m1_m3.sql` contains additive durable records.

**Legacy upload and all PUBLIC publishing are disabled.** A new M3 PRIVATE-only upload adapter is available after a separate human final-video review, verified account OAuth, and opt-in. No actual live upload has been tested. M2 Studio PREVIEW renders are watermarked and cannot be sent. Users must not treat an owner-attested claim or downloaded RSS title as independently verified.

## M2 CPU Studio v0.3 — new in this checkpoint

The old working M0–M3 endpoints, scripts and schema are retained. The new `app/studio_contracts.py`, `app/studio_routes.py` and `app/studio_render.py` provide an **actual CPU-rendered overlay/timeline studio prototype**, SQL migration `005_studio.sql`, rights-attested owner assets, owner-timed captions, WAV duration guard and QC manifest. The dashboard contains the **M2 Studio Director** panel.

Read [docs/M2_STUDIO_IMPLEMENTATION.md](docs/M2_STUDIO_IMPLEMENTATION.md) and [docs/STATUS_M2.md](docs/STATUS_M2.md). Technical video previews remain **NOT PUBLISH READY**. No automatic web footage ingestion, dubbing, GPU generation or uploads are enabled.

## M2.1 Creative Director + voice timing — new

The `M2.1 Automatic Creative Draft` panel now generates a first editable **deterministic script-based** HOOK → EXPLANATION → PAYOFF scene plan, with no generated sports facts. Upload narration WAV clips for each sentence/scene, or optionally synthesize locally with a licensed and matching-language Piper installation. The system measures individual WAV durations, composes an immutable per-plan voice track and produces **measured segment-level (not word-level)** caption timing. It also accepts owner-reviewed target-locale scripts, with locale-specific visuals/text and separate voice assets. A measured scene-boundary SRT is downloadable, and only unambiguous existing script claim links are transferred (not independently verified). Rendering is still CPU/Pillow/FFmpeg and not publish ready.

**Full instructions:** [docs/M2_1_DIRECTOR_IMPLEMENTATION.md](docs/M2_1_DIRECTOR_IMPLEMENTATION.md) and [docs/STATUS_M2_1.md](docs/STATUS_M2_1.md).

**Optional Piper configuration** on Windows PowerShell before starting the app:

```powershell
$env:VIRALOS_PIPER_EXE = "C:\path\to\piper.exe"
$env:VIRALOS_PIPER_MODEL = "C:\path\to\licensed-voice.onnx"
$env:VIRALOS_PIPER_MODEL_RIGHTS_OK = "1"
$env:VIRALOS_PIPER_LOCALE = "en-US" # MUST match the project's Director draft
```

No model is bundled or downloaded automatically. The app will refuse synthesis if the model, license attestation or locale is absent. Tests include a mocked Piper adapter, not a live installed model test.

`sql/006_m21_director.sql` is additive to all previous databases (001–005 migrations retained). The full test suite now includes director, locale, source isolation, audio hash and real-render tests. Run `python -m pytest -q` and `python tools/verify_package.py` after extraction. This is development software, not yet tested on the target Windows PC.

## M2.2 and M3 owner-reviewed final-video path (new)

Read **[docs/M2_2_AND_M3_PRIVATE_IMPLEMENTATION.md](docs/M2_2_AND_M3_PRIVATE_IMPLEMENTATION.md)**. This update adds source/shot creative QA, original CPU tactical-motion graphics, per-word **owner-reviewed timestamp** VTT import (NOT automated alignment), human-approved final video exports, and optional strictly PRIVATE YouTube upload with separate OAuth desktop CLI. Default upload state OFF. Existing source/evidence research, video studio and read-only analytics remain intact.

Run `python -m pytest -q`, then `python tools/verify_package.py`. Production approval, copyrighted footage clearance and YouTube monetization are **not** guaranteed.


## M2.3 evidence-to-screen + optional offline ASR; M3.1 audience/revenue learning

New incremental modules: `app/production_m23.py`, `app/alignment_m23.py`, `app/analytics_m31.py`; additive migrations `009_m23_intelligence.sql` and `010_m31_analytics.sql`; optional Google monetary desktop OAuth CLI; tests; updated dashboard panels 14–17. Original evidence cards are generated locally from *owner-reviewed source context*, not from unlicensed media. Studio video provenance invalidates if a linked reviewed claim/source changes. **This is not independent fact verification.**

Word-timestamp proposals are opt-in `faster-whisper` **ASR estimates** for user-installed local models, never automatically accepted; the final owner-reviewed word-VTT workflow remains unchanged. This is NOT acoustic forced alignment, natural TTS or automatic translation. Model binaries are not bundled and the real ASR model was not run in delivery tests.

M3.1 adds opt-in **authorized monetary estimates**, owned-video scene-retention mapping, and owner-attested `REMOTE_UNKNOWN` private-video reconciliation. None of these integrations used live Google credentials in delivery tests. Existing upload remains **PRIVATE ONLY** and OFF by default; all revenue metrics remain unavailable until the owner authorizes appropriate scope and real Google data is returned.

**Read first:** [M2.3 / M3.1 detailed engineering guide](docs/M2_3_M3_1_ENGINEERING.md), [verified-vs-pending status](docs/STATUS_M2_3_M3_1.md). Run `python -m pytest -q` and `python tools/verify_package.py`. On Windows run `tools/start_windows.ps1`; binding is `127.0.0.1` only. Example: `examples/m23_evidence_demo.mp4` is fictional technical demonstration, not real sports evidence or professional final content.

---

## v0.7 additive milestone: M2.4 + M3.2

This **same working Launch codebase** now has additional `m24` and `m32` API modules and SQLite migrations `011–012`. Existing migration history and current source spec are preserved. The dashboard has new **M2.4 Multilingual Director** and **M3.2 Read-only Acceptance** panels. 

- M2.4 creates **separate, independently reviewed hi-IN and en-US project variants**, supports per-scene owner WAV, reviewed pronunciation cues, optional license-approved local Piper, original Hindi/English screen labels and individual MP4/SRT technical previews. Two real Linux/FFmpeg demo files are in `examples/m24_*`. This is **not automatic translation, voice cloning or professional dubbed video delivery**.
- Optional locally installed WhisperX CTC adapter creates a **genuine forced-alignment proposal** only if the owner provides a compatible local model; it has **not** been exercised with a real model in this delivery. A human must review words and timings. See `docs/M2_4_M3_2_ENGINEERING.md`.
- M3.2 adds **pre-upload acceptance checks**, exact channel/approval binding, blocker reporting, read-only remote verification opt-in, private-video readback and `REMOTE_UNKNOWN` protection. Owner's Google OAuth channel not available in this environment; real live acceptance remains pending.
- Demo speech uses robotic eSpeak *only as a synthetic fixture*. It is not a demonstration of natural Hindi or English voice quality. The source video is a fictional field-position lesson, not a real cricket event.
- No new public-upload workflow; no credential JSON or model weights are bundled. See `docs/STATUS_M2_4_M3_2.md` for a precise gap ledger.

`python -m pytest -q` covers all old and new modules. `python tools/verify_package.py` checks ZIP integrity. The Windows startup script remains bound to localhost and requires Python 3.12 and FFmpeg installed.
