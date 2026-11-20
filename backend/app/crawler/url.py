from ipaddress import ip_address
from urllib.parse import urlparse, urlunparse

import httpx


def normalize_target_input(value: str) -> str:
    candidate = value.strip().strip("'\"")
    if "://" not in candidate:
        scheme = "https"
        host = urlparse(f"//{candidate}").hostname or ""
        if host == "localhost" or host == "::1":
            scheme = "http"
        else:
            try:
                ip_address(host)
                scheme = "http"
            except ValueError:
                pass
        candidate = f"{scheme}://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("La URL debe incluir un dominio http(s) válido")

    return candidate.split("#", 1)[0].rstrip()


def upgrade_to_https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "http":
        return url

    netloc = parsed.netloc.removesuffix(":80")

    return urlunparse(parsed._replace(scheme="https", netloc=netloc))


async def resolve_target_url(url: str, timeout_ms: int, user_agent: str) -> str:
    target = normalize_target_input(url)

    async with httpx.AsyncClient(
        timeout=timeout_ms / 1000,
        follow_redirects=True,
        verify=False,
        headers={"User-Agent": user_agent},
    ) as client:
        try:
            response = await client.get(target)
        except httpx.HTTPError:
            return target

        final_url = str(response.url).split("#", 1)[0]
        if urlparse(final_url).scheme == "https":
            return final_url

        https_candidate = upgrade_to_https(final_url)
        try:
            https_response = await client.get(https_candidate)
        except httpx.HTTPError:
            return final_url

        final_https = str(https_response.url).split("#", 1)[0]
        if urlparse(final_https).scheme == "https":
            return final_https

        return final_url
