import httpx

from app.core.domain import normalize_domain


async def discover_subdomains(
    target: str,
    user_agent: str,
    timeout: float = 8.0,
    limit: int = 200,
) -> list[str]:
    domain = normalize_domain(target)
    if "." not in domain:
        return []

    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": user_agent},
    ) as client:
        try:
            response = await client.get(url)
        except httpx.HTTPError:
            return []

    if response.status_code != 200:
        return []

    try:
        payload = response.json()
    except ValueError:
        return []

    discovered: set[str] = set()
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        for name in str(item.get("name_value") or "").splitlines():
            cleaned = name.strip().lower().lstrip("*.")
            if cleaned.endswith(domain) and cleaned != domain and "." in cleaned:
                discovered.add(cleaned)

    return sorted(discovered)[:limit]
