# GAP AUDIT & FIX REGISTRY — v2.1

**Reviewed inputs:** ViralOS Launch & Ultimate self-contained v2 documents and canonical 84-file v2.0 ZIP. This is a specification consistency review, **not** a code audit of a running platform. Gaps below are addressed as design contracts; external sources, permissions and hardware need live validation.

**Never claim all unknowns removed.** `CLOSED_IN_SPEC` = prescribed safe behavior, not working tested software. The agent must keep the actual implementation tracker separate.

| Gap | Severity | V2 finding | v2.1 closure artifact | Status |
|---|---|---|---|---|
| G-001 | CRITICAL | Engine interfaces declare generic input/output text; no typed operation protocol | ExecutionRequest/Result schemas, core/14, engine execution registry | CLOSED_IN_SPEC |
| G-002 | HIGH | Many OpenAPI success/error bodies vague and pagination not fully modeled | Typed OpenAPI 38 operation responses, response schemas, strict new request DTOs and conformance registry | CLOSED_IN_SPEC |
| G-003 | CRITICAL | Launch/Ultimate had blended release gates and cross-referenced deferred features | distinct manifest profiles and dedicated validators | CLOSED_IN_SPEC |
| G-004 | HIGH | No exact priority or precedence when canonical requirements contradict addenda | SPEC_PRECEDENCE.md; conflict is blocker, not choose-by-guess | CLOSED_IN_SPEC |
| G-005 | CRITICAL | Runtime sources/rights/OAuth unspecified could be silently fabricated | blocker ledger, live connector qualification, offline fallback | CLOSED_IN_SPEC |
| G-006 | HIGH | Engine registry 144 names but not individual state/IO/output requirements | Engine execution registry, per-engine negative-case fixture, domain-specific playbooks | CLOSED_IN_SPEC |
| G-007 | CRITICAL | Human approval revocation and upload timeout reconciliation not executable | core/16 side-effect state machines + migration 002 | CLOSED_IN_SPEC |
| G-008 | HIGH | Per-source reliability vs independence groups and metadata-only access ambiguous | core/17 evidence gates, SourceCoverageReport | CLOSED_IN_SPEC |
| G-009 | HIGH | No explicit negative caching, source change invalidation boundaries | core/17 cache TTL and downstream invalidation rules | CLOSED_IN_SPEC |
| G-010 | HIGH | Research completion lacked mandatory report of inaccessible or unsearched sources | SourceCoverageReport and bounded stopping conditions | CLOSED_IN_SPEC |
| G-011 | HIGH | Sports event corrections/time-zone/partial score invalidation insufficiently tested | playbooks/sports plus sport specific negative fixtures | CLOSED_IN_SPEC |
| G-012 | HIGH | No mandatory technology/security benchmark replay artifacts | playbooks/technology, immutable benchmark logs | CLOSED_IN_SPEC |
| G-013 | HIGH | GPU scaling assumes model capability without live model/driver benchmark | core/18 capability negotiation and GPU only hold | CLOSED_IN_SPEC |
| G-014 | HIGH | Media generation prompt/shot chain lacks explicit scene to claims provenance | core/18, scene-scoped source IDs and reconstruction labels | CLOSED_IN_SPEC |
| G-015 | HIGH | LLM prompt injection and tool side effects insufficiently contract-bound | core/14 untrusted input isolation + typed API and source gates | CLOSED_IN_SPEC |
| G-016 | HIGH | Filesystem Windows paths, ffmpeg crash checkpoints and CPU budgets underspecified | core/18 staging and deterministic rendering profiles | CLOSED_IN_SPEC |
| G-017 | HIGH | No zero-trust source connector qualification evidence | configs/provider_acceptance.json; tests/provider cases | CLOSED_IN_SPEC |
| G-018 | MEDIUM | Audience optimization might reward sensational or unsupported thumbnails | core/19 learning guardrails and truthful packaging | CLOSED_IN_SPEC |
| G-019 | HIGH | No independent external acceptance owner sign-off for release | tests/OPERATOR_RELEASE_CHECKLIST.md | CLOSED_IN_SPEC |
| G-020 | HIGH | No robust ZIP separation/integrity with root manifests | PACK_MANIFEST.json, FILE_HASHES.json, ZIP_SELF_TEST.py | CLOSED_IN_SPEC |
| G-021 | HIGH | Spec validator previously checked document shape but not operation fixtures | tools/validate_pack.py including JSON schema examples and SQL behavior | CLOSED_IN_SPEC |
| G-022 | HIGH | No upload-reconciliation journal / actual observed vs forecast provenance | database/002_operational_controls.sql; core/16 | CLOSED_IN_SPEC |
| G-023 | MEDIUM | No explicit non-functional limits and resourcing policy for 32GB i7 | core/18 conservative profile with real benchmark calibration | CLOSED_IN_SPEC |
| G-024 | MEDIUM | Revenue and GPU goals risk equating views with earnings | core/19 actuals, scenario segregation and zero income guarantee | CLOSED_IN_SPEC |
| G-025 | HIGH | Domain agent roles may be mistaken for independent fact-checking | playbook rules require external records and deterministic tests | CLOSED_IN_SPEC |
| G-026 | HIGH | Spec archival v1/v2 copies repeated and potentially conflicting | v2.1 single canonical file per module; earlier versions excluded from runtime spec | CLOSED_IN_SPEC |
| G-027 | HIGH | No enforced idempotency checks for external side effects and mismatched payload keys | core/16 idempotency hashing and remote reconciliation | CLOSED_IN_SPEC |
| G-028 | HIGH | Database migration forward-only policy and downgrade policy underdefined | core/16 migration preflight backup, smoke test, read-only recovery | CLOSED_IN_SPEC |
| G-029 | HIGH | Sensitive allegation right-of-reply and dispute burden unclear | playbooks/newsroom high-risk audit and human gate | CLOSED_IN_SPEC |
| G-030 | MEDIUM | License and model commercial use need review at GPU activation | core/18 model provenance and capability gate | CLOSED_IN_SPEC |

## Externally blocked facts that cannot be fixed by inventing details

YouTube owner credentials/authorizations, real channel audiences and revenue, permitted league statistics APIs, sports broadcast licenses, internet conditions, individual SSD capacity, installed model licences, Windows OS build, measured render speeds, future CUDA hardware, local GPU cost/stock, and jurisdiction-specific legal advice are **unknown until actually verified**. Each becomes a `BLOCKED_EXTERNAL` or `OWNER_DECISION_REQUIRED` task with visible manual fallback. Release evidence may not be faked or replaced by mock screenshots.

## Conflict review

- Cricket, NFL, MLB, NBA and soccer are **Sports subadapters**; never create five parallel top-level OSs.
- One evidence store, one shared source registry, one publication service, one rights authority, one analytics ledger. A domain may add rules, never duplicate side-effect clients.
- Launch is a narrow release profile, not a fork; Ultimate must ingest existing project IDs, DB schema, source history, content exports, rights and audit trails without manual copy.
- Research completeness means **bounded, transparent attempted coverage**, not omniscience. Score and insight are different from a verified claim.
- CPU-only baseline must genuinely run without CUDA; image/video generation is optional, blocked until compatible GPU/models/licensing confirmed.
- YouTube manual export is a first-class success mode without OAuth; optional auto-publication requires explicit owner opt-in, hard gates and channel authentication.
- External AI tools are not independent corroboration simply because multiple roles requested an answer.
- SaaS is deferred; owner-only YouTube revenue is the initial business goal.

**v2.1 additional closure:** `configs/workflow_dag.json` expresses actual event triggers and dependency order. Each registered engine now carries its own negative-case test ID. Typed API DTOs are versioned. No code implementation is implied.


> v3.0 NOTE: This is v2.1 historical gap audit; the authoritative content-production changes are `V3_CHANGELOG_AND_RESIDUAL_GAPS.md` and `core/21`–`core/26`. All functionality still requires implementation tests.
