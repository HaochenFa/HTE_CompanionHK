from typing import Any

from app.providers.base import ChatProvider
from app.prompts.role_prompts import resolve_role_system_prompt
from app.runtime.base import ConversationRuntime

_KNOWN_ROLES = {"companion", "local_guide", "study_guide"}


class SimpleConversationRuntime(ConversationRuntime):
    runtime_name = "simple"

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
        return provider.generate_reply(message, runtime_context)
