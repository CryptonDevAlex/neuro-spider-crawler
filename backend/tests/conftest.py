from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import AUTH_COOKIE
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.database import Base, get_session
from app.db.models import User
from app.db.repository import create_user
from app.main import app


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


@pytest.fixture
def user(session: Session) -> User:
    return create_user(
        session,
        email="operator@neurospider.local",
        password_hash=hash_password("password123"),
        full_name="Operador",
    )


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_for_user(session: Session) -> Iterator[Callable[[User], TestClient]]:
    def build(target: User) -> TestClient:
        app.dependency_overrides[get_session] = lambda: session
        token = create_access_token(target.id, get_settings(), target.email)
        test_client = TestClient(app)
        test_client.cookies.set(AUTH_COOKIE, token)
        return test_client

    try:
        yield build
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def authorized_client(client_for_user, user: User) -> TestClient:
    return client_for_user(user)
