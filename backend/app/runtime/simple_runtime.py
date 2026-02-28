from typing import Any

from app.providers.base import ChatProvider
from app.runtime.base import ConversationRuntime


class SimpleConversationRuntime(ConversationRuntime):
    runtime_name = "simple"

    def generate_reply(
        self,
        *,
        message: str,
        provider: ChatProvider,
        context: dict[str, Any]
    ) -> str:
        return provider.generate_reply(message, context)
