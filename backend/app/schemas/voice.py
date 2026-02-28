from typing import Literal

from pydantic import BaseModel, Field

VoiceProviderName = Literal["elevenlabs", "cantoneseai"]


class VoiceTTSRequest(BaseModel):
    text: str = Field(min_length=1)
    language: str = "en"
    preferred_provider: Literal["auto", "elevenlabs", "cantoneseai"] = "auto"
    voice_id: str | None = None


class VoiceTTSResponse(BaseModel):
    request_id: str
    provider: VoiceProviderName
    audio_base64: str
    mime_type: str
    degraded: bool = False
    fallback_reason: str | None = None


class VoiceSTTResponse(BaseModel):
    request_id: str
    provider: VoiceProviderName
    text: str
    degraded: bool = False
    fallback_reason: str | None = None
