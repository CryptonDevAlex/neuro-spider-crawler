from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import crawl, health, history, monitoring
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import init_db
from app.services.monitoring_service import MonitoringScheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    init_db()
    scheduler = MonitoringScheduler(get_settings())
    scheduler.start()
    app.state.monitoring_scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.3.0",
        description="Suite de reconocimiento pasivo, historial y monitoreo continuo sobre alcances autorizados.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router)
    application.include_router(crawl.router)
    application.include_router(history.router)
    application.include_router(monitoring.router)
    return application


app = create_app()
