# v0.7 verified-vs-pending checkpoint

| Capability | Evidence | Status |
|---|---|---|
| Prior M0–M2.3 + M3.1 | Regression tests | Preserved working foundation |
| Parallel Hindi/English reviewed variants in same source project | SQLite 011, API, negative tests | Implemented |
| Per-scene independent localized narration and captions | Actual WAV+FFmpeg+SRT English/Hindi samples | Implemented technical previews |
| Native localized on-screen text and basic illustrations | Manual frame inspection | Implemented for launch sport demos |
| Pronunciation dictionary | Explicit owner-reviewed TTS string substitutions | Implemented; real model voice not tested |
| Offline optional Piper model | Safe local file/locale/rights checks | Adapter only; actual model not tested |
| Genuine forced CTC aligner | Optional WhisperX adapter + owner review path | Code/mocks; real model not tested |
| Audiovisual QC | FFprobe, frame variance, RMS, clipping and duration | Objective technical metrics only |
| Natural professional TTS/voice | No licensed model provided | NOT VERIFIED |
| Automatic Hindi-English translation | Requires owner input | NOT IMPLEMENTED |
| Autonomous multi-locale audio dubbing | Owner text + recordings are mandatory | NOT IMPLEMENTED |
| M3.2 offline account/rights preflight | Exact export/channel/intent tests | Implemented |
| M3.2 read-only Google check | Mock OAuth and wrong-channel/privacy tests | Mock-tested; live pending |
| Real private YouTube upload | Previous M3 opt-in integration | Owner OAuth acceptance pending |
| Real Analytics/retention/revenue | Previous M3.1 adapters | Owner OAuth & YPP/processed-data pending |
| Windows i7/32GB CPU | Container Linux only | NOT VERIFIED |
| 12 independently expert directors | Profiles, cricket/NFL renderer | NOT IMPLEMENTED |
| Production quality/actual channel revenue | No owned-channel acceptance metrics | NOT VERIFIED |

**Release classification:** CPU-first development checkpoint; not an autonomous world-class production product, not a live account acceptance certificate.
