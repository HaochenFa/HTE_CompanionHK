from app.providers.base import RetrievalProvider


class ExaRetrievalProvider(RetrievalProvider):
    provider_name = "exa"

    def retrieve(self, query: str) -> list[dict[str, str]]:
        _ = query
        return []
