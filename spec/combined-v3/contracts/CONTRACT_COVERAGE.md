# v2.1 Typed API Conformance

`contracts/openapi.yaml` has concrete response DTO references per operation. `configs/api_operation_registry.json` lists all operations. Every response schema under `contracts/api_responses/` wraps a named strict data contract in a standard request-id/version envelope. Prior v2.0 generic object placeholders were replaced for the documented operations; no server endpoints are implemented here.

Strict request body DTOs are in `contracts/` for connector sync, channel revision edit, rendering, analytics sync, script revision, experiment creation and compute mode. An endpoint returning a model that lacks actual provider fields must be updated via versioned schema and ADR before release; do not forge missing fields just to satisfy validation. Models and data getters may return availability/status data instead of pretending external systems were queried. HTTP 2xx does not prove publishing state.

**Known API semantic limitation:** an API may require deeper provider-specific subtypes in live implementation. These must be defined and tested before enabling that provider, not inferred at runtime.

Publication lookup uses `PublicationStatus` containing independently observed remote status; experimentation uses `ExperimentRecord`, not its create request DTO.
