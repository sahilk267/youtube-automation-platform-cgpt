# ViralOS recovery-first changelog

## 2026-11-13 — Canonical GitHub source import

- Bootstrapped public repository and imported v0.7 CPU-first runnable FastAPI/SQLite/FFmpeg prototype, Launch v3 and Combined v3 specifications, competitor research, 120-channel desk research and safety/Windows/agent-recovery docs.
- [PR #1](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/1) merged; [main-branch CI](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43341866207) 82 offline tests passed.
- Source transfer audit: 573/573 imported file Git blob SHA1 hashes matched, 574 initial files including README; no proprietary MP4, model weights, tokens or SQLite data committed.
- README and [CURRENT_CHECKPOINT](CURRENT_CHECKPOINT.md) record real capabilities, historical claims and unmet acceptance gates. Created 10 specific tracking issues #2–#11.

## 2026-11-13 — Exact Ultimate v3 edition recovery

- [PR #12](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/12) merged; [CI](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43344067226) 83 offline tests passed.
- Ultimate design differs from Combined v3 in six changed files plus one Ultimate-only and one Combined-only; new `spec/ultimate-v3-overlay/` stores edition differences, `tools/materialize_ultimate.py` reconstructs and checks original 250 files via SHA-256. Total readable Git files: 586 before this changelog/doc update.
- No extra fork of runtime, no real voice/YouTube account acceptance and no professional finished-video claim.

**Following changes** must update both implementation status and applicable test/hardware/rights gates. Recover from main branch, read [START_HERE](START_HERE.md), [AGENTS](../AGENTS.md), [ROADMAP](ROADMAP.md), and Issues.

### 2026-11-14 — M2.5 opt-in local Piper execution (partial, owner acceptance pending)

- Added `tools/run_local_piper.py` and Windows PowerShell helper: owner-selected trusted local Piper executable + language-matched hi_IN/en_US model + private UTF-8 script -> raw audio, FFmpeg 16-kHz WAV, SHA/provenance, wall-clock time and **UNAPPROVED** evaluation manifest.
- Added synthetic executable/FFmpeg and negative tests; no model weights or owner media committed. Guide: `docs/M2_5_LOCAL_PIPER_RUNNER.md`.
- [PR #15](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/15) merged with commit `80e84d58a736ca1b957a1343648ffa40eff9cdbd`; [CI run](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43570844894) verified 127 Linux tests and 41 Windows focused tests (one skipped, one deselected). Details in `docs/CURRENT_CHECKPOINT.md`. This is *not* independent trained-model inference, voice quality, real alignment, Windows owner-device acceptance or YouTube publishing. Issue #2 remains OPEN.

### 2026-11-14 — M2.5 supervised local alignment operator, partial milestone

- Added optional separate CPU worker around the existing WhisperX adapter: exact-script binding to owner Piper WAV, local model-tree SHA verification, offline environment, fail-closed missing/mismatched Hindi/English words, timeout, optional sampled process memory and three PRIVATE unreviewed outputs.
- Added Windows wrapper, [operator guide](M2_5_LOCAL_ALIGNMENT_RUNNER.md) and 20 synthetic tests (one real child process with a *synthetic* library shim).
- Real Hindi/English models, independent model licence checks, ground-truth alignment accuracy, owner Windows CPU/RAM, human video quality and Google publishing remain **unverified**. [PR #16](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/16) merged as `3516b5b27b5df06e2e781474624f485367042173`; [CI 43589799336](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43589799336) verified 147 Linux passes and 60 Windows passes (2 skipped, 1 deselected). See Issue #2 and `docs/CURRENT_CHECKPOINT.md`.
