from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.google_auth import is_configured


def test_register_login_and_me(client: TestClient) -> None:
    email = f"user-{uuid4().hex[:8]}@neurospider.local"
    payload = {
        "full_name": "Operador de prueba",
        "email": email,
        "password": "password123",
    }

    registered = client.post("/auth/register", json=payload)
    token = registered.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    logged_in = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )

    assert registered.status_code == 200
    assert registered.json()["expires_in"] == get_settings().access_token_expire_minutes * 60
    assert me.status_code == 200
    assert me.json()["email"] == email
    assert me.json()["role"] == "user"
    assert logged_in.status_code == 200


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    email = f"duplicate-{uuid4().hex[:8]}@neurospider.local"
    payload = {"full_name": "Primero", "email": email, "password": "password123"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    email = f"invalid-{uuid4().hex[:8]}@neurospider.local"
    client.post(
        "/auth/register",
        json={"full_name": "Operador", "email": email, "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "incorrecta"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_google_login_has_informative_fallback(client: TestClient) -> None:
    if is_configured(get_settings()):
        pytest.skip("Google OAuth2 está configurado en el entorno de pruebas")

    response = client.get("/auth/google/login", follow_redirects=False)

    assert response.status_code == 503
    assert "GOOGLE_CLIENT_ID" in response.json()["detail"]
