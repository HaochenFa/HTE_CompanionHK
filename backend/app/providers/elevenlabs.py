from app.providers.base import VoiceProvider


class ElevenLabsVoiceProvider(VoiceProvider):
    provider_name = "elevenlabs"

    def synthesize(self, text: str) -> bytes:
        _ = text
        return b""
