from sqlalchemy import text
from fastapi import APIRouter, Response, status

from app.core.database import SessionLocal
from app.core.redis_client import get_redis_client
from app.core.settings import settings
from app.providers.router import ProviderRouter
from app.schemas.health import DependencyStatus, HealthDependenciesResponse, HealthResponse

router = APIRouter()
provider_router = ProviderRouter(settings)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="companionhk-api")


@router.get("/health/dependencies", response_model=HealthDependenciesResponse)
def health_dependencies() -> HealthDependenciesResponse:
    dependencies = _collect_dependency_statuses()
    ready = (
        dependencies["db"].status == "ok"
        and dependencies["redis"].status == "ok"
    )
    return HealthDependenciesResponse(
        status="ok" if ready else "degraded",
        ready=ready,
        dependencies=dependencies,
    )


@router.get("/ready", response_model=HealthDependenciesResponse)
def readiness(response: Response) -> HealthDependenciesResponse:
    payload = health_dependencies()
    if not payload.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


def _collect_dependency_statuses() -> dict[str, DependencyStatus]:
    dependency_statuses: dict[str, DependencyStatus] = {}

    dependency_statuses["db"] = _check_db_dependency()
    dependency_statuses["redis"] = _check_redis_dependency()

    chat_provider = provider_router.resolve_chat_provider()
    dependency_statuses["chat_provider"] = DependencyStatus(
        status=(
            "degraded"
            if settings.chat_provider != "mock" and chat_provider.provider_name == "mock"
            else "ok"
        ),
        detail=chat_provider.provider_name,
    )

    safety_provider = provider_router.resolve_safety_provider()
    safety_status = "ok"
    if settings.feature_safety_monitor_enabled and safety_provider.provider_name != "minimax":
        safety_status = "degraded"
    dependency_statuses["safety_provider"] = DependencyStatus(
        status=safety_status,
        detail=safety_provider.provider_name,
    )

    weather_provider = provider_router.resolve_weather_provider()
    dependency_statuses["weather"] = DependencyStatus(
        status="degraded" if weather_provider.provider_name == "weather-stub" else "ok",
        detail=weather_provider.provider_name,
    )

    maps_provider = provider_router.resolve_maps_provider()
    dependency_statuses["maps"] = DependencyStatus(
        status="degraded" if maps_provider.provider_name == "maps-stub" else "ok",
        detail=maps_provider.provider_name,
    )

    retrieval_provider = provider_router.resolve_retrieval_provider()
    dependency_statuses["exa"] = DependencyStatus(
        status=("degraded" if retrieval_provider.provider_name == "retrieval-stub" else "ok"),
        detail=retrieval_provider.provider_name,
    )

    voice_provider = provider_router.resolve_voice_provider("auto")
    dependency_statuses["voice"] = DependencyStatus(
        status="ok" if voice_provider is not None else "degraded",
        detail=(None if voice_provider is None else voice_provider.provider_name),
    )

    return dependency_statuses


def _check_db_dependency() -> DependencyStatus:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return DependencyStatus(status="ok", detail="db_connected")
    except Exception:
        return DependencyStatus(status="failed", detail="db_unreachable")


def _check_redis_dependency() -> DependencyStatus:
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        return DependencyStatus(status="ok", detail="redis_connected")
    except Exception:
        return DependencyStatus(status="failed", detail="redis_unreachable")
