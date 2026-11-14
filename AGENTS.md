# ViralOS — mandatory handoff instructions for any coding agent

**Read order:** `README.md` → `docs/START_HERE.md` → `docs/IMPLEMENTATION_STATUS.md` → `docs/ARCHITECTURE.md` → `docs/ROADMAP.md` → `docs/SECURITY_AND_RIGHTS.md`. Then inspect *actual code* and run tests. Do not treat any previous chat, ZIP reference, or alleged engine count as executable proof.

## Canonical ownership and boundaries

- One Python/JavaScript application in `app/`, migrations in `sql/`, automated tests in `tests/`, operator scripts in `tools/`. `spec/combined-v3/` is the long-term architectural reference; `spec/launch-v3/` is an immutable Launch design snapshot. **They are specifications, not deployable alternatives.**
- `research/` contains competitor/channel **desk research** and research-source caveats. Channel inventories are **not** 120 verified subscriber rankings and do **not** establish that every channel's full videos were watched.
- No duplicate renderer, repeated shared evidence services, or per-domain fork. Every domain has specialized research/creative policies while using shared orchestration/timeline/media/metrics infrastructure.
- Maintain backward-compatible typed contracts and additive SQLite migrations; never silently redefine a term or overwrite existing migration. Check tests and database upgrade/downgrade/backup procedures.
- Scripts, evidence, narrative, scene plans, timeline, audio, localized graphics, permissions and approval must be independently versioned and content-hashed. Source change invalidates downstream human approvals when applicable.

## Coding standards

1. Small vertical slices: hypothesis → interface → implementation → unit/negative/integration tests → actual artifact → human review. No placeholder named as an engine and no fabricated external evidence.
2. Default **local-only, private-first, owner-approved**; never publish, spend, sign in, download licensed models, copy broadcaster footage or modify an account without explicit owner authorization.
3. External providers: implement optional adapters with explicit credentials/rights; test in mocks without claiming live verification. Never bypass YouTube restrictions, and never assume legal fair use or monetization.
4. Distinguish code validation, local integration, Windows-specific acceptance, licensed-model quality acceptance, real-account OAuth/YouTube acceptance and video-human approval. A passing pytest suite cannot establish a professional video.
5. Every change updates `docs/IMPLEMENTATION_STATUS.md`, `docs/ROADMAP.md`, integration instructions, and a reproducible test log/commit reference. Preserve failures and blockers rather than hiding them.
6. Keep development private when required: **this repository is PUBLIC at initial import**; no secrets, local DB, raw licensed/broadcast clips, OAuth caches, proprietary model weights, or sensitive channel analytics in Git.
7. User hardware baseline: i7 8th Gen / 32 GB RAM / no GPU. CPU-only must remain functional, future RTX 3090/A6000/other GPUs and remote workers are optional. Do not rewrite old projects on hardware upgrade.
8. Business constraint: own YouTube channel earnings first; recurring budget ideally ₹0. Do not invent guaranteed channel profitability or virality.

## Definition of done for a video/domain

Source-backed claims and provenance; tested story arc; planned and original/authorized shots; professional natural voice; measured alignment; culturally appropriate multilingual narration, on-screen text and captions; sound/music rights and mixing; authentic 9:16 and 16:9 exports; human complete-watch approval; publication permissions; real YouTube analytics and useful feedback. For each domain a genuinely differentiated research and visual director. Current v0.7 does NOT meet this definition.

## When chat context is missing

Clone repository, inspect current main/PRs, run tests, open `docs/START_HERE.md`. Rebuild from committed source. If any references to an older `/mnt/data/*.zip` remain, **do not assume access to that path**. Ask only for missing private inputs (credentials, owned media rights, source data and human approval); never invent them.


## Offline Windows/backup acceptance tool (Issue #4)

`tools/owner_acceptance.py` and `docs/WINDOWS_CPU_ACCEPTANCE.md` define environment, CPU FFmpeg benchmark, consistent SQLite-only backups and clean-profile recovery. Do not bypass restore-time final-export invalidation, auto-retry remote-unknown uploads, overwrite an existing DB, or put private backups/owner reports in Git. Windows GitHub runner CI **is not** acceptance on owner's actual i7/32GB PC.


## M2.5 voice alignment evidence contract

For real voice-model claims, read `docs/M2_5_VOICE_ALIGNMENT_ACCEPTANCE.md`. `tools/audio_acceptance.py` is a **metrics evaluator** of a privately supplied WAV, transcript reference and candidate timestamps; it never runs or verifies a model or listener. `tools/create_voice_manifest.py` creates **unapproved** template, not an accepted voice. Synthetic fixtures can pass metric-code tests, but **cannot** be counted as a real Piper/WhisperX sample or a professional voice approval. No automatic publishing. Preserve user/WAV/model SHA binding and redacted private reports outside Git.

## M2.5 local Piper execution handoff

`tools/run_local_piper.py` is an **optional owner-executed subprocess wrapper** around an already installed, licence-reviewed local Piper binary and matching on-device `hi_IN`/`en_US` model. It does not download models, prove model output or rights, generate automatic word alignment or approve publication; see `docs/M2_5_LOCAL_PIPER_RUNNER.md`. Synthetic CLI shims and tones in `tests/test_run_local_piper.py` verify code paths only, **never** a real neural voice. Real inference, professional audio, word-timing and CPU/RAM acceptance remain owner gates. Do not weaken Git-private storage, no-overwrite, language checks or licence opt-in. An owner-specified binary is not sandboxed; trust its source.
