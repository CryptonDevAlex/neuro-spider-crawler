import hashlib
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import Settings


def _signing_key(settings: Settings) -> bytes:
    return hashlib.sha256(settings.jwt_secret_key.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def create_access_token(
    subject: int | str,
    settings: Settings,
    email: str | None = None,
) -> str:
    issued_at = datetime.now(UTC)
    payload: dict[str, object] = {
        "sub": str(subject),
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.access_token_expire_minutes),
    }
    if email:
        payload["email"] = email
    return jwt.encode(payload, _signing_key(settings), algorithm="HS256")


def decode_access_token(token: str, settings: Settings) -> str | None:
    try:
        payload = jwt.decode(token, _signing_key(settings), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

    subject = payload.get("sub")
    return str(subject) if subject is not None else None
