# Canonical specification mapping, tested subset

Source authority: `spec/ViralOS_Launch_v3` (copied as a snapshot from the independently supplied Launch v3 ZIP). Do not edit it to make failing code appear compliant. `sql/001_schema.sql`, `002_controls.sql`, and `003_creative.sql` are byte-identical to canonical Launch v3 `database/` files.

| Canonical requirement | Evidence implemented in this milestone | Remaining blocker |
|---|---|---|
| L-001 local install/launcher | `tools/start_windows.ps1`, FastAPI localhost dashboard | User's Windows i7 verification, application installer |
| L-002 channel isolation | `app/main.py` channel/profile and FK checks | Policy/brand profiles, secrets, channel OAuth |
| L-003 sport statistics | Domain IDs and unique project research plans | Licensed/official real sports data collectors |
| L-004 trend collectors | None | Provider access + quotas, coverage reports |
| L-005 source and claim graph | manual sources, source_versions, claims, evidence_edges, script_claim_links | Independent source verification and full claim extraction |
| L-006 domain-specific visual policy | original cricket vs NFL background graphics | Real tactical visualizations and story directors |
| L-007 CPU media assembly | Pillow + FFmpeg multi-scene original MP4; owner WAV optional | Piper voices, speech alignment, polished assets, accessible captions |
| L-008 rights manifest | preview only uses original generated artwork | Full rights policy engine and third-party clip review |
| L-009 approval/corrections | final publishing disabled | full human approval records and correction cascade |
| L-010 YouTube upload | deliberately disabled | OAuth, official API tests, private-first upload |
| L-011 analytics | disabled | authorized observed reports, experimentation |
| L-012 GPU savings | disabled | real YouTube revenue read and expense ledger UI |
| L-013 scheduler | CPU capability report + sequential queued preview jobs | proper worker lease and GPU/Hybrid/Auto adapters |
| L-014 crash recovery | durable job statuses and manual retry | automatic crash recovery, backups/restore |
| L-015 secrets/privacy | localhost only, bounded upload, no network fetch, no tokens | local auth, secret encryption, full threat-model testing |
| L-016 QA | pytest API, FK, negative and video stream tests | 12-domain golden video reviews, human final QC |
| L-017 audience | not implemented | intent and portfolio analytics |
| L-018 typed contracts | Pydantic API + canonical SQL schema | complete v3 media/schema API mapping |
| L-019 research dossiers | manual research_plans + source provenance | automated research/completeness checks |
| L-020 scripts | revisions + optional exact quote link | thorough script-level claim coverage and story alignment |
| L-021 packaging | not implemented | titles, thumbnails, disclosure, metadata and source verification |
| L-022 UI | diagnostic dashboard | accessible professional React production dashboard |

**Acceptance restriction:** This implementation can be used to test workflow mechanics, but must not auto-publish or be described as a complete YouTube content production system. Output is `TECHNICAL_PREVIEW`, `publish_ready=false` regardless of narration availability.


## v0.7 additive map

- `app/multilingual_m24.py`, `sql/011_m24_localization.sql`: owner-reviewed hi-IN/en-US variants, independent local WAV tracks, synthesized TTS optional, separate captioned MP4 *technical previews*; no auto translation or final upload.
- `app/alignment_m24.py`: opt-in offline local CTC forced-alignment proposal for existing M2.1 plans, never silently accepted; local WhisperX/model installation required and untested with real model.
- `app/voice_quality_m24.py`: clipping/RMS/peak technical diagnostics, not subjective voice quality scoring.
- `app/acceptance_m32.py`, `sql/012_m32_acceptance.sql`: frozen final export + selected upload/analytics account local gates, optional exact channel/private video remote READ-ONLY verification; no remote write or auto-retry.
- `docs/M2_4_M3_2_ENGINEERING.md` and `docs/STATUS_M2_4_M3_2.md`: current procedure and explicit remaining limitations.
