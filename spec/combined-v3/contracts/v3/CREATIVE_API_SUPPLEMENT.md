# ViralOS v3.0 Creative Operations HTTP API supplement (NOT implemented code)

Do **not** silently extend the stable v2 `contracts/openapi.yaml` without compatibility tests. Routes below are proposed job dispatch only; they are not direct YouTube/media uploads. All require local authentication, channel ownership check, idempotency-key validation, stored artifact references, strict input schema and bounded execution. All responses use `contracts/v3/CreativeOperationResponse.schema.json`. `op` field in request must match path-restricted allowed operation(s), or HTTP 422. Errors use v2 typed API errors with `error_code` and user-action. A blocked job returns a typed state, not a fabricated success.

| POST route | Allowed operations | Side effect policy |
|---|---|---|
| `/v3/creative/briefs` | CV3-01 | Internal state only |
| `/v3/creative/beats` | CV3-02, CV3-04 | Internal only; cite claims |
| `/v3/creative/shot-plans` | CV3-03, CV3-05, CV3-06, CV3-08 | Asset-side effect only with rights/capability checks |
| `/v3/creative/reactions` | CV3-07 | No automatic source download |
| `/v3/creative/localizations` | CV3-09, CV3-10, CV3-11 | Voice asset only when authorized |
| `/v3/creative/timelines` | CV3-12, CV3-13 | Local media staging |
| `/v3/creative/renders` | CV3-14, CV3-15 | Local rendering only |
| `/v3/creative/approvals` | CV3-16 | Human decision via existing editorial service |

**Uploads and owned-channel analytics MUST reuse v2 publication/analytics routes and outbound-intent lifecycle (CV3-17/18).** No second upload endpoint. On stale revision return 409, no duplicate action. Access unavailable/rights unclear return `BLOCKED` with blocker and next action. The HTTP layer never guarantees task completion synchronously.
