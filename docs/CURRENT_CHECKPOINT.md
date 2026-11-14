# ViralOS — verified GitHub checkpoint (2026-11-13)

**This is the canonical continuation record if the chat is lost.** Read [START_HERE](START_HERE.md), [AGENTS](../AGENTS.md), [Architecture](ARCHITECTURE.md), [Roadmap](ROADMAP.md) and [Implementation truth table](IMPLEMENTATION_STATUS.md).

## Repository and recovery

- GitHub: https://github.com/sahilk267/youtube-automation-platform-cgpt
- Default branch: `main`; **public** on 2026-11-13. Do not commit user secrets/media/analytics.
- Import PR: https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/1 — **MERGED**.
- Import commit: `22a6a2c39829f6483cc0f5d88b89fe0c2e078f27`; merge commit: `1c3ae1784ff59c481350e6635af5464047d4a31a`.
- Tree: **574 text/source/spec/research files** (573 imported from local approved non-sensitive source + bootstrap README). File-by-file Git blob SHA1 comparison: **573/573 matched**, zero missing or mismatched.
- Post-merge GitHub Actions Linux CI: https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43341866207 — **SUCCESS, 82 passed, 1 warning in 30.40 seconds**. Also Python compilation, dashboard JS syntax and high-confidence secret scan passed. Do not mistake this for Windows/real model/YouTube acceptance.
- Separate Combined v3 structural validation on importer workspace: `PACK COMBINED DOMAINS 12 ENGINES 144 SCHEMAS 48 GAP_CHECKS 30; VALIDATION PASS` and `V3_SCHEMAS 15 DIRECTORS 12 FORMAT_PACKS 9 OPERATIONS 18 GOLDENS 29 NEGATIVE_CASES 25 CHANNEL_REFERENCES 120; V3 SPEC VALIDATION PASS`. **These are schema/document validators, NOT 144 running engines, research verification or professional quality tests.**

## Actual source and support

`app/` FastAPI/SQLite research-to-preview, creative director drafts, multi-locale reviewed variants, evidence-to-screen, technical-video QC, private upload and analytics adapter code.

`sql/` additive migrations through 012. `tests/` offline regressions. `tools/` Windows launcher and local diagnostics. `examples/` source scripts and small text fixtures; generated MP4/PNG excluded from Git.

`spec/launch-v3/` historical Launch v3 spec snapshot and `spec/combined-v3/` long-term combined/Ultimate architecture. They are NOT two runtime forks; runtime remains in root `app/`. `research/` competitor comparisons, 120 channel desk-research profiles, 600-video future sampling methodology. See [research limitations](RESEARCH_STATUS.md).

## Explicitly incomplete acceptance

- Windows i7 8th-gen/32GB/no-GPU performance: **NOT TESTED on owner PC**.
- Natural hi-IN/en-US licensed offline voice model: **NOT live validated**.
- Model-backed word alignment (WhisperX) and automatic professional translation/dubbing: **NOT demonstrated**.
- 12 genuinely expert domain audiovisual directors: **NOT implemented end-to-end**.
- Automated independent fact verification and rights-cleared real sports footage: **NOT demonstrated**.
- Actual owned Google OAuth, supervised private upload, retention/estimated revenue scope verification: **NOT live tested**.
- World-class finished videos, YPP approval, user retention improvement and actual revenue: **NO ACCEPTANCE EVIDENCE**.

## Issues ready for future agent

- [#2 Real voice / alignment](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/2)
- [#3 Owned YouTube live acceptance](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/3)
- [#4 Owner Windows CPU / recovery](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/4)
- [#5 GPU capability / workers](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/5)
- [#6 Real research source verification](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/6)
- [#7 Domain creative directors](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/7)
- [#8 Rights-aware reactions](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/8)
- [#9 Empirical 600-video competitor study](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/9)
- [#10 Owned three-video pilot and real metrics](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/10)
- [#11 Public/private governance and branch protection](https://github.com/sahilk267/youtube-automation-platform-cgpt/issues/11)

## Recommended next work order

1. Owner Windows fresh clone → local tests and basic CPU export (#4).
2. Verified licensed real offline hi-IN/en-US voice + actual word alignment and localization QC (#2).
3. Source-proven, original visual Cricket/NFL/Technology pilot, rigorous human QA (#6, #7, #10).
4. Supervised private YouTube OAuth/Analytics acceptance (#3).
5. Scale licensing/reactions, 600 sample observations, reliability/GPU and other domains (#5, #8, #9).
6. Owner determines repository visibility, enables branch protection and private backup (#11).

**Do not rely on previous sandbox ZIP links.** Everything necessary to begin *development* now lives in this repository. Runtime passwords, model binaries, raw licensed assets, channel data and videos intentionally do not.

## Update: exact Ultimate v3 edition merged (2026-11-13)

- [PR #12](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/12) **MERGED**; merge commit `83ff3a7fa58cadfd7e836cbdbb6f4ab4636a425a`.
- Added 11 readable files: 7 Ultimate-only/changed historical files, SHA-256 manifest, Python reconstruction tool, documentation and test; canonical runtime remains unchanged.
- Original 250-file Ultimate v3 contents can be reconstructed from `spec/combined-v3/` + `spec/ultimate-v3-overlay/` via `python tools/materialize_ultimate.py` and every file SHA-256 verified.
- Updated branch [CI run](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43344067226) passed **83 tests, 1 warning in 28.60 seconds**. This is Linux offline software only, not live model/account acceptance.
- Repo contents now **586 files before this documentation-only update** (575 after initial import/status docs + 11 Ultimate additions). Latest info also in [ULTIMATE_REFERENCE](ULTIMATE_REFERENCE.md).


### Next implementation — Issue #4 offline owner acceptance & recovery

Branch `feature/windows-offline-acceptance-and-private-recovery` adds CPU benchmark and private SQLite recovery tools, 12 new tests, plus a final-export invalidation bypass regression test. Local staged code passed **95/95 pytest tests on Linux**. GitHub Actions Linux and Windows-runner checks must be read on the linked PR before merging. Actual owner i7/32GB Windows acceptance, professional quality and Google live tests remain pending. Use `docs/WINDOWS_CPU_ACCEPTANCE.md` on the owner's device; keep sensitive local reports/data outside Git.


### Next partial checkpoint — M2.5 offline voice evidence and alignment protocol (2026-11-13)

Branch `feature/m25-offline-voice-alignment-evidence` adds `tools/audio_acceptance.py`, `tools/create_voice_manifest.py`, `tools/voice_accept_windows.ps1`, an explicit [owner protocol](M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md) and 17 synthetic-fixture/negative tests. **Merged PR #14** (commit `e0e5819cf0718ab7ca1f03725ec506024bbbc27c`). [GitHub CI run 43424993561](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43424993561): **113 passed on Linux; 28 passed, 1 benchmark deselected on Windows**, with one non-failing deprecation warning. The first Windows CI attempt failed because Hindi synthetic JSON was written using the default CP1252 encoding; explicit UTF-8 fixed it. The full external-model quality goal remains **OPEN** (#2): no locally installed real Hindi or English TTS/aligner, no measured human quality, no owner Windows CPU results, and no YouTube login was tested. Tests do not demonstrate actual TTS or alignment; report records owner-supplied evidence only.

### In-progress milestone — M2.5 owner-triggered local Piper run (2026-11-14)

Branch `feature/m25-local-piper-execution-proof` adds `tools/run_local_piper.py`, Windows helper, technical guide and **14 focused tests** (including one actual FFmpeg conversion using a **synthetic**, non-model local shim on Linux). **Merged PR #15** ([GitHub diff](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/15)), squash commit `80e84d58a736ca1b957a1343648ffa40eff9cdbd`. [GitHub CI run 43570844894](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43570844894) passed: **127 Linux tests**, **41 Windows focused tests** (one Unix-only synthetic test skipped, one CPU benchmark deselected), Python compile + dashboard JS + secret-pattern scan. One non-failing dependency warning. The trained-model/owner-PC gates remain OPEN. No trained Piper/WhisperX model or voice quality was tested; real Windows owner-machine benchmarks and YouTube authorization still need owner action. This checkpoint enables actual owner-invoked private sample production but **never auto-approves** the generated manifest.

### In-progress milestone — M2.5 supervised local WhisperX word-timing runner (2026-11-14)

Branch `feature/m25-local-forced-align-operator-gate` adds `tools/run_local_alignment.py`, `tools/run_alignment_windows.ps1`, `tests/test_run_local_alignment.py` (**20 focused tests** locally, synthetic fixtures), and `docs/M2_5_LOCAL_ALIGNMENT_RUNNER.md`. One test uses a **real child process with a synthetic WhisperX shim**, **not real model inference**. **Merged [PR #16](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/16)** as squash commit `3516b5b27b5df06e2e781474624f485367042173`. [Fresh GitHub CI run 43589799336](https://github.com/sahilk267/youtube-automation-platform-cgpt/actions/runs/43589799336) **PASSED**: Linux **147 pytest tests**, Windows **60 passed, 2 skipped, 1 benchmark deselected**; one non-failing Starlette warning, Python compilation, JavaScript syntax and bounded high-confidence secret-pattern scan passed. Tests are synthetic and do NOT constitute real WhisperX neural inference or owner hardware acceptance. Source/WAV/model hashes and exact Hindi tokens must agree; outputs are unreviewed and existing original Piper manifest unchanged. Owner machine and licensed real-model/human-reviewed alignment acceptance remain open in Issue #2. CI results/merge commit will be recorded after verification.
