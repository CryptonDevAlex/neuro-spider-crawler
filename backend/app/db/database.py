from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

from sqlalchemy import Table, create_engine, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

BACKEND_DIR = Path(__file__).resolve().parents[2]
_configured_path = Path(get_settings().database_path)
DATABASE_PATH = (
    _configured_path if _configured_path.is_absolute() else BACKEND_DIR / _configured_path
)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def _column_names(session: Session, table: str) -> set[str]:
    return {column["name"] for column in inspect(session.get_bind()).get_columns(table)}


def _ensure_admin(session: Session) -> int:
    from app.core.security import hash_password
    from app.db.models import User

    settings = get_settings()
    user = session.scalar(select(User).where(User.email == settings.admin_email))
    if user is None:
        user = User(
            email=settings.admin_email,
            full_name=settings.admin_user,
            password_hash=hash_password(settings.admin_password),
        )
        session.add(user)
    else:
        user.full_name = settings.admin_user
        user.password_hash = hash_password(settings.admin_password)
    session.commit()
    session.refresh(user)
    return int(user.id)


def _rebuild_monitored_targets(session: Session) -> None:
    global_domain_unique = any(
        index.get("unique")
        and len(index.get("column_names") or []) == 1
        and (index.get("column_names") or [None])[0] == "domain"
        for index in inspect(session.get_bind()).get_indexes("monitored_targets")
    )
    if not global_domain_unique:
        return

    session.execute(text("ALTER TABLE monitored_targets RENAME TO monitored_targets_legacy"))
    session.execute(
        text(
            """
            CREATE TABLE monitored_targets (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                domain VARCHAR(255) NOT NULL,
                frequency VARCHAR(16) NOT NULL,
                active BOOLEAN NOT NULL,
                webhook_url VARCHAR(2048),
                last_run_at DATETIME,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
    )
    session.execute(
        text(
            """
            INSERT INTO monitored_targets
                (id, user_id, domain, frequency, active, webhook_url, last_run_at, created_at)
            SELECT id, user_id, domain, frequency, active, webhook_url, last_run_at, created_at
            FROM monitored_targets_legacy
            """
        )
    )
    session.execute(text("DROP TABLE monitored_targets_legacy"))
    session.execute(
        text("CREATE INDEX ix_monitored_targets_domain ON monitored_targets (domain)")
    )
    session.execute(
        text("CREATE INDEX ix_monitored_targets_user_id ON monitored_targets (user_id)")
    )
    session.execute(
        text("CREATE INDEX ix_monitored_targets_created_at ON monitored_targets (created_at)")
    )
    session.execute(
        text(
            "CREATE UNIQUE INDEX uq_monitor_user_domain "
            "ON monitored_targets (user_id, domain)"
        )
    )
    session.commit()


def init_db() -> Path:
    from app.db import models as _models

    tables = [
        cast(Table[Any], _models.User.__table__),
        cast(Table[Any], _models.ScanRecord.__table__),
        cast(Table[Any], _models.MonitoredTarget.__table__),
    ]
    Base.metadata.create_all(bind=engine, tables=tables)
    with SessionLocal() as session:
        admin_id = _ensure_admin(session)

        if "user_id" not in _column_names(session, "scans"):
            session.execute(text("ALTER TABLE scans ADD COLUMN user_id INTEGER"))
            session.commit()
        if "user_id" not in _column_names(session, "monitored_targets"):
            session.execute(text("ALTER TABLE monitored_targets ADD COLUMN user_id INTEGER"))
            session.commit()

        session.execute(
            text("UPDATE scans SET user_id = :admin_id WHERE user_id IS NULL"),
            {"admin_id": admin_id},
        )
        session.execute(
            text(
                "UPDATE monitored_targets SET user_id = :admin_id WHERE user_id IS NULL"
            ),
            {"admin_id": admin_id},
        )
        session.commit()
        _rebuild_monitored_targets(session)

    return DATABASE_PATH


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
