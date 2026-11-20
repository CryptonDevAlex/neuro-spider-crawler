from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
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


def init_db() -> Path:
    from app.db import models as _models

    _tables = (_models.ScanRecord, _models.MonitoredTarget)
    Base.metadata.create_all(bind=engine)
    return DATABASE_PATH


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
