import base64
import logging
from uuid import uuid4

from app.core.database import SessionLocal
from app.core.settings import settings
from app.models.enums import ProviderEventScope, ProviderEventStatus
from app.providers.cantoneseai import CantoneseAIVoiceProvider
from app.providers.elevenlabs import ElevenLabsVoiceProvider
from app.repositories.audit_repository import AuditRepository
from app.schemas.voice import VoiceSTTResponse, VoiceTTSRequest, VoiceTTSResponse

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self):
        self._settings = settings

    def synthesize(self, request: VoiceTTSRequest) -> VoiceTTSResponse:
        request_id = str(uuid4())
        if not self._settings.feature_voice_api_enabled:
            return VoiceTTSResponse(
                request_id=request_id,
                provider="elevenlabs",
                audio_base64="",
                mime_type="audio/mpeg",
                degraded=True,
                fallback_reason="voice_api_disabled",
            )

        fallback_reasons: list[str] = []
        for provider_name in self._ordered_provider_names(request.preferred_provider):
            try:
                if provider_name == "elevenlabs":
                    if not self._settings.feature_elevenlabs_enabled:
                        fallback_reasons.append("elevenlabs_disabled")
                        continue
                    provider = ElevenLabsVoiceProvider()
                    audio = provider.synthesize(
                        request.text,
                        language=request.language,
                        voice_id=request.voice_id,
                    )
                    if audio:
                        self._log_voice_provider_event(
                            request_id=request_id,
                            provider_name=provider_name,
                            status=ProviderEventStatus.success,
                            fallback_reason=None,
                            metadata={"operation": "tts"},
                        )
                        return VoiceTTSResponse(
                            request_id=request_id,
                            provider="elevenlabs",
                            audio_base64=base64.b64encode(audio).decode("utf-8"),
                            mime_type="audio/mpeg",
                            degraded=bool(fallback_reasons),
                            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else None,
                        )
                    fallback_reasons.append("elevenlabs_no_audio")
                elif provider_name == "cantoneseai":
                    if not self._settings.feature_cantoneseai_enabled:
                        fallback_reasons.append("cantoneseai_disabled")
                        continue
                    provider = CantoneseAIVoiceProvider()
                    audio = provider.synthesize(
                        request.text,
                        voice=request.voice_id,
                        output_format="wav",
                    )
                    if audio:
                        self._log_voice_provider_event(
                            request_id=request_id,
                            provider_name=provider_name,
                            status=ProviderEventStatus.success,
                            fallback_reason=None,
                            metadata={"operation": "tts"},
                        )
                        return VoiceTTSResponse(
                            request_id=request_id,
                            provider="cantoneseai",
                            audio_base64=base64.b64encode(audio).decode("utf-8"),
                            mime_type="audio/wav",
                            degraded=bool(fallback_reasons),
                            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else None,
                        )
                    fallback_reasons.append("cantoneseai_no_audio")
            except Exception:
                logger.exception("voice_tts_provider_failed provider=%s", provider_name)
                fallback_reasons.append(f"{provider_name}_error")
                self._log_voice_provider_event(
                    request_id=request_id,
                    provider_name=provider_name,
                    status=ProviderEventStatus.fallback,
                    fallback_reason=f"{provider_name}_error",
                    metadata={"operation": "tts"},
                )

        self._log_voice_provider_event(
            request_id=request_id,
            provider_name="voice-unavailable",
            status=ProviderEventStatus.failed,
            fallback_reason="all_voice_tts_providers_failed",
            metadata={"operation": "tts"},
        )
        return VoiceTTSResponse(
            request_id=request_id,
            provider="elevenlabs",
            audio_base64="",
            mime_type="audio/mpeg",
            degraded=True,
            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else "all_voice_tts_providers_failed",
        )

    def transcribe(
        self,
        *,
        audio_bytes: bytes,
        language: str,
        preferred_provider: str,
    ) -> VoiceSTTResponse:
        request_id = str(uuid4())
        if not self._settings.feature_voice_api_enabled:
            return VoiceSTTResponse(
                request_id=request_id,
                provider="elevenlabs",
                text="",
                degraded=True,
                fallback_reason="voice_api_disabled",
            )

        fallback_reasons: list[str] = []
        for provider_name in self._ordered_provider_names(preferred_provider):
            try:
                if provider_name == "elevenlabs":
                    if not self._settings.feature_elevenlabs_enabled:
                        fallback_reasons.append("elevenlabs_disabled")
                        continue
                    provider = ElevenLabsVoiceProvider()
                    text = provider.transcribe(audio_bytes, language=language)
                    if text:
                        self._log_voice_provider_event(
                            request_id=request_id,
                            provider_name=provider_name,
                            status=ProviderEventStatus.success,
                            fallback_reason=None,
                            metadata={"operation": "stt"},
                        )
                        return VoiceSTTResponse(
                            request_id=request_id,
                            provider="elevenlabs",
                            text=text,
                            degraded=bool(fallback_reasons),
                            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else None,
                        )
                    fallback_reasons.append("elevenlabs_empty_text")
                elif provider_name == "cantoneseai":
                    if not self._settings.feature_cantoneseai_enabled:
                        fallback_reasons.append("cantoneseai_disabled")
                        continue
                    provider = CantoneseAIVoiceProvider()
                    result = provider.transcribe(audio_bytes, language=language)
                    text = str((result or {}).get("text", "")) if isinstance(result, dict) else ""
                    if text:
                        self._log_voice_provider_event(
                            request_id=request_id,
                            provider_name=provider_name,
                            status=ProviderEventStatus.success,
                            fallback_reason=None,
                            metadata={"operation": "stt"},
                        )
                        return VoiceSTTResponse(
                            request_id=request_id,
                            provider="cantoneseai",
                            text=text,
                            degraded=bool(fallback_reasons),
                            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else None,
                        )
                    fallback_reasons.append("cantoneseai_empty_text")
            except Exception:
                logger.exception("voice_stt_provider_failed provider=%s", provider_name)
                fallback_reasons.append(f"{provider_name}_error")
                self._log_voice_provider_event(
                    request_id=request_id,
                    provider_name=provider_name,
                    status=ProviderEventStatus.fallback,
                    fallback_reason=f"{provider_name}_error",
                    metadata={"operation": "stt"},
                )

        self._log_voice_provider_event(
            request_id=request_id,
            provider_name="voice-unavailable",
            status=ProviderEventStatus.failed,
            fallback_reason="all_voice_stt_providers_failed",
            metadata={"operation": "stt"},
        )
        return VoiceSTTResponse(
            request_id=request_id,
            provider="elevenlabs",
            text="",
            degraded=True,
            fallback_reason="; ".join(fallback_reasons) if fallback_reasons else "all_voice_stt_providers_failed",
        )

    @staticmethod
    def _ordered_provider_names(preferred_provider: str) -> list[str]:
        if preferred_provider == "elevenlabs":
            return ["elevenlabs", "cantoneseai"]
        if preferred_provider == "cantoneseai":
            return ["cantoneseai", "elevenlabs"]
        return ["elevenlabs", "cantoneseai"]

    def _log_voice_provider_event(
        self,
        *,
        request_id: str,
        provider_name: str,
        status: ProviderEventStatus,
        fallback_reason: str | None,
        metadata: dict[str, object],
    ) -> None:
        try:
            with SessionLocal() as session:
                audit_repository = AuditRepository(session)
                audit_repository.create_provider_event(
                    user_id=None,
                    request_id=request_id,
                    role=None,
                    scope=ProviderEventScope.voice,
                    provider_name=provider_name,
                    runtime=None,
                    status=status,
                    fallback_reason=fallback_reason,
                    metadata_json=metadata,
                )
                session.commit()
        except Exception:
            logger.exception(
                "voice_provider_event_log_failed request_id=%s provider=%s",
                request_id,
                provider_name,
            )
