# CORE-14 — AGENT EXECUTION, ENGINE CONTRACTS AND BOUNDED AUTOMATION

## Executable unit of work
1. Caller produces `contracts/ExecutionRequest.schema.json`; validate exact `contract_version=2.0.0`, engine ID in registry, domain and channel/project linkage, input artifact IDs+SHA256, mode, deadline, policy digest and idempotency key. Invalid input fails **before** tool/model call.
2. Router loads `configs/engine_execution_registry.json`, checks `owner_module` matches true canonical service and enabled profile. Deferred engine returns `FEATURE_NOT_ENABLED` with upgrade hint; no inferred alternative engine.
3. Acquire job lease and resource budget. Persist attempt ID, lease expiry, input digest and expected output type before execution. If provider unavailable, terminal or waiting state as specified; no fabricated data.
4. Deterministic tools first where possible: parse official records, verify hashes and units, perform actual local calculations/tests; use an optional LLM only for draft classification, retrieval plans and narratives. Treat model outputs as proposals validated against schemas and real evidence.
5. On success, write immutable artifact atomically (temp file -> fsync -> sha256 -> rename -> DB transaction); persist provenance, agent/model version, source timestamps, extracted evidence, quality status and warnings. Emit `ExecutionResult` with persisted references only.
6. On retryable failures use capped retries from policy, circuit breaker, deadline and backoff; non-retryable/license/auth/human-blocked work surfaces a review task. Failed steps must not be marked skipped-success.
7. Publish is a unique privileged side effect owned by `publication_service`; domain plugins never publish/like/comment/subscriber-engage. Other side-effect classes (OAuth, payment, deletion, rights override) require separate permission policy.

## Algorithmic job completion
Inputs must be validated and source coverage report attached. A result can be `SUCCEEDED`, `FAILED`, `BLOCKED`, `REVIEW_REQUIRED` or `CANCELLED`; never `VERIFIED` simply because a local model said so. Successful research may have unanswered low-impact questions, which are visibly reported. High-impact unresolved questions block verified factual narration or public publication.

## Scheduling & order
Dependence DAG: SOURCE_QUALIFICATION -> TOPIC_OBSERVATION -> RESEARCH_PLAN -> SOURCE_VERSIONS -> CLAIM_EVIDENCE -> CRITIQUE -> SCRIPT -> SCENES -> RIGHTS_ASSETS -> RENDER -> QC -> EDITORIAL_APPROVAL -> EXPORT/UPLOAD -> ANALYTICS -> LEARNING. Missing prerequisites stay waiting; cancellation cascades to children only if those child jobs have not already caused external side effects.

## Concurrency / split-brain prevention
SQLite has one transaction writer queue. Per-project revision is compare-and-swap; outputs always include input revision and content digest. Checkpoint every bounded stage. Worker lease expiration makes an attempt **suspect**, not immediately safe to double-execute external calls. Render attempts may restart if output hash not committed; publication attempts require external reconciliation.

## Untrusted input & prompt attacks
Webpage text, transcripts, comments, PDF contents, subtitles and model responses have **no authority** to change rules, execute code, reveal secrets or call privileged functions. Separate quoted evidence data from instruction templates with typed parameters; model output cannot write raw shell arguments or arbitrary file paths. Validate URLs against redirect-time DNS/IP checks and restrict downloaded assets by type/size/duration.

## Engine-specific procedure authority
Every registry engine has exact ID, one canonical owner, domain, execution-phase, prerequisites, generated artifact type, local policy gates, error family and test link. `configs/engine_execution_registry.json` refines v2's index; `playbooks/<domain>.md` defines domain sequencing. If an engine has no supported source or test fixture, mark blocked/deferred, don't replace it with generic creative text.
