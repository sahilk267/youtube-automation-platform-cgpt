# SPORTS OS sub-adapters — mandatory distinct data + creative algorithms (v3)

**Single top-level sports OS; these are rules engines, NOT extra global domain IDs.** Source stats must have provider, time and official/permission status. Unknown license = blocked, not auto-download.

| Sport | Canonical match state and calculations | Primary visual grammar | Domain-specific failures |
|---|---|---|---|
| Cricket | Format T20/ODI/Test; balls, overs (`17.3` = 17 complete overs + 3 **legal** balls = 105), innings, wickets, target, run rate, bowling economy, lineup changes, DLS context | Original oval/pitch field plan, striker/non-striker, bowling length, fielder positions, ball-path arrows labeled illustrative unless genuinely measured | Fractional-over math, team or player alias collisions, score revisions, missing venue/pitch evidence |
| NFL | League/season/week, possession, downs/distance, game clock/quarter, timeouts, scoring play, injuries/roster versions | Original gridiron diagram, down marker, routes, blocking/coverage zones, play-call alternatives labeled hypothetical | Local/ET DST mismatch, down/yardline reversal, fabricated playbook motive, game clock mismatch |
| MLB | Season/game/inning/top-bottom, balls-strikes-outs, base runners, roster/lineup, pitcher/batter handedness, advanced statistics only with definitions | Original baseball diamond, pitch zone heat-map with source data, defensive alignment, matchup split | Claimed pitch data unavailable, wrong inning half, stats denominator omitted, protected game broadcast footage |
| NBA | Quarter/game clock/shot clock, possession, score, lineups, play types, pace/statistical definitions | Original court half/full diagrams, shot chart with source and date, spacing/cut arrows | Shot chart sampled from partial season represented as complete, player/injury mismatches |
| Soccer | Match minute, stoppage, competition rules, formation, xG source/model, possessions and offside context | Original pitch heat maps/formation, pass network with uncertainty, event timeline | Unverifiable xG treated as ground truth, fan highlight used unlicensed, wrong competition rule |

**Profiles:** `hi-IN` conversational for Cricket pilot, `en-US` technical for NFL pilot; don't assume locale hard-coded forever. Source-driven tactical analysis and source rights rules are mandatory. Face-cam/green-screen permitted only with authentic supplied creator footage and cleared source media / valid in-platform feature.
