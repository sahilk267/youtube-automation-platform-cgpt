# CORE-22 — Reactions, Reuploads, Green Screen and Source Footage (v3.0 NORMATIVE)

**Never auto-download and repost a third-party viral video merely because it is public.** Distinguish media rights, monetization originality, factual context and platform tooling. An AI voiceover, crop, split screen or face overlay alone supplies no automatic copyright license and no guaranteed monetization.

## Intake classifications
1. `OWNER_OWNED`: original owned clip, recorded/owned media and all embedded audio/music rights verified. Allowed for automation subject to factual QC.
2. `EXPLICIT_LICENSE`: permission/license evidence stored with territory, purpose, expiration, editing, monetization, underlying soundtrack and sublicensing limitations. Allowed only within scope.
3. `PLATFORM_NATIVE_REMIX`: eligible YouTube Remix/Green Screen source using **supported YouTube creation tools**, not a general download-and-reupload license. Manual Studio/mobile handoff if no documented official interface; recheck source restrictions/deletions.
4. `LEGAL_EXCEPTION_REVIEW`: third-party excerpt with proposed criticism/commentary or fair-use/fair-dealing argument. Case-specific human legal/editorial assessment; AI cannot certify clearance; default HOLD.
5. `UNKNOWN_OR_DENIED`: do NOT include video/audio. Use original diagram, original recording or licensed alternative; preserve research reference metadata only.

## Source-to-commentary map: required for every excerpt
Record source URL, uploader, original full context and date, file digest where legitimately acquired, excerpt `in_ms/out_ms`, rights-decision ID, source speech transcription, quoted propositions, contextual risk, `commentary_segment_id`, exact new insight or critique, visual annotations and publication risk. Forbidden: clip excerpt without meaningful independent insight; invented on-camera creator; hidden watermark removal; license evasion; deceptively edited public speech; undocumented source media download.

## Editorial workflow
`intake -> media/source verification -> rights class -> contextual fact check -> independent thesis -> excerpt-to-analysis map -> own narration -> permitted excerpt(s) + original diagrams -> machine QC -> owner full watch-through -> optional approved export/publication -> ongoing rights/correction monitoring`.

**Output guards:** In-app remix export is a **manual platform workflow** unless a future legitimate API is confirmed and authorized. If owner has no on-camera footage, do not generate a fake owner face. Source-restriction changes invalidate downstream rights approvals. Reaction style is optional; originality may be achieved with footage-free source discussion and diagrams. Publish decision is not based solely on an LLM 'transformative' score.

## Official sources to re-verify at implementation
- YouTube channel monetization, inauthentic/reused content: https://support.google.com/youtube/answer/1311392
- YouTube Remix and limitations: https://support.google.com/youtube/answer/10623810
- YouTube video upload API: https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
Research checked 2026-11-11; future changes override archived wording.

**Mandatory execution edge:** `CV3-08 ASSET_BUILD` depends on `CV3-07 SOURCE_CLIP_REVIEW`. With no third-party clips, the stage must persist `NOT_APPLICABLE` after scanning all shots; merely omitting the stage is not sufficient. With any third-party clip, a reviewed `ReactionClipMap` is required before asset creation.
