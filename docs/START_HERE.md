# Start here — complete handoff if the ChatGPT conversation disappears

**Project:** ViralOS, a local-first, multi-channel YouTube intelligence and professional video production platform.

**Owner goals:** first content and revenue from owned channels, not agency/SaaS. Starting themes: Hindi/Hinglish India Cricket, English US NFL, optional practical Technology tutorials. Eventually 10–12 channels with twelve domain operating systems (Newsroom, Science, Technology, Business, Gaming, History, Space, Learning, Sports, Career, Productivity, Culture). Research/verification and cinematic execution must be domain-specialized, sharing infrastructure.

**Hardware:** Intel i7 eighth generation, 32 GB RAM, **no dedicated GPU**. Zero recurring cost where possible. Future RTX 3090 (24 GB), RTX A6000 (48 GB) or other GPU, then perhaps more workers. The application must run with CPU-only, auto, GPU, hybrid strategies and keep data portable. Actual speed/quality not yet measured on owner's Windows PC.

## Critical current reality

The runnable Python FastAPI/SQLite/Pillow/FFmpeg **development prototype** lives in `app/`, `sql/`, `tests/`, `tools/`, `configs/`. It was built incrementally from M0 through v0.7 (M2.4/M3.2). It has real code, tests and technical preview capabilities. It is NOT an autonomous, professional-quality, 12-category YouTube production system. Read `docs/IMPLEMENTATION_STATUS.md` for exact passes/limitations.

**Never confuse:** `spec/combined-v3/` is design documentation including engine registries (144 declared in older work), not 144 implemented engines. `spec/launch-v3/` is a versioned Launch snapshot. `research/` is desk research, not verified video-by-video empirical channel study.

## Repo layout

`app/` FastAPI/backend + Studio logic, local dashboard assets; `sql/` additive 001–012 migrations; `tests/` offline regressions; `tools/` startup, environmental diagnosis, helpers; `docs/` implementation/acceptance/operations guides; `research/` competitor and creator benchmark methodology; `spec/` Launch and Combined v3 snapshots; `examples/` source/demo scripts and small non-video fixtures (generate MP4s locally). Git deliberately excludes generated videos, data, Google OAuth tokens and model weights.

## Rebuild on a fresh Windows PC

1. Install Git, Python 3.12 and FFmpeg/ffprobe; clone `https://github.com/sahilk267/youtube-automation-platform-cgpt.git`.
2. From repo root run `powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1` (creates venv, installs dependencies, diagnostics, runs tests and starts server).
3. Open `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`. By default local-only.
4. Read `docs/WINDOWS_SETUP.md`, `docs/M2_4_M3_2_ENGINEERING.md`, `docs/SECURITY_AND_RIGHTS.md` before enabling optional feeds, Piper, WhisperX or Google adapters.
5. Run `python -m pytest -q`. Any test failure is a blocker; record exact environment, commit and logs. Runtime DB and assets are **not** part of Git; restore them separately if available.

## Current flow

Channel → project → owner-provided approved sources → claim review → script/revision → creative draft → approved voice WAV/optional local Piper → Studio timeline + timed overlays/source cards → technical QC and full human review → hash-bound export → opt-in private YouTube upload adapter → optional authorized Analytics/retention/revenue → feedback.

Source verification is **not autonomous**. Automatic high-quality Hindi/English translation/dubbing is **not implemented**. Live Piper and WhisperX model integration, real YouTube account and owner hardware acceptance are **pending**. No user should equate mock tests with provider verified.

## What to build next

Read `docs/ROADMAP.md`: high priority real offline Hindi/English voice/word alignment acceptance, high-quality local creative pipelines, domain directors, owner supervised OAuth/Analytics, empirically measured retention and time-cost comparisons. Roll out pilot Cricket Short, NFL analysis and screen-recorded Tech tutorial before scaling 12 domains. Avoid premature microservices; prefer durable workers behind a modular monolith.

## Safety & rights

This GitHub repo was PUBLIC when initialized. Do not commit API keys, personally identifiable/account data, private financial details, raw copyrighted sports broadcast footage, local SQLite/voice models or licensed third-party assets. In-app Remix is not broad reupload permission. YouTube reused-content monetization eligibility is separate from copyright clearance. Explicit user approval for legal risks, allegations, branded claims and private uploads; no automated public posting.

## What is known only outside Git

Prior chat had milestone ZIPs and generated demonstration MP4s. Those MP4s are technical examples (sometimes fictional inputs and eSpeak voices), not definitive training/evaluation targets. Git includes reproducible demo scripts where possible; do not rely on temporary sandbox links. If local DB, owner OAuth or proprietary footage/model assets are lost, they cannot be recreated from the public repo.


### Windows acceptance and clean-profile recovery

Run the [Windows CPU & private SQLite recovery checklist](WINDOWS_CPU_ACCEPTANCE.md). The DB-only backup excludes media and OS credentials, restore refuses overwrites and invalidates old final exports, and a Windows GitHub CI runner does **not** prove the owner's PC performance. Preserve local private media separately.


### Offline M2.5 voice and alignment acceptance (partial)

The optional [M2.5 operator guide](M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md) explains how to create a **private unapproved manifest** for an existing Hindi/English narration WAV and how to compare real local aligner output with human-reviewed word timings. Code: `tools/create_voice_manifest.py`, `tools/audio_acceptance.py`, `tools/voice_accept_windows.ps1`. Do not upload real WAVs, token-level word transcripts, proprietary model files or audio/metadata reports to this public repository. No real model inference or naturalness validation has happened on the owner's PC.

### Next owner action — local Piper live model acceptance

After the M2.5 evaluator, the new opt-in [Piper CLI runner](M2_5_LOCAL_PIPER_RUNNER.md) bridges an **owner-installed/licensed** Hindi/English voice model to SHA-bound private audio, wall-time and an unapproved manifest. Start with `tools/run_voice_local_windows.ps1`, keep all voice weights and media outside the public Git repo. The GitHub synthetic audio test is **not** proof of a neural voice model, naturalness, forced alignment, genuine owner Windows performance or publication readiness. [M2.5 acceptance protocol](M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md).

### Next owner action: genuine local word alignment (unapproved proposals)

After generating an owner-controlled private Piper sample, follow [M2.5 local alignment operator guide](M2_5_LOCAL_ALIGNMENT_RUNNER.md) to execute an **already installed** local WhisperX CPU aligner with its reviewed model and exact private script. The runner makes candidate word boundaries, a new `voice-evaluation-WITH-PROPOSAL-UNAPPROVED.json`, and a redacted technical report outside Git; human ground-truth timing/listening remains mandatory. Optional `psutil` measures sampled peak child RSS if installed; without it memory is explicitly unmeasured. Do not call this feature proof of real hi-IN/en-US model inference until actual owner-device logs and human checks exist.
