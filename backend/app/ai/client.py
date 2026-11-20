import httpx

from app.ai.local_summary import local_summary
from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.ai.schemas import ExecutiveSummary


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def summarize(self, pages: list[dict[str, object]]) -> ExecutiveSummary:
        if not self.api_key:
            return local_summary(pages)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {
                                "role": "user",
                                "content": USER_PROMPT_TEMPLATE.format(
                                    pages=self._format_pages(pages)
                                ),
                            },
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return ExecutiveSummary.model_validate_json(content)
        except Exception:
            return local_summary(pages)

    @staticmethod
    def _format_pages(pages: list[dict[str, object]]) -> str:
        blocks = [
            f"URL: {page.get('url')}\nTÍTULO: {page.get('title')}\nTEXTO: {str(page.get('text') or '')[:4000]}"
            for page in pages
        ]
        return "\n\n".join(blocks)[:28000]
