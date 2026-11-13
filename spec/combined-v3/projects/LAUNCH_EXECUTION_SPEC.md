# PROJECT L — ViralOS Launch Edition: Agent Implementation Contract v2.0

**Scope:** The first actually usable release on Windows, Intel i7 8th-generation, 32GB RAM, no dedicated graphics card, with real research-to-original-video workflow. Owner's own YouTube channels only; save earned net YouTube income toward hardware upgrades. **No client work, no SaaS, no A6000 purchase promise.** Future Ultimate requirements remain preserved but disabled. Do not call the product complete until tests and human sample review pass.

## L.1 Launch behavioral product contract

An owner installs the app, connects zero or more permitted public data sources and optionally YouTube credentials, creates a channel profile, chooses a topic, obtains verifiable research with citations, receives original script/storyboard, creates CPU-friendly media with original diagrams/voiceover, previews the result, reviews source/rights/originality/disclosure issues, exports 9:16 Short or 16:9 long-form video, optionally uploads it to an authorized channel, and later views **actual** authorized analytics. A task may safely stop when source access/rights/approval is missing. UI must never pretend that every module ran successfully or the video will be monetized.

## L.2 Launch scope (source of truth: `tests/REQUIREMENTS.csv`)

**P0 (must be working before v1 release):**
- `L-001` Windows first-run/bootstrap/launcher, health, clean restart, local dashboard; CPU-only operation.
- `L-002` Isolated per-channel market/language/voice/brand/rights/approval profiles.
- `L-003` Permitted, provenance-checked Cricket/NFL fixture/result/stat collection with freshness, and manual source fallback.
- `L-004` Multi-source trend collection, deduplication, quota tracking, honest coverage/failure dashboard.
- `L-005` SourceVersions and atomic claim/evidence graph: every factual script claim linked or flagged.
- `L-006` Deep domain-specific creative strategy: cricket/NFL distinct narrative, visual style, vocabulary and checks; technology optional control.
- `L-007` CPU narration, original diagrams, subtitles, FFmpeg 9:16 Short and 16:9 long-form exports.
- `L-008` Asset-rights and reuse/originality audit including broadcast footage risk.
- `L-009` Editorial approval, protected high-risk content workflow and correction propagation.
- `L-010` Optional authorized YouTube OAuth/upload + working manual export; revoked token fails safely.
- `L-011` Authorized YouTube Analytics import, format-specific experiments and actual observed metrics.
- `L-012` Real revenue/expense ledger and owner-entered A6000 GPU fund target.
- `L-013` Capability-aware scheduler Auto/CPU_ONLY/CUDA_ONLY/HYBRID; CPU no-GPU pass, GPU jobs held.
- `L-014` Durable resumable jobs, crash recovery, backups and real restore test.
- `L-015` Secrets, privacy, source ingestion and local security controls.
- `L-016` Golden regression fixtures, factual/sports/media/rights QA and honest release evidence.
- `L-017` Content portfolio, audience intent, truthful hooks, story planning and cross-channel duplication gates.
- `L-018` Fully typed API/contract implementation, database migrations and idempotent service routing.
- `L-019` Persistent original research dossier and bounded completeness/counterevidence review.
- `L-020` Original script/storyboard with passage-level citations and edits invalidating approval.
- `L-021` Source/rights/disclosure aware creation of final title/thumbnail/description and upload intent.
- `L-022` Professional operator UX: accessible actionable screens, blockers, source coverage, repair controls and logs.

**P1/P2 growth after pilot:** technology hands-on benchmark adapter, upgraded sports seasonal intelligence, better retention/cohort experiments, thumbnail alternatives, advanced subtitles/audio, corrections dashboard, more active channels only after operator acceptance.

**Not required until Ultimate:** full Newsroom, Science, Business, Gaming, History, Space, Learning, Career, Productivity, Culture OS implementations; GPU image/video generation; SaaS/tenant billing; multi-GPU/remote workers. Their contract IDs must already have expansion slots and not be eliminated from roadmap.

## L.3 Formal end-to-end workflow, including when to stop

| Seq | Service owner | Preconditions | Produced durable output | If cannot proceed |
|---:|---|---|---|---|
| 1 | channel_registry | User opens dashboard | `ChannelProfile` UUID and revision | Invalid profile -> validation UI |
| 2 | connector_registry | Allowed API/source configured or manual topic | `ConnectorHealth`, SourceVersion or explicit gap | No feed -> manual-input path |
| 3 | trend_engine | Observed provider data | `TopicObservation`, opportunity features/coverage | Insufficient sample -> don't claim trend |
| 4 | editorial_council | Chosen angle and channel | Production/Research decision | Rights high-risk -> review/hold |
| 5 | research_engine | Question, source scope, budget | `ResearchDossier`, source hashes and gaps | Source absent -> incomplete dossier |
| 6 | sports/tech plugin | Sport/domain entity resolution | Verified stats/claim review, specific visual plan | Ambiguous team/player -> review |
| 7 | creator_studio | Evidence-linked script claims | Original ScriptVersion, NarrativePlan, SceneSpec | Missing critical evidence -> edit/review |
| 8 | asset_rights | Asset list and intended use | Rights manifest and risk assessment | Unknown license -> replace/hold |
| 9 | media_pipeline | Audio/visual files and CPU resources | Narration, captions, composed media | Optional TTS missing -> manual voice import |
| 10 | media_pipeline | All scenes renderable | FFmpeg file and render manifest/hash | Fails -> logged retry/recover |
| 11 | editorial_council | QA and final revision | PASS/REVIEW/FAIL, approval record | Material edit -> approval expired |
| 12 | publication_service | Approved revision and user intent | Export bundle or authorized API intent | No OAuth -> manual export |
| 13 | analytics_service | Authorized metrics available | Observed snapshots and comparison | Missing metrics -> unavailable state |
| 14 | revenue_ledger | Actual verified payouts and expenses | GPU savings report | No revenue -> no fabricated value |

All transitions and idempotency are governed by CORE-03; this table is an edition-activation map, not a second state machine.

## L.4 Domain pilot experiment policy

Hypotheses, not claims of highest audience: India Cricket (`sports.cricket`, Hindi/Hinglish) and US NFL (`sports.nfl`, English) are initial candidates; AI/Tech (`technology`, market configurable) is control/fallback. Validate sources, broadcast rights and production effort before starting. Maximum two simultaneously active pilots until 3 accepted end-to-end sample videos and stable weekly workflow. MLB/NBA can replace a pilot following recorded owner decision, not as automatic scope creep.

**Pilot plan:** For each active channel define distinct audience/positioning, permitted source inventory, 2–3 editorial formats, original visuals strategy, short/long mix, manual upload/approval preference, recorded 4–8-week **observation** window and production effort ceiling. Prelaunch content test: three source-backed scripts (with one counterevidence case) and one complete rights-safe original video; real publish optional after explicit owner authorization. Track impressions/CTR/watch time/subscriptions and rights claims only when actually available. Don't infer revenue before monetization eligibility.

## L.5 Acceptance tests for Launch

- Windows CPU-only first-run with no CUDA drivers passes `/health` and settings persistence.
- Manual topic link or permitted cricket/NFL source -> captured canonical SourceVersion and a citation-linked claim -> accepted original script.
- Sports calculations use base-six overs and NFL down/clock/season semantics; off-by-one and wrong era cases flagged.
- 9:16 and 16:9 playable original samples rendered via CPU at full target profile or declared approved fallback; captions/voice synchronized and actual FFmpeg manifest stored.
- Unlicensed broadcast media cannot enter published asset list; cosmetic reupload cannot pass originality gate as-is.
- Unknown quote or unsupported statistical claim cannot be passed as verified fact.
- Public upload always blocked without OAuth and required approval; timeout retries reconcile remote ID.
- Fake Analytics fixtures cannot be displayed as observed earnings; missing account shows access not zeros.
- Killing worker during render permits safe restart and final artifact hash validation; backup restored on clean path.
- CPU-only and dummy CUDA workers have separate honest capability states; no UI fake GPU installed.
- Three sample projects tested end-to-end; at least one actual owner-selected video reviewed for originality and factual accuracy. If real YouTube upload unavailable, do not claim upload integration verified.

## L.6 Minimum UI screens and interactions

1. `Home/Command Center`: today’s jobs, sources, channels, blockers and recent outputs; cards actionable.
2. `Channels`: create/edit/activate/deactivate; locale/market/language/voice/risk and OAuth state; separate accounts.
3. `Trend Observatory`: coverage matrix, topics, original links/timestamps, scores/uncertainty, manual add.
4. `Research Dossier`: questions, claim/evidence matrix, supporting and conflicting sources, transcript/timecode, gaps and review.
5. `Creative Studio`: edit original script with citation overlays, scene timeline, asset/rights inspector, narration settings, preview.
6. `Production`: render modes and resource estimates, CPU worker progress, retries, logs and output inspection.
7. `Publish`: gate report, human approval, title/thumbnail/description, export/manual upload, optional OAuth authorized upload.
8. `Audience Lab`: observed metrics, format cohorts, experiments, missing reports; channel earnings status.
9. `GPU Fund`: real revenue, expenses, savings, owner-entered target/quotes and uncertainty.
10. `Settings/Operations`: resource toggles, installed models and licenses, source connectors, backup/restore, audit/security, diagnostics.

Every visual control has a backend endpoint or clearly disabled status. No inert decorative toggles. Accessible labels, Indian and English font handling, light/dark usable dashboard, safe narrow-screen layout.

## L.7 Repo implementation order (agent instruction)

**Milestone M0:** Inspect actual available starter ZIP/repo before editing; inventory genuine code and tests, identify reusable modules, do not assume prior starter code is production-complete. Deliver review, commit base tests, Windows preflight.

**M1:** DB/migrations/typed contracts, source registry, job queue, logs, channel profile, manual topic/source intake, CPU health UI. Exit: restart preserves profile/source/job integrity.

**M2:** cricket/NFL domain adapters, topics/opportunity, research/evidence, narrative/script, source line mapping, rights records. Exit: fixture + at least one genuine source-backed project reviewed.

**M3:** CPU scene compiler + local TTS/manual narration + captions + FFmpeg export, QC and editorial approval, sample Short/long-form. Exit: media/rights/claim gates pass; clean restart/resume.

**M4:** Authorized YouTube API upload/analytics optional; manual export fully usable regardless. Exit: mock integration tests pass; live verified only with owner permission.

**M5:** Audience feedback, experiments, earnings/GPU fund and resource toggles. Exit: honest dashboard, recovery and feature flag tests, CPU-only full regression.

Never schedule a stage as done without attached test evidence and a list of blocked external prerequisites.

## L.8 Release boundary and handoff

Deliver source code, dependencies, setup/run/backup scripts, migrations, sample fixtures and a real original 9:16 + 16:9 video (owner-selected sources), rights + source manifests, operator guide and test output. Export must work fully offline for saved projects. Don’t represent future generative GPU features as already present. This file plus referenced canonical shared specs is the Launch build authority.


## v3.0 creative-production integration (NORMATIVE ADDITION)
Launch video production MUST implement contracts/v3, core/21–core/26, and Sports/Technology creative directors. CPU-first originals with voice, captions, animations, factual/rights review and owner watch-through are P0. Older generic SceneSpec audio/subtitle dicts are metadata only, not executable rendering contracts.
