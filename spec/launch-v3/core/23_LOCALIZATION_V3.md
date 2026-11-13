# CORE-23 — Localization, Voice, Captions and Region Publishing (v3.0 NORMATIVE)

## Variant planning
A master verified story has one provenance graph. Each target `locale_id` produces a `LocalizationVariant` with: audience fit, source language, translated and culturally adapted script, verified terminology and entity names, unit/currency/date conversions, localized metadata, voice persona/accent/license, audio, captions, independent on-screen text, visual adjustments, timing and a separate approval revision/hash. Language is not the same as region. Example: `hi-IN` with Hindi spoken narration and Hinglish audience vernacular; `en-US` with American football terminology. No universal one-script-fits-all claim.

## Deterministic localization pipeline
Claim-locked master -> locale relevance decision -> intent-preserving translation -> glossary/attribution/number verification -> speech synthesis or imported approved recording -> pronunciation human spot check -> measured word or phrase timing -> native-script subtitles -> translation of overlaid text/graphics/source cards -> resize/recompose timeline -> localized QC -> human approval -> export/publish depending on actual account features. Corrections invalidate every affected derivative locale and the related publish approvals.

**Text processing:** exact locale tag (BCP 47); separate RTL/bidi and script fallback; never render Hindi via Latin-only font; avoid automatic metric conversion errors; time zone is explicit for sports; do not translate copyrighted direct quotes without clear labeling. Provide captions even if dubbing fails: `VOICE_NOT_AVAILABLE` is separate from `CAPTIONS_READY`.

## Publishing support
A) One video with alternate audio tracks is supported for eligible YouTube accounts via Studio; verify Advanced-feature status and audio duration requirements. Do NOT assume an official API endpoint to upload arbitrary additional audio tracks. `NEEDS_STUDIO_HANDOFF` is an allowed terminal step with an operator checklist.
B) Separate region/channel upload only with owner policy and differentiated value; check duplication and channel originality.
C) YouTube automatic dubbing may require manual human assessment of names, claims and accents; don't silently accept incorrect tracks.
D) Localized metadata via supported API or manual Studio path is capability-gated, as are localized thumbnails.

References checked 2026-11-11:
- https://support.google.com/youtube/answer/13338784
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- https://developers.google.com/youtube/data/reference/rest/v3/captions/insert
