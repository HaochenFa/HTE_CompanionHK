import logging
from uuid import uuid4

from app.core.settings import settings
from app.memory.context_builder import ConversationContextBuilder
from app.providers.router import ProviderRouter
from app.runtime.base import ConversationRuntime
from app.runtime.factory import build_runtime
from app.schemas.chat import ChatRequest, ChatResponse, SafetyResult

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """Mock orchestrator boundary for provider routing and safety hooks."""

    def __init__(
        self,
        provider_router: ProviderRouter | None = None,
        runtime: ConversationRuntime | None = None,
        context_builder: ConversationContextBuilder | None = None
    ):
        self._provider_router = provider_router or ProviderRouter(settings)
        self._runtime = runtime or build_runtime(settings)
        self._context_builder = context_builder or ConversationContextBuilder(
            settings)

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

        reply = self._runtime.generate_reply(
            message=chat_request.message,
            provider=provider,
            context=context
        )
        return ChatResponse(
            request_id=request_id,
            thread_id=thread_id,
            runtime=self._runtime.runtime_name,
            provider=provider_route,
            reply=reply,
            safety=SafetyResult(risk_level="low", show_crisis_banner=False)
        )
