import base64

import pytest

from app.providers.cantoneseai import CantoneseAIVoiceProvider


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        json_data: dict | None = None,
        content: bytes = b"",
        text: str = ""
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self._json_data = json_data
        self.content = content
        self.text = text

    def json(self) -> dict:
        if self._json_data is None:
            raise ValueError("No JSON payload")
        return self._json_data


def test_synthesize_uses_voice_key_in_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANTONESEAI_API_KEY", "test-key")
    provider = CantoneseAIVoiceProvider()
    captured_payload: dict = {}

    def fake_post(url: str, json: dict, timeout: int) -> FakeResponse:
        _ = (url, timeout)
        captured_payload.update(json)
        return FakeResponse(
            status_code=200,
            headers={"content-type": "audio/wav"},
            content=b"audio"
        )

    provider.session.post = fake_post  # type: ignore[assignment]
    audio = provider.synthesize("你好", voice="female")

    assert audio == b"audio"
    assert captured_payload["voice_key"] == "female"


def test_synthesize_returns_bytes_when_timestamp_requested(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CANTONESEAI_API_KEY", "test-key")
    provider = CantoneseAIVoiceProvider()
    encoded_audio = base64.b64encode(b"audio-bytes").decode("utf-8")

    def fake_post(url: str, json: dict, timeout: int) -> FakeResponse:
        _ = (url, json, timeout)
        return FakeResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            json_data={"file": encoded_audio, "request_id": "req-1"}
        )

    provider.session.post = fake_post  # type: ignore[assignment]
    audio = provider.synthesize("你今日點呀？", should_return_timestamp=True)

    assert audio == b"audio-bytes"


def test_synthesize_with_metadata_returns_expected_fields(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CANTONESEAI_API_KEY", "test-key")
    provider = CantoneseAIVoiceProvider()
    encoded_audio = base64.b64encode(b"voice").decode("utf-8")

    def fake_post(url: str, json: dict, timeout: int) -> FakeResponse:
        _ = (url, json, timeout)
        return FakeResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            json_data={
                "file": encoded_audio,
                "request_id": "req-2",
                "timestamps": [{"start": 0, "end": 1, "text": "你好"}],
                "srt_timestamp": "1\n00:00:00,000 --> 00:00:01,000\n你好\n"
            }
        )

    provider.session.post = fake_post  # type: ignore[assignment]
    result = provider.synthesize_with_metadata("你好", return_srt=True)

    assert result["audio_raw"] == b"voice"
    assert result["request_id"] == "req-2"
    assert result["timestamps"][0]["text"] == "你好"
    assert result["srt_timestamp"] is not None
