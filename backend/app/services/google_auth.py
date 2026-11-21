from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import Settings

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleAuthError(Exception):
    pass


def is_configured(settings: Settings) -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def authorization_url(settings: Settings, state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"


async def exchange_code(code: str, settings: Settings) -> str:
    payload = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(TOKEN_URL, data=payload)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GoogleAuthError("No se pudo intercambiar el código de Google") from exc

    access_token = data.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise GoogleAuthError("Google no devolvió un access_token")
    return access_token


async def fetch_userinfo(access_token: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GoogleAuthError("No se pudo obtener el perfil de Google") from exc

    if not isinstance(data, dict):
        raise GoogleAuthError("Respuesta de perfil de Google inválida")
    return data
