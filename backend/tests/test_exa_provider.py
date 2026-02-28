import pytest

from app.providers.exa import ExaRetrievalProvider


class FakeResponse:
    def __init__(self, *, status_code: int, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


def test_exa_provider_normalizes_results(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = ExaRetrievalProvider(
        api_key="exa-key",
        base_url="https://api.exa.ai",
        top_k=2,
        timeout_seconds=5,
    )

    def fake_post(*_args, **_kwargs):
        return FakeResponse(
            status_code=200,
            payload={
                "results": [
                    {
                        "title": "Event 1",
                        "url": "https://example.com/1",
                        "summary": "Summary 1",
                    },
                    {
                        "title": "Event 2",
                        "url": "https://example.com/2",
                        "text": "Summary 2",
                    },
                ]
            },
        )

    monkeypatch.setattr("app.providers.exa.requests.post", fake_post)
    results = provider.retrieve("hong kong events")

    assert len(results) == 2
    assert results[0]["title"] == "Event 1"
    assert results[1]["summary"] == "Summary 2"


def test_exa_provider_returns_empty_on_non_200(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = ExaRetrievalProvider(
        api_key="exa-key",
        base_url="https://api.exa.ai",
        top_k=2,
        timeout_seconds=5,
    )

    monkeypatch.setattr(
        "app.providers.exa.requests.post",
        lambda *_args, **_kwargs: FakeResponse(status_code=500, text="error"),
    )

    assert provider.retrieve("hong kong") == []
