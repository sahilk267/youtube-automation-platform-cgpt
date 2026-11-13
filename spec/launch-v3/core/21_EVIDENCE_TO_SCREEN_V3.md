# CORE-21 — Evidence-to-Screen Production Contract (v3.0 NORMATIVE)

**Status:** specification, not an implemented engine. **Scope:** Launch, Ultimate, Combined. Supersedes production-specific ambiguities in `core/07`, `core/18`, older SceneSpec prose, v2.2 addendum and ADR-001; preserves v2.0 source/claim, rights, compute, jobs and publication contracts.

## Critical definitions
- **Research fact**: sourced proposition with an ID, time/context, verification state, source-version references and known uncertainty. A narration or text-card *factual* statement has valid `claim_ids`; no invented stats, quotes, images or confidence values.
- **CreativeBrief**: viewer question, format, locale, category + sport if applicable, real value proposition, originality thesis, permitted footage modes and brand policy.
- **TimedBeatGraph**: narrative beats with explicit start/end ranges, evidence, question, reveal, what viewer gains and end payoff; timings are hypotheses, not platform laws.
- **ShotPlan**: exact approved visual asset or deterministic SVG/render recipe, role (EVIDENCE/DEMONSTRATION/ILLUSTRATION/RECONSTRUCTION/COMMENTARY), composed layers, motion, allowed uses, factual/rights dependencies.
- **SpeechSegment**: exact spoken words, intended language/voice, pronunciation dictionary, timestamps *measured from real output* (not LLM guesses), sample rate, speaking style and clip hash.
- **OverlaySpec**: independent informational text layer with locale, safe-box normalized coordinates, entry/exit timing, font fallback, contrast/safe-area test. Captions and decorative text MUST be separate semantic tracks.
- **VideoTimeline**: immutable, versioned, hardware-neutral program of shots/audio/text/transition lanes with millisecond timebase and source/rights hashes. The renderer consumes only a validated timeline.
- **CreativeQualityReport**: machine tests + human video preview status + blockers. A technically valid MP4 is not a proof of worthwhile content.

## Ownership: exactly one canonical implementation per shared service
`creative_director` owns CreativeBrief and TimedBeatGraph; `shot_planner` owns ShotPlan; `asset_service` owns selection/rights link, never license adjudication by an LLM; `voice_service` owns synthesis/import and timing alignment; `overlay_service` owns text and caption geometry; `audio_mixer` owns loudness/ducking; `timeline_compiler` owns VideoTimeline; `render_service` owns FFmpeg; `localization_service` owns translated variants; `reaction_director` owns source-to-commentary map; `creative_qc` owns quality reports. Domain plugins own ontologies and policy adapters only. See `configs/creative_operation_registry_v3.json` for typed boundaries. Reuse `shared.asset_rights`, existing factual verifier and publication service; do not clone them.

## End-to-end algorithm (idempotent; all steps persist typed artifacts)
0. Verify channel, edition, source permissions, required compute and actual available tools. Missing source/API = `BLOCKED`, not success.
1. Fix audience, original analytical angle and claimed viewer benefit in CreativeBrief. Dedupe against the same channel's published backlog.
2. Research domain-specific facts and alternatives. Lock `EvidenceBundle` / claim IDs and note uncovered questions.
3. Select format pack, domain audiovisual director, locale strategy and channel brand; reject incompatible combinations with a visible reason.
4. Plan question/context/evidence/reveal/payoff beats, each tied to claims or explicit non-factual intention. No fixed 2-second cut rule.
5. Plan each shot: visual purpose and evidence class, original/cleared asset recipe, camera/motion, text, audio cue, source attribution, factual uncertainty and legal disclosure.
6. Obtain or generate only permitted assets. For CPU: original SVGs/maps/charts/screencasts/authorized photos and subtle keyframe motion. For GPU later: model-specific adapter + tested resources + provenance; never fake proof.
7. Narrate with authorized voice; inspect actual duration, speech quality and pronunciation. Align captions from rendered audio with a verified alignment tool or human-supplied timing—not estimated characters-per-second.
8. Build localized variants independently: rewrite meaning, preserve verified claims/units, synthesize voice, adapt text overlays, recalculate shot durations and inspect accents/terms.
9. Compose in separate tracks: background; primary visual; contextual insert; evidence/chart; semantic overlay; captions; branding/disclosure; narration; permitted source audio; ambience/music/SFX. Maintain audio ducking and readable text-safe areas.
10. Validate timeline and run deterministic CPU/GPU rendering. Keep render manifest with exact source, asset, parameter, tool and output hashes. Retry bounded transient errors only.
11. Machine QC: valid dimensions, audio/silence, timing coverage, title/text readability, font support, overlay collisions, loudness, rights availability, synthetic disclosure, missing citations, duplicate frames and unexpected media.
12. **Human watch-through gate** for each distinct master format/locale and every risky or third-party-derived video. Material edit invalidates approval, including voice/translation/rights changes.
13. Export master and locale-specific bundles; optional authorized upload via existing outbound-action intent. Studio-only features remain manual; no fabricated endpoint.
14. Import actual owned-channel Analytics metrics only when authorized and available. Compare format/locale/channel cohorts with confounding disclosures. Propose experiments; do not silently rewrite editorial policy.

## Temporal contracts and invalidation
All times `start_ms`, `end_ms` are integer, half-open intervals `[start,end)`, relative to video zero. Scene duration must be positive; outputs have exactly one frame rate and timebase; track overlaps are permitted *only across distinct lanes*, and disallowed within the primary visual lane unless transition policy explicitly specifies compositor handles. Spoken text cannot extend past audio segment. Captions must align to measured words/phrases. Locale versions have independent durations and timeline hashes. Evidence correction, source rights expiration, transcript correction, or rendered-asset changes invalidate dependent stages, QC and approvals recursively. Drafts can be retained but cannot be published until reapproved.

## Text-on-screen contract
Quote cards preserve the actual quoted source; translated quotes explicitly say translated. Numbers show units and date of observation. Graph axes cannot be altered to falsely imply trends. Per-locale glyphs have real fallback fonts, bidirectional text shaping where needed, line wrapping and contrast against video frames. Do not claim safe zone universal across devices; preview Shorts on representative phone layouts.

## Audio contract
Voice > clarity > ambience > effects. Narration, source dialogue, music and SFX have separate licensed assets and lanes. Looping music without license is blocked. No impersonation or unconsented voice cloning. No fixed loudness target claimed universally optimal; record actual peaks, loudness and a listening check. Silence can be intentional; only unexpected gaps fail.

## Content quality vs manipulation
Watch-time optimization cannot rewrite evidence or add misleading hooks. Scene changes serve comprehension, not an arbitrary speed. Engagement claims must distinguish measured owner-retention from inferred competitor/public view counts. Expert status requires real domain output review, not 144 registry entries.

## Required release evidence
Three actually rendered CPU-only original examples (Hindi/Hinglish Cricket Short, English NFL analysis Short, accurate Technology screencast/video) are Launch exit fixtures; Ultimate requires a reviewed short AND long-form golden sample per domain before marking it expert. These are future implementation acceptance requirements, **not samples already produced**.
