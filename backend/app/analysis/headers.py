from app.models.security import Finding, SecurityHeader, Severity

HEADER_CHECKS = [
    (
        "Content-Security-Policy",
        Severity.HIGH,
        "No se declaró una política de seguridad de contenido; el sitio es más vulnerable a XSS y carga de recursos no autorizados.",
        "Publicar una cabecera CSP estricta con directivas default-src, script-src y object-src 'none', usando nonces o hashes en lugar de 'unsafe-inline'.",
    ),
    (
        "Strict-Transport-Security",
        Severity.MEDIUM,
        "Falta HSTS; un atacante podría degradar conexiones HTTPS a HTTP en clientes que ya visitaron el sitio.",
        "Añadir Strict-Transport-Security: max-age=31536000; includeSubDomains; preload en todas las respuestas HTTPS.",
    ),
    (
        "X-Frame-Options",
        Severity.MEDIUM,
        "No se impide incrustar la página en iframes, lo que facilita clickjacking.",
        "Configurar X-Frame-Options: DENY o SAMEORIGIN, o usar frame-ancestors dentro de CSP.",
    ),
    (
        "X-Content-Type-Options",
        Severity.MEDIUM,
        "Falta la directiva nosniff; el navegador podría interpretar archivos con un MIME distinto al declarado.",
        "Añadir X-Content-Type-Options: nosniff y corregir los tipos MIME devueltos por el servidor.",
    ),
    (
        "Referrer-Policy",
        Severity.LOW,
        "No se controla la información de referencia enviada a destinos externos.",
        "Definir Referrer-Policy: strict-origin-when-cross-origin o no-referrer según las necesidades del sitio.",
    ),
]


def analyze_headers(
    headers: dict[str, str], target: str
) -> tuple[list[SecurityHeader], list[Finding]]:
    normalized = {key.lower(): value for key, value in headers.items()}
    security_headers: list[SecurityHeader] = []
    findings: list[Finding] = []

    for name, severity, description, remediation in HEADER_CHECKS:
        value = normalized.get(name.lower())
        present = bool(value and value.strip())
        security_headers.append(
            SecurityHeader(name=name, present=present, value=value, severity=severity)
        )
        if not present:
            findings.append(
                Finding(
                    id=f"header-{name.lower()}",
                    severity=severity,
                    category="Cabeceras HTTP",
                    title=f"Cabecera ausente: {name}",
                    description=description,
                    evidence="La cabecera no está presente en la respuesta analizada.",
                    remediation=remediation,
                    target=target,
                    source=target,
                )
            )

    return security_headers, findings
