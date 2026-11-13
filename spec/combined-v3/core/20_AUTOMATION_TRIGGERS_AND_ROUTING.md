# CORE-20 — AUTOMATIC EVENTS AND RUN-TO-COMPLETION

`configs/workflow_dag.json` is canonical machine-readable job order and event trigger registry. Every periodic trigger is **off until owner authorizes its source, query scope and cadence**; no uncontrolled scraping or task storm. Engine dependencies are acyclic, persisted, rate-limited and idempotent.

## Fully automated processing, bounded by approvals
Once configured and authorized: source change/fixture event -> trend observation -> deduplicated topic -> editorial decision -> bounded source research with coverage/gaps -> claim verification -> script/storyboard -> licensed assets -> compute reservation -> image/diagram/video generation if available -> FFmpeg composition -> technical/rights/factual gate -> (human required when policy says) -> export -> optionally owner-enabled upload -> authorized analytics and learning. Unknown rights/claim/data/provider state pauses only the affected branch, not all channels. Sensitive claims are NEVER auto-approved by AI roles.

## Per-operation state
Every step has event trigger, input digest, idempotency key, input/output schema, independent gate, timeout/retry budget, and explicit error state; jobs cannot skip prerequisites via speculative status. Polling retries only for transient network errors; quota exhaustion waits, provider policy blocks, OAuth revocation holds, GPU absence queues. High-impact source correction invalidates dependent script/reviews/approval and surfaces correction decision.

## Auto publication policy
Default MANUAL. Owner may explicitly enable a channel-scoped low-risk trusted mode with policy version, revocation, expiration and visibility limit. Any suspected allegations, news reconstructions or unknown media rights override this and require human approval. YouTube external side effects always require remote reconciliation to avoid duplicate uploads. AI is allowed to draft and analyze but cannot claim guaranteed reach, income or eligibility.

## Operational feedback
Observe actual durations, retries, quota, API source health, time to complete, media failures and rights rejections. Self-learning may propose prompt/storytelling changes and controlled experiments but cannot autonomously alter hard safety policy, external credentials or published corrections.
