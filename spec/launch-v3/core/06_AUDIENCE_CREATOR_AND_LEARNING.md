# CORE-06 — Audience Psychology, Creator Direction, Portfolio and Learning

## 6.1 Per-channel audience model

A channel profile includes market, primary/secondary languages, target viewer intents, subcategories, allowed formats, editorial style, brand voice, thumbnails, source risk policy, time zone, upload approval and preferred production constraints. No engagement predictions without data. Segment viewers conceptually into newcomer, returning, subscriber and subject-matter levels only when metrics support it; do not attempt deanonymization.

Audience intent vocabulary: `UPDATE, EXPLANATION, DEEP_INVESTIGATION, ENTERTAINMENT, PRACTICAL_TUTORIAL, TACTICAL_ANALYSIS, COMPARISON, REFERENCE`. Format choice requires intent fit: cricket quick result != forensic political investigation != scientific lesson.

## 6.2 Creator Strategy Analyzer

Observe published techniques such as pacing, visual grammar, hook structure, evidence disclosure, analogy, chaptering, sound design and narrative payoff; record **abstract style patterns**, not copyrighted scripts, faces, distinctive catchphrases, exact thumbnails or voice identity. Use consented/licensed assets only. Recommendation is an editable hypothesis; originality gate ensures materially unique output.

## 6.3 Narrative Director contracts

Input: verified dossier, audience intent, time budget, output format, allowed visuals. Output: `NarrativePlan {promise, hook, core_questions, beat_list, evidence_anchors, counterevidence, viewer_takeaway, expected_duration, original_angle}`.

Workflow:
1. Identify viewer question and honest answer boundaries.
2. Map factual claims/uncertainties to story beats; distinguish reveal from assertion.
3. Draft concise opening promise that is fulfilled; prohibit deceptive hook or unjustified outrage.
4. Plan 3–8 narrative beats for short and variable chapter structure for long-form; durations are editing preferences, not rigid assumptions.
5. For each scene, specify whether evidence shown, custom explanatory diagram, original demo, commentary or illustrative recreation.
6. Check explanatory clarity, trust, pacing, accessibility and payoff; specialist domain critic must sign off domain accuracy.
7. Package relevant titles/thumbnails: promise matches supported script, avoid fabricated claims or misidentification.

## 6.4 Production formats by domain

- Newsroom: question -> original source -> timeline -> competing evidence -> limits -> conclusion; documented reconstructions labelled.
- Science/Space: phenomenon -> mechanism -> scientific evidence -> caveats -> implications; no false simulation labels.
- Tech: problem -> reproducible setup -> demo/test -> measurements -> limitations -> recommendation.
- Sports: match moment -> original tactical/score illustration -> measurable context -> strategy explanation -> audience takeaway.
- History: archival question -> timeline/maps -> primary record -> scholarly interpretations -> uncertainty.
- Learning/Career/Productivity: objective -> prerequisite -> worked example -> practice/result -> safe limitations.
- Gaming/Culture: genuine community/original observations -> context -> creative interpretation -> game/creator rights.

## 6.5 Portfolio Decision Engine

Tracks last 30/90 days by channel and topic family: evergreen/timely mix, Shorts vs long-form, repeated subtopics, publishing spacing, fatigue, series continuity, content cost, rights risk, available research depth. It suggests queue ordering but will not force unproven frequency. Original content quality outranks calendar volume. Historical near-duplicates trigger `CONTENT_DUPLICATE_REVIEW`.

## 6.6 Packaging Lab and experiments

A test record contains hypothesis, channel, candidate title/thumbnail variants, launch window, measurement period, observed metrics, confounding changes and conclusions. Only use platform A/B capabilities actually available to account via permitted methods. If official A/B not available, use sequential observational cohorts and label inference weak. Do not impersonate competitor titles or mislead with fake screen captures.

## 6.7 Audience analytics and reasoned iteration

Observed YouTube metrics can include impressions, CTR, views, average view duration, watch time, retention, returning viewers, subs, monetization revenue by eligible reports. All must include `provider, channel_id, video_id, metric_definition, date_window, as_of_utc, timezone, availability_status, sample limitations`. Shorts and long-form have distinct denominators and revenue mechanics; do not combine as identical cohorts.

Improvement cycle: collect -> segment/channel/format compare -> formulate clear hypothesis -> one controlled change when feasible -> observe enough data -> human review -> store finding. Correlation ≠ causation. Low sample sizes => `INSUFFICIENT_EVIDENCE` rather than definitive optimization.

## 6.8 Community and feedback

Authorized comments/questions collected subject to API scope/privacy; normalize topic, requests, corrections, helpful confusion signals and harassment/privacy handling. Comments generate research leads, not factual validation. Automated abusive reply, vote manipulation, synthetic testimonials, fake community consensus and spam prohibited. Any comment reply action requires separate explicit owner opt-in and platform policy review.

## 6.9 Quality rubric and launch metrics

Rubric dimensions each 1–5 with evidence: truth/citations, original insight, narrative clarity, audio intelligibility, visual legibility, audience intent fit, caption accessibility, source/rights compliance. `rights` and `source factuality` are hard gates, not additive score offsets. Store human review notes. Launch goal is improving acceptable research-to-video quality and repeatable workflow; **no fake subscriber/RPM target**.

## 6.10 Evaluation cases

- Trend high but rights impossible -> HOLD/skip, not publish.
- Low CTR despite high retention -> test packaging hypothesis; not alter factual reporting.
- Shorts view spike cannot be treated as proof of long-form revenue potential.
- Same footage/title on two channels -> duplicate editorial review.
- Missing Analytics permission -> empty metric state with access instruction, not placeholder numbers.
