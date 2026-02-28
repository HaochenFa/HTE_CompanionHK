from fastapi.testclient import TestClient

from app.api.routes import voice as voice_route
from app.main import app
from app.schemas.voice import VoiceSTTResponse, VoiceTTSResponse

client = TestClient(app)


def test_voice_tts_endpoint_returns_response(monkeypatch) -> None:
    def fake_synthesize(_payload):
        return VoiceTTSResponse(
            request_id="voice-req-1",
            provider="elevenlabs",
            audio_base64="YXVkaW8=",
            mime_type="audio/mpeg",
            degraded=False,
            fallback_reason=None,
        )

    monkeypatch.setattr(voice_route.voice_service, "synthesize", fake_synthesize)

    response = client.post(
        "/voice/tts",
        json={
            "text": "hello",
            "language": "en",
            "preferred_provider": "auto",
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "elevenlabs"


def test_voice_stt_endpoint_accepts_multipart(monkeypatch) -> None:
    def fake_transcribe(*, audio_bytes: bytes, language: str, preferred_provider: str):
        assert audio_bytes == b"audio-bytes"
        assert language == "en"
        assert preferred_provider == "auto"
        return VoiceSTTResponse(
            request_id="voice-req-2",
            provider="elevenlabs",
            text="transcribed",
            degraded=False,
            fallback_reason=None,
        )

    monkeypatch.setattr(voice_route.voice_service, "transcribe", fake_transcribe)

    response = client.post(
        "/voice/stt",
        data={"language": "en", "preferred_provider": "auto"},
        files={"file": ("sample.wav", b"audio-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "transcribed"
