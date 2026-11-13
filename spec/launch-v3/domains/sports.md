# DOMAIN-SPORTS — Multi-Sport Intelligence OS (Cricket / NFL / MLB / NBA / Soccer)

**ID:** `sports` | **Edition:** Launch P0 (Cricket India and NFL US pilots), Ultimate all supported sport adapters | **Ownership:** one Sports OS with specialized league schemas. **Not** five duplicate domain OS.

## Mission and restrictions

Produce timely, accurate, original, tactically and statistically valuable videos using permitted sport-specific sources. Contextual narration in market language, original field graphics and accurate event timing. **Game data access ≠ broadcast footage rights.** A sports clip with cropped edges/green-screen reaction alone does not guarantee copyright clearance or YouTube monetization.

## Shared sports entities

`Competition {sport_id, league_id, season_id, edition, country, rights_policy}`; `Team {team_id, aliases, country, active_interval}`; `Athlete {player_id, aliases, nationality_optional, team_temporal_roster}`; `Fixture {event_id, teams, venue, scheduled_start_utc, local_timezone, status, official_source_version_id}`; `ScoreSnapshot {event_id, period/innings/quarter, score, clock/time, status, source_version_id, fetched_at}`; `StatisticObservation {entity, metric, value, units, period, definition, datasource}`; `Injury/Availability {official_statement, updated_at, uncertainty}`; `TacticalBoard {sport, entities, court/field coordinates, explanation, evidence, rights}`.

All displayed match metadata must be tied to an exact official/current source snapshot and UTC time. A fixture postponed/rescheduled is a new version, not silently mutated history. Player traded/transferred across dates may not be assumed to play for current team retrospectively. Maintain legal source catalog per league, no invented licensed live data.

## Shared engines

| Engine | Input -> algorithm -> output | Key failure |
|---|---|---|
| Event Calendar | Schedule with season/timezone -> normalization, DST conversion, event-update monitoring -> content queue | No fixture source => no predicted date |
| Entity Resolver | Teams, player aliases, roster dates -> temporal entity mapping -> stable IDs | Ambiguous player name => review |
| Stat Validator | Official table and metric dictionary -> unit, denominator, era and game-state checks -> cited statistics | Incompatible stats cannot be compared |
| Performance Trend | Time-scoped official stats -> moving/rolling series and sample size/caveats -> chart | Tiny samples shown as uncertain |
| Tactics Board | Verified play/field formation -> draw original vector positions and causal hypothesis -> analysis animation | Do not claim unseen play or certainty |
| Injury/Roster Monitor | Official team/league reporting -> status timestamp and confidence -> availability note | Rumor != confirmed injury |
| Match Storyline | Actual match evidence -> score event, strategy, records and creative question -> original narration | No result before confirmed result |
| Rights-Safe Footage Planner | Asset manifests -> own/authorized media or animated diagrams -> storyboard | Unknown broadcast rights -> HOLD |
| Community Questions | Permitted forum comments -> popular questions as leads -> research backlog | Fan speculation not proof |
| Seasonality Planner | League calendar and publication history -> preseason/live/postseason/offseason mix -> portfolio plan | No forced daily upload |

## CRICKET adapter (`sport_id=cricket`) — India pilot

### Ontology

`format` enum `TEST, ODI, T20, OTHER`; `innings`, `overs`, `legal_balls`, `runs`, `wickets`, `extras`, `target`, `strike_rate`, `economy_rate`, `required_run_rate`, `powerplay`, `bowler`, `batting_order`, `venue`, `pitch_context`, `rain_rule_version` as applicable. Never infer pitch condition or actual injury from generic venue lore.

### Cricket engines and exact computations

1. **Fixture/score intake:** retrieve competition/event IDs from a permitted official feed; normalize time, playing XI if verified, innings/overs, match status and subsequent corrections. If current feed unavailable use historical/preview format with explicit date; never fabricate live score.
2. **Score semantics:** overs are **base-six legal balls** (e.g., 17.3 overs = 17 overs + 3 balls, not decimal 17.3). `run_rate = runs / (legal_balls / 6)` when balls>0. `strike_rate = 100*runs_scored / balls_faced` when balls>0. `economy = runs_conceded*6 / legal_balls_bowled` where official rules identify qualifying extras. Label denominator and definitions. Duckworth-Lewis-Stern result requires official target; do not implement guesswork.
3. **Tactical graphics:** top-down cricket field coordinate system with striker/bowler, marked fielders and ball path from verified description or **illustrative** strategic hypothesis. Never render imagined match delivery as authenticated replay.
4. **Editorial angles:** why result changed, bowling strategy, batter match-up, actual records, verified controversy with contextual source, historical tactics, match preview with uncertainties. Hinglish/Hindi narration configurable; retain exact player names.
5. **Rights:** stadium/broadcast footage only with documented permission or legal review; default to original pitch/field diagrams, score graphics and own narration.

### Cricket acceptance fixtures

- 17.3 overs interpreted as 105 legal balls, not 17.3 decimal overs.
- Revised rain target not inferred by algorithm; official result verified.
- T20 vs Test averages/statistic denominators not silently mixed.
- Wrong player of identical surname/team aliases blocked.
- Viral edited six clip has no rights record -> excluded from edit.

## NFL adapter (`sport_id=nfl`) — US pilot

### Ontology

Season, week, `phase=PRESEASON|REGULAR|PLAYOFFS`, home/away, field position, down/distance, drive, snap, possession, period/quarter, game clock, play type, formation, route, injury designation, roster as-of, official score correction, overtime rules by applicable season. Historical comparisons must preserve rule era.

### NFL engines

1. **Schedule/status:** official permitted data -> events and result snapshots with `America/New_York` schedule conversion and actual team/venue local time; DST-aware calendar. No future winner predictions presented as result.
2. **Play-state parser:** ingest official play-by-play when licensed/available; capture down, distance, line-of-scrimmage, possession, game clock, penalty uncertainty. If no play-by-play, restrict to documented high-level analysis, do not simulate real specific snaps.
3. **Tactics animator:** render original X/O/route line diagrams for verified formation concepts and **clearly label hypothetical illustration vs confirmed play**.
4. **Performance analysis:** official player/team stats with denominator, playing time, injuries, sample size and opponent context; never equate advanced metric names without definitions.
5. **Editorial angle:** offensive/defensive decision, red-zone execution, drive context, matchup/roster, season narratives, rules explainers, preseason vs playoff distinctions. Native English language with vocabulary review.
6. **Rights:** game broadcasts/highlights and field audio not imported by default; permissible data can support original animations but does not grant video clip rights.

### NFL acceptance fixtures

- A future scheduled fixture is not a completed result.
- Overtime/rule era from different season not silently applied.
- Sack/penalty misattribution caught by official stat comparison.
- Unknown injury status shown as uncertain.
- Eastern and local time/DST conversion verified.

## MLB adapter (`sport_id=mlb`) — Ultimate/backlog

### Ontology and engines

Inning/top/bottom, outs, runners/base occupancy, balls/strikes, pitch count, batting average/OBP/SLG/OPS definition, earned runs, ERA, pitcher/hitter matchup, lineups, season/postseason. Validate denominators (e.g. BA = hits/at-bats; OBP includes proper components per rule definition). Scoreboard/strike-zone and original diamond graphics. Historical advanced metrics must state provider/definition, not assume universally equivalent. Source/play-by-play rights reviewed. Offseason analytical formats supported.

### MLB tests

Wrong inning side, impossible runners/outs state, uncorrected batting denominator, score after official correction, copyrighted highlight reused without permission.

## NBA and soccer adapters — Ultimate/backlog

NBA: team/player, game clock/quarter, shots and court coordinates, possessions, offensive/defensive rating with source metric definition, lineup, injuries and pace era. Soccer: competition, season, match clock/stoppage, players/team lineup, xG model provenance (not a universal ground truth), formations, offside context, transfers and rights. Both require source licensing/availability and original tactical graphics. No implementation claim until respective fixture tests exist.

## End-to-end sports automation

For each active team/competition: scheduled permitted data refresh -> source health -> topic lifecycle -> rights and original angle check -> stats/evidence verification -> matchup/tactical board/approved narration -> render -> QA (scores/labels, audio, license) -> owner preview/approval by default -> official YouTube upload optional -> authorized analytics and correction monitor. If any official game status changes, related planned video receives stale-data alert and approval invalidation. Never trade factual correctness for timeliness.

## Benchmarks and economics

Measure: score/stat error rate against official known fixtures, lineup/roster date correctness, translation of athlete names, narrative originality, rights gate catches, production effort, Short/long format retention (if authorized), copyright claim incidents, channel actual earnings. One high-view clip does not prove channel monetization or profitability.
