# CORE-10 — Security, Reliability, Testing, Operations, Later SaaS

## 10.1 Local trust boundaries

Untrusted input: websites, documents, video subtitles, CSV exports, model responses, prompts, files uploaded/imported, remote service payloads. Model outputs are data, never shell instructions. Explicit allowlist of subprocess commands/arguments (FFmpeg, renderer, Python sandbox) and safe argument escaping; no arbitrary generated shell execution. Clip/media decoders run in constrained subprocess with temp directory and resource limits. Sanitize URLs against local/network metadata endpoints and redirects.

## 10.2 Secrets and channels

Use OS protected secrets storage (Windows Credential Manager/DPAPI-backed abstraction) with identity scoped to channel/account, redact logs, never export secrets in project backups by default. If backup includes encrypted secrets, require explicit key strategy and restoration instructions. CSRF, localhost binding, origin protection, safe file permissions, no debug admin endpoints in release build. Lock down future browser remote access with TLS/auth/RBAC.

## 10.3 Operational health and observability

Health board shows actual CPU/RAM/disk/optional GPU, jobs by state, model availability, FFmpeg/TTS readiness, connector quotas and age of last successful fetch, OAuth state without tokens, backup last validated, failed QA and rights blockers. Logs JSON lines with trace_id/job_id/revision/status/error_code, rotated and redacted. Track latency, retries, I/O, render time, source freshness, percent job success and recovery. No fabricated performance dashboard. Provide operator-friendly diagnostic bundle excluding credentials and protected source identities.

## 10.4 Backups and disaster recovery

SQLite backup API or consistent transaction-aware snapshot; pair with artifact inventory and checksum manifest. Test clean restore to separate directory, compare integrity + file hashes + route health. Migration failure rolls back using verified backup. Alerts on insufficient free disk and corrupted source hash. User can export/import individual projects in a versioned archive without exposing secrets.

## 10.5 Windows lifecycle

Installer/bootstrap script checks Python, FFmpeg, SSD, writable workspace, RAM and optional voice engines. `run.ps1` starts service and browser at loopback; `health.ps1` checks DB/renderer/workers; `stop.ps1` terminates owned process tree; `backup.ps1` and `restore.ps1` present safe instructions; uninstall never silently deletes content. Offline mode reopens stored projects and doesn't claim fresh trends. Setup dependencies pinned/tested for target Windows hardware.

## 10.6 Evaluation layers

1. Static/lint/type safety: Python type checking/linting, React TS strict, vulnerability/license scan.
2. Schema contracts: validate JSON schemas and DB constraints; data migration tests.
3. Unit: scoring, entity matching, sports metric calculations, evidence classification rule check, rights gates, currency arithmetic, job transitions.
4. Integration: SQLite source->claim->script, media renderer FFmpeg, connector mock quotas, OAuth callback mock, render recovery.
5. E2E: Windows UI->research->script->assets->QC->approved exported video; negative paths.
6. Human editorial: factual citation audit, storytelling, visual accessibility, source independence and originality rubric.
7. Hardware compatibility: i7/32GB/no GPU baseline; optional CUDA machine separate; test crash/cancel/restart.
8. Live external: separate, consented credentials and controlled YouTube test; never use production accounts in CI.

## 10.7 Release integrity

Per release: dependency lock manifest, source license inventory, signed artifact or hash list, migration rollback plan, performance/quality benchmark evidence, acceptance matrix, known limitations, upgrade compatibility and operator changelog. No feature marked `VERIFIED` based solely on screenshots or synthetic fixtures. Security tests include injection via retrieved webpage text, malicious font/media, token leakage, manipulated URL, cross-channel OAuth and cache poisoning.

## 10.8 Future SaaS (Ultimate only, explicitly deferred)

Optional migration path: hosted identity/tenant separation, tenant-scoped rows and artifact paths, PostgreSQL with policy-enforced tenancy, object store, queues/worker isolation, per-account OAuth and provider terms, billing/usage meters, privacy rights, deletion/export, security review, SLOs, support. Business model is **not chosen** and may remain owner-only indefinitely. Avoid putting tenant_id into current hard-coded UI behavior; design schema extensions via migrations and test isolation. Never move user content to cloud automatically.

## 10.9 Performance criteria and honest benchmarks

Implementer must report on actual current hardware: boot and health-check latency, peak RAM for local model, tokens/s if a model is installed, latency for collecting a 20-link research fixture (using permitted sources), 60-second CPU render wall time, file size, sample short/long export, cancel/restart time. No arbitrary promise of throughput or earning timeline. Thresholds may be set after baseline capture, with owner acceptance and ADR.
