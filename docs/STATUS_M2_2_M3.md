# ViralOS engineering checkpoint M2.2 + M3 / 2026-11-12

## VERIFIED LOCALLY IN LINUX

- Preserved all earlier Python/FastAPI/SQLite migrations and tests (M0–M3, Studio, M2.1).
- Additive SQL migrations `007_m22_creative.sql` and `008_m3_publishing.sql` pass migration and regression tests.
- `app/creative_m22.py` implements per-project visual/claim audit and human-reviewed word-level VTT import, not automatic ASR alignment.
- Domain creative profiles for all 12 canonical OS with distinct subprofiles for five sports; **only Cricket/NFL graphical renderer is implemented**.
- Original animated Cricket/NFL tactical markers now move at shot-frame timestamps; movement is labelled illustrative.
- Human reviewed Studio preview can be re-rendered into final local MP4 without preview watermark. Integrity fingerprints bind review, source/claim status, asset rights, script revision, voice and plan. `OWNER_APPROVED_FINAL_EXPORT` is NOT a YouTube policy/legal endorsement.
- New Google OAuth **private-only** upload adapter code, mock-verified response path and network-uncertainty no-retry state machine; separate OS-keyring desktop auth helper.
- Existing optional read-only YouTube Analytics adapter retained; live remote calls unverified.
- Dashboard panels let owner audit latest Studio render, attest full watch-through, download approved final MP4 and prepare a PRIVATE upload intent.
- Real rendered CPU preview and PNG screenshot included in `examples/`; synthetic eSpeak voice demonstration, **not professional narration**.
- `python -m pytest -q`, `node --check app/static/app.js`, `python tools/verify_package.py` required; test output and current environment noted in `BUILD_REPORT.json`.

## STILL UNSUPPORTED / NOT VERIFIED

- No autonomous full 12-domain video expertise; category profiles alone are not running specialist agents.
- No independent real-world source fact checking, rights determination, sports broadcast license, professional music/voice quality certification or originality guarantee.
- No full automatic translation, natural localized dubbing, lip synchronization or automated word-level forced alignment. Imported word timestamps are human-verified.
- No remote YouTube account/OAuth, upload or Analytics verified in this environment. Credentials not included. `VIRALOS_ENABLE_PRIVATE_UPLOAD` defaults OFF.
- No public publishing, scheduled upload automation, viral/revenue guarantee, subscriber/retention validation or commercial footage downloader.
- Exact Windows i7 8th-gen/32GB performance and future CUDA/3090/A6000 execution remain untested.

## SECURITY RULES

1. Bind to 127.0.0.1; do not expose dev dashboard over network or Internet. No public multi-tenant security claim.
2. Never store Google refresh tokens or client secrets in SQLite, source code, ZIP or logs; OS credential store required.
3. Only the owner can connect his/her own YouTube account through real OAuth browser consent; API checks exact channel ID before private upload.
4. Never upload public automatically. Private upload needs a reviewed local MP4, separately confirmed metadata and private-upload environment flag.
5. Any `REMOTE_UNKNOWN` outcome must be manually checked in YouTube Studio before a new upload; no implicit retry or dedupe bypass.
6. Never assume rights due to a downloaded URL or green-screen face/crop/voiceover. Reused-content monetization and copyright are independent.

## Next measurable gates

- Validate Windows installation with the owner's exact PC and fonts, FFmpeg playback, CPU time and memory.
- Owner reviews sample video honestly: editing/voice/overlay factual correctness, readability and creative usefulness.
- Owner connects OAuth and runs one supervised private upload. Independently confirm private status in YouTube Studio, compare metadata, and test revocation/failure recovery.
- Verify actual Analytics report retrieval, observe video measurements and correct any data source attribution gaps.
- Add tested local word aligner / ASR, enhanced TTS and licensed footage handling with controlled reviews; no silent model downloads.
- Benchmark domain creative policies against real video samples before calling any domain "expert".
