from urllib.parse import urlparse

import httpx

from app.models.security import Finding, Severity

TLS_ERROR_MARKERS = ("certificate", "ssl", "tls", "verify", "cert")


async def inspect_target_tls(
    url: str, timeout_ms: int, user_agent: str
) -> Finding | None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return None

    origin = f"https://{parsed.netloc}"
    headers = {"User-Agent": user_agent}
    timeout = timeout_ms / 1000

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=False,
        headers=headers,
    ) as permissive_client:
        try:
            await permissive_client.get(origin)
        except httpx.HTTPError:
            return None

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        verify=True,
        headers=headers,
    ) as strict_client:
        try:
            await strict_client.get(origin)
        except httpx.HTTPError as exc:
            reason = str(exc)
            if not any(marker in reason.lower() for marker in TLS_ERROR_MARKERS):
                return None
            return Finding(
                id=f"tls-certificate-{parsed.netloc}",
                severity=Severity.HIGH,
                category="TLS/SSL",
                title="Certificado TLS inválido detectado",
                description=(
                    "El sitio fue accesible ignorando la validación TLS, pero una verificación "
                    "estricta rechazó el certificado. Puede estar vencido, ser autofirmado o "
                    "no corresponder al dominio."
                ),
                evidence=reason[:300],
                remediation=(
                    "Renovar el certificado, instalar la cadena intermedia completa y verificar "
                    "que el nombre del certificado coincida con el dominio publicado."
                ),
                target=origin,
                source=origin,
            )

    return None
