from urllib.parse import urlparse


def normalize_domain(value: str) -> str:
    candidate = value.strip()
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    hostname = (urlparse(candidate).hostname or candidate).lower().rstrip(".")
    return hostname.removeprefix("www.")
