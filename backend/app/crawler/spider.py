import asyncio
from collections import deque
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import cast
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page
from pydantic import HttpUrl

from app.crawler.extractors import extract_page_data
from app.crawler.policy import CrawlPolicy
from app.models.security import PageAsset


@dataclass
class PageExtract:
    page: PageAsset
    data: dict[str, object]
    headers: dict[str, str]
    cookies: list[dict[str, object]]


@dataclass
class PageError:
    url: str
    code: str
    message: str


def normalize_url(base: str, href: str) -> str:
    absolute = urljoin(base, href)
    parsed = urlparse(absolute)

    if parsed.scheme not in ("http", "https"):
        return ""

    return absolute.split("#", 1)[0]


class Spider:
    def __init__(self, policy: CrawlPolicy, page: Page) -> None:
        self.policy = policy
        self.page = page
        self.visited: set[str] = set()

    @staticmethod
    def _error_code(exc: Exception) -> str:
        message = str(exc).lower()
        if "timeout" in message:
            return "NAVIGATION_TIMEOUT"
        if "certificate" in message or "ssl" in message or "tls" in message:
            return "TLS_ERROR"
        if "err_connection_refused" in message:
            return "CONNECTION_REFUSED"
        if "err_name_not_resolved" in message:
            return "DNS_ERROR"
        if "err_aborted" in message:
            return "NAVIGATION_ABORTED"
        return "NAVIGATION_ERROR"

    async def crawl(self, start_url: str) -> AsyncIterator[PageExtract | PageError]:
        queue: deque[tuple[str, int]] = deque([(start_url, 0)])
        start_host = urlparse(start_url).netloc
        pages = 0

        while queue and pages < self.policy.max_pages:
            url, depth = queue.popleft()

            if url in self.visited or depth > self.policy.max_depth:
                continue

            self.visited.add(url)

            try:
                response = await self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.policy.timeout_ms,
                )
                data = await extract_page_data(self.page)
                cookies = await self.page.context.cookies()
            except Exception as exc:
                yield PageError(url, self._error_code(exc), str(exc)[:300])
                continue

            status = response.status if response else 0
            if status in (401, 403):
                yield PageError(
                    url,
                    f"HTTP_{status}",
                    f"Acceso no autorizado ({status}) al abrir {url}. Se continúa con el resto del alcance.",
                )
                continue
            if status == 429:
                yield PageError(
                    url,
                    "HTTP_429",
                    f"Límite de peticiones alcanzado ({status}) en {url}. Se continúa con el resto del alcance.",
                )
                continue
            if status >= 500:
                yield PageError(
                    url,
                    f"HTTP_{status}",
                    f"Error del servidor ({status}) en {url}. Se continúa con el resto del alcance.",
                )
                continue

            links = [
                str(link)
                for link in cast(list[object], data.get("links") or [])
            ]
            scripts = [
                str(script)
                for script in cast(list[object], data.get("scripts") or [])
            ]
            forms = cast(list[object], data.get("forms") or [])

            page_asset = PageAsset(
                id=f"n{pages + 1}",
                url=HttpUrl(url),
                title=str(data.get("title") or url),
                depth=depth,
                links=len(links),
                forms=len(forms),
                scripts=len(scripts),
                word_count=int(str(data.get("word_count") or 0)),
            )

            headers = {
                str(key).lower(): str(value)
                for key, value in (response.headers if response else {}).items()
            }

            yield PageExtract(
                page=page_asset,
                data=data,
                headers=headers,
                cookies=[dict(cookie) for cookie in cookies],
            )
            pages += 1

            if depth < self.policy.max_depth:
                for href in links:
                    normalized = normalize_url(url, href)
                    if (
                        normalized
                        and urlparse(normalized).netloc == start_host
                        and normalized not in self.visited
                    ):
                        queue.append((normalized, depth + 1))

            await asyncio.sleep(self.policy.delay_ms / 1000)
