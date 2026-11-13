# Sports OS — SPECIFIC AUTOMATED ENGINE CHAIN

**Canonical parent:** `sports`; cricket/NFL/MLB/NBA/soccer are sport adapters, not independent `domain_id` values. Launch enables cricket and NFL, others stay staged. All data sources require terms and provenance checks.

1. Event calendar -> canonical UTC event ID, league season/week/match format, teams and aliases, original provider timestamps, revision watermark. Missing fixture provider => manually entered event marked `UNVERIFIED` until checked.
2. Entity resolver -> team/player identity with same-name and transfers/roster disambiguation. Missing confidence => `REVIEW_REQUIRED` before statistics narration.
3. Stat validator -> checks source freshness + units + score-state constraints. Cricket: overs/base-six, innings wickets, strike rate/economy, T20/ODI/Test, DLS/rain not assumed. NFL: downs, distance, drives, possession, clock and regular/post season; baseball: innings and pitcher/batter statistics; NBA: possession and pace; soccer xG model and provider provenance.
4. Tactics -> original generated field/pitch diagrams from verified structured game data, not copied sports broadcast footage. Distinguish tactical **hypothesis** from observed play if no footage or play-by-play detail.
5. Narrative -> choose preview, recap, tactical explainer or evergreen history. Cite all statistics; run data revision check immediately before publish if live or recently concluded.
6. Rights -> third-party league footage, logos, audio and statistics licensing considered independently; unknown rights => use original diagrams/voice/screen and manual footage-exclusion. A green-screen edit is not a rights grant.
7. QC -> synthetic fixtures for cricket 17.3 overs=105 legal balls, NFL clock state DST, corrected scores, abandoned game, duplicate player names, delayed stats, season transition and rejected footage.
8. Recovery -> when score changes after script, invalidate related cited spans, re-record narration/render and revoke approval; published content requires correction review, not blind replacement.

**Output artifacts:** canonical event record, verified stat ledger, tactical scene spec, rights-safe production plan, correction flags. **Metric:** factual stat error rate, source recency, original visual rate, actual retention, rights incidents.
