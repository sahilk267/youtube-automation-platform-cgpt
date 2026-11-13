# ViralOS M2.1 — Automated Creative Draft + Measured Voice Segments

**Version:** 0.4.0-dev | **Scope:** additive to runnable M0–M3 + M2 Studio v0.3; **status:** CPU technical preview, NOT publish ready.

## Reality / verification boundaries

This is a *deterministic, script-based creative assistant*, not a domain-expert autonomous video director or a general-purpose AI filmmaking model. It extracts sentences/phrase blocks from the **current author-supplied script** and builds a limited HOOK → EXPLANATION → PAYOFF video plan. It never invents an NFL result, player statistic or citation. Facts remain the author's responsibility and other claim/evidence reviews remain mandatory.

**Narration alignment = measured segment boundaries.** Each sentence/shot gets an individually uploaded or optionally locally synthesized WAV; the system normalizes to 16kHz PCM16 mono, measures sample frames, adds 180ms padding, produces precise segment-boundary captions, and synthesizes a matching continuous voice WAV. **It does not identify individual spoken words, detect whether the speaker read the supplied text correctly, or provide forced word-level alignment.** Segment-level timestamps can be precise while spoken content remains unverified. Human listening review required.

**Multilingual** means an owner can supply a separate reviewed complete script (`locale`, `translated_script`, `locale_reviewed=true`) and matching voice segments, then render separate localized video/text tracks. It does **not** auto-translate, auto-dub, provide lip-sync, or validate a translation's semantic accuracy. At present only a subset of installed OS fonts may support some locales; native glyph validation on each Windows locale is pending.

**Optional Piper:** if operator installed Piper executable + licensed voice model, `VIRALOS_PIPER_EXE`, `VIRALOS_PIPER_MODEL`, `VIRALOS_PIPER_MODEL_RIGHTS_OK=1` and **matching** `VIRALOS_PIPER_LOCALE` are configured, the app may synthesize each segment locally and measure audio. No silent model download, no voice cloning. Test suite contains a **mocked Piper adapter test**, not a live Piper-model performance validation.

## UX: local desktop/browser workflow

1. In Launch dashboard create channel/project and save an original script. Use owner-supplied evidence and link reviewable factual claims when applicable.
2. In `M2.1 Automatic Creative Draft`, enter original channel locale, or a target locale plus **full owner-reviewed translated narration**. Create draft. Its segments show exactly what will be narrated.
3. Record speech WAV for each segment, press `Upload scene N WAV`, OR configure licensed matching-language Piper and press `Generate using opt-in local Piper`.
4. Press `Assemble measured timeline`. The app creates immutable, project-bound narration, measured segment captions and a validated M2 studio plan. No script text is secretly replaced.
5. Optional: download measured, per-segment sidecar SRT from `/api/projects/{id}/director/plans/{plan_id}/captions.srt` (no word-level timing). Use existing **M2 Studio** queue/run buttons to render CPU MP4. Watch the entire video and inspect QC report. Output remains NOT PUBLISH READY.
6. To change source script, save a new script revision and generate a new M2.1 draft. Old drafts/plans become stale. The release does not overwrite global `voice.wav`.

## API contracts

| HTTP | Route | Description |
|---|---|---|
| GET | `/api/director/capabilities` | Supported and unsupported features |
| POST | `/api/projects/{id}/director/drafts` | Typed `{locale, translated_script?, locale_reviewed}`; bound to latest script/project revision |
| GET | `/api/projects/{id}/director/drafts/{draft_id}` | Human-readable segments, upload states |
| POST | `/api/projects/{id}/director/drafts/{draft_id}/voice/{index}` | Multipart audible owner WAV; one per shot |
| POST | `/api/projects/{id}/director/drafts/{draft_id}/synthesize-piper` | Optional local licensed TTS, matching model locale only |
| POST | `/api/projects/{id}/director/drafts/{draft_id}/assemble` | Verify every WAV and generate project-bound Studio plan + voice |
| GET | `/api/projects/{id}/director/plans/{plan_id}/captions.srt` | Download bounded, measured scene-segment caption file |
| POST | `/api/projects/{id}/studio/queue` | Existing stable queue; hashes plan/script/voice |
| POST | `/api/studio/run-next` | Existing CPU video render and technical QC |

Draft validation: 2–12 segments; each segment maximum 160 visible caption chars; narration 0.7–11.4 seconds per segment; after 180ms pad each shot <= 12 seconds; total <= 90 seconds. Full script paragraphs split by sentence and at most 19 words per segment; script with >12 chunks fails **without silently losing the remainder**. Unsupported script lengths require another project or future long-form processing.

### Persistence & compatibility

`sql/006_m21_director.sql` is a **new additive migration** (001–005 are unmodified). Tables:
- `m21_director_drafts`: script version, project revision, locale, reviewed source text hash, segment list, status.
- `m21_voice_segments`: per draft/index, local WAV hash, measured frames, source kind owner WAV / opt-in Piper.
- `m21_plan_audio`: immutable bound voice WAV hash, sources hash and plan mapping.

`StudioPlanIn` accepts a new caption provenance: `SEGMENT_TIMED_MEASURED` (never represented as `OWNER_TIMED` or phoneme alignment). Existing studio routes prefer plan-bound narration if present; otherwise they retain the legacy owner-imported `voice.wav`. Old Studio plans remain valid and unchanged. Original source-linked claim IDs are **not fabricated by the draft generator**. Exact unambiguous source-script quote spans may be transferred into their matching shot; ambiguous or translated spans remain unlinked and require manual editorial mapping. Presence of a link does not independently verify the claim.

## Failure policy and data safety

- Missing script, unknown project, wrong draft/project pair, stale script/revision → 404/409.
- Translated script without owner review, alternate locale without translation, overlong script → 422.
- Unsupported/oversized/silent WAV, per-shot duration outside limits → 413/422.
- Missing or tampered source WAV, absent FFmpeg, incomplete voice segments → fail closed; no fabricated audio or captions.
- Duplicate unchanged director draft returns same ID; voice segments may be revised only before assembly. Assembled audio is immutable and hash checked.
- Rights ownership, native speaker fluency, factual truth, copyright, YPP policies and actual publication are **not** inferred from tests. YouTube uploads still disabled.

## Technical validation

Use `python -m pytest -q` and `python tools/verify_package.py`. Tests include original-language + Hindi localization, tampered audio, cross-project isolation, empty/silent/invalid input, script revision invalidation, measured per-shot audio and real H.264/AAC render. The Piper test is a mock adapter test; voice quality and model licensing require real review.

**Demo:** `examples/m21_spoken_demo.mp4` uses local eSpeak TTS purely for *technical demonstration*, with a hypothetical original NFL-style field diagram. It is **not** broadcast footage, realistic voice quality, match data or creator-ready video.

## Known important omissions — do not mark as complete

- Real autonomous domain-specific artistic direction beyond simple script segmentation and role cues.
- Word-level ASR alignment; multilingual translation QA; real native voices for all languages.
- Sophisticated sound design, footage editing, genuine reactions/remixes, GPU image/video generation.
- Full fact retrieval, official NFL/cricket data/licensing, visual factual cross-checking.
- Actual Windows i7/32GB performance benchmarks; human fully watched video-quality approval.
- OAuth authorized uploads, copyright/monetization approvals, YouTube revenue results.

**Next engineering gate:** M2.2 real source/claim-aware creative planning, on-screen media dependency graph, optional word-level forced aligner, nonredundant script/visual variation, domain-specific human golden-set evaluations, explicit Windows quality benchmarking before public publishing.
