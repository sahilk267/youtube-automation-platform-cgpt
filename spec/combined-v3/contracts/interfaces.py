"""ViralOS v2 canonical *interface stubs* for implementing agents.

This is NOT running application logic. All methods return persisted artifacts/errors,
not model assertions. Do not add parallel data stores in plugins.
"""
from __future__ import annotations
from typing import Any, Literal, Protocol, TypedDict

DomainId = Literal[
    'newsroom','science','technology','business','gaming','history',
    'space','learning','sports','career','productivity','culture'
]
ComputeMode = Literal['AUTO','CPU_ONLY','CUDA_ONLY','HYBRID','REMOTE_WORKER']
GateDecision = Literal['PASS','FAIL','REVIEW_REQUIRED','NOT_APPLICABLE']

class ArtifactRef(TypedDict):
    artifact_id: str
    schema_version: str
    content_sha256: str
    relative_path: str

class DomainContext(TypedDict):
    domain_id: DomainId
    channel_id: str
    project_id: str | None
    locale: str
    market: str
    source_version_ids: list[str]
    policy_version: str
    correlation_id: str

class OperationResult(TypedDict):
    status: Literal['SUCCEEDED','BLOCKED','REVIEW_REQUIRED','FAILED']
    artifact_refs: list[ArtifactRef]
    error_code: str | None
    review_task_ids: list[str]

class SourceFetchRequest(TypedDict):
    provider_id: str
    query: str
    market: str
    locale: str
    max_items: int
    cursor: str | None
    deadline_utc: str

class SourceFetchResult(TypedDict):
    source_version_ids: list[str]
    observation_ids: list[str]
    next_cursor: str | None
    quota_consumed: int | None
    coverage_state: str
    error_code: str | None

class DomainPlugin(Protocol):
    domain_id: DomainId
    manifest_version: str
    async def discover(self, context: DomainContext, query: str) -> OperationResult: ...
    async def plan_research(self, context: DomainContext, topic_id: str) -> OperationResult: ...
    async def investigate(self, context: DomainContext, research_plan_id: str) -> OperationResult: ...
    async def verify(self, context: DomainContext, claim_ids: list[str]) -> OperationResult: ...
    async def reason(self, context: DomainContext, research_plan_id: str) -> OperationResult: ...
    async def create(self, context: DomainContext, project_id: str) -> OperationResult: ...
    async def evaluate(self, context: DomainContext, artifact_ids: list[str]) -> OperationResult: ...
    # NO publish() here. Only publication_service can perform outbound upload.

class ConnectorProvider(Protocol):
    provider_id: str
    async def discover_capabilities(self) -> dict[str, Any]: ...
    async def validate_access(self, credential_ref: str | None, market: str) -> OperationResult: ...
    async def fetch(self, request: SourceFetchRequest) -> SourceFetchResult: ...
    async def normalize(self, source_version_ids: list[str]) -> OperationResult: ...
    async def reconcile(self, source_version_id: str) -> OperationResult: ...

class ComputeProvider(Protocol):
    provider_id: str
    async def capabilities(self) -> dict[str, Any]: ...
    async def estimate_resources(self, job_id: str) -> dict[str, int]: ...
    async def can_run(self, job_id: str) -> tuple[bool, str | None]: ...
    async def execute(self, job_id: str, lease_id: str) -> OperationResult: ...
    async def cancel(self, job_id: str) -> OperationResult: ...

class MediaBackend(Protocol):
    backend_id: str
    async def support(self, scene_spec_id: str, model_id: str | None) -> tuple[bool,str|None]: ...
    async def render(self, scene_spec_id: str, worker_id: str) -> OperationResult: ...

class EditorialGate(Protocol):
    gate_id: str
    async def evaluate(self, project_id: str, revision: int) -> tuple[GateDecision, list[str]]: ...

# The orchestrator owns dispatching of Protocol methods and validating outputs.
# Plugins MUST use canonical core APIs for sources, claims, rights, jobs and uploads.
