import re

from app.models.security import Finding, Severity

PATTERNS = [
    (
        Severity.CRITICAL,
        "Secretos",
        "Posible clave de acceso AWS expuesta",
        r"AKIA[0-9A-Z]{16}",
        "Se detectó un patrón compatible con un AWS Access Key ID.",
        "Revocar la credencial en IAM, eliminarla del código y del historial de Git, y usar un rol con permisos mínimos o un secret manager.",
    ),
    (
        Severity.CRITICAL,
        "Secretos",
        "Posible clave API de Google expuesta",
        r"AIza[0-9A-Za-z_-]{35}",
        "Se detectó un patrón compatible con una clave API de Google.",
        "Restringir la clave por dominio/IP, regenerarla y almacenarla en un secret manager.",
    ),
    (
        Severity.CRITICAL,
        "Secretos",
        "Clave privada incrustada en contenido",
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "Se encontró un bloque de clave privada en texto plano.",
        "Eliminar la clave, rotarla de inmediato y revisar los permisos de los sistemas que la utilizaban.",
    ),
    (
        Severity.HIGH,
        "Secretos",
        "Token o secreto en configuración",
        r"(?i)(api[_-]?key|apikey|client[_-]?secret|access[_-]?token|secret)\s*[:=]\s*['\"]([A-Za-z0-9_.-]{16,})['\"]",
        "Una variable con nombre sensible contiene un valor de longitud elevada.",
        "Mover el secreto a variables de entorno o a un secret manager y aplicar rotación periódica.",
    ),
    (
        Severity.HIGH,
        "Secretos",
        "JWT expuesto en contenido",
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        "Se detectó un token JWT incrustado en el contenido analizado.",
        "No exponer tokens en HTML/JS, reducir su vigencia y verificar el almacenamiento seguro en el cliente.",
    ),
    (
        Severity.MEDIUM,
        "Rutas internas",
        "Ruta administrativa o interna referenciada",
        r"(?i)(/api/internal|/internal/|/admin(?:istrator)?/|/private/|/debug/|/actuator/|/swagger(?:-ui)?/|/graphql)",
        "El contenido hace referencia a rutas que podrían no estar destinadas a usuarios públicos.",
        "Confirmar que estas rutas exigen autenticación y autorización, y evitar enumerarlas en contenido público.",
    ),
    (
        Severity.LOW,
        "Información expuesta",
        "Correo electrónico expuesto",
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "Se encontró una dirección de correo en HTML o JavaScript.",
        "Validar si la exposición es intencional; en caso contrario, sustituirla por un formulario de contacto.",
    ),
]


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def scan_text(
    text: str, source: str, target: str, media: str, limit: int = 5
) -> list[Finding]:
    findings: list[Finding] = []

    for severity, category, title, pattern, description, remediation in PATTERNS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))[:limit]
        for match in matches:
            raw = match.group(match.lastindex or 0)
            findings.append(
                Finding(
                    id=f"secret-{severity.value}-{abs(hash((title, raw, source))) % 10**10}",
                    severity=severity,
                    category=category,
                    title=f"{title} ({media})",
                    description=description,
                    evidence=mask(raw)[:160],
                    remediation=remediation,
                    target=target,
                    source=source,
                )
            )

    return findings
