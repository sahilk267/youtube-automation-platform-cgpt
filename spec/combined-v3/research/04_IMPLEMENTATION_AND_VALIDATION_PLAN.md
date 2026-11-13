# Implementation and validation plan — build from the research, not from hype

**Project constraint:** Owner earns from own YouTube channels; no initial services/SaaS. Computer: Intel i7 8th gen, 32 GB RAM, no dedicated GPU; scale later to CUDA workstation and optionally A6000 48GB. Build a reliable original-content system before claiming any domain expert/master status.

## Research evidence quality policy

- `DIRECT_OBSERVATION`: exact video URL/timecodes/screenshots/transcript or video file obtained lawfully and manually verified.
- `CREATOR_SOURCE`: verified producer description, official format explanation, public research/source catalog.
- `CURATED_REPORT`: independent creator guide, publicly accessible about-page/metadata.
- `INFERENCE`: suspected strategy not demonstrably measured; never displayed as empirical observation.
- `UNAVAILABLE`: data lacks authorization. Competition channels' retention, CTR, RPM, watch time are normally non-public; leave NULL.

Every CreatorBenchmark sample stores `channel_id`, `channel_handle`, `video_url`, `observed_at`, `publication_date`, `format`, `locale`, `duration_ms`, `hook_start_ms`, `payoff_ms`, `shots_observed`, `evidence_links`, `source_licensing`, `accuracy_notes`, `confidence`, `assessor`, `limitations` and `captured_public_metrics`. No video metric should be auto-guessed.

## Repeatable 120-channel deep-video validation protocol

Sample **5 videos per channel** after obtaining permitted playback access: 1 recently published long-form, 1 recent Short, 1 evergreen standout, 1 comparable baseline, 1 distinct format. 120 × 5 = **600 video-level observations**. A researcher may select fewer videos initially if constrained, but must display the actual sample size. For each video:

1. Capture stable URL, channel, market, language, video type, date/time, title, public visible metrics and citation.
2. Timecode first 30s: what is promised, when the central question appears, whether visuals substantiate that promise.
3. Segment major beats/chapters; mark question/context/evidence/tension/payoff/CTA and unresolved plotlines.
4. Sample **every shot/layer type**: face, licensed source footage, original field diagram, document, chart, B-roll, generated image, captions, kinetic text, picture-in-picture, screen record, music and SFX. Record observed, not inferred timing.
5. Record creator's originality mechanism (firsthand access, experiment, analysis, primary research, distinctive acting/voice) and inputs an owner-only CPU setup cannot reproduce.
6. Search citations/primary records if factual. Log questionable shortcuts separately from confirmed errors.
7. Label reused clips, copyright/creator-rights risks and potential monetization limitations without claiming adjudication.
8. Record alternatives: an original CPU-safe rendering approach and, later, a GPU-assisted option.
9. Propose a testable ViralOS video format. Do not mimic proprietary edits, jokes or media.
10. Human reviewer signs off on observed sample before format benchmarking.

**Metrics method:** public competitor `views`/`likes`/upload date can support outlier hypothesis only against matched channel baseline and format/time window. Private `CTR`, `retention`, `RPM`, monetization state, or ad revenue must not be inferred. Your own channels can be evaluated through authorized YouTube Analytics API. A difference in retention between videos is correlation absent a properly designed experiment.

## Release milestones and locked tests

### R0 — Source-to-screen functional baseline on CPU
Research saved → claim/evidence → original short narrative → original graphics + voice → text captions/overlay → actual H.264 file → owner watch-through. Evaluate three original samples with no downloaded league footage. **Fail** if video is static text slide with generic imagery, lacks factual citations, clips captions, or cannot restore after interrupted render.

### R1 — Sports and tech differentiation
Sports produces a verified tactical explainer with original field graphics (Hindi cricket or English NFL) and real source/citation; Technology produces an authentic local screencast and reproducible tool test. Use distinct domain factual validators, opening structures and audio styles. **Fail** if simply swapping narration between the same generic template.

### R2 — Locale variants
Same evidence bundle generates hi-IN and en-US scripted speech, native-script captions, translated on-screen graphics, adjusted durations, source terms checked; changing a factual claim invalidates all relevant variants. Test audio sync and region-safe UI overlays. Auto-dubbing/lip sync is optional GPU/cloud adapter, not a baseline promise.

### R3 — Rights-first reaction workflow
Provide source video of which owner has rights → original transcript → claim/commentary map → edited original interpretation → full preview → rights/novelty gate. A third-party clip with unknown rights triggers a blocker; decorative voiceover alone is not accepted. YouTube policy approval remains unknowable in advance.

### R4 — Real owned-channel learning
Explicit OAuth → approved upload/private export → actual metrics available to user → retention and packaging hypotheses; A6000 savings ledger based on actual collected money. No promises of monetization or revenue.

### R5 — Domain mastery and graphics expansion
Each of 12 domains passes **minimum one golden short + one long** with domain-specific visuals, evaluated facts, accessible voice and rights review; then build deeper suites. Newsroom allegations require specific editorial/legal review. Declare each subsystem `SPECIFIED`, `IMPLEMENTED`, `TESTED`, or `RELEASED` separately.

### R6 — Hardware evolution
GPU provider registry, ComfyUI optional adapter, job routing and VRAM checks, image/video prompt compiler, character continuity and generation QC; benchmark actual machine and models before enabling. Preserve same project/scene IDs. Multi-worker infrastructure only after demonstrated throughput need.

## No-go conditions

- Any product claims "all categories mastered" without tested representative outputs.
- Startup depends on RTX/A6000, paid SaaS subscriptions or a GPU on CPU-only box.
- An AI agent invents source quotes, interviews, rights grants, video samples, retention figures, title-test results or personal experiences.
- Originality checker confuses "voiceover added" with copyright permission.
- Translation changes numerical or disputed factual meaning without review.
- API/YouTube feature capability inferred from an obsolete blog rather than the live account and docs.

## Handoff checklist to coding agent

- Read `03_FINAL_ARCHITECTURE_DECISION_ADR-001.md` before modifying v2.1 code/spec.
- Inventory existing assets and schemas; add a change request and migration impact matrix; keep v2.1 stable IDs.
- Build contract tests for `TimedBeatGraph`, `VideoTimeline`, `OverlaySpec`, `SpeechSegment`, `LocalizationVariant`, `ReactionClipMap`.
- Implement one complete rights-safe CPU video and inspect it, before scaling to 12 categories.
- When outcome or API permission is unknown, explicitly mark blocked, not success.
