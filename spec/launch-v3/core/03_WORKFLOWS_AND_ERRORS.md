# CORE-03 — Workflow State Machines, Automation, Reliability and Editorial Council

## 3.1 Canonical pipeline DAG

`CHANNEL_CONFIGURED -> DISCOVERED_TOPIC -> RESEARCH_PLAN -> SOURCES_FETCHED -> CLAIMS_REVIEWED -> SCRIPT_VERSION -> SCENE_PLAN -> ASSET_RIGHTS_CHECK -> AUDIO/GRAPHICS -> RENDER -> TECHNICAL_QA -> FACT/RIGHTS_QA -> EDITORIAL_APPROVAL -> EXPORT / AUTHORIZED_UPLOAD -> ANALYTICS_SYNC -> LEARNING_UPDATE`.

Each node has explicit input hash, output hash, schema, preconditions, progress, retry class, cancellation checkpoint and audit log. If a prerequisite fails, its downstream nodes remain blocked, never fabricated.

## 3.2 Durable job state machine

| State | Allowed transitions | Meaning |
|---|---|---|
| `QUEUED` | RUNNING, CANCELLED, BLOCKED | Eligible, awaiting resources |
| `RUNNING` | SUCCEEDED, RETRY_WAIT, BLOCKED, WAITING_FOR_APPROVAL, WAITING_FOR_CAPABILITY, FAILED, CANCELLED | Leased by worker; heartbeat maintained |
| `RETRY_WAIT` | QUEUED, FAILED, CANCELLED | Transient error, backoff scheduled |
| `BLOCKED` | QUEUED, CANCELLED | Missing nontransient prerequisite (rights, auth, evidence, quota policy) |
| `WAITING_FOR_APPROVAL` | QUEUED, CANCELLED | Human decision needed |
| `WAITING_FOR_CAPABILITY` | QUEUED, CANCELLED | Missing model/GPU/disk/capability; safe hold |
| `SUCCEEDED` | terminal | Output hashes persisted and verified |
| `FAILED` | QUEUED (manual retry as new attempt), CANCELLED | Exhausted attempts/irrecoverable error |
| `CANCELLED` | terminal | User/system cancel, cleanup recorded |

Worker lease expires -> reconciler marks abandoned RUNNING job retryable only if safe and idempotent, and rechecks external side effects. Queue concurrency defaults: CPU heavy jobs 1, source HTTP jobs 2 per provider unless policy lower, TTS 1, FFmpeg render 1; limits adjustable after benchmarks. Quota exhaustion => do not hammer provider; schedule after reset or wait for permission. Max retry 3 for network transient, exponential 5s/30s/120s plus random jitter; these are local implementation defaults, not API guarantees.

## 3.3 Fail-closed gates (never traded against opportunity score)

1. `EVIDENCE_GATE`: factual assertions reference cited passage/source version, verified domain rule and review state. Verified numbers not invented. Unsupported assertions removed, marked open or explicitly hypothetical; serious allegations cannot leave review.
2. `RIGHTS_GATE`: each third-party asset has permission/license record for platform and use type; review broadcast footage, music, typography and datasets. Unknown rights => hold/replace with original licensed asset.
3. `ORIGINALITY_GATE`: substantive analysis, authentic narration, original capture or diagram; superficial crop/speed/green-screen alone never sufficient; output not a near duplicate across channels.
4. `DISCLOSURE_GATE`: meaningful realistic synthetic/reconstructed footage assessed, marked where required; never pass off synthetic image as actual documentary evidence.
5. `TECHNICAL_GATE`: playable media, dimensions/codec, safe audio, visible captions, no missing media/blackouts, known output hash.
6. `EDITORIAL_GATE`: approvals tied to final revision and risk summary; special categories require explicit human decision.
7. `AUTH_AND_CHANNEL_GATE`: authorized YouTube account/channel and quota before attempting external upload; default draft/manual export.

Each gate yields structured `PASS | FAIL | REVIEW_REQUIRED | NOT_APPLICABLE`, checks, issue IDs, reviewer and timestamp. **Never treat NOT_APPLICABLE as PASS without rationale.**

## 3.4 Editorial risk and automation policy

| Content risk | Automation permitted | Public upload |
|---|---|---|
| Low-risk factual tutorial based on user-created demonstrations | Discovery/research/script/production/QA automatic | Only after owner enables channel-level trusted auto-publish AND all hard gates and authorized API; default manual |
| Routine score/previews with official data | Research and production automatic with freshness checks | Manual by default; trusted mode only with explicit opt-in, source accuracy and time constraints |
| Serious allegations, investigative politics, criminal accusations, election misinformation, personal privacy, financial/medical harm claims | Research gathering, transcripts and drafts automatically; reviewer must assess interpretations | **Human approval always**, with legal/right-of-reply where appropriate |
| AI reconstruction of actual events/people | Generate with scene-level labels and provenance only | Human disclosure review; never present as authentic footage |
| Missing rights, fabricated/unverified claim, revoked OAuth | No bypass | Never publish |

Owner approvals have scopes and expiration; a material content edit invalidates previous approval automatically.

## 3.5 Decision Council algorithm

Inputs: `topic candidates`, verified source coverage, opportunity features, channel fit, rights risk, total estimated production load, recent content overlap, freshness, user-set priorities. Algorithm:
1. Enforce hard exclusions (`RIGHTS_UNRESOLVED`, forbidden scraping, unsupported model, sensitive pending review).
2. Reject duplicate or near-identical production plan across active channels unless angle materially different and logged.
3. For eligible topics calculate explainable opportunity score (CORE-04), uncertainty and required research depth.
4. Allocate compute/production budget; do not starve scheduled correction or owner-requested investigation.
5. Propose `INVESTIGATE_MORE`, `PRODUCE_DRAFT`, `HOLD_FOR_REVIEW`, `SKIP` with reason codes.
6. Record decision and inputs; allow owner override only if overriding non-hard business priority, never law/rights or factual fabrication.

## 3.6 Side-effect safety

Before public upload: stage `publication_intent` with unique idempotency key and project content hash. Make API upload resumable if provider supports; on timeout, **reconcile existing external video/list/account and quota state** before attempting retry. If uncertain, `BLOCKED_UPLOAD_RECONCILIATION`, do not upload duplicate. Publishing timestamps use timezone-aware UTC conversion with DST tests. Never auto-delete published video as a rollback: propose correction/action requiring owner approval.

## 3.7 Structured error codes

`INVALID_CONTRACT, CONTRACT_VERSION_UNSUPPORTED, INVALID_DOMAIN, INVALID_LOCALE, SOURCE_FETCH_FAILED, SOURCE_TERMS_BLOCKED, SOURCE_STALE, QUOTA_EXCEEDED, EVIDENCE_INCOMPLETE, SOURCE_INDEPENDENCE_UNKNOWN, CONTRADICTION_CONTEXT_MISSING, RIGHTS_UNRESOLVED, CONTENT_DUPLICATE_REVIEW, DISCLOSURE_REQUIRED, RISK_REVIEW_REQUIRED, AUTH_REQUIRED, TOKEN_REVOKED, MODEL_UNAVAILABLE, MODEL_LICENSE_UNVERIFIED, WAITING_FOR_CAPABILITY, RESOURCE_EXHAUSTED, DISK_FULL, RENDER_FAILED, QC_FAILED, APPROVAL_EXPIRED, UPLOAD_RECONCILIATION_REQUIRED, API_POLICY_CHANGED, INTEGRITY_FAILED, CANCELLED_BY_USER`.

Every error stores `reason_code`, `retryable`, affected node, user-safe explanation, machine details, recovery suggestion and relevant audit event. Do not leak secret values in machine details.

## 3.8 Crash recovery and graceful stop

Journal job state before work; checkpoint download/page cursor/audio scenes/render segments when possible. On restart verify last stored artifact digest, re-run only incomplete work. Request cancellation cooperatively between FFmpeg segments or LLM batches; terminate spawned process tree safely after grace period and save incomplete output only if explicitly marked draft. Run restore test, resource exhaustion and interrupted upload tests before v1 released.
