from dataclasses import dataclass

CHROME_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class CrawlPolicy:
    max_depth: int = 2
    max_pages: int = 30
    respect_robots: bool = False
    delay_ms: int = 500
    timeout_ms: int = 15000
    user_agent: str = CHROME_USER_AGENT
