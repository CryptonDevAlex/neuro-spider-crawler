from app.core.config import Settings, get_settings
from app.services.crawler_service import ScanService

_app_settings = get_settings()
_scan_service = ScanService(settings=_app_settings)


def get_app_settings() -> Settings:
    return _app_settings


def get_scan_service() -> ScanService:
    return _scan_service
