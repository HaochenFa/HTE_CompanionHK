import logging
import time

from sqlalchemy import text
from fastapi import APIRouter, Response, status

from app.core.database import SessionLocal
from app.core.redis_client import get_redis_client
from app.core.settings import settings
from app.providers.router import ProviderRouter
from app.schemas.health import (
    DependencyStatus,
    ExaProbeResult,
    HealthDependenciesResponse,
    HealthResponse,
    RuntimeStatusResponse,
)

logger = logging.getLogger(__name__)
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


@router.get("/health/runtime", response_model=RuntimeStatusResponse)
def health_runtime() -> RuntimeStatusResponse:
    from app.runtime.factory import build_runtime
    from app.runtime.langgraph_runtime import LANGGRAPH_AVAILABLE

    runtime = build_runtime(settings)
    checkpointer_backend = None
    if hasattr(runtime, "checkpointer_backend"):
        checkpointer_backend = runtime.checkpointer_backend

    feature_flags = {
        "langgraph": settings.feature_langgraph_enabled,
        "minimax": settings.feature_minimax_enabled,
        "elevenlabs": settings.feature_elevenlabs_enabled,
        "cantoneseai": settings.feature_cantoneseai_enabled,
        "exa": settings.feature_exa_enabled,
        "safety_monitor": settings.feature_safety_monitor_enabled,
        "voice_api": settings.feature_voice_api_enabled,
        "weather": settings.feature_weather_enabled,
        "google_maps": settings.feature_google_maps_enabled,
    }

    try:
        import langchain_core
        langchain_available = True
    except ImportError:
        langchain_available = False

    libraries = {
        "langchain_core": langchain_available,
        "langgraph": LANGGRAPH_AVAILABLE,
    }

    logger.info(
        "health_runtime_check runtime=%s langgraph_enabled=%s langgraph_available=%s",
        runtime.runtime_name,
        settings.feature_langgraph_enabled,
        LANGGRAPH_AVAILABLE,
    )

    return RuntimeStatusResponse(
        runtime=runtime.runtime_name,
        langgraph_enabled=settings.feature_langgraph_enabled,
        langgraph_available=LANGGRAPH_AVAILABLE,
        checkpointer_backend=checkpointer_backend,
        feature_flags=feature_flags,
        libraries=libraries,
    )


@router.get("/health/exa-probe", response_model=ExaProbeResult)
def health_exa_probe(query: str = "popular cafes") -> ExaProbeResult:
    retrieval_provider = provider_router.resolve_retrieval_provider()
    provider_name = retrieval_provider.provider_name

    if provider_name == "retrieval-stub":
        logger.info("exa_probe_skipped provider=retrieval-stub")
        return ExaProbeResult(
            provider=provider_name,
            query=query,
            result_count=0,
            latency_ms=0.0,
            degraded=True,
            fallback_reason="exa_not_configured",
        )

    start = time.monotonic()
    try:
        results = retrieval_provider.retrieve(query)
        elapsed_ms = (time.monotonic() - start) * 1000
        degraded = len(results) == 0
        logger.info(
            "exa_probe_completed provider=%s results=%d latency_ms=%.1f degraded=%s",
            provider_name, len(results), elapsed_ms, degraded,
        )
        return ExaProbeResult(
            provider=provider_name,
            query=query,
            result_count=len(results),
            latency_ms=round(elapsed_ms, 1),
            degraded=degraded,
            fallback_reason="no_results_returned" if degraded else None,
        )
    except Exception as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.exception("exa_probe_error provider=%s", provider_name)
        return ExaProbeResult(
            provider=provider_name,
            query=query,
            result_count=0,
            latency_ms=round(elapsed_ms, 1),
            degraded=True,
            fallback_reason=str(exc)[:200],
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

    from app.runtime.factory import build_runtime
    runtime = build_runtime(settings)
    dependency_statuses["runtime"] = DependencyStatus(
        status="ok",
        detail=runtime.runtime_name,
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
