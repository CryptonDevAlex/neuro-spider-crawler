from app.ai.schemas import ExecutiveSummary


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def summarize(self, pages: list[dict[str, object]]) -> ExecutiveSummary:
        raise NotImplementedError
