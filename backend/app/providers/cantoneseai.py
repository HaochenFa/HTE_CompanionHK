from app.providers.base import VoiceProvider


class CantoneseAIVoiceProvider(VoiceProvider):
    provider_name = "cantoneseai"

    def synthesize(self, text: str) -> bytes:
        _ = text
        return b""
