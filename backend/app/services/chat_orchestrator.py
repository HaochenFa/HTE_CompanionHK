import logging
from datetime import datetime, timezone
from typing import cast
from uuid import uuid4

from app.core.database import SessionLocal
from app.core.redis_client import (
    build_short_term_memory_key,
    get_redis_client,
    serialize_json,
)
from app.core.settings import settings
from app.memory.embeddings import build_embedding_provider
from app.memory.context_builder import ConversationContextBuilder
from app.models.enums import (
    AuditEventType,
    MemoryEntryType,
    ProviderEventScope,
    ProviderEventStatus,
    RoleType,
    SafetyRiskLevel,
)
from app.providers.router import ProviderRouter
from app.repositories.audit_repository import AuditRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.user_repository import UserRepository
from app.runtime.base import ConversationRuntime
from app.runtime.factory import build_runtime
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatRole,
    ChatTurn,
    ClearHistoryResponse,
    SafetyResult,
)
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.safety import SafetyEvaluateRequest
from app.services.safety_monitor_service import SafetyMonitorService

logger = logging.getLogger(__name__)
_SUPPORTIVE_REFUSAL_REPLY = (
    "I hear that you are in a lot of pain right now. I cannot help with anything that could "
    "harm you, but I care about your safety and we can take one small step together. "
    "If you may be in immediate danger, please call 999. You can also contact The Samaritans "
    "Hong Kong (2896 0000), Suicide Prevention Services (2382 0000), or The Samaritan "
    "Befrienders Hong Kong (2389 2222)."
)


class ChatOrchestrator:
    """Mock orchestrator boundary for provider routing and safety hooks."""

    def __init__(
        self,
        provider_router: ProviderRouter | None = None,
        runtime: ConversationRuntime | None = None,
        context_builder: ConversationContextBuilder | None = None,
        safety_monitor_service: SafetyMonitorService | None = None,
    ):
        self._settings = settings
        self._provider_router = provider_router or ProviderRouter(settings)
        self._runtime = runtime or build_runtime(settings)
        self._embedding_provider = build_embedding_provider(
            api_key=settings.minimax_api_key,
            model=settings.memory_embedding_model,
            base_url=settings.minimax_base_url,
            dimensions=settings.memory_embedding_dimensions,
        )
        self._context_builder = context_builder or ConversationContextBuilder(
            settings)
        self._safety_monitor_service = safety_monitor_service or SafetyMonitorService(
            self._provider_router
        )

    def _persist_short_term_memory(
        self,
        *,
        user_id: str,
        role: str,
        thread_id: str,
        request_id: str,
        user_message: str,
        assistant_reply: str,
    ) -> None:
        redis_client = get_redis_client()
        redis_key = build_short_term_memory_key(
            user_id=user_id,
            role=cast(ChatRole, role),
            thread_id=thread_id,
        )
        payload = {
            "request_id": request_id,
            "user_message": user_message,
            "assistant_reply": assistant_reply,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        pipeline = redis_client.pipeline()
        pipeline.lpush(redis_key, serialize_json(payload))
        pipeline.ltrim(
            redis_key, 0, self._settings.memory_short_term_max_turns - 1)
        pipeline.expire(
            redis_key, self._settings.memory_short_term_ttl_seconds)
        pipeline.execute()

    def _persist_chat_turn(
        self,
        *,
        request_id: str,
        user_id: str,
        role: str,
        thread_id: str,
        user_message: str,
        assistant_reply: str,
        runtime: str,
        provider_route: str,
        provider_fallback_reason: str,
        context_snapshot: dict[str, object],
        safety: SafetyResult,
    ) -> None:
        role_enum = RoleType(role)
        provider_status = (
            ProviderEventStatus.success
            if provider_fallback_reason == "not_applicable"
            else ProviderEventStatus.fallback
        )
        with SessionLocal() as session:
            user_repository = UserRepository(session)
            chat_repository = ChatRepository(session)
            memory_repository = MemoryRepository(session)
            audit_repository = AuditRepository(session)

            user_repository.ensure_user(user_id)
            thread = chat_repository.get_or_create_thread(
                user_id=user_id,
                role=role_enum,
                thread_id=thread_id,
            )

            message = chat_repository.create_chat_message(
                thread_pk=thread.id,
                user_id=user_id,
                role=role_enum,
                thread_id=thread_id,
                request_id=request_id,
                user_message=user_message,
                assistant_reply=assistant_reply,
                runtime=runtime,
                provider=provider_route,
                provider_fallback_reason=provider_fallback_reason,
                context_snapshot=context_snapshot,
            )
            chat_repository.create_safety_event(
                chat_message_id=message.id,
                thread_pk=thread.id,
                user_id=user_id,
                role=role_enum,
                thread_id=thread_id,
                request_id=request_id,
                risk_level=SafetyRiskLevel(safety.risk_level),
                show_crisis_banner=safety.show_crisis_banner,
                emotion_label=safety.emotion_label,
                emotion_score=safety.emotion_score,
            )

            audit_repository.create_provider_event(
                user_id=user_id,
                request_id=request_id,
                role=role_enum,
                scope=ProviderEventScope.chat,
                provider_name=provider_route,
                runtime=runtime,
                status=provider_status,
                fallback_reason=provider_fallback_reason,
                metadata_json={"thread_id": thread_id},
            )
            audit_repository.create_provider_event(
                user_id=user_id,
                request_id=request_id,
                role=role_enum,
                scope=ProviderEventScope.safety,
                provider_name=safety.monitor_provider,
                runtime=runtime,
                status=(
                    ProviderEventStatus.degraded
                    if safety.degraded
                    else ProviderEventStatus.success
                ),
                fallback_reason=safety.fallback_reason,
                metadata_json={
                    "risk_level": safety.risk_level,
                    "policy_action": safety.policy_action,
                },
            )
            fresh_retrieval = (
                ((context_snapshot.get("memory") or {}).get("fresh_retrieval"))
                if isinstance(context_snapshot, dict)
                else None
            )
            if isinstance(fresh_retrieval, dict):
                retrieval_source = str(fresh_retrieval.get("source", "retrieval-stub"))
                retrieval_status = (
                    ProviderEventStatus.degraded
                    if fresh_retrieval.get("status") == "degraded"
                    else ProviderEventStatus.success
                )
                audit_repository.create_provider_event(
                    user_id=user_id,
                    request_id=request_id,
                    role=role_enum,
                    scope=ProviderEventScope.retrieval,
                    provider_name=retrieval_source,
                    runtime=runtime,
                    status=retrieval_status,
                    fallback_reason=(
                        None
                        if retrieval_status == ProviderEventStatus.success
                        else str(fresh_retrieval.get("fallback_reason") or "retrieval_unavailable")
                    ),
                    metadata_json={
                        "entry_count": len(fresh_retrieval.get("entries", [])),
                    },
                )
            audit_repository.create_audit_event(
                event_type=AuditEventType.safety_event,
                user_id=user_id,
                request_id=request_id,
                role=role_enum,
                thread_id=thread_id,
                metadata_json={
                    "risk_level": safety.risk_level,
                    "show_crisis_banner": safety.show_crisis_banner,
                    "emotion_label": safety.emotion_label,
                    "emotion_score": safety.emotion_score,
                    "policy_action": safety.policy_action,
                    "monitor_provider": safety.monitor_provider,
                    "fallback_reason": safety.fallback_reason,
                },
            )

            summary_excerpt = user_message.strip()[:200]
            memory_entry = memory_repository.create_memory_entry(
                user_id=user_id,
                role=role_enum,
                thread_id=thread_id,
                entry_type=MemoryEntryType.summary,
                content=f"User intent summary: {summary_excerpt}",
                write_reason="chat_turn_summary",
                source_provider=provider_route,
                created_by_request_id=request_id,
                metadata_json={
                    "runtime": runtime,
                    "request_id": request_id,
                },
                is_sensitive=False,
            )
            memory_embedding = self._embedding_provider.embed(
                f"{user_message}\n{assistant_reply}"
            )
            memory_repository.create_memory_embedding(
                memory_entry_id=memory_entry.id,
                user_id=user_id,
                role=role_enum,
                embedding_model=self._settings.memory_embedding_model,
                embedding_dimensions=len(memory_embedding),
                embedding=memory_embedding,
                distance_metric="cosine",
            )
            audit_repository.create_audit_event(
                event_type=AuditEventType.memory_write,
                user_id=user_id,
                request_id=request_id,
                role=role_enum,
                thread_id=thread_id,
                metadata_json={
                    "memory_entry_id": memory_entry.id,
                    "entry_type": memory_entry.entry_type.value,
                },
            )

            session.commit()

    def generate_reply(self, chat_request: ChatRequest) -> ChatResponse:
        request_id = str(uuid4())
        role = chat_request.role
        thread_id = chat_request.thread_id or f"{chat_request.user_id}-{role}-thread"
        provider = self._provider_router.resolve_chat_provider()
        provider_route = provider.provider_name
        fallback_reason = (
            "provider_disabled_or_unavailable"
            if provider_route != settings.chat_provider and settings.chat_provider != "mock"
            else "not_applicable"
        )
        context = self._context_builder.build(
            user_id=chat_request.user_id,
            thread_id=thread_id,
            role=role,
            message=chat_request.message
        )
        if chat_request.attachment is not None:
            context["attachment"] = {
                "mime_type": chat_request.attachment.mime_type,
                "filename": chat_request.attachment.filename,
                "size_bytes": chat_request.attachment.size_bytes,
                "has_base64": True,
            }

        logger.info(
            "chat_orchestrated request_id=%s role=%s thread_id=%s runtime=%s provider_route=%s fallback_reason=%s user_id=%s",
            request_id,
            role,
            thread_id,
            self._runtime.runtime_name,
            provider_route,
            fallback_reason,
            chat_request.user_id
        )

        safety_result = self._safety_monitor_service.evaluate(
            SafetyEvaluateRequest(
                user_id=chat_request.user_id,
                role=role,
                thread_id=thread_id,
                message=chat_request.message,
            )
        )
        safety = SafetyResult(
            risk_level=safety_result.risk_level,
            show_crisis_banner=safety_result.show_crisis_banner,
            emotion_label=safety_result.emotion_label,
            emotion_score=safety_result.emotion_score,
            policy_action=safety_result.policy_action,
            monitor_provider=safety_result.monitor_provider,
            degraded=safety_result.degraded,
            fallback_reason=safety_result.fallback_reason,
        )
        runtime_context = dict(context)
        if chat_request.attachment is not None:
            runtime_context["attachment_base64"] = chat_request.attachment.base64_data
        runtime_context["safety"] = safety.model_dump()

        if safety.policy_action == "supportive_refusal":
            reply = _SUPPORTIVE_REFUSAL_REPLY
        else:
            reply = self._runtime.generate_reply(
                message=chat_request.message,
                provider=provider,
                context=runtime_context
            )

        try:
            self._persist_chat_turn(
                request_id=request_id,
                user_id=chat_request.user_id,
                role=role,
                thread_id=thread_id,
                user_message=chat_request.message,
                assistant_reply=reply,
                runtime=self._runtime.runtime_name,
                provider_route=provider_route,
                provider_fallback_reason=fallback_reason,
                context_snapshot=runtime_context,
                safety=safety,
            )
        except Exception:
            logger.exception(
                "chat_persistence_failed request_id=%s user_id=%s role=%s thread_id=%s",
                request_id,
                chat_request.user_id,
                role,
                thread_id,
            )

        try:
            self._persist_short_term_memory(
                user_id=chat_request.user_id,
                role=role,
                thread_id=thread_id,
                request_id=request_id,
                user_message=chat_request.message,
                assistant_reply=reply,
            )
        except Exception:
            logger.exception(
                "redis_short_term_memory_write_failed request_id=%s user_id=%s role=%s thread_id=%s",
                request_id,
                chat_request.user_id,
                role,
                thread_id,
            )

        return ChatResponse(
            request_id=request_id,
            thread_id=thread_id,
            runtime=self._runtime.runtime_name,
            provider=provider_route,
            reply=reply,
            safety=safety,
        )

    def get_history(
        self,
        *,
        user_id: str,
        role: ChatRole,
        thread_id: str | None = None,
        limit: int = 50,
    ) -> ChatHistoryResponse:
        bounded_limit = max(1, min(limit, 200))
        resolved_thread_id = thread_id or f"{user_id}-{role}-thread"
        role_enum = RoleType(role)
        with SessionLocal() as session:
            chat_repository = ChatRepository(session)
            rows = chat_repository.list_recent_messages_with_safety(
                user_id=user_id,
                role=role_enum,
                thread_id=resolved_thread_id,
                limit=bounded_limit,
            )

        turns: list[ChatTurn] = []
        for message, safety_event in reversed(rows):
            safety = SafetyResult(
                risk_level=(
                    cast(str, safety_event.risk_level.value)
                    if safety_event is not None
                    else "low"
                ),
                show_crisis_banner=(
                    safety_event.show_crisis_banner if safety_event is not None else False
                ),
                emotion_label=safety_event.emotion_label if safety_event is not None else None,
                emotion_score=safety_event.emotion_score if safety_event is not None else None,
            )
            turns.append(
                ChatTurn(
                    request_id=message.request_id,
                    thread_id=message.thread_id,
                    created_at=message.created_at,
                    user_message=message.user_message,
                    assistant_reply=message.assistant_reply,
                    safety=safety,
                )
            )
        return ChatHistoryResponse(
            user_id=user_id,
            role=role,
            thread_id=resolved_thread_id,
            turns=turns,
        )

    def clear_history(
        self,
        *,
        user_id: str,
        role: ChatRole,
        thread_id: str | None = None,
    ) -> ClearHistoryResponse:
        resolved_thread_id = thread_id or f"{user_id}-{role}-thread"
        role_enum = RoleType(role)
        new_thread_id = f"{user_id}-{role}-thread-{uuid4().hex[:8]}"

        cleared_message_count = 0
        cleared_memory_count = 0
        cleared_recommendation_count = 0

        with SessionLocal() as session:
            chat_repo = ChatRepository(session)
            memory_repo = MemoryRepository(session)
            recommendation_repo = RecommendationRepository(session)

            messages = chat_repo.list_recent_messages(
                user_id=user_id,
                role=role_enum,
                thread_id=resolved_thread_id,
                limit=10000,
            )
            request_ids = [m.request_id for m in messages]

            cleared_message_count = chat_repo.delete_thread_messages(
                user_id=user_id,
                role=role_enum,
                thread_id=resolved_thread_id,
            )
            cleared_memory_count = memory_repo.delete_by_thread(
                user_id=user_id,
                role=role_enum,
                thread_id=resolved_thread_id,
            )
            if request_ids:
                cleared_recommendation_count = recommendation_repo.delete_by_request_ids(
                    user_id=user_id,
                    role=role_enum,
                    request_ids=request_ids,
                )

            session.commit()

        try:
            redis_client = get_redis_client()
            redis_key = build_short_term_memory_key(
                user_id=user_id,
                role=cast(ChatRole, role),
                thread_id=resolved_thread_id,
            )
            redis_client.delete(redis_key)
        except Exception:
            logger.exception(
                "clear_history_redis_cleanup_failed user_id=%s role=%s thread_id=%s",
                user_id, role, resolved_thread_id,
            )

        logger.info(
            "clear_history_completed user_id=%s role=%s thread_id=%s new_thread_id=%s msgs=%d mem=%d rec=%d",
            user_id, role, resolved_thread_id, new_thread_id,
            cleared_message_count, cleared_memory_count, cleared_recommendation_count,
        )

        return ClearHistoryResponse(
            user_id=user_id,
            role=role,
            cleared_thread_id=resolved_thread_id,
            new_thread_id=new_thread_id,
            cleared_message_count=cleared_message_count,
            cleared_memory_count=cleared_memory_count,
            cleared_recommendation_count=cleared_recommendation_count,
        )
