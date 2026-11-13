# CORE-07 — Creator Studio, Cinematic Prompt Intelligence and Media Pipeline

## 7.1 Produce original, source-traceable video, not a generic automated reupload

Default local CPU output: primary-source backed script -> original diagram/chart/animation/original screen capture or footage with explicit rights -> license-compatible TTS/own narration -> accurate subtitles -> FFmpeg video and audio mix -> machine QC -> editorial review -> export. Future GPU adds optional `ai_image` and `ai_video` asset generation, **not** a replacement for the source provenance or approval pipeline. CPU mode must generate watchable 9:16 and 16:9 without ComfyUI.

## 7.2 ScriptSpec, Storyboard and ShotSpec

`ScriptVersion`: immutable script text, language, channel, voice style, narrative plan, factual `claim_id` ranges with link to exact source version, cited computed numbers, audience intent, policy status, word count, target format. Distinguish spoken text vs on-screen text and optional illustrative text.

`SceneSpec` (canonical JSON schema in contracts): `scene_id`, `project_id`, `script_revision`, `purpose`, `source_claim_ids`, `visual_type`, `subject`, `setting`, `composition`, `lighting`, `camera_motion`, `subject_motion`, `duration_ms`, `fps`, `aspect_ratio`, `reference_asset_ids`, `continuity_profile_id`, `dialogue_segment_id`, `audio_mix`, `subtitle_policy`, `model_profile_id`, `seed`, `quality_requirements`, `rights_record_ids`, `synthetic_disclosure`, `editorial_status`. Every scene's provenance and intended semantics must survive hardware upgrades. `duration_ms > 0`, source-claims must exist in research dossier, no unbound third-party media.

`RenderManifest`: source artifact hashes, scene ordering, track timing, TTS/STT configs, FFmpeg command/filtergraph version, input digests, output checksum, measured media properties, QC results, model parameters, working hardware and attempted revisions.

## 7.3 Media source preference hierarchy

1. Original self-recorded demos, screen captures or vector/animated diagrams, factual charts and typography.
2. Properly licensed footage, public domain/eligible licensed media with tracked attribution/restrictions.
3. AI illustrations when context permits, with provenance and truthful synthetic label; news recreations clearly identified.
4. Other footage only after separate rights/legal and reused-content policy review. No assumption “under 5 seconds” or “crediting owner” grants rights.

## 7.4 CPU scene compiler and FFmpeg renderer

Given SourceClaims + SceneSpec list:
1. Build scene timeline with millisecond precision, tracks: `background, diagrams, media, overlays, subtitles, narration, music/ambience`.
2. Normalize audio sample rate (recommended 48 kHz), preview loudness, avoid clipping; do not ship music with unknown rights.
3. Generate SVG/PNG diagrams (pitch, field, flowchart, science, maps) from deterministic data with explicit unit scales; include captions and source note for numeric charts.
4. Encode video using locally supported FFmpeg codecs with explicit resolution/framerate/pixel format: Launch profiles 1080x1920 30fps vertical and 1920x1080 30fps horizontal; permit 720p performance fallback only after user choice and manifest entry.
5. Add animated pans/zoom, cuts, b-roll switches and source cards with deterministic timing; do not rely on unsupported text filters/fonts without preflight.
6. Embed subtitles or export `.srt`/`.vtt`; validate glyph coverage for Hindi/English, contrast, safe areas and line overflow.
7. Write output to temporary file; probe all tracks; verify length and hashes; atomic rename to immutable published candidate path.

A CPU-only computer can produce high-quality diagram/audio-based videos, but speed and quality depend on actual benchmark; do not claim all 1080p effects real-time.

## 7.5 Cinematic Prompt Intelligence Engine (CPIE) components

| Component | Input | Deterministic contract / output |
|---|---|---|
| Script-to-Scene Planner | Verified script, domain policy, runtime budget | Ordered scenes tied to claims, audience intent and duration |
| Visual Director | Scene purpose and source truth | Visual modality selection, responsible depiction constraints |
| Cinematographer | Scene and visual grammar | Shot size, composition, lens language, lighting, camera movement, transition |
| Motion Director | Subject and scene continuity | Physically plausible subject/camera action, velocity intent, shot boundaries |
| Continuity Keeper | Reference pack, previous scene outputs | Named character/prop/location IDs, appearance/accessory/state invariants |
| Factual Visual Critic | Verified evidence, visual depiction | Reject anachronisms, misleading staged news, wrong sporting field/data |
| Model Capability Adapter | SceneSpec + installed model manifest | Supported nodes/parameters, aspect/duration budget, precise unsupported reason |
| Prompt Compiler | Domain visual policy + scene + model adapter | Model-specific positive/negative prompt and control images, provenance |
| Generation Experiment Lab | Prompt, seed, parameters, artifact hash | Variant records and human-preference outcomes, not self-reported quality |
| Temporal Quality Lab | Generated frames and scene requirements | Flicker/morphing/identity drift/text deformation/legibility issue report |
| Export Director | Approved scenes, media effects, music rights | FFmpeg render plan + output QC and disclosure report |

This is one **shared** studio; category plugins supply visual policy templates and validators, not twelve incompatible prompt compilers.

## 7.6 Prompt compiler algorithm (GPU optional)

Input: `SceneSpec`, `DomainVisualPolicy`, `ModelManifest`, `CharacterBible`, `RightsManifest`.
1. Refuse missing high-risk source claims, unlicensed reference images, unrealistic model request or unsupported source type.
2. Extract fixed constraints: must retain characters, setting, action, measured geometry, language, labels, truth and privacy.
3. Plan framing, camera movement, lighting, motion extent, shot duration, visual intent, consistent reference assets.
4. Query model capability registry: supported text/image/video mode, resolution, max duration, control inputs, precision, VRAM/RAM estimate, license. If no compatible runtime => `WAITING_FOR_CAPABILITY` with possible CPU illustration alternative **only with user approval for modality change**.
5. Compile model-specific text prompt and structured settings; preserve original **semantic SceneSpec** as canonical independent of model.
6. Generate short shots with captured seed/model digest/software version and attempt index; no claims of bit-identical GPU output.
7. Inspect frames and temporal consistency, overlay text separately instead of expecting perfect text generation; test any historical/scientific accuracy visually.
8. Score using domain-specific rubric and human review for serious reconstructions; regenerate targeted shot at bounded attempt count, never infinite silent retries.
9. Approve chosen artifact in asset manifest, discard/retain failed attempts according to storage policy.

## 7.7 Scene continuity objects

`CharacterBible`: stable character ID, authorized identity/reference rights, age category if relevant, wardrobe, hair/style, accessories, environment, proportions, optional pose/control maps; no fabricated depiction of actual identifiable person in apparent real-news event without explicit reconstruction disclosure/rights review. `LocationBible`: time/era, geography, layout, lighting/weather constraints, historical evidence. `MotionPlan`: camera path, subject motion, beginning/ending pose, action limits, physics constraints. New shots use previous accepted reference assets, not merely repeated text prompts.

## 7.8 Media and AI safety gates

- Scientific animation: label illustrative vs measured, avoid invented phenomena or unsupported data.
- Historical reconstruction: period verification, disclose uncertainty and AI visualization where relevant.
- News/politics: cannot misrepresent real footage, speeches, public events; human signoff for synthetic likeness.
- Sports: prefer original tactical diagrams instead of game/broadcast highlights; scoreboard/stat must match source/version.
- Finance/health/career: avoid synthetic authoritative testimonial and unsupported promises.
- Copyright: rights checks on music, footage, models, fonts, textures, TTS voice, reference images.

## 7.9 Quality control acceptance criteria

Machine: ffprobe reads stream; correct aspect ratio, positive duration, recognized codec, audio stream when narration expected, audio not entirely silent, no empty input scenes, subtitle file nonempty with consistent timecodes, full-frame scene limits, media hashes match, source cards generated as planned. Video QC uses sampled frames to flag unusual blackouts, output FPS stability, audio peak, captions offscreen, video duration within configured tolerance (default ±2 sec for short, ±3% for long, with report). These rules are screening heuristics, not substitutes for human watching. Human review: factual depiction, engaging but truthful hook, continuity, comprehensibility, natural voice, color/contrast, rights/disclosure.

## 7.10 Editing and correction-aware rerender

If one source claim corrected, compute dependency graph from Claim -> ScriptSegment -> SceneSpec -> RenderManifest; rerender only affected scenes and regenerate final export. Store old versions and approved version IDs. Cancel stale scheduled upload if approval invalidated. No overwriting external published video; owner must choose correction or replacement.

## 7.11 Media tests

- Hindi glyph coverage and caption line breaking; English code snippets correct in tutorials.
- Audio off by 350ms, mismatched subtitle, missing scene visual -> fail QC.
- Unlicensed image reused through scene cache -> fail rights gate.
- GPU image-to-video unsupported with CPU-only provider -> held; CPU export still functional.
- Source changed after initial storyboard -> invalidated approval and source card recomputed.
- 4:3 or 9:16 unsupported by model -> explicit alternative and user review, not cropped silently.
