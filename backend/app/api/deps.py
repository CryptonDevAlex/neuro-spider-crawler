from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.database import get_session
from app.db.models import User
from app.db.repository import get_user
from app.services.crawler_service import ScanService

AUTH_COOKIE = "neurospider_token"
_bearer = HTTPBearer(auto_error=False)

_app_settings = get_settings()
_scan_service = ScanService(settings=_app_settings)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    email: str
    full_name: str
    role: str


def get_app_settings() -> Settings:
    return _app_settings


def get_scan_service() -> ScanService:
    return _scan_service


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_app_settings),
    session: Session = Depends(get_session),
) -> AuthenticatedUser:
    token = (
        credentials.credentials
        if credentials is not None and credentials.scheme.lower() == "bearer"
        else request.cookies.get(AUTH_COOKIE)
    )
    if not token:
        raise _unauthorized("Token de acceso requerido")

    subject = decode_access_token(token, settings)
    if subject is None:
        raise _unauthorized("Token de acceso inválido o expirado")
    try:
        user_id = int(subject)
    except ValueError:
        raise _unauthorized("Token de acceso inválido o expirado") from None

    user: User | None = get_user(session, user_id)
    if user is None:
        raise _unauthorized("Cuenta no encontrada o sesión revocada")

    role = (
        "admin"
        if user.email.lower() == settings.admin_email.lower()
        or user.full_name == settings.admin_user
        else "user"
    )
    return AuthenticatedUser(
        id=int(user.id),
        email=user.email,
        full_name=user.full_name,
        role=role,
    )
