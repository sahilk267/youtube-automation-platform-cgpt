# ViralOS — YouTube Intelligence & Production Platform

> **Status: active CPU-first engineering prototype. NOT a finished autonomous publishing platform.**

**Latest verified GitHub snapshot:** [CURRENT_CHECKPOINT](docs/CURRENT_CHECKPOINT.md) — full source import MERGED, 587 files, GitHub Actions **83 tests passed** on main; user Windows, natural voices and live YouTube acceptance remain pending.

**Start here:** [Project recovery guide](docs/START_HERE.md) · [Architecture](docs/ARCHITECTURE.md) · [Current verified status](docs/IMPLEMENTATION_STATUS.md) · [Roadmap](docs/ROADMAP.md) · [Security](docs/SECURITY_AND_RIGHTS.md).

## Product mission

Build **one local-first, Windows-friendly multi-channel YouTube operating system** with shared infrastructure and **12 truly specialized domain operating systems**: Newsroom, Science, Technology, Business, Gaming, History, Space, Learning, Sports, Career, Productivity and Culture. Sports has independent Cricket, NFL, MLB, NBA and Soccer adapters. Specialization must include evidence/research, narrative strategy, original visuals, voice, localization, production QC and empirical learning—not just differently named prompts.

### Non-negotiable principles

- **One modular monorepo:** shared orchestration, research/evidence, provenance, scene/timeline renderer, audio, publishing and analytics; category-specific domain logic and creative directors.
- **Hardware:** develop on Intel i7 8th Gen / 32 GB RAM / no dedicated GPU. Design for CPU-only today and NVIDIA GPU / hybrid / distributed workers later. Do not claim target Windows benchmarks until measured there.
- **Revenue:** owner's YouTube channels first; recurring budget as close to ₹0 as feasible. No obligation to commercialize or sell SaaS/services.
- **Evidence:** a stored source URL is not independently verified; no invented statistics, claims, retention figures or channel income.
- **IP safety:** original/licensed/authorized content only. In-app YouTube Remix/Green Screen is NOT general re-download/re-upload permission; monetization eligibility and copyright permission are separate checks.
- **Publishing:** no silent upload. Real-account acceptance, explicit channel confirmation, human approval, SHA-256 locked exports, private-first verification, uncertain-upload reconciliation.
- **No fake completeness:** registered 'engines' are not necessarily executable. Technical tests are not human creative-quality validation.

## Where is the application?

The canonical planned application tree is `app/`, `sql/`, `tests/`, `tools/`, `configs/` and `spec/`. See [source-sync status](docs/SOURCE_SYNC_STATUS.md) for which files actually exist **in this GitHub branch**. Never infer that a prior chat ZIP is automatically committed here.

**Before running:** Python 3.12 and FFmpeg. On Windows (after source import):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_windows.ps1
```

Dashboard: http://127.0.0.1:8000 ; API: http://127.0.0.1:8000/docs . Default bound to localhost. Tests: `python -m pytest -q`. See [Windows setup](docs/WINDOWS_SETUP.md).

## Maturity and release gates

- **Specifications**: architecture and contract documentation; validate structural integrity, NOT actual implementation.
- **Local working prototype**: source/evidence intake, claim-review workflow, script/storyboards, CPU preview, selected visual overlays, Hindi/English reviewed video variants, human review and private-only YouTube adapter.
- **Model-/account-dependent**: live Piper voices, actual WhisperX alignment, Google OAuth private upload, YouTube Analytics/estimated revenue, independent real-data verification and actual Windows GPU performance remain subject to acceptance tests.
- **Long-term vision**: professional end-to-end videos and independent expert-quality creative directors for 12 domains are **not yet proven**.

## Repository governance

Development branch + pull-request review; never force-push or rewrite historical milestones. No tokens, customer/private analytics, full copyrighted videos, licensed voice weights, persistent SQLite databases, or generated MP4s committed. GitHub is currently **public**; check visibility before adding sensitive commercial material. Read [contributor handoff](AGENTS.md).

## Historical artifacts

The v0.7 handoff ZIP `ViralOS_Launch_M2_4_M3_2_v0_7_Working_Source.zip` was created outside GitHub; do not treat a mention of that filename as a GitHub download. The repository will carry the canonical reproducible source and docs as they are imported and verified. The progress/status reports must distinguish **local tested** vs **GitHub synced** vs **live provider verified**.

**Maintainer's rule:** If this chat is lost, begin at [docs/START_HERE.md](docs/START_HERE.md) and [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md). Do not restart the project from scratch.

### Recover the original Ultimate v3 edition

The [exact Ultimate v3 reconstruction guide](docs/ULTIMATE_REFERENCE.md) rebuilds all 250 original Ultimate specification files from the Combined v3 snapshot plus a tiny edition delta, checking 250 SHA-256 hashes. It is a design reference, not a second application. Current full GitHub source tree has 587 files, and the latest Ultimate PR [#12](https://github.com/sahilk267/youtube-automation-platform-cgpt/pull/12) passed 83 offline CI tests.
