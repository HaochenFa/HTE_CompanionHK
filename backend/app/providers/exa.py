import logging
from typing import Any

import requests

from app.providers.base import RetrievalProvider

logger = logging.getLogger(__name__)


class StubRetrievalProvider(RetrievalProvider):
    provider_name = "retrieval-stub"

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        _ = query
        return []


class ExaRetrievalProvider(RetrievalProvider):
    provider_name = "exa"

    def __init__(self, *, api_key: str, base_url: str, top_k: int, timeout_seconds: float):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._top_k = max(1, top_k)
        self._timeout_seconds = timeout_seconds

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        if not self._api_key:
            return []

        try:
            response = requests.post(
                f"{self._base_url}/search",
                headers={
                    "x-api-key": self._api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "numResults": self._top_k,
                    "useAutoprompt": True,
                },
                timeout=self._timeout_seconds,
            )
            if response.status_code != 200:
                logger.warning(
                    "exa_request_failed status=%s body=%s",
                    response.status_code,
                    response.text,
                )
                return []
            payload = response.json()
        except Exception:
            logger.exception("exa_request_error")
            return []

        raw_results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(raw_results, list):
            return []

        normalized: list[dict[str, Any]] = []
        for item in raw_results[: self._top_k]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("author") or "Untitled")
            url = item.get("url")
            summary = item.get("text") or item.get("summary") or item.get("highlights")
            normalized.append(
                {
                    "title": title,
                    "url": None if url is None else str(url),
                    "summary": None if summary is None else str(summary),
                    "source": self.provider_name,
                }
            )
        return normalized
