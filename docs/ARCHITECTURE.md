# ViralOS Architectural Decision — modular monolith + specialist domain packs

**Decision:** Adopt one plugin-based modular monolith with durable queued workers, NOT twelve separately maintained apps, twelve duplicated renderers or 144 resident “AI agents”. `spec/combined-v3/research/03_FINAL_ARCHITECTURE_DECISION_ADR-001.md` contains the detailed historically researched decision.

## Layer ownership and contracts

| Layer | Single owner | Variation |
|---|---|---|
| Command Center | shared portfolio, task/job system, approvals, local settings | multi-channel brand profiles |
| Research/evidence | shared source registry, immutable provenance, claim-to-source graph, correction history | domain-specific source rules, quality thresholds, tools |
| 12 Domain OS packs | domain registry and specialist adapters | specialized research, fact checks, data interpretation, script/visual director rules |
| Creative Studio | narrative beat graph, evidence-to-screen shot map, timed tracks, overlays, captions, audio mixers, render manifests | domain × format × locale × brand policy composition |
| Production workers | CPU/Pillow/FFmpeg baseline, optional TTS/ASR/model adapters, eventual GPU | capability scheduling, budgets, fallback, model/asset licensing |
| Publishing/analytics | approval-bound YouTube OAuth, private-only acceptance; retention and revenue ingestion | different channel goals and accepted experiments |

### Domains

Newsroom (forensic political reporting with public primary source triangulation, context, contradictions and legal review); Science (mechanisms/exact diagrams/experiments); Technology (real screen captures and reproducibility); Business (financial case methods/earnings provenance); Gaming (review and mechanical analysis, footage rights); History (source periods/maps/chronology); Space (astronomical data and model caveats); Learning (step-by-step validation); Sports (Cricket/NFL/MLB/NBA/Soccer adapters, stats rules and original tactical diagrams); Career (source-backed work advice); Productivity (evidence-aware workflow demonstrations); Culture (rights-aware criticism and contextual analysis).

## Video composition

`CreativeBrief` → source-backed `NarrativePlan/TimedBeatGraph` → domain/format/locale/brand director → immutable `ShotSpec` with evidence and rights references → `VideoTimeline` (voice, music, captions, images, diagrams, PIP, animated overlays, safe regions, transition timebase) → render worker → objective QC → human full-watch → version-locked export → optional approved private upload → real observed analytics. No “generic AI stock footage under every script” shortcut.

Locale is not merely subtitles: independent voice, pronunciation, regional graphic/text layout, captions, screen titles, local examples, safety claims and human QA. Claim changes must invalidate dependent plan/approval.

## Compute

Default owner machine CPU-only; make no heavy resident GPU service mandatory. Worker capability keys include `cpu_render`, `tts`, `asr`, `image_gen`, `video_gen`, `gpu_mem_gb`; route jobs to available worker and require deterministic manifests. GPU addition changes scheduling capability, not project schemas. Optional separate remote workers only after local bottlenecks are measured.

## Evidence/rights

A source link is not proof; owner review is not automatic independent verification. Third-party clips require provenance, excerpt purpose, risk class, rights check and meaningful commentary; in-product Remix eligibility does not license exported reuploads. Newsroom must verify allegations and context with competing evidence and human editorial approval.

## Future discipline

Launch and Ultimate share **one canonical runtime**. `spec/launch-v3/` and `spec/combined-v3/` are immutable release specifications retained for traceability, NOT maintained copies of code. Never fork runtime code by edition. See `AGENTS.md` and `docs/ROADMAP.md`.
