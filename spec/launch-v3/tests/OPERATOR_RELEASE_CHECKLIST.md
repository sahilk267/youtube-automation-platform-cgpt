# Operator Acceptance & Evidence Plan (release checklist)

Every check has 3 states: `NOT_RUN`, `PASS_WITH_ATTACHED_EVIDENCE`, `BLOCKED_EXTERNAL`. No pre-ticked passes, no screenshots claiming tests without logs.

- [ ] Clean install on actual Windows i7 8th-gen / 32GB / no GPU, no CUDA installed, offline dashboard opens.
- [ ] Fresh channel profile saved/reopened; two channels have isolated sources, language, approval settings and analytics.
- [ ] Manual URL source path works even when sports API returns restricted; no fabricated live score or trends.
- [ ] At least one original cricket and one NFL researched example with source URLs/date spans and notes on uncertainty.
- [ ] Fact-check detects reprints, old scores, mismatched subjects, invalid base-six overs, NFL DST edge.
- [ ] Rights gate blocks unknown broadcast highlight; original pitch/field diagrams render.
- [ ] Narration/audio/subtitle/FFmpeg outputs playable 9:16 and 16:9 files (inspect actual codecs/durations).
- [ ] Material script change revokes approval; high-risk allegation cannot auto-publish.
- [ ] Manual upload-ready package exports with no OAuth; optional authorized API upload only with owner consent.
- [ ] Timed-out YouTube upload triggers remote reconciliation, no duplicate video.
- [ ] Revoked OAuth safely blocks ingestion/upload and displays correct reason.
- [ ] Analytics/revenue display NOT_AVAILABLE if account inaccessible, not 0 or invented numbers.
- [ ] Interrupted job resumes or clearly restarts; backup restored with checksums, projects and assets verified.
- [ ] Real CPU time/RAM peak benchmark recorded; CUDA-only jobs wait honestly.
- [ ] Ultimate domain enables require their source connector, unique engine tests and human signoff.
- [ ] Model/GPU upgrade reopens old projects and rerenders without changing original sources/rights.
- [ ] License versions, platform policies and source access rechecked before live deployment.

**Release approval sign-off fields:** reviewer ID, UTC time, git commit, artifact hashes, test report IDs, allowed unresolved external blockers, signature and deployment profile. A passed spec-pack validator does **not** satisfy these checkboxes.
