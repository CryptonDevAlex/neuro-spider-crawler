import re

from app.models.security import CookieInfo, Finding, Severity

SESSION_COOKIE_PATTERN = re.compile(
    r"(?:phpsessid|wordpress_logged_in|wp_logged_in|laravel_session|jsessionid|connect\.sid"
    r"|(?:^|[-_.])(?:session|sess|sid|auth|jwt|token)(?:$|[-_.]))",
    re.IGNORECASE,
)
ANALYTICS_COOKIE_PREFIXES = ("sbjs_", "_ga", "_gid", "_fbp", "_gcl", "utm_")

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


def cookie_role(name: str) -> str:
    if SESSION_COOKIE_PATTERN.search(name):
        return "session"
    if name.lower().startswith(ANALYTICS_COOKIE_PREFIXES):
        return "analytics"
    return "other"


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
        role = cookie_role(name)
        role_label = {
            "session": "sesión/autenticación",
            "analytics": "analítica/marketing",
            "other": "general",
        }[role]
        cookie_info.append(
            CookieInfo(
                name=name,
                http_only=http_only,
                secure=secure,
                same_site=str(same_site) if same_site else None,
            )
        )

        if not http_only:
            if role == "session":
                http_only_severity = Severity.HIGH
                http_only_title = f"Cookie de sesión sin HttpOnly: {name}"
                http_only_description = (
                    "La cookie de sesión o autenticación es accesible desde JavaScript, "
                    "lo que aumenta el impacto de un XSS sobre la cuenta del usuario."
                )
                http_only_remediation = (
                    "Añadir HttpOnly a esta cookie de sesión y mantener el valor fuera del DOM."
                )
            elif role == "analytics":
                http_only_severity = Severity.INFO
                http_only_title = f"Cookie de analítica sin HttpOnly: {name}"
                http_only_description = (
                    "Cookie de rastreo no crítica: las librerías de analítica suelen leerla "
                    "desde JavaScript para medir tráfico, por lo que HttpOnly no es aplicable."
                )
                http_only_remediation = (
                    "No añadir HttpOnly si la librería de analítica requiere lectura por JS; "
                    "revisar consentimiento, retención y dominio de la cookie."
                )
            else:
                http_only_severity = Severity.MEDIUM
                http_only_title = f"Cookie sin HttpOnly: {name}"
                http_only_description = (
                    "La cookie es accesible desde JavaScript, lo que aumenta el impacto de un XSS."
                )
                http_only_remediation = (
                    "Añadir el atributo HttpOnly a las cookies de sesión y de autenticación."
                )

            findings.append(
                Finding(
                    id=f"cookie-httponly-{name}",
                    severity=http_only_severity,
                    category="Cookies",
                    title=http_only_title,
                    description=http_only_description,
                    evidence=f"{name} -> HttpOnly=false ({role_label})",
                    remediation=http_only_remediation,
                    target=target,
                    source=target,
                )
            )

        if not secure:
            if role == "session":
                secure_severity = Severity.MEDIUM
                secure_title = f"Cookie de sesión sin Secure: {name}"
                secure_description = (
                    "La cookie de sesión o autenticación puede enviarse por conexiones HTTP no cifradas."
                )
                secure_remediation = (
                    "Añadir Secure a esta cookie de sesión y servir toda la aplicación sobre HTTPS."
                )
            elif role == "analytics":
                secure_severity = Severity.INFO
                secure_title = f"Cookie de analítica sin Secure: {name}"
                secure_description = (
                    "Cookie de rastreo no crítica: Secure evita envíos por HTTP, pero su impacto "
                    "es informativo si el tráfico de analítica ya viaja sobre HTTPS."
                )
                secure_remediation = (
                    "Habilitar Secure cuando el sitio sirva exclusivamente HTTPS y revisar "
                    "política de consentimiento de cookies de analítica."
                )
            else:
                secure_severity = Severity.LOW
                secure_title = f"Cookie sin Secure: {name}"
                secure_description = "La cookie puede enviarse por conexiones HTTP no cifradas."
                secure_remediation = (
                    "Añadir el atributo Secure y servir toda la aplicación sobre HTTPS."
                )

            findings.append(
                Finding(
                    id=f"cookie-secure-{name}",
                    severity=secure_severity,
                    category="Cookies",
                    title=secure_title,
                    description=secure_description,
                    evidence=f"{name} -> Secure=false ({role_label})",
                    remediation=secure_remediation,
                    target=target,
                    source=target,
                )
            )

    return cookie_info, findings


def detect_server(headers: dict[str, str]) -> str | None:
    normalized = {key.lower(): value for key, value in headers.items()}
    return normalized.get("server") or normalized.get("x-powered-by")
