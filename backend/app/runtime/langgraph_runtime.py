import logging
from typing import Any

from app.providers.base import ChatProvider
from app.prompts.role_prompts import resolve_role_system_prompt
from app.runtime.base import ConversationRuntime

logger = logging.getLogger(__name__)
_KNOWN_ROLES = {"companion", "local_guide", "study_guide"}

try:
    import langgraph  # type: ignore  # noqa: F401
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class LangGraphConversationRuntime(ConversationRuntime):
    """
    LangGraph-capable runtime boundary.

    This currently preserves existing chat behavior and provides a safe activation
    path while full graph/checkpointer wiring is implemented in the next slices.
    """

    runtime_name = "langgraph"

    def __init__(self, checkpointer_backend: str = "memory"):
        self._checkpointer_backend = checkpointer_backend

    def generate_reply(
        self,
        *,
        message: str,
        provider: ChatProvider,
        context: dict[str, Any]
    ) -> str:
        role = context.get("role")
        if role not in _KNOWN_ROLES:
            role = "companion"

        runtime_context = dict(context)
        runtime_context["system_prompt"] = resolve_role_system_prompt(role)

        if not LANGGRAPH_AVAILABLE:
            logger.warning(
                "langgraph_runtime_requested_but_unavailable checkpointer_backend=%s thread_id=%s",
                self._checkpointer_backend,
                runtime_context.get("thread_id")
            )
            return provider.generate_reply(message, runtime_context)

        # Placeholder execution path: runtime is selected and context is passed,
        # while preserving provider response behavior for the foundation slice.
        logger.info(
            "langgraph_runtime_selected checkpointer_backend=%s thread_id=%s",
            self._checkpointer_backend,
            runtime_context.get("thread_id")
        )
        return provider.generate_reply(message, runtime_context)
