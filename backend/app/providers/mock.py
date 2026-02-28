from typing import Any

from app.providers.base import ChatProvider


class MockChatProvider(ChatProvider):
    provider_name = "mock"

    def generate_reply(self, message: str, context: dict[str, Any] | None = None) -> str:
        _ = message
        role = (context or {}).get("role", "companion")
        _system_prompt = (context or {}).get("system_prompt")
        _ = _system_prompt

        if role == "local_guide":
            return (
                "I can help you explore this with a local lens. Tell me your area, budget, and"
                " timing, and I will suggest practical options."
            )
        if role == "study_guide":
            return (
                "Let us build a focused study plan together. Share your topic and deadline, and I"
                " will break it into clear next steps."
            )
        return (
            "Thank you for sharing this with me. I am here with you, and we can take this one"
            " step at a time."
        )
