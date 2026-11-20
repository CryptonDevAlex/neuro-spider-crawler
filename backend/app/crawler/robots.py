from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx


class RobotsChecker:
    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent
        self._cache: dict[str, RobotFileParser] = {}

    async def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        parser = self._cache.get(origin)

        if parser is None:
            parser = RobotFileParser()
            try:
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                    response = await client.get(
                        f"{origin}/robots.txt",
                        headers={"User-Agent": self.user_agent},
                    )
                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
            except httpx.HTTPError:
                parser.parse([])
            self._cache[origin] = parser

        return parser.can_fetch(self.user_agent, url)
