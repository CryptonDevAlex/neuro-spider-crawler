import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import (
    AUTH_COOKIE,
    AuthenticatedUser,
    get_app_settings,
    get_current_user,
)
from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_session
from app.db.repository import (
    create_user,
    get_user_by_email,
    get_user_by_google_id,
    get_user_by_identity,
    link_google_id,
)
from app.models.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.google_auth import (
    GoogleAuthError,
    authorization_url,
    exchange_code,
    fetch_userinfo,
    is_configured,
)

router = APIRouter(prefix="/auth", tags=["auth"])
GOOGLE_STATE_COOKIE = "neurospider_google_state"


def _set_auth_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=AUTH_COOKIE,
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.environment == "production",
    )


def _token_response(user_id: int, email: str, settings: Settings) -> TokenResponse:
    token = create_access_token(user_id, settings, email)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: RegisterRequest,
    response: Response,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    if get_user_by_email(session, payload.email) is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    user = create_user(
        session,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    result = _token_response(int(user.id), user.email, settings)
    _set_auth_cookie(response, result.access_token, settings)
    return result


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    user = get_user_by_identity(session, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    result = _token_response(int(user.id), user.email, settings)
    _set_auth_cookie(response, result.access_token, settings)
    return result


@router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(key=AUTH_COOKIE, path="/")
    response.delete_cookie(key=GOOGLE_STATE_COOKIE, path="/")
    return {"logged_out": True}


@router.get("/me", response_model=UserResponse)
async def current_user(user: AuthenticatedUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.get("/google/login")
async def google_login(
    settings: Settings = Depends(get_app_settings),
) -> RedirectResponse:
    if not is_configured(settings):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Google OAuth2 no está configurado. Define GOOGLE_CLIENT_ID y "
                "GOOGLE_CLIENT_SECRET en backend/.env."
            ),
        )

    state = secrets.token_urlsafe(32)
    response = RedirectResponse(authorization_url(settings, state), status_code=302)
    response.set_cookie(
        key=GOOGLE_STATE_COOKIE,
        value=state,
        max_age=600,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.environment == "production",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_app_settings),
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> RedirectResponse:
    if not is_configured(settings):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth2 no está configurado en este servidor.",
        )
    if error:
        raise HTTPException(status_code=400, detail=f"Google rechazó el acceso: {error}")

    expected_state = request.cookies.get(GOOGLE_STATE_COOKIE)
    if not state or not expected_state or not secrets.compare_digest(state, expected_state):
        raise HTTPException(status_code=400, detail="Estado OAuth2 inválido")
    if not code:
        raise HTTPException(status_code=400, detail="Código OAuth2 no recibido")

    try:
        access_token = await exchange_code(code, settings)
        profile = await fetch_userinfo(access_token)
    except GoogleAuthError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    google_id = str(profile.get("sub") or "")
    email = str(profile.get("email") or "").strip().lower()
    full_name = str(profile.get("name") or email.split("@")[0])
    if not google_id or not email or profile.get("email_verified") is False:
        raise HTTPException(
            status_code=400,
            detail="El perfil de Google no incluye un correo verificado.",
        )

    user = get_user_by_google_id(session, google_id)
    if user is None:
        user = get_user_by_email(session, email)
    if user is None:
        user = create_user(session, email, None, full_name, google_id)
    elif not user.google_id:
        user = link_google_id(session, user, google_id)

    token = create_access_token(int(user.id), settings, user.email)
    response = RedirectResponse(settings.frontend_url, status_code=302)
    _set_auth_cookie(response, token, settings)
    response.delete_cookie(key=GOOGLE_STATE_COOKIE, path="/")
    return response
