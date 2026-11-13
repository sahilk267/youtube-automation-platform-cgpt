# v3.0 Change Audit — what changed and what remains unproven

## Integrated in ALL THREE independent archives
- Previous 2.1 canonical research/evidence, API, workflows, security/compute, domain manifests and 144 engine registrations preserved (Launch retains its launch-scoped subset).
- v2.2 Content Production Audit preserved **as research history**, its 25 gap items addressed by new v3 normative contracts, workflows, 12 distinct audiovisual directors and 9 formats. Historical addendum is not a second source of authority.
- Competitor and 120-channel desk research included with evidence-level limitations. Architecture ADR-001 adopted via `core/24` without claiming software deployed.
- 15 strict, new v3 JSON schemas for creative brief, beats, shots, overlays, speech, mixing, localization, reactions, timeline, QC, brand, benchmark, domain director and operation dispatch.
- 18 canonical creative operation stages, each with owner/input/output/error/gate/test ID; no duplication of v2 publisher, evidence store or rights service.
- Additive SQL migration `003_content_production_v3.sql` preserves v2 records and source IDs. No migration is deployed to the user's actual PC by these documents.
- New standalone `tools/validate_v3.py` and v3 fixture/golden/negative-test registries. Structural PASS does not equal completed functionality.

## Critical gaps addressed in specification (NOT claimed implemented)
| Gap family | Canonical file | Future working evidence |
|---|---|---|
| Research-to-visual alignment | core/21 + ShotPlan | Citation/visual correctness on real video |
| Hooks, narrative and payoff timing | TimedBeatGraph + format packs | Real owner-reviewed Short and long form |
| Text/caption/overlay geometry | OverlaySpec + VideoTimeline | Actual device captures, native scripts |
| Voice timing, persona and music | SpeechSegment + SoundMixSpec | Measured audio/align/loudness tests |
| Localization independent voice/graphics | LocalizationVariant + core/23 | Dual-locale watch-through |
| Viral clip reaction and reupload safeguards | ReactionClipMap + core/22 | Rights-cleared source clip test |
| 12 category-specific creative mastery | creative/directors/ | Two real golden videos per domain |
| CPU now / GPU future | core/21/25, existing compute | Actual Windows i7 render and future GPU tests |
| Monetization/reused content | core/22, inherited policy | Account-level review, not internal promise |
| Competition study limits | research/ | Five verified video observations per channel (future 600) |

## Honest residual risks
- No functional React/FastAPI application created by v3 specification package.
- Many external API/source licenses, actual channels, YouTube access, creator catalog videos and hardware measurements remain unknown.
- JSON schemas and fixture tests cannot judge narrative artistic quality or legal fair use; humans must review actual outputs.
- Machine-checkable contracts are necessary but do not by themselves prevent all AI hallucinations or code bugs.
