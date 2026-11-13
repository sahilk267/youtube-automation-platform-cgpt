# ViralOS Content Production Intelligence — v2.2 gap audit & implementation blueprint

**Prepared:** 2026-11-09  |  **Basis:** local inspected `ViralOS_Combined_v2_1`, including `core/06`, `core/07`, `core/09`, `core/18`, `core/20`, `contracts/SceneSpec.schema.json`, `configs/workflow_dag.json`, 12 domain research playbooks and current YouTube public policy/help pages.  
**Type:** proposed *production specification addendum*; it is **not incorporated** into existing Launch/Ultimate/Combined ZIPs and is **not running code**. Existing documents remain controlling unless this addendum is formally adopted with versioned changes.

## 0 — Definitive audit decision

Current v2.1 **has** canonical research/evidence contracts, basic narrative beats, script-to-scene/SceneSpec, media rights, FFmpeg audio/video/subtitle layer composition, futuristic image/video model adaptation, limited retention learning and explicit publication safety gates.

It **does not specify enough** to guarantee what appears on screen for each spoken phrase, how multilingual audio/subtitles/on-screen typography synchronize, how real-world clips become original commentary instead of minimally edited copies, or how 12 categories differ as video *directors*. Those are scope gaps, not proof the existing research architecture is defective. No amount of documentation guarantees zero hallucinations or legal clearance; required objective tests and owner approval remain mandatory.

| Gap code | Missing or underspecified contract | Proposed canonical owner | Blocking gate / validation |
|---|---|---|---|
| CP-001 | Audience promise and narrative beats tied to timed evidence/visual timeline | `creative/narrative_director` | Each key beat has purpose, facts, payoff and shots |
| CP-002 | Typed `VideoTimeline`, lanes, transitions, compositing, safe zones | `creative/timeline_compiler` | deterministic scene duration/overlap test |
| CP-003 | Overlay animation geometry/typography and text hierarchy | `creative/overlay_director` | mobile legibility, occlusion and glyph test |
| CP-004 | Word/phrase narration alignment and subtitle profiles | `creative/speech_alignment` | measured speech-to-caption sync |
| CP-005 | Region-localization package with dubbing, text, graphics and title versions | `localization/variant_builder` | locale review and no source-claim mutation |
| CP-006 | Human review for names, quotes, idioms, native terms and AI-dub errors | `localization/linguistic_qc` | approval before exporting sensitive locale |
| CP-007 | Speech style, pronunciations, voice identity rights and mixing | `audio/voice_director` | pronunciation and intelligibility listening test |
| CP-008 | Music/SFX selection, sidechain ducking and audio rights | `audio/sound_director` | rights and loudness QA |
| CP-009 | Third-party clip rights, reuse originality, and official remix status | `media/clip_rights_adjudicator` | BLOCK until lawful basis and independent monetization review |
| CP-010 | Clip transcript/context, critique mapping, source link, substantive transformation | `creative/commentary_clip_director` | owner review of actual transformed output |
| CP-011 | Category-specific VIDEO director profiles, not just research playbooks | `domains/*/visual_policy` | 12 visual golden samples |
| CP-012 | Format grammar: news brief / sports reaction / lesson / documentary / review | `creative/format_director` | at least one approved sample each |
| CP-013 | Visual coverage ratio: shot backed by spoken claim/context, not random stock b-roll | `creative/evidence_visual_matcher` | unsupported illustrative-shot flag |
| CP-014 | Vertical and horizontal reframe with faces, scoreboards and subtitles | `creative/reframe_director` | device viewport safe zone snapshot QA |
| CP-015 | Prompt-to-asset fallback for CPU now; GPU/video generation later | existing `compute + creative/prompt_compiler` | no unsupported claim of photorealistic output |
| CP-016 | Fact/correction dependency chain across every locale & render variant | existing `evidence/invalidator` | corrected fact invalidates localized dubbing/overlays |
| CP-017 | Scene-by-scene engagement diagnostics and creative hypothesis registry | `audience/creative_lab` | only observed analytics; control for uncertainty |
| CP-018 | Storytelling ending and next-video handoff, platform end screens | `creative/ending_director` | payoff answered, outro not deceptive |
| CP-019 | Explicit video-level content novelty assessment across channels | existing `audience/portfolio` | near-duplicate review; no mass templating |
| CP-020 | Distinct `audio-language track` vs localized separate videos strategy | `publishing/localization_adapter` | account feature capability check; no imaginary API endpoint |
| CP-021 | Accessibility: caption readability, color contrast, audio description needs | `creative/accessibility_qc` | sample caption/audio review |
| CP-022 | Clip remix attribution and original deletion/restriction lifecycle | `publishing/remix_status_tracker` | manual/source-tool status and update notice |
| CP-023 | Audio-video render approval by full watch-through, not just ffprobe | `creative/editorial_preview` | owner approves actual final file |
| CP-024 | Source-led shot storyboard not derivable from a single generic prompt | `creative/shot_director` | each shot has evidence/illustration class |
| CP-025 | Detailed release/profile feature flags prevent partial v2.2 from being claimed implemented | `core/release_controller` | feature is SPECIFIED until tested |

**Uniqueness:** Do not create 12 separate FFmpeg, subtitle, asset-rights, citation, prompt-compiler, upload, or audio-mixer implementations. These are shared services. Domains supply *policy, vocabulary, and transformations* through typed profile interfaces. Sports remains **one domain** with cricket/NFL/MLB/NBA/soccer adapters.

## 1 — Human-visible production contract

Every video must have a `CreativeBrief` recording viewer intent, audience sophistication, locale, duration budget, original angle, viewer promise, factual scope, format, narrator persona, audiovisual treatment, language plan, rights budget and measurable payoff. The generated `NarrativePlan` breaks a promise into **beats**, each with a reveal, evidence, audience question and audience takeaway. A beat is not synonymous with a fixed 2-second cut. High-information documentary sources may need a 10-second hold, while fast sports stats might benefit from short cuts. No fixed cut cadence is assumed optimal.

### 1.1 Shot and timeline model

Each shot binds exactly these fields:
- `shot_id`, `parent_scene_id`, `start_ms`, `end_ms`, `duration_ms`, `format`, `region_variant_id`, `language_variant_id`.
- `spoken_segment_ids`, `claim_ids`, `asset_ids`, `asset_rights_decision_ids`, `factual_role` in `PRIMARY_EVIDENCE, ORIGINAL_CAPTURE, ORIGINAL_DIAGRAM, LICENSED_BROLL, RECONSTRUCTION, ILLUSTRATION, COMMENTARY_WINDOW`.
- `base_visual` with crop/frame, motion plan, playback speed, color treatment; content must preserve truth if underlying clip is a real event.
- `layers[]` with z-index, placement constraints, entry/exit animation, alpha, scale, in/out, text id, font fallback, caption/hierarchy and maximum overlap.
- `audio_tracks[]`: narration, original excerpt where permitted, ambience, music, SFX; relative loudness, fade and ducking.
- `transition`, `next_shot_reason`, `accessibility`, `source_card`, `disclosure`, `qc_status`, `approval_revision_hash`.

`VideoTimeline`: one global timebase, immutable render graph hash, scene durations, global style theme, chapter schedule, end-screen reserve, all variant links. Validate no gaps, duplicate timestamps, impossible resource conflicts, offscreen overlay, caption overlap, silent dialogue, expired rights or unreferenced research evidence. Actual rendering uses FFmpeg and caches deterministic graphics/assets. This is a **proposed extension** of existing `SceneSpec`, not a replacement or incompatible project model.

### 1.2 Seven main on-screen layers (z-order by policy, not absolute)

1. **Background / canvas:** brand colors, documentary background, original demonstration, or scene environment.
2. **Primary visual:** approved full-screen footage, software capture, chart, diagram, original gameplay or abstract model.
3. **Supporting insert:** picture-in-picture witness/source comparison, reference photo, historical side-by-side, alternate angle with cleared rights.
4. **Evidence and graphic overlay:** citations, scoreboxes, arrows, highlights, units, equations, sourced quote cards, geography/time cues.
5. **Captions:** accurate per-language dialogue captions, with strong contrast and device-safe coordinates; not mandatory burnt into every format when optional caption track is better.
6. **Brand and disclosure:** unobtrusive channel marker, visual reconstruction/AI label if needed, creator commentary indicator.
7. **UI-safe margins / end-screen reserve:** adapt to platform player and real device screenshots; never assume a permanently fixed Shorts UI safe-zone size.

Overlay policy: Every animation must explain information or emphasize a relevant event. Avoid simultaneous unrelated captions, moving scorebars and loud effects. Use native-script font fallback for Devanagari, Latin and other locales. Text overlays must be semantically translated; *do not* burn Hindi labels into the sole global master if an English version is also needed. Preserve clean graphics and relayer text per locale.

### 1.3 Story structures by video format (illustrative defaults; test and adapt)

**Short-form, 30–60 seconds**: 0–3s direct evidence-backed hook; 3–10s context/stakes; 10–35s primary demonstration/analysis with visual proof; 35–50s takeaway/payoff; remaining time for relevant next-step question, concise CTA or follow-up. No intro logo animation by default. For 15-second Shorts compress without fake urgency. For 3-minute Shorts, use more narrative beats rather than simply slowing the same story.

**Long-form, ~6–12 minutes as an example, not a rule**: 0–20s promise and relevant visual; 20–60s context; then 3–6 substantive chapters; halfway examine alternative evidence or practical test; end with conclusion and what remains unknown; place relevant next-video suggestion near end. YouTube allows end screens in the last 5–20s for videos >=25s, subject to availability, so reserve a clean composition when applicable. A documentary investigation may demand longer context and less artificial fast editing.

**Reaction/critical review**: begin with the exact question to be assessed; show only contextually necessary excerpt(s) where rights/legal basis is established; pause/freeze and provide *original criticism* with annotations, independent data, comparisons or demonstrations; return to source only when necessary; conclude with original analysis and transparent uncertainty. Not a contiguous republishing of most of the source video.

### 1.4 Audio, captions and accessibility

Voice profile: language, regional accent, speed, tone, punctuation pause tags, proper-name pronunciation lexicon, approved/licensed TTS voice, forbidden impersonations and human pronunciation reviewer. Post-process silence and breaths conservatively; avoid robotic forced speed. Segment narration per scene with sample-accurate alignment. Mix coherent voice first, SFX second and music last; duck music under speech. Music/sound/voice clips must each have rights records. Generate accurate SRT/VTT subtitles, optional accessible CC, and independent animated/emphasis text overlays. Do not conflate *subtitles* with decoration or assume autogenerated captions are flawless. Spoken words, on-screen quotes and attribution must remain distinguishable.

Export/QA: use YouTube-compatible progressive MP4/H.264, 48 kHz audio with supported codec and correct FPS/color; choose CPU-friendly profiles based on an actual device benchmark. FFprobe checks and caption geometry checks are necessary but not sufficient: human preview must watch every format/locale representative before release.

## 2 — Language & region intelligence

**Different locale ≠ simple direct translation.** A Video Locale Pack is a versioned derivative of a single evidence-locked story: `master_story_id`, `locale_id` (e.g. `hi-IN`, `en-US`), target cultural context, source language, translated/rewritten script, localized glossary, number/unit/date formatting, voice profile, audio file, caption track, text overlays, search title, description, thumbnail texts, legal/reconstruction labels, QA report and final render id.

Workflow: choose master story -> lock verified claims -> region suitability check (sports leagues, legal/regulatory issues, cultural sensitivities) -> translate meaning not literal wording -> human check named entities, idioms and numeric statements -> produce dialect-appropriate narration -> force-align timestamps -> regenerate text card dimensions/line breaks -> reflow all timeline items -> render locale variant -> separate QA and approval -> publish per chosen strategy -> monitor language-specific results. *Fact changes propagate to every locale and withdraw stale approvals.*

Publishing choices:
A. **One video with multiple audio tracks:** YouTube's multi-language audio feature supports additional tracks on eligible creator accounts, along with translated titles/descriptions and localized thumbnails for long videos. Availability and Studio upload workflow must be checked. Do not invent an API for adding the audio track.
B. **Separate regional videos/channels:** only when audience or content really differs; localize examples, structure and graphics sufficiently and avoid duplicate low-value mass uploads. Track cross-region novelty and policy review.
C. **YouTube automatic dubbing:** may be offered, but errors in proper names/idioms and eligibility mean it needs manual language QC and monitoring; do not assume the owner can edit the automatic dub.

Recommended owner-first tests: one primary locale, then one second language on a rights-safe evergreen video; measure watch time by audio language *if accessible*. For India cricket, use `hi-IN` conversational Hindi/Hinglish and select English adaptation by evidence of demand. For US NFL, use `en-US` with accurate American football terminology; do not literally translate cricket jargon into NFL vocabulary.

## 3 — Remixes, reactions and third-party viral video handling

**Four-way classification for every incoming clip:**
1. **Owner-original footage:** use rights and evidence records, validate original recording, create derived commentary cuts.
2. **Explicitly licensed footage:** record exact rights scope, allowed territory, term, modifications, sublicensing/music restrictions, model-training restrictions, and retain permission evidence; still check channel originality/YouTube reused-content policy.
3. **YouTube in-app Shorts Remix/Green Screen:** eligible source and tool must permit action; use platform UI and source attribution. This is not a universal license to download the original clip and reupload it externally. Upstream deletion/restriction can invalidate remixes. Do not claim a general automated official API exists.
4. **Unlicensed third-party clip with potential commentary exception:** no blanket approval. US fair use and applicable regional law are case-specific. If a relevant legal basis cannot be established and reviewed, block footage; use approved stills only where lawful, a paraphrase, own footage, charts or original diagrams instead. Human reviewer required for uncertain commercial footage and sports broadcasts.

**Fully documented reaction pipeline, with fail-closed decisions:**
- `intake`: source URL/uploader/date, original publication, original context/full-length source, source hash, platform rights/remix status and known restrictions.
- `transcribe`: exact speech/timestamps and language with context validation; sensitive quotes get manual review.
- `research`: fact-check substantive claims, compare independent sources, identify what new information this video contributes.
- `rights`: decide media assets that may actually be included; do not confuse license with reused-content monetization approval.
- `commentary`: write *original thesis* with at least one meaningful added explanation/criticism/external test, not just a play-by-play paraphrase of everything already visible.
- `clip_map`: each licensed/exceptions-reviewed excerpt time range to specific spoken critical analysis and visual annotation; no arbitrary 'safe seconds' threshold.
- `render`: original narrator or original-on-camera reaction (if user provides it), pause, side-by-side original commentary diagrams, voice+captions, source attribution and suitable sound. Green-screen template is optional only where rights/platform feature permits.
- `review`: review full source and full final edit for context, genuine transformation, attribution, copyright/reused-content/ad suitability, channel-level repetition, defamation/privacy and sponsor/AI disclosure.
- `publish`: authorized UI Remix where appropriate, or export compliant owned/licensed independent edit; YouTube approval remains non-guaranteed.
- `monitor`: watch rights claims, source removal, corrections, eligible reuse revocation, appeals and policy updates; flag affected published variants.

**Important:** Simply adding synthesized voiceover to a popular video or placing one's face over it may still be minimally changed reuse. Sports broadcast reuploads are especially high risk. Never remove watermarks to conceal origin, alter clips to defeat Content ID, or use misleading synthetic footage as real events.

## 4 — 12 domain-specific VIDEO director profiles

The following are proposed examples/creative rules. They do not imply source access, actual clip rights, test results or guaranteed retention.

### 4.1 Sports OS — Cricket (India), NFL/MLB/NBA/soccer (global)
- **Promise/hook:** an accurate game-changing question, verified decision, surprising statistic or technical play; avoid fabricated controversy.
- **Primary screen:** original pitch/gridiron/baseball diamond/court/field SVG; verified score/time clock, arrows, player positions and statistic comparison. Match footage only with accepted rights/legal review.
- **Voice:** Hindi/Hinglish cricket terminology for `hi-IN`; English broadcast/tactical terms for `en-US`. Do not confuse overs with time or sacks with turnovers. Team/player name pronunciation lexicon.
- **Beats:** moment -> essential game situation -> draw field -> animate player movements/decision points -> compare outcome and alternative -> takeaway; preview and recap are distinct modes.
- **Retention:** open tactical loop resolved by a clear diagram; use short stat callouts only when viewer can parse units; for a match recap, explain *why* a result happened.
- **Ending:** answer tactical question, optional next matchup/series continuation; do not claim certain predictions.
- **Rights:** league clips, logos, stadium audio and stats each have distinct conditions. Never assume copyrighted highlights may be reuploaded simply with narration.
- **Golden tests:** wrong score corrections, cricket overs 17.3=105 legal balls, NFL possession/clock and DST, MLB innings/pitcher name confusion.

### 4.2 Newsroom OS — investigative accountability
- **Hook:** one public-interest question, contextualized statement, or discrepancy; avoid claiming guilt up front.
- **Visuals:** original full-speech reference card with exact timestamp, time-indexed two-column quotation comparisons, public records, law/budget charts, historically grounded timelines, relationship graph with documented edges, low-distraction archival images.
- **Voice:** calm, precise and visibly separates verified statement, interpretation, rebuttal and uncertain evidence. Present material contradictions alongside changed circumstances and context.
- **Beats:** full context -> atomic claim -> historical record -> actions/outcomes -> competing evidence -> remaining questions and proportionate conclusion.
- **Retention:** consequential revelation follows evidence, not speculation; source card can be held long enough to read rather than cut too fast.
- **Ending:** what documents establish, what they don't, right of reply/correction avenue and sources.
- **Rights:** news footage not automatically public-domain; never use fabricated photorealistic scenes as real original recording. Editorial/legal review mandatory for allegations.

### 4.3 Science OS — research explainers
- **Hook:** a surprising phenomenon with accurate caveat; avoid headline that overstates single study.
- **Visuals:** original mechanism animation, controlled comparison, units/axis-labeled graphs, readable paper citation cards, observation vs simulation split screen.
- **Voice:** clear definitions before jargon, uncertainty naturally explained, numeric values carefully paced.
- **Beats:** question -> mechanism -> primary study design -> evidence and effect size -> contrary evidence/limitations -> practical meaning.
- **Retention:** successive 'how/why' questions answered with spatial diagrams, without invented experiments.
- **Ending:** consensus vs open research, specific viewer takeaway; no medical treatment promises.
- **Rights:** paper figures/photos have their own licenses; original recreation of charts must remain accurate and cite source.

### 4.4 Technology OS — proof through demos
- **Hook:** a user problem and testable promise ('Does it really run locally?') rather than generic launch announcement.
- **Visuals:** authentic screen recording, workflow steps, benchmark overlay with hardware/version, side-by-side outputs from repeatable same prompt/test, terminal output with secrets redacted.
- **Voice:** concise directions with a beginner track and optional advanced segment; names/versions pronounced accurately.
- **Beats:** claim -> setup -> hands-on test -> measured outcomes -> shortcomings -> who should use it.
- **Retention:** do the real demonstration early; use speed-up only when clearly indicated and not hiding failure.
- **Ending:** reproducible settings, result summary and limitations.
- **Rights:** vendor screenshots/logos/software recordings subject to applicable licenses; don't invent tests.

### 4.5 Business OS — corporate and financial intelligence
- **Hook:** a precise company economics question ('Where does the money come from?').
- **Visuals:** filing source/period card, revenue waterfall, unit economics, audited vs unaudited labels, historical charts, ownership graph with dated documented connections, scenario sliders as illustration not empirical proof.
- **Voice:** explain currency, absolute figures and period, avoid unverified fraud accusations.
- **Beats:** business model -> financial evidence -> driver decomposition -> peer comparison -> risk and alternate explanation -> conclusion.
- **Retention:** progressively reconcile a numerical puzzle, show calculation steps.
- **Ending:** evidence-supported conclusions, biggest open assumption.
- **Rights:** avoid stock footage that implies a claim not supported by records; protect potentially defamatory implications.

### 4.6 Gaming OS — authentic entertainment/strategy
- **Hook:** genuine unusual play, tactic or challenge with clear game title/version.
- **Visuals:** original authorized capture with HUD, game-specific animated labels, map position, replay path, patch note comparison and live reaction from owner if provided.
- **Voice:** matched to entertainment/guide intent; do not fake gameplay achievements using AI shots.
- **Beats:** goal/challenge -> attempt -> unexpected outcome -> mechanics breakdown -> next attempt/lesson.
- **Retention:** meaningful gameplay progression and reactions, less generic stock b-roll.
- **Ending:** honest result, concise next build/strategy and relevant series pointer.
- **Rights:** respect publisher permissions, music licenses and streamer clips.

### 4.7 History OS — archival storytelling
- **Hook:** a historically meaningful mystery or misconception with real records.
- **Visuals:** archive document zoom/citation, chronology, period-accurate map/borders, genealogical or troop movement diagrams where sourced, visually labeled reconstruction vs authentic photograph.
- **Voice:** narrative but context-sensitive; distinguish documented sequence from interpretation.
- **Beats:** historical question -> era/context -> artifact -> timeline -> competing interpretations -> uncertainty-aware answer.
- **Retention:** reveal provenance and contextual consequences, not dramatized fake quotes.
- **Ending:** strongest established facts and archives for deeper learning.
- **Rights:** archives may have scan, museum or photographer reproduction rights; check every asset.

### 4.8 Space OS — observation and scale
- **Hook:** verified celestial event/milestone or scale puzzle.
- **Visuals:** mission map, NASA/agency imagery where permitted, scale annotations, orbit diagrams, simulation labels, actual signal/data vs artistic view split.
- **Voice:** patient cosmic scale and numerical context, no overexcited unsupported discovery claims.
- **Beats:** question -> observation -> mission instruments -> physics/geometric explanation -> uncertainties -> significance.
- **Retention:** gradual zoom revealing real scale without misleading spatial proportions.
- **Ending:** next observational milestone and what remains unknown.
- **Rights:** each agency/image/data license checked; mark speculative renderings.

### 4.9 Learning OS — designed for comprehension
- **Hook:** one concrete learning outcome or problem that viewers can solve by end.
- **Visuals:** whiteboard steps, progressively revealed diagram, highlighted equation, examples/counterexamples, captions that never obscure the problem.
- **Voice:** deliberate pace with wait time for practice; bilingual glossary if needed.
- **Beats:** objective -> prior knowledge -> worked example -> misconception -> guided practice -> solution/summary.
- **Retention:** active prediction/question moments, not artificial rapid cuts; test with actual learning checks when possible.
- **Ending:** answer explanation, practice task and next prerequisite.
- **Rights:** no copying complete third-party courses/slides under vague fair-use claims.

### 4.10 Career OS — local job guidance
- **Hook:** an actionable decision ('Which skill gives better options in this market?').
- **Visuals:** real dated job posting excerpts where permitted, regional salary ranges with sample caveats, skill pathway flowchart, portfolio walkthrough, credential/source verification.
- **Voice:** practical, region-specific, avoids income guarantees.
- **Beats:** goal -> market evidence -> skill gap -> demonstration -> action plan -> caveats.
- **Retention:** visibly build one job-ready sample rather than motivational filler.
- **Ending:** measurable next step and sources/checklists.
- **Rights:** employer logos/portals used in accordance with terms; no fabricated 'placement success'.

### 4.11 Productivity OS — real workflow evidence
- **Hook:** one measurable bottleneck and promised method, no fake productivity multiplier.
- **Visuals:** before/after original screen demo, workflow diagram, task timer/test logs, step-by-step automation, safe redaction of real data.
- **Voice:** brisk practical instructions, teach what can go wrong.
- **Beats:** baseline -> bottleneck -> setup -> demonstration -> retest -> limitation.
- **Retention:** visible success/failure checkpoints with measurable evidence.
- **Ending:** reusable workflow and rollback warning.
- **Rights:** third-party tools, screen-recording content and privacy approvals.

### 4.12 Culture OS — internet phenomena with context
- **Hook:** an unfamiliar origin/context question, not a hostile pile-on.
- **Visuals:** dated original platform/source references where allowed, meme evolution timeline, diffusion/network diagram, clearly attributed excerpts, anonymized comments if appropriate.
- **Voice:** curious and contextual, does not frame online rumor as fact.
- **Beats:** trend -> earliest *observed* origin -> mutations -> community context -> competing interpretations -> cultural takeaway.
- **Retention:** compare changes and explain why they matter; balance levity with verification.
- **Ending:** what can be verified, uncertainty and optional related cultural story.
- **Rights:** meme creator, music, minors/privacy and harassment safeguards.

## 5 — Example production: 45-second India cricket tactical Short (no league footage needed)

This is **fictional placeholder game data**, not an actual match result. All facts would be replaced by verified sources before a public video.

| Time | Narrator function | Primary visual | Overlay/caption | Interaction rationale |
|---|---|---|---|---|
| 00–03 | “Ek field change ne match kaise badla?” (question, no unverified factual assertion) | Custom cricket field board | concise hook; no intro logo | instant promise |
| 03–08 | verified score/over/wicket state | original scoreboard / dots on pitch | verified score and source/dated cue | context |
| 08–17 | explain field placement and batter plan | animated field map | arrows, highlighted fielder, no ambiguous abbreviations | spatial understanding |
| 17–28 | original tactical analysis / possible alternatives | side-by-side diagrams | compare two placements, label hypothetical alternative | added insight |
| 28–37 | show observed source-linked outcome or explain lack of permitted footage | result state on custom chart | factual source / uncertainty label | payoff |
| 37–45 | summarize learning, tease related tactical breakdown | clean field diagram | takeaway caption and optional next-story cue | conclusion |

**Audio:** one original Hindi/Hinglish narration, timed captions, conservative licensed ambience or silence, no copyrighted match broadcast audio. **Fallback:** if fixture/score cannot be validated, block its factual discussion and choose evergreen tactical example, labeled illustrative.

## 6 — Source-aware end-to-end AUTOMATION DAG

```
OWNER selects channel + locale + release policy
 -> discover opportunity / obtain licensed-or-original clip
 -> research dossier + source independence
 -> editorial truth/rights eligibility gate
 -> CreativeBrief (audience promise, originality thesis)
 -> NarrativePlan (script, hook, beats, counterargument, takeaway)
 -> media asset coverage plan (every claim/scene gets truthful visual)
 -> VideoTimeline + overlay/audio direction + per-locale derivatives
 -> CPU/GPU capability reservation + fallbacks
 -> scene assets, TTS/voice, word alignment, screen/diagram/video generation
 -> assembly / audio mix / captions / disclosure
 -> machine QC: factual overlays + A/V sync + rights + caption safe areas
 -> domain visual critic + full human preview where required
 -> approved revision hash
 -> manual export OR explicitly allowed private/scheduled upload
 -> actual analytics + categorized scene retention hypotheses
 -> no automatic policy bypass / no guarantee of revenue
```

Each event carries idempotency key, source hashes, scene version and rights expiry. Failed localization pauses that locale only. A corrected sports score invalidates affected artwork/voice/script and every dependent language version. Missing GPU only blocks GPU-required shots, and any change of creative modality needs explicit user consent. The `CreativeBrief` and `Timeline` layers are additions; do not duplicate shared research/rights/publishing implementations.

## 7 — Implementation increments and acceptance evidence

**Stage CP-A (CPU, before public uploads):** CreativeBrief, VideoTimeline typed contracts, overlay/caption/sound directors, format grammar for Cricket/NFL/Tech; manual/licensed clip intake; one 9:16 and one 16:9 sample per pilot. Required evidence: original assets, cited script, full export, a viewer review, captions in-frame, no unexpected rights material.

**Stage CP-B (regionalization):** initial Hindi and English locale packs with pronunciation dictionary, voiced tracks, translated visual labels and subtitles. Verify localized dates/units and reflow. One multilingual video test under owner account features; failure must fall back to manual Studio procedure, not fabricated API success.

**Stage CP-C (commentary):** actual rights-reviewed clip -> transcript -> independent thesis/criticism -> pause/diagram annotations -> approval -> upload method with source and derivative manifest. Test denial for unlicensed broadcast clip, mere green-screen overlay, or single added voiceover with no substantive contribution.

**Stage CP-D (12-domain expansions):** integrate domain-specific visual profiles above with sample films and visual regression tests. Same timeline compiler, rights checker, audio mixer and localization service.

**Stage CP-E (GPU):** optional image/video/animation generation with prompt compiler preserving SceneSpec, character continuity and model licenses. Not essential for CPU launch. Add remote GPU workers without changing story/locale IDs.

**Stage CP-F (learning):** after real publications, map retention dips/spikes back to scene IDs and test creative hypotheses. Do not infer causation from one video, no fabricated analytics or guaranteed virality.

### Must-fail tests
- Unsupported source voiceover converted into verified claim without independent research.
- Unknown broadcast footage rights bypassed through AI voice, green-screen, short duration or altered color.
- `hi-IN` captions or score overlays clipped by platform UI or font fallback.
- `en-US` narrator misreads NFL down-and-distance, team abbreviation or season week.
- Voice/TTS word alignment drifts beyond configured sync tolerance.
- Source correction updates English script but leaves Hindi narration or infographic stale.
- Region-specific title promises a result not depicted in that locale's actual video.
- Music track lacks commercial-use permission or causes narration unintelligible.
- AI recreation of real political speech passed off as genuine footage.
- Render QA passes technical checks but owner rejects confusing or unwatchable edit; release remains blocked.
- Auto dubbing, multi-language feature or Remix API reported as successful without feature/account availability.
- A channel mass-publishes identical template videos with minimal semantic variation.

## 8 — Official references checked (2026-11-09)

- YouTube monetization, inauthentic and reused content: https://support.google.com/youtube/answer/1311392
- Shorts in-app Remix and Green Screen / source removal: https://support.google.com/youtube/answer/10623810
- Fair use is case-specific; courts decide: https://support.google.com/youtube/answer/9783148
- Additional audio languages and localized titles/thumbnails: https://support.google.com/youtube/answer/13338784
- Automatic dubbing limitations: https://support.google.com/youtube/answer/15569972
- YouTube subtitles/captions: https://support.google.com/youtube/answer/2734796
- Altered/synthetic realistic content disclosure: https://support.google.com/youtube/answer/14328491
- Engagement and viewer retention: https://support.google.com/youtube/answer/12942217
- End screens: https://support.google.com/youtube/answer/6388789
- Upload encoding: https://support.google.com/youtube/answer/1722171
- YouTube Data API videos.insert (known metadata/localizations fields, **not evidence of a general multi-audio-track API**): https://developers.google.com/youtube/data/reference/rest/v3/videos/insert

**Editorial disclaimer:** This report describes an *engineering design with illustrative filmmaking heuristics*, not a claim that YouTube mandates particular hook timings or edit speeds. Monetization, copyright, third-party clip permission, creator feature eligibility and real view results must be verified for each case. It does not modify or overwrite the three existing v2.1 ZIPs.
