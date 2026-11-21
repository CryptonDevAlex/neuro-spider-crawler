import asyncio
import logging
from datetime import UTC
from typing import Any

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import Settings
from app.db.database import SessionLocal
from app.db.repository import (
    due_monitored_targets,
    latest_scan_for_domain,
    mark_monitored_run,
)
from app.models.security import ScanRequest, ScanStatus
from app.services.crawler_service import ScanService

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scheduler = BackgroundScheduler(timezone=UTC)

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.scheduler.add_job(
            self.run_due_targets,
            trigger="interval",
            minutes=5,
            id="neurospider-monitoring",
            replace_existing=True,
        )
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def run_due_targets(self) -> None:
        with SessionLocal() as session:
            targets = due_monitored_targets(session)

        for target in targets:
            if target.user_id is None:
                continue
            try:
                asyncio.run(
                    self._run_target(
                        domain=target.domain,
                        user_id=target.user_id,
                        webhook_url=target.webhook_url or self.settings.monitoring_webhook_url,
                    )
                )
            except Exception as exc:
                logger.warning("Monitoreo de %s falló: %s", target.domain, exc)
            finally:
                with SessionLocal() as session:
                    refreshed = session.merge(target)
                    mark_monitored_run(session, refreshed)

    async def _run_target(self, domain: str, user_id: int, webhook_url: str) -> None:
        with SessionLocal() as session:
            previous = latest_scan_for_domain(session, domain, user_id)
            previous_ids = self._critical_ids(previous.findings) if previous else set()

        service = ScanService(self.settings)
        payload = ScanRequest(
            url=f"https://{domain}",
            max_depth=min(self.settings.max_depth, 2),
            max_pages=min(self.settings.max_pages, 10),
            audit_mode=True,
        )
        scan_id, _ = await service.start(payload, user_id)

        result = None
        for _ in range(240):
            await asyncio.sleep(1)
            result = await service.get(scan_id, user_id)
            if result is not None and result.status in (
                ScanStatus.COMPLETED,
                ScanStatus.FAILED,
            ):
                break

        if result is None or result.status != ScanStatus.COMPLETED:
            return

        current = [
            finding
            for finding in result.findings
            if finding.severity.value in ("CRITICO", "ALTO")
            and finding.id not in previous_ids
        ]
        if current and webhook_url:
            await self._send_webhook(domain, scan_id, current, webhook_url)

    @staticmethod
    def _critical_ids(findings: list[dict[str, Any]]) -> set[str]:
        return {
            str(item.get("id") or "")
            for item in findings
            if isinstance(item, dict)
            and str(item.get("severity") or "") in ("CRITICO", "ALTO")
        }

    @staticmethod
    async def _send_webhook(
        domain: str,
        scan_id: Any,
        findings: list[Any],
        webhook_url: str,
    ) -> None:
        summary = "\n".join(
            f"- {item.severity.value}: {item.title}" for item in findings[:10]
        )
        message = (
            f"NeuroSpider detectó {len(findings)} hallazgos nuevos ALTO/CRÍTICO en {domain}.\n"
            f"Escaneo: {scan_id}\n{summary}"
        )
        payload = {
            "text": message,
            "content": message,
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": message}}],
            "alerts": [
                {
                    "id": item.id,
                    "severity": item.severity.value,
                    "title": item.title,
                    "target": item.target,
                }
                for item in findings[:10]
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("No se pudo enviar webhook de monitoreo: %s", exc)
