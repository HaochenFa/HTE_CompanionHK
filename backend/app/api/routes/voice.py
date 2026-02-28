from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.voice import VoiceSTTResponse, VoiceTTSRequest, VoiceTTSResponse
from app.services.voice_service import VoiceService

router = APIRouter()
voice_service = VoiceService()


@router.post("/voice/tts", response_model=VoiceTTSResponse)
def voice_tts(payload: VoiceTTSRequest) -> VoiceTTSResponse:
    return voice_service.synthesize(payload)


@router.post("/voice/stt", response_model=VoiceSTTResponse)
async def voice_stt(
    file: UploadFile = File(...),
    language: str = Form("en"),
    preferred_provider: str = Form("auto"),
) -> VoiceSTTResponse:
    audio_bytes = await file.read()
    return voice_service.transcribe(
        audio_bytes=audio_bytes,
        language=language,
        preferred_provider=preferred_provider,
    )
