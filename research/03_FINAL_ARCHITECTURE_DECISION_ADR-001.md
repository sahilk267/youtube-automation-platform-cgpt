# ADR-001 — ViralOS Final Architectural Direction After Competitor + Creator Research

**Date:** 2026-11-09  |  **Status:** PROPOSED-FOR-ADOPTION (not yet merged into canonical v2.1 packs)  |  **Project scope:** Own YouTube channels first, not services/SaaS. Baseline i7 8th-gen, 32GB RAM, no dedicated GPU; future RTX 3090/A6000 or other NVIDIA GPUs, then optional distributed workers. Never promise income/virality or universal local video-model compatibility.

## Decision in one sentence
Adopt **one plugin-based modular monolith + durable process workers**, with **12 domain research/creative policy packs**, **one evidence store**, **one shared evidence-to-screen video compiler**, **independent format, locale and channel-brand profiles**, and **capability-routed CPU/GPU render workers**. Do NOT build 12 products, 12 renderers, or 144 permanently resident AI agents.

## Evidence driving the decision

- Outlier analytics tools (1of10, vidIQ, Viewstats) separate *topic/packaging research* from actual production. Their scores are public-observation hypotheses, not predictions of our revenue.
- Pictory creates scene drafts from scripts; Descript makes editing transcript-native; InVideo preserves multitrack editable drafts. These all demonstrate the need for non-destructive revisions at scene/word level.
- OpusClip demonstrates source video understanding and reframing before clip extraction; rights to input footage remain a separate gate.
- HeyGen/Synthesia demonstrate that dubbing must propagate to on-screen text, durations and layouts.
- ComfyUI demonstrates reusable model workflows with parameters, checkpoints, and asset provenance.
- n8n's distributed queue architecture adds external coordination infrastructure; it's valuable inspiration but inappropriate as hard initial dependency for a local 32GB desktop.
- Benchmarked YouTube channels differ primarily in **domain evidence, on-screen explanatory grammar, storytelling identity, and format**, not in requiring separate copies of every generic service.

## Decision registry

| ID | Decision | Rationale / nonnegotiable test |
|---|---|---|
| ADR-01 | One codebase; edition profiles `LAUNCH`, `ULTIMATE`, `COMBINED` are packaging/feature flags, not forks | Migrations and project IDs identical; Launch never falsely displays deferred modules as functional |
| ADR-02 | Windows-local FastAPI backend + React dashboard + lightweight launcher | Confirm clean CPU-only setup and restart |
| ADR-03 | SQLite WAL/FTS5 and filesystem artifact blobs first; schema migrations from day one | Atomic job state; backup/restore; limit writers |
| ADR-04 | Each queued task durable, idempotent, resumable and observable | Crash/restart and duplicate upload tests pass |
| ADR-05 | Shared source connector registry and source version store | No 12 copies of RSS/YouTube/client code; stale source tracked |
| ADR-06 | Domain plugins contain **specialist ontologies, tools, reasoning checks and creative policy** | Golden tests must demonstrate genuinely different behavior, not reworded prompts |
| ADR-07 | Sports is one top-level domain, with cricket/NFL/MLB/NBA/soccer subadapters | Shared infrastructure plus sport-specific stats/rules/diagram schemas |
| ADR-08 | Format pack orthogonal to domain: reaction, tactical, tutorial, explainer, documentary, review, breaking brief, Shorts, long | Same subject can produce different *original* formats |
| ADR-09 | Locale pack orthogonal to both: language, accent, spelling, timing, typography, cultural context | Change in claim invalidates every affected localized variant |
| ADR-10 | Channel brand pack: voice rights, intro/outro, graphics, colors, audience persona, upload policy | Two channels in one domain need not look alike |
| ADR-11 | Canonical `EvidenceBundle` → `NarrativePlan` → `TimedBeatGraph` → `ShotPlan` → `VideoTimeline` | Every spoken major claim linked to research or marked opinion/illustration |
| ADR-12 | Track-based programmatic timeline with edit-in-place revision history | Replace one scene or audio segment without unrelated rerender |
| ADR-13 | Text overlays and subtitles are separate tracks | Translating captions alone cannot leave stale on-screen terms |
| ADR-14 | Audio tracks separate voice/music/ambience/SFX/source clip | Loudness, permissions, timing and intelligibility validated separately |
| ADR-15 | High-risk factual claims and unlicensed source clips fail closed | Explicit human review; no arbitrary safe-length copyright myth |
| ADR-16 | Competitor scanner stores public metadata and research notes, not private retention/RPM | No fictitious competitor metrics or copying material |
| ADR-17 | Trend data with observed source coverage and confidence | 100% trend discovery not claimed |
| ADR-18 | CPU-only mode provides true research, original diagrams, titles, captions, voice and FFmpeg render | No dedicated GPU needed for runnable core |
| ADR-19 | Optional local LLM engine; factual claims verified through source tools | Model memory never substitutes for evidence |
| ADR-20 | GPU image/video via provider adapters and model registry, later | No unsupported automatic photorealism promise; VRAM/OOM fallback visible |
| ADR-21 | All assets carry rights, provenance, source hash, derivative relationships | No unidentified broadcast/music/model license used to publish |
| ADR-22 | Owner approves final rendered file or grants explicit bounded auto-policy for genuinely low-risk workflows | Approvals invalidate on material facts/rights/localization changes |
| ADR-23 | Only owned-channel authorized analytics can provide retention/revenue; monetization ledger distinguishes actual and estimated | No invented RPM or competitor conversion |
| ADR-24 | Observed experiments update category/format/locale strategies through reviewed proposals | No model-driven auto changes to source truth or high-risk policy |
| ADR-25 | No external orchestrator as required launch dependency; optional n8n adapter is external | Keep core self-contained; preserve event contracts |
| ADR-26 | Phase gates over feature counts | Testable complete end-to-end videos, audit and usability before activating more domains |

## End-to-end data flow

```text
PUBLIC RESEARCH / LICENSED SOURCES / OWNER FOOTAGE
       |
[Connector & Rights Registry] --> [Versioned Source Store]
       |
[Trend+Competitor Opportunity Discovery] --> [Editorial Council]
       |
[Domain OS Research Expert] --> [EvidenceBundle + Counterevidence]
       |
[Domain Creative Director] + [FormatDirector] + [LocalePlan] + [BrandPack]
       |
[NarrativePlan] --> [TimedBeatGraph] --> [ShotPlan]
       |
[Media Asset Selector] --> [Rights Gate] --> [VideoTimeline]
       |                                  |
[Audio Director + Overlay Director + Caption Alignment]     
       |
[CPU Vector/Screencast / Optional GPU Generation Provider]
       |
[FFmpeg/Frame Renderer] --> [QC] --> [Human Preview]
       |
[Private Export / Approved YouTube Upload]
       |
[OWN Channel Analytics] --> [Hypothesis Registry] --> [Reviewed Improvements]
```

**Every intermediate artifact** has `id`, `schema_version`, `content_sha256`, `producer_engine_id`, `source_ids`, `rights_ids`, `created_at`, `dependency_hash`, `review_state`, `locale_variant_id` if relevant. Material change invalidates downstream approval/render caches.

## Missing typed v2.2 contracts to add (new IDs, never silently overwrite old schemas)

- `CreativeBrief`, `DomainVideoPolicy`, `FormatPolicy`, `LocaleProfile`, `ChannelBrandProfile`
- `TimedBeatGraph` with beat objective/payoff, evidence IDs, linked audio and target milliseconds
- `SpeechSegment` with voice permission, language, SSML/prosody safe subset, text, audio hash, word timings
- `VideoTimeline` with integer millisecond timebase, tracks, z-index, gaps, transitions, render-safe masks
- `OverlaySpec` and `TypographySpec` with native-script fonts and safe-region constraints
- `AssetUseDecision` distinguishes ownership, documented license, exception-reviewed and blocked
- `ReactionClipMap` with source URL/hash, legal review, excerpt time ranges, original commentary, contextual QA
- `LocalizationVariant` with translated script, dubbing, text overlay, glossary, numeral style, word timing and final approval
- `SoundMixSpec` (relative level, measured loudness check, rights), `CaptionTrackSpec` (sync, line limits, reading QA)
- `CreativeQualityReport`, `ReviewRequest`, `HumanPreviewApproval`, `ViewerExperimentHypothesis`
- `CompetitorChannelSnapshot` with `public_only: true`, `sample_ids`, `evidence_grade`, not unsupported insight metrics
- `VideoBenchmarkSample` with channel/video permalink, date, observed scenes, timecodes, assessor notes and confidence

**Contract changes:** v2.1 `SceneSpec.audio_mix` and `subtitle_policy` are generic objects. Define versioned typed child models, keep v2.1 reader compatible and use migration adapters with regression tests. Don't merge this ADR as running source until contracts compile.

## Exact module ownership boundaries

| Owner | Owns | Must NOT own |
|---|---|---|
| `source_registry` | Network ingestion, permission/status, source versions | Deciding a scientific claim is true |
| `evidence_graph` | Atomic claims, quotes, provenance, source independence, corrections | Camera style or upload decisions |
| `domain/<id>` | Specialist tools/calculations, evidence challenge, domain creative policy | Shared FFmpeg, OAuth, common TTS runtime |
| `trend_intelligence` | Time series, trends, coverage, competitor *public* metadata | Factual truth, guaranteed reach |
| `creative_director` | Promise, story beats, shot semantics, audience value | Vendor model-specific API calls |
| `visual_compositor` | Timed layers, transitions, captions, captions-safe geometry | Fact-checking content claims |
| `audio_studio` | Narration generation, dialogue alignment, music/SFX mixing and audio rights | Publishing authorization |
| `localization_service` | Language/region variants, text reflow, pronunciation QC | Changing factual claim independently |
| `compute_router` | Capability check, queue scheduling, resources, checkpointing | Topic choice or editorial truth |
| `publication_service` | Owner approval, OAuth/upload, external reconciliation | Modifying approved media |
| `analytics` | Observed owned-channel metrics, experiments | Competitor private metrics or invented RPM |

## Example executable-ready policy resolution

```yaml
video_job:
  domain: sports.cricket
  format: tactical_short
  locale: hi-IN
  channel_brand: india_cricket_01
  compute_mode: AUTO
  required_visual: original_field_diagram
  source_policy: versioned_primary_and_secondary
  third_party_clips: block_without_reviewed_rights_basis
  generated_visuals: label_if_realistic_reconstruction
  publishing: private_until_final_owner_approval
```

Each layer composes in precedence order: **global hard gates > jurisdiction/platform requirements > domain safety/correctness > format constraints > locale semantics > channel-brand style > user aesthetic preferences**. User preference can never override an evidence/legal hard gate. Violations produce typed blockers rather than arbitrary fallback guesses.

## Human-in-the-loop boundary

**Automatically safe to attempt after consent and source permissions:** discover public topics, poll API within quotas, draft research, compile evidence, draft scripts/shots, render original graphics, build voice tracks, run tests, record analytics. **Review required:** unlicensed/exception-reviewed media, consequential allegations, health/financial guidance when high-risk, potentially misleading AI reconstruction, ambiguous translations, final launch sample, material source correction. **Never automatic:** impersonating creator, bypassing Content ID, fake engagement, claiming private competitor retention.

## Performance + scaling

### Launch profile on i7 8th gen / 32GB / no GPU
- One heavy local model and one heavy render at a time; queue-based CPU worker. Maintain OS RAM headroom and benchmark task-specific limits instead of a rigid assumed throughput.
- SQLite WAL/FTS5 + versioned artifact hashes; media blobs on disk rather than in SQLite.
- Source-licensed images/owner footage, SVG/Canvas diagrams, source cards and motion typography; FFmpeg H.264 output. Local small LLM, speech synthesis and forced alignment optional and installed explicitly.
- GPU-required jobs are blocked/held with clear UI, **not** silently substituted with fake assets.

### GPU upgrade profile
- Detect CUDA and free VRAM; reserve resources per model manifest, queue image/video generation, checkpoint model/version/seed, choose quantization only after validation.
- Local ComfyUI-compatible workflows as an adapter, not as the canonical document store or mandatory launch dependency.
- CPU-based infographic and narrative tracks remain valid; optional GPU clips replace chosen shots without changing verified evidence IDs.

### Distributed future
- Add worker heartbeat, authenticated artifact transfer and database migration as a separate milestone. No claim that SQLite across a distributed worker farm is safe without a coordinator/migration.

## 12 domain specialization requirements (no generic-prompt substitution)

| Domain | Essential domain-specific reasoning | Essential visual grammar and QC |
|---|---|---|
| Sports | Cricket overs/wickets; NFL downs/clock; MLB innings/pitch; NBA possession | Field/court overlays, score version, league-footage rights |
| Newsroom | Original full speeches, archival claims, contradictions, policy/action/outcome, right-of-reply | Timestamped documents, balanced source cards, labeled reconstruction |
| Science | Study methods, effect sizes, retractions, consensus | Mechanism diagrams, units, limitations, simulation labeling |
| Technology | Reproducible device/code benchmarks, version status | Actual screen capture and test-condition overlays |
| Business | Source filings, periods, currency, unit economics, ownership graphs | Reconciled graphs, audited/estimated labels, risk factors |
| Gaming | Original gameplay, patch awareness, rules, challenge authenticity | HUD-safe capture, replay and input/state comparisons |
| History | Primary archives, chronology, historiography, translation | Geotemporal maps, artifact provenance, reconstructions |
| Space | Mission sources, orbital mathematics, observation vs model | Scale-correct mission and science visualizations |
| Learning | Curriculum prerequisites, misconceptions, checked solutions | Stepwise board/coding proof, comprehension exercises |
| Career | Region/career-level skills, credentials, job market evidence | Evidence-based scenarios, resume privacy, actionable checklist |
| Productivity | Actual baseline/after comparison, permissioned automations | Real workflow capture, measured time savings, no fake habits |
| Culture | Meme provenance, platform change, cultural context, rumor checks | Chronological source examples, original commentary and rights |

## Acceptance tests before calling architecture implemented

1. Same `Story` can generate 9:16 Hindi and 16:9 English variants with different captions/overlays, unchanged factual claim IDs and independent QA.
2. Change a verified cricket score → invalidate script, voice line, score overlay, thumbnail if affected, translations, render hash, approval and publication intent.
3. Feed a protected NFL clip without established rights → BLOCK media usage; still offer independent original tactical diagram workflow.
4. Render a full original Short with moving diagrams, correct word timings and mixed narration on CPU-only test machine; exported file actually watched by owner.
5. GPU setting toggled with no GPU installed → `WAITING_FOR_CAPABILITY` for GPU-only model job; CPU render path still works.
6. Imported competitor snapshot has public views/metadata only; private retention fields absent, never fabricated.
7. Same domain `sports` produces meaningfully different cricket, NFL and baseball fact checks and field visuals.
8. Repeated `publish` request cannot produce two uncontrolled remote uploads; remote reconciliation path tested.
9. Human approval expires on material edit; external source correction reaches every dependent locale.
10. All 12 domains must pass domain-specific benchmark video cases; a generic shared template alone is not domain completeness.

## Open decisions / no permission to hallucinate

- Actual source provider accounts, paid rights, league film permission, original voice/face, music assets, channel brand identity, SSD capacity, OS build, exact GPU model purchase are unknown.
- Current formal YouTube API quotas and policy change; implement provider capability/feature checks.
- Preferred initial channels remain testable hypotheses (India cricket / US NFL, optional tech fallback), **not verified highest-RPM winners**.
- Video style extraction from 120 public benchmarks is desk research; 5+ manually inspected representative videos/channel remain a proposed later test to calibrate actual shot timing, audio design, upload cadence and retention correlations.

**ADR adoption criterion:** owner approval + v2.2 contract migration design + no broken v2.1 consumer + golden sample videos. This document is an informed architectural decision, not a claim of completed running implementation.
