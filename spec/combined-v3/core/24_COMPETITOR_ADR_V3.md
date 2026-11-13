# CORE-24 — Research-to-Production Review, Competitor Lessons and ADR (v3.0 NORMATIVE)

**Adopt ADR-001:** modular monolith, durable jobs, shared evidence and media primitives, independent domain/format/locale/channel brand policies, CPU-first render worker, future optional GPU compute adapters. See `research/03_FINAL_ARCHITECTURE_DECISION_ADR-001.md` for original rationale. ADR status is **ADOPTED AS v3 SPECIFICATION**, not implementation.

## Lessons mapped to actionable decisions
- Script-to-scene competitors demonstrate editable scene drafts: preserve ScriptVersion -> BeatGraph -> ShotPlan -> Timeline with revision hashes; do not render irrecoverable black-box output.
- Transcript-native editors: allow spoken segment edit, regeneration of only affected audio/caption/shot range, invalidate local approvals as needed.
- Long-video clippers: semantic analysis before clipping; **does not transfer rights**. Never auto-repost.
- Outlier/competitor research products: compare publicly observed views against matched baselines, not estimated competitor retention or RPM; no fake 'viral probability'.
- Dubbing providers: separate speech, translated overlays, duration and cultural context; consistent core claims but distinct local QC.
- ComfyUI-like workflows: store workflow revision, model license/hash, seed, request/response digests; only enable a validated provider.
- Workflow orchestrators: durable idempotency, resource budgets, queue and pause; no mandatory third-party cloud queue on local PC.

## Empirical evidence guardrails
The bundled `research/02_120_CHANNEL_CONTENT_BENCHMARK.md` and `research/120_channel_benchmarks.csv` are 120-channel **desk-research benchmark inventory**, not a verified top-subscriber ranking, not proof of viewing 600 videos, and not evidence of private audience analytics. `CreatorBenchmark` has observation level `DIRECT_VIDEO` / `CHANNEL_SOURCE` / `CURATED_REPORT` / `INFERENCE` / `UNAVAILABLE` and exact source, timestamp, observer. A planned 5-video/channel follow-up requires real timecodes/screenshots and human checks. No copying identifiable scripts, footage or proprietary visuals.

## Engineering decision
- **Modules:** 12 domain dossiers; sports subadapters for cricket/NFL/MLB/NBA/soccer.
- **Orthogonal dimensions:** domain expertise × content format × locale × channel brand × compute profile.
- **Shared services:** source registry, evidence graph, asset rights, speech service, overlay composer, audio mixer, timeline renderer, YouTube OAuth/upload/analytics, change invalidation and approvals.
- **Scoped releases:** Launch activates sports and optional technology, with other categories documented but disabled; Ultimate/Combined hold all domain specs without claiming functionality; SaaS only after owner validation.
- **No scope inflation:** follow test evidence and owner outcomes, not number of named agents.

## Versioning
`contracts/*.schema.json` v2 schema remain valid inputs to v2 adapters. New creative artifacts use `contracts/v3/*.schema.json` with `contract_version=3.0.0`. Mapping to/from old `SceneSpec` is described in `core/25_MIGRATION_AND_COMPATIBILITY.md`; an agent must not silently edit already published project revisions.
