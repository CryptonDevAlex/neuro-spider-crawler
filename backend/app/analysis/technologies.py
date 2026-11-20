import re

from app.models.security import CookieInfo, Finding, Severity

FRAMEWORK_SIGNATURES = [
    ("Angular", r"angular|ng-version"),
    ("React", r"react|__REACT_DEVTOOLS"),
    ("Next.js", r"/_next/|next\.js"),
    ("Vue", r"vue|__VUE"),
    ("Nuxt", r"__NUXT__|_nuxt/"),
    ("jQuery", r"jquery"),
    ("Svelte", r"svelte"),
    ("Astro", r"astro"),
]


def detect_frameworks(html: str, scripts: list[str]) -> list[str]:
    corpus = f"{html} {' '.join(scripts)}"
    found = [
        name
        for name, pattern in FRAMEWORK_SIGNATURES
        if re.search(pattern, corpus, re.IGNORECASE)
    ]
    return list(dict.fromkeys(found))


def analyze_cookies(
    cookies: list[dict[str, object]], target: str
) -> tuple[list[CookieInfo], list[Finding]]:
    cookie_info: list[CookieInfo] = []
    findings: list[Finding] = []

    for cookie in cookies:
        name = str(cookie.get("name") or "anonymous")
        http_only = bool(cookie.get("httpOnly") or cookie.get("http_only") or False)
        secure = bool(cookie.get("secure") or False)
        same_site = cookie.get("sameSite") or cookie.get("same_site")
        cookie_info.append(
            CookieInfo(
                name=name,
                http_only=http_only,
                secure=secure,
                same_site=str(same_site) if same_site else None,
            )
        )

        if not http_only:
            findings.append(
                Finding(
                    id=f"cookie-httponly-{name}",
                    severity=Severity.MEDIUM,
                    category="Cookies",
                    title=f"Cookie sin HttpOnly: {name}",
                    description="La cookie es accesible desde JavaScript, lo que aumenta el impacto de un XSS.",
                    evidence=f"{name} -> HttpOnly=false",
                    remediation="Añadir el atributo HttpOnly a las cookies de sesión y de autenticación.",
                    target=target,
                    source=target,
                )
            )

        if not secure:
            findings.append(
                Finding(
                    id=f"cookie-secure-{name}",
                    severity=Severity.LOW,
                    category="Cookies",
                    title=f"Cookie sin Secure: {name}",
                    description="La cookie puede enviarse por conexiones HTTP no cifradas.",
                    evidence=f"{name} -> Secure=false",
                    remediation="Añadir el atributo Secure y servir toda la aplicación sobre HTTPS.",
                    target=target,
                    source=target,
                )
            )

    return cookie_info, findings


def detect_server(headers: dict[str, str]) -> str | None:
    normalized = {key.lower(): value for key, value in headers.items()}
    return normalized.get("server") or normalized.get("x-powered-by")
