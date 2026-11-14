# ViralOS prioritized engineering roadmap and proof gates

**Policy:** One codebase; first own-channel YouTube revenue; CPU-only works on current owner PC. Each milestone requires executable tests, actual media/source artifacts and honest negative cases. No unexplained “complete” badges.

## Next release — real multimodal quality (highest priority)

**A. Voice acceptance:** Test explicit licensed offline Hindi/English Piper/other suitable local voice models on owner PC with stable device, pronunciation glossary, natural timing, pause/emphasis controls, no clipping and an opt-in model path. Measure characters/sec, total RAM and user-rated naturalness; store model+voice license and reproducible output manifest. Do not ship proprietary model weights without authorization.

**B. Genuine alignment/dubbing:** Run a real language-compatible aligner on truth-labelled audio; measure word start/end error, punctuation and mixed Hindi-English/code-switch error; treat proposals as unverified until human correction. Add true translation/dubbing later with claim equivalence, on-screen graphics translation, pronunciation and editorial region-specific review; do NOT call owner-written locale text automatic translation.

**C. Domain visual proof:** Produce Cricket tactical Short, NFL analysis and Technology screen tutorial with original diagrams, source-linked shots, natural narration, readable mobile typography, music/SFX mixing, intentional ending and expert watch-through; compare against documented category benchmarks, not invented retention. Add Newsroom forensic proof next, 12 directors sequentially only with real domain acceptance.

**D. Rights-driven reaction:** Clip-by-clip provenance, owner original/permission/license, claim-to-excerpt necessity, independent criticism rather than superficial narrated reupload, no blanket fair-use assurance, final human legal check.

## M3.2 real owned-account acceptance

On owner's Windows PC (credentials never in Git), implement explicit OAuth and channel identity readback, rights and reviewed-MP4 SHA lock, private upload, remote privacy readback, crash/retry uncertainty reconciliation, Analytics/retention scopes, monetary scope only if authorized/eligible. No public publishing without a separate user decision and quality/legal gate. Record evidence in **private local log**, public repo stores only redacted test results and test protocol.

## M4 reliability & operations

SQLite backups/restores, durable queue + job leasing, deterministic retry policies, outbox/idempotency, concurrency and async worker isolation, cancellation, audit logs, licensing metadata, secret storage, regression/cross-project isolation. Windows CPU and Linux CI smoke tests; GPU capability router and benchmark only after actual hardware available. Optional paid connectors strictly opt-in/cost-tracked; prefer ₹0 recurring.

## M5 deeper research and 12 real expert OS packs

Research source connectors for Cricket/NFL/MLB/NBA and other domains with terms/commercial use verified; primary evidence triangulation, contradiction tracking and independence; deep scripts/creative directors with domain-specific test cases. Newsroom adversarial fact verification/human approval. Expand to 12 specialist domains only when pilot category exports clear editorial tests.

## Measurement and scaling

First 3 pilot videos: Cricket Hindi Short, NFL English long-form/analysis, practical Tech tutorial; then locale variants/Short-long-form comparison; only real channel metrics accepted. Retention curve by scene, CTR/packaging, watch time, creator review effort, render cost, licensing risk, actual YPP eligibility. Launch vs Ultimate are feature configurations of same codebase, not two maintained copies.

### Issue template per feature

**Inputs & evidence** / explicit API and rights / domain×format×locale policy / expected artifact / failure + stale-state behavior / unit+integration+owner test / independent factual and creative QC / performance budget / docs and migration impact. Never close based on unit tests alone where human or live external acceptance is required.


### Issue #4 checkpoint — offline tools implemented; real Windows owner gate OPEN

Preflight, two original synthetic FFmpeg renders, SQLite WAL-safe backup/verify/clean-profile restore, invalidation of earlier final approvals, and cross-platform safety tests are now in `tools/owner_acceptance.py` + `tests/test_owner_acceptance.py`. GitHub CI adds Windows-runner recovery tests. **Not accepted yet:** real owner 8th-gen i7 32GB benchmark, Hindi font and audio checks, restored media paths/rights, complete video watch-through, installed model license/quality checks and local encrypted backups. Follow [operator procedure](WINDOWS_CPU_ACCEPTANCE.md).


### M2.5 checkpoint — evaluation mechanism implemented, actual voice models still blocked

Offline input/quality and word-alignment acceptance harness exists: `tools/audio_acceptance.py`; safe private manifest initializer `tools/create_voice_manifest.py`; Windows helper, cross-platform negative tests and [protocol](M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md). The harness records SHA-bound WAV/voice model/aligner provenance, human correction, word errors/phonetic code-switch and owner voice rating without downloading or running models. **Next real acceptance gates:** obtain owner-reviewed/licensed hi-IN and en-US model files, run actual local TTS+WhisperX (or licensed alternative) on owner's i7/32GB CPU, capture wall-time/peak RAM, ground-truth word errors, human listen-pronunciation scores, 30–60s original pilot videos and retained local evidence. Only then consider M2.5 complete. Issue #2 stays open.

### M2.5 next checkpoint — local Piper runner implemented, owner real-model run still open

An [opt-in Piper CLI harness](M2_5_LOCAL_PIPER_RUNNER.md) creates private SHA-bound RAW/16k WAV and an **UNAPPROVED** QA manifest from an owner-installed hi_IN/en_US model; it measures wall-clock synthesis and safely rejects missing rights, bad model metadata, timeout/silence and unsafe paths. Synthetic CLI and FFmpeg tests are not voice-acceptance proof. **Next:** actual model licence review, trusted Piper install, **real** model inference on owner Windows i7/32GB, memory monitoring and pronunciation/naturalness scoring, genuine local forced-alignment output versus human timings and original 30–60s Cricket/NFL videos. Do not close #2 or permit publishing until all relevant human/external gates pass.

### M2.5 current checkpoint — CPU aligner execution gate added, real-word accuracy gate remains

`tools/run_local_alignment.py` adds an owner-controlled, private and offline-configured process boundary for a locally installed WhisperX-compatible aligner. Model/WAV/script SHA checks, locale gating, token omission rejection, timeouts, copied UNAPPROVED QA manifest, timing and sampled RSS (when available) make real-model acceptance **possible** without falsely declaring it successful. [Operator instructions](M2_5_LOCAL_ALIGNMENT_RUNNER.md). **Next external gate:** owner installs licensed hi-IN and en-US neural voices and align models on i7/32GB Windows; collects true CPU/RAM/elapsed and model version evidence, human-labelled word start/end reference vs candidate MAE/p95, naturalness/pronunciation listener scores, and full 30–60s original Cricket/NFL videos. Nothing closes #2 until these pass. No automatic YouTube actions.
