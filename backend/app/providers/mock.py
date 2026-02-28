from typing import Any

from app.providers.base import ChatProvider


class MockChatProvider(ChatProvider):
    provider_name = "mock"

    def generate_reply(self, message: str, context: dict[str, Any] | None = None) -> str:
        _ = (message, context)
        return (
            "Thank you for sharing this with me. I am here with you, and we can take this one"
            " step at a time."
        )
