# API and storage contract bridge (v3)

| Old record/service | New typed data | Shared ownership | Migration rule |
|---|---|---|---|
| `ChannelProfile` | `ChannelBrandPack` | channels/branding | Keep original channel_id, create versioned brand pack |
| `ResearchDossier`, `Claim`, `EvidenceEdge` | `CreativeBrief.fact_claim_ids` + `TimedBeatGraph.beats[].claim_ids` | evidence engine (existing) | Never copy LLM text as proof; use existing IDs |
| `NarrativePlan` + `ScriptVersion` | `CreativeBrief`, `TimedBeatGraph` | creative_director | Store mapping and source revision; do not rewrite old script history |
| `SceneSpec` | `ShotPlan` + `OverlaySpec` + `SpeechSegment` | shot/overlay/voice services | Old free-form audio/subtitle dicts are not execution parameters |
| `AssetRights` | `ShotPlan.shots[].rights_decision_id` / `ReactionClipMap` | existing asset-rights service | Missing rights -> hard block; don't create second licenses store |
| `RenderManifest` | `VideoTimeline` + actual output | existing render service | Manifest links timeline and artifact SHA256 |
| `ApprovalRecord` / `PublicationIntent` | `CreativeQualityReport` final state | existing editorial/publication | Approval bound to exact content/render/source revision; no duplicate upload orchestration |
| `AnalyticsObservation` | measured owner channel outcome | analytics service | No inferred private competitor retention/RPM |

**Implementation note:** The JSON Schema verifies object shapes. Cross-object/temporal/rights verification is additional application logic and must pass `tools/validate_v3.py` fixtures as examples; real video QC cannot be replaced by fixture tests.

## Failure codes and operator action
- `EVIDENCE_UNAVAILABLE`: display sources/attempts/coverage; user can supply source; do not fabricate.
- `UNKNOWN_RIGHTS`: replace media, obtain license or escalate to legal review; no automatic publish.
- `REUPLOAD_NOT_AUTHORIZED`: force full-context and true originality analysis plus legal rights review.
- `LOCALIZATION_CLAIM_DRIFT`: block locale, regenerate preserving source numbers/names.
- `TEXT_OVERFLOW_OR_BAD_SOURCE`: reflow graphics or correct translation; don't silently crop text.
- `VOICE_RIGHTS_OR_ALIGNMENT_FAIL`: use authorized voice, correct pronunciation and real alignment.
- `TIMELINE_INVALID`: repair lanes, timing, captions and source/asset references.
- `RENDER_FAILED`: retry bounded transient failure, maintain idempotency; show logs.
- `QC_FAILED` / `APPROVAL_REQUIRED`: show measurable QC and preview; never auto-publish.
- `UPLOAD_NOT_AUTHORIZED`: private export or manual Studio handoff; preserve publication intent.
- `METRICS_NOT_AVAILABLE`: show unavailable, never 0 or fabricated earnings.
