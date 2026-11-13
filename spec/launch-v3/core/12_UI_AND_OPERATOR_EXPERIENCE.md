# CORE-12 — Dashboard Screen Contract and Operator Experience

## 12.1 UI invariants

No inert controls: every button/toggle has endpoint/validated state, actual backend capability and visible result. Unknown data is explicitly unknown, no mock charts mixed with observed metrics. All screens accessible by keyboard and usable at typical Windows laptop display widths. Persist filters/channel selection. User controls AI suggestions, editorial approvals and outbound publishing.

## 12.2 Screen-level interfaces

| Screen | Required elements | Backend source / actions | Empty/degraded |
|---|---|---|---|
| First-run setup | Detected CPU/RAM/GPU, FFmpeg/voices/models/SSD, workspace, terms | `/health`, `/capabilities`, settings | Missing optional model not fatal; no-GPU normal |
| Command Center | Channel summary, queue, source freshness, risk, backlogs, revenue actual | channel/jobs/connector/ledger | Unknown status shown, not 0 or green |
| Channels | Name, domain/sport, locale, market, time zone, voice, review mode, OAuth status | profile CRUD, OAuth connect/disconnect | No account -> manual export |
| Trend Observatory | Topic cards, source rows, observed timestamps, lifecycle, opportunity components, source gaps | topics/connectors, sync jobs | No data -> prompt for permitted sources |
| Research Studio | Question tree, source excerpts/timecodes, claim/evidence matrix, contradictions, gaps | research/sources/claims | Cite unavailable -> review badge |
| Domain Desk | Domain-specific tools and verified facts, calculators, domain creative format | domain manifest, domain jobs | Deferred domain -> disabled with roadmap, not fake action |
| Script/Storyboarding | Original script with inline citation refs, version history, scene list, footage rights | scripts/scenes/assets | Unsourced fact highlighted, can't approve |
| Media Studio | Timeline, visuals, narration, captions, render attempts, quality and disclosure | render/jobs/rights/QA | Unsupported GPU -> explain and keep CPU path |
| Publishing Director | Thumbnail/title variants, source descriptions, disclosure, approval, privacy, schedule, upload/export | approval/publication | No OAuth -> export; no review -> blocked |
| Audience Lab | Actual imported metrics by video/channel/format, window and availability | analytics/experiments | No monetization -> Not eligible/unavailable (not zero earnings) |
| Earnings/GPU Fund | Actual earnings, expenses, savings, owner quote, forecasts separately | ledger | Unknown quote -> prompt, no invented target |
| Operations/Security | CPU/GPU mode, model license/version, disk/jobs/logs, backup/restore, audit | compute/settings/health/audit | No GPU -> not detected, do not fake it |

## 12.3 Common interaction patterns

- Long operations POST -> job_id, UI subscribes via polling/WebSocket only if implemented; loading never signifies success until persisted job output inspected.
- Every `BLOCKED` job exposes exact reason code, prereq, last attempt, safe recovery action and responsible user or provider.
- User approval screen shows source summary, rights manifest, risk/uncertainty, synthetic disclosure and exact video checksum before action.
- On edited script/asset/thumbnail, affected approvals show expired, upload button disabled until re-review.
- Display origin links for factual statements and original documents where terms permit.
- Destructive action confirmation includes ID and effect; never delete source archives/backups inadvertently.

## 12.4 Internationalization

Channel-level `hi-IN` / `en-US` with separate spoken language and on-screen text font; layout must support Hindi glyphs, mixed Latin/Devanagari and subtitles. Time zones IANA e.g. `Asia/Kolkata`, `America/New_York`; all DB timestamps UTC. Currency in display `INR/USD` based on authorized reporting and stored code, no silent FX conversion. Sports terms verified by sport adapter.

## 12.5 Operator safety controls

`Auto/CPU_ONLY/CUDA_ONLY/HYBRID` selection must update backend scheduler and actual worker registry, not only UI state. Publish is **manual by default**; conditional low-risk trusted publishing requires explicit per-channel opt-in and passing all gates; contested news never automatically made public. Data export and offline view operate without Google account connection.

## 12.6 Human review tasks

Queue types: `SOURCE_ACCESS`, `EVIDENCE_CONFLICT`, `RIGHTS_UNRESOLVED`, `ALLEGATION_OR_PRIVACY`, `SYNTHETIC_MEDIA`, `MODEL_LICENSE`, `PUBLICATION`, `CORRECTION`, `GPU_PROFILE`, `EXTERNAL_POLICY_CHANGE`. Each has affected project/source IDs, urgency, blocking state, evidence and action. Approval actions are persisted with actor and hash; LLM can't impersonate owner.

## 12.7 UI E2E checks

New profile persists after reboot; switching between two channels never leaks OAuth/source data; missing feed shows coverage warning; unsupported claim blocks; legal-risk footage hold; CPU video preview works; GPU toggle reflects backend, missing model shows explanation; upload button refuses unauthenticated; analytics panel does not display fixture metrics as observed; backup restore and cancellation control work.
