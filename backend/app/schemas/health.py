from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class DependencyStatus(BaseModel):
    status: str
    detail: str | None = None


class HealthDependenciesResponse(BaseModel):
    status: str
    ready: bool
    dependencies: dict[str, DependencyStatus]


class RuntimeStatusResponse(BaseModel):
    runtime: str
    langgraph_enabled: bool
    langgraph_available: bool
    checkpointer_backend: str | None = None
    feature_flags: dict[str, bool]
    libraries: dict[str, bool]


class ExaProbeResult(BaseModel):
    provider: str
    query: str
    result_count: int
    latency_ms: float
    degraded: bool
    fallback_reason: str | None = None
