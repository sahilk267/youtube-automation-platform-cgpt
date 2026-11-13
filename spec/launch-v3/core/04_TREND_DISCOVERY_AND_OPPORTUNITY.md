# CORE-04 — Trend Observatory, Coverage Metrics and Opportunity Engine

## 4.1 Purpose and truthful coverage model

Discover emerging/growing/peaking/declining topics relevant to the selected channel and locale from **permitted observable** sources. Never claim complete access to YouTube, Google Trends, Reddit, Instagram, TikTok, X or all regional news. Each collector registers `provider_id`, allowed method, terms/version reviewed, auth type, rate limit, market/languages, source type, expected latency, retrieval cursor, quota ledger, error history, current health. `UNAVAILABLE` provider is **displayed**, not quietly replaced with LLM guesses.

## 4.2 Provider classes (not promises of availability)

| Source class | Data acquired | Mandatory limitations |
|---|---|---|
| Official sports sources | Fixtures, official stats, team/player news where legally accessible | Check per-league data license, season, update lag, rights distinct from highlights video |
| YouTube Data API | Public channel/video metadata with authorized quota | No global exhaustive view count API or private analytics for unauthorized channels |
| Google News/RSS | News items, publisher pages, titles and dates | Duplicated syndication, editorial coverage bias, access permissions |
| Google Trends | Trend indicators only when legitimate official/allowed access available | Relative indices, sampled data; not absolute searches or guaranteed public API |
| Reddit API / permitted public data | Discussion leads and audience questions | Access terms, quota, terms, privacy; comments not truth |
| Other social platforms | Official/allowed APIs when available | If inaccessible, disable; never scrape by bypassing restrictions |
| User-supplied links/files | Curated starting topics | Distinguish owner submissions from independently verified facts |
| Newsroom archives/public records | Historical context | Publication coverage incomplete; source versioning |

## 4.3 Collector algorithm and failure states

Input `ConnectorConfig + TopicQuery + WatermarkUTC + Market/Language + quota_budget`. Output `ObservationBatch {items, retrieved_at, source_status, next_cursor, quota_used, raw_digest, errors}`.

1. Validate provider terms, credentials, allowed regions and remaining quota. If not available -> `SOURCE_TERMS_BLOCKED` / `AUTH_REQUIRED` / `QUOTA_EXCEEDED` with coverage gap.
2. Fetch with timeout and retry budget; respect robots/official API conditions. Capture HTTP status, response headers where permissible and raw payload digest.
3. Normalize timestamps to UTC, locale tags, external IDs, publisher, canonical URL and content kind. Unknown field remains null; do not infer values.
4. Detect exact duplicate via canonical external ID/URL/hash, then near-duplicate via textual similarity; preserve all source observations and independence families, never delete provenance.
5. Resolve entity aliases (team, politician, company, game, event); ambiguous names require context rather than confident merge.
6. Cluster observations by topic/event/date/location/sport season; save cluster version and confidence. Off-topic or insufficient data goes `UNCLASSIFIED`.
7. Maintain time series at **known sample intervals**; do not interpolate fabricated popularity. Save source lag and observation count per time bucket.
8. Update provider coverage: attempted, successful, failed, disabled, blocked, delayed, and market/language scope.

## 4.4 Topic lifecycle logic

A topic is `EMERGING` when observed growth is positive across sufficient independent time samples; `GROWING` for sustained positive momentum; `PEAKING` when growth decelerates with significant demand; `DECLINING` when recent signals drop; `INSUFFICIENT_DATA` otherwise. Thresholds must be calibrated per source/market using historical observations. Until calibration exists, show **heuristic labels**, not causal certainty. Require at least 3 distinct time bins before a trend state beyond `INSUFFICIENT_DATA`; high-stakes counterexamples reviewed.

Seasonal and event-specific adjustments: distinguish IPL/ICC and bilateral schedules, NFL preseason/regular/postseason, MLB season/postseason, NBA schedule, technology launch cycles, local festivals. No unsupported predicted fixtures.

## 4.5 Opportunity score (explainable recommendation, not virality probability)

Normalized features in [0,1] with explicit observation coverage and confidence:
- `D` demand proxy; `M` growth/momentum; `A` audience fit; `N` novel angle/differentiation; `V` availability of reliable verifiable evidence; `T` freshness/timing opportunity; `E` production efficiency; `F` evergreen value; `R` footage/defamation/rights risk; `S` saturation/fatigue.

Initial **declared heuristic**, subject to measured calibration:
`raw = 100 * (0.16D + 0.13M + 0.16A + 0.12N + 0.13V + 0.10T + 0.08E + 0.07F + 0.05(1-S))`.
Apply `risk_gate`: `R >= 0.7` => `HOLD_FOR_RIGHTS_REVIEW` regardless of score; rights violations => `REJECT`. For otherwise eligible candidates, show `raw`, per-feature provenance, observation timestamp and **coverage confidence**, never an absolute success forecast. Missing features default **null** and are excluded from numeric recommendations until at least demand, audience fit and evidence availability are known; do not replace missing data with 0.5/LLM guesses. The formula is a documented starting policy, not a statistically validated predictor.

## 4.6 Audience and multi-channel routing

Filter candidate by domain, format, language, region, viewer intent, availability of legitimate footage/visuals and CPU render budget. Prevent topic cannibalization: if same project/angle recently published on channel, flag and propose substantively new angle or skip. One event can serve Science and Tech only if distinct sourced insights. Topics involving misinformation may be worth investigating even with low audience score; high-impact editorial override can allocate investigation, but factual/rights gates still apply.

## 4.7 Coverage UI contract

`coverage_dashboard` shows for every provider: access method, last successful retrieval, last attempt, error code, geographic/language scope, rate/usage, source lag, data sample count, known blind spots, excluded platforms and whether any data is an estimate. Labels: VERIFIED_ACCESS / DEGRADED / BLOCKED / NOT_CONFIGURED / NO_DATA; never a green complete-coverage mark when sources absent.

## 4.8 Tests

- Identical RSS copies do not create separate independent events; publication dates preserved.
- Disconnected source displayed explicitly, no hallucinated trending card.
- Three insufficient/nonuniform time samples do not imply guaranteed trend growth.
- Cricket score updated/corrected does not rewrite earlier captured snapshot; marks downstream script stale.
- Same title for two unrelated entities does not merge without contextual match.
- Changing market, locale, source availability or licensed data does not produce fabricated default values.
