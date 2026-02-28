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
