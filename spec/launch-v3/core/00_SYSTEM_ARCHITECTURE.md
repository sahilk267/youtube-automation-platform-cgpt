# CORE-00 — System Architecture and Ownership Map

## 0.1 Architectural decisions (normative for v2.0)

| Choice | Implementation | Rationale / exclusions |
|---|---|---|
| Product style | Windows local-first browser dashboard launched by lightweight Windows launcher | No Electron requirement; mobile support future only |
| User interface | React + TypeScript + Vite, static build served by FastAPI | Separate dev server allowed only in development |
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Version lockfiles must be generated and tested, not fabricated |
| Durable store | SQLite with foreign keys, WAL, FTS5 and single-writer discipline | No fake production Postgres. Later use documented migration |
| File storage | Local workspace content-addressed media/evidence/artifacts | File bytes not inserted wholesale into SQLite |
| CPU renderer | FFmpeg with scene-spec-defined overlays, diagrams, audio, captions | No generative video dependency for Launch |
| Local LLM | Replaceable Ollama/llama.cpp adapter, optional; deterministic fallback if absent | Model outputs do not prove factual claims |
| TTS/STT | Piper / whisper.cpp adapters where installed/licensed; manual voice import fallback | Never auto-clone celebrity voice |
| Heavy job scheduling | Durable DB-backed single-machine job queue with lease and heartbeat; at most one heavyweight CPU worker by default | Avoid mandatory Redis/Docker/paid infra in Launch |
| GPU | Optional CUDA capability provider; never required to boot Launch | Check actual compatible model manifests |
| YouTube | Official authorized API adapter, manual export fallback | No scraping private analytics/no approval bypass |
| Runtime distribution | Portable Windows bootstrap/launcher + documented setup; build installer later | First release need not claim one-click EXE before tested |
| Target markets | Configurable country/language/time zone per channel | No automatic assumption of audience profitability |

Decisions above are **engineering defaults** selected to close ambiguity, not claims that owner personally specified exact library versions. Agents may not silently change them; propose ADRs with acceptance evidence.

## 0.2 Layers, modules and single ownership

```
LOCAL WINDOWS LAUNCHER -> REACT UI -> FASTAPI (localhost)
                                  |
                 AUTH / CHANNEL PROFILES / EDITORIAL COUNCIL
                                  |
                      WORKFLOW DAG / JOB SCHEDULER
                 /                |                   \
       DOMAIN PLUGIN ROUTER  RESEARCH/EVIDENCE     CREATOR STUDIO
           |               CONNECTORS/FTS            |
         Sports, Newsroom, ...                   CPU/GPU COMPUTE
                 \                |                   /
                  SQLite + Artifact Store + Audit Events
                                  |
                   Publishing -> Analytics -> Learning
```

| Canonical owner module | Responsible for | May NOT duplicate |
|---|---|---|
| `channel_registry` | Channel config, market, style, approvals | Analytics imports, direct YouTube OAuth logic |
| `connector_registry` | Source API adapters, quotas, provenance intake | Domain-local duplicated HTTP scrapers |
| `trend_engine` | Observations, time series, topics/clusters | Claim truth decisions |
| `research_engine` | Plans, retrieval orchestration, completeness | Domain-specific fact calculators |
| `evidence_service` | Source versions, claims, evidence edges, contradiction metadata | A second domain evidence database |
| `domain_router` | Domain/plugin selection and domain-specific jobs | Common source store, publication |
| `editorial_council` | Hard risk/rights/disclosure gates and approvals | Topic scoring or legal guarantees |
| `creator_studio` | Script/storyboard/asset plan, scene sequencing | Truth verification by visual model |
| `media_pipeline` | Render profiles, FFmpeg, TTS, caption and media QC | Parallel handwritten render pipelines per domain |
| `compute_scheduler` | Worker capability discovery, admission, leases and resources | Domain-specific ad hoc GPU selection |
| `publication_service` | Authorized YouTube upload, reconciliation, editorial immutable snapshot | Direct plugin upload calls |
| `analytics_service` | Authorized observations and performance cohort analysis | Synthetic real revenue |
| `revenue_ledger` | Actual earnings, costs and GPU savings | Predicted view-based income as actual |
| `asset_rights` | Asset provenance, restrictions and license review | Treat provider availability as rights grant |
| `audit_backup` | Audit, backups, recovery, security observability | Model-written audit events as sole proof |

## 0.3 Repository layout (target implementer output)

```
viral-os/
  pyproject.toml, requirements.lock, uv.lock or equivalent
  frontend/{package.json,package-lock.json,src/}
  backend/viralos/{api,auth,config,models,db,core,connectors,domains,
                   evidence,trend,research,creator,media,compute,
                   editorial,publishing,analytics,revenue,observability}/
  backend/migrations/versions/
  windows/{setup.ps1,run.ps1,health.ps1,backup.ps1,restore.ps1}
  configs/{domains,channels,policies,model_registry}/
  tests/{unit,integration,contract,e2e,fixtures,golden}/
  docs/{operator,developer,security,rights,release_notes}/
```

Runtime state MUST live outside source repository, under chosen workspace such as `%LOCALAPPDATA%\\ViralOS\\` (config override allowed). Secrets MUST live in OS-protected store, not repository or JSON config.

## 0.4 API design discipline

- Prefix `/api/v1`. Request/response JSON typed by Pydantic matching `contracts/`.
- All mutating operations have idempotency key; every long-running operation returns `job_id`, not fake immediate completion.
- Auth: loopback-only per-session CSRF-aware UI; if LAN/remote is enabled later require auth, TLS and explicit access control. CORS off by default except local dev origin.
- Expected endpoint groups: `/health`, `/capabilities`, `/channels`, `/topics`, `/research`, `/claims`, `/sources`, `/projects`, `/scenes`, `/assets`, `/renders`, `/reviews`, `/publications`, `/analytics`, `/ledger`, `/jobs`, `/models`, `/settings`, `/audit`. Exact per-route behavior in CORE-01.
- List endpoints paginate, filter by channel/domain and return observation freshness. Unknown fields rejected by contract parsers; incompatible contract versions are errors.

## 0.5 Cross-domain execution protocol

A single news item may be relevant to multiple domains. The `domain_router` computes relevant audiences and proposes distinct `content_project`s only when each has a different factual question, value proposition and script. It shares cached research SourceVersion IDs and source citations. It never blindly clones near-identical videos. A `content_similarity_hash` and semantic review compare planned titles, scripts and media across channels. Overlap produces `REVIEW_DUPLICATE_CONTENT` rather than automatic publication.

## 0.6 Hardware continuity invariant

All artifacts and jobs are hardware-independent records. A job can be re-run on CPU, single-GPU or remote worker by choosing a compatible adapter and new `render_attempt_id`; existing source citations, scripts, review history and project IDs remain identical. GPU-only job is `WAITING_FOR_CAPABILITY`, not a fatal launch failure. Rendering derived assets with new generation models requires a new output version and new approval.

## 0.7 Out-of-scope Launch features

Full generative video, GPU multiworker coordination, autonomous source interviewing, bought datasets, custom voice cloning, 12 simultaneously operating full research domains, and SaaS billing are **not** launch acceptance requirements. They remain mapped to Ultimate rather than silently discarded.
