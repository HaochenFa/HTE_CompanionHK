from typing import Any

from app.providers.base import ChatProvider


class MiniMaxChatProvider(ChatProvider):
    provider_name = "minimax"

    def generate_reply(self, message: str, context: dict[str, Any] | None = None) -> str:
        _ = (message, context)
        return (
            "MiniMax adapter stub is active. I hear what you are going through, and I am here to"
            " support you."
        )
