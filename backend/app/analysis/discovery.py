import re
from urllib.parse import urlparse

import httpx


def origin_of(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


async def discover_recon_paths(url: str) -> tuple[list[str], list[str]]:
    origin = origin_of(url)
    robots_paths: list[str] = []
    sitemap_paths: list[str] = []

    async with httpx.AsyncClient(
        timeout=8.0, follow_redirects=True, headers={"User-Agent": "NeuroSpider/0.2"}
    ) as client:
        try:
            robots = await client.get(f"{origin}/robots.txt")
        except httpx.HTTPError:
            robots = None

        if robots is not None and robots.status_code == 200:
            for line in robots.text.splitlines():
                match = re.match(r"\s*(?:Allow|Disallow)\s*:\s*(.+)", line, re.IGNORECASE)
                if not match:
                    continue
                path = match.group(1).strip()
                if path and path != "/":
                    robots_paths.append(path)

        try:
            sitemap = await client.get(f"{origin}/sitemap.xml")
        except httpx.HTTPError:
            sitemap = None

        if sitemap is not None and sitemap.status_code == 200:
            for location in re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap.text, re.IGNORECASE):
                if location:
                    sitemap_paths.append(location)

    return list(dict.fromkeys(robots_paths)), list(dict.fromkeys(sitemap_paths))
