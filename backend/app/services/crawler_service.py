import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import httpx

from app.analysis.analyzer import AnalysisInput, SecurityAnalyzer
from app.analysis.discovery import discover_recon_paths, origin_of
from app.analysis.subdomains import discover_subdomains
from app.core.config import Settings
from app.core.events import ScanPhase
from app.crawler.browser import BrowserSession
from app.crawler.policy import CrawlPolicy
from app.crawler.spider import PageError, Spider
from app.crawler.tls import inspect_target_tls
from app.crawler.url import resolve_target_url
from app.db.database import SessionLocal
from app.db.repository import save_scan
from app.models.events import (
    DoneEvent,
    ErrorEvent,
    EventBase,
    FindingEvent,
    NodeEvent,
    StatusEvent,
    SummaryEvent,
)
from app.models.security import (
    FormDetail,
    FormInput,
    ScanRequest,
    ScanResult,
    ScanStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class ScanJob:
    scan_id: UUID
    result: ScanResult
    events: list[EventBase] = field(default_factory=list)
    queue: asyncio.Queue[EventBase | None] = field(default_factory=asyncio.Queue)


class ScanService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.jobs: dict[UUID, ScanJob] = {}

    def policy_for(self, payload: ScanRequest) -> CrawlPolicy:
        return CrawlPolicy(
            max_depth=payload.max_depth,
            max_pages=payload.max_pages,
            respect_robots=False,
            delay_ms=self.settings.request_delay_ms,
            timeout_ms=self.settings.navigation_timeout_ms,
        )

    async def start(self, payload: ScanRequest) -> tuple[UUID, ScanResult]:
        scan_id = uuid4()
        result = ScanResult(
            scan_id=scan_id,
            status=ScanStatus.QUEUED,
            target=str(payload.url),
            started_at=datetime.now(UTC),
        )
        job = ScanJob(scan_id=scan_id, result=result)
        self.jobs[scan_id] = job
        asyncio.create_task(self._run(job, payload))
        return scan_id, result

    async def get(self, scan_id: UUID) -> ScanResult | None:
        job = self.jobs.get(scan_id)
        return job.result if job else None

    async def stream(self, scan_id: UUID) -> AsyncIterator[EventBase]:
        job = self.jobs.get(scan_id)
        if job is None:
            return

        cursor = len(job.events)
        for event in job.events[:cursor]:
            yield event

        if job.result.status in (ScanStatus.COMPLETED, ScanStatus.FAILED):
            return

        while True:
            next_event = await job.queue.get()
            if next_event is None:
                break
            yield next_event

    @staticmethod
    def _base(scan_id: UUID) -> dict[str, Any]:
        return {"scan_id": scan_id, "timestamp": datetime.now(UTC)}

    async def _emit(self, job: ScanJob, event: EventBase) -> None:
        job.events.append(event)
        await job.queue.put(event)

    async def _status(
        self,
        job: ScanJob,
        phase: ScanPhase,
        pages_done: int,
        pages_total: int,
    ) -> None:
        await self._emit(
            job,
            StatusEvent(
                **self._base(job.scan_id),
                phase=phase.value,
                pages_done=pages_done,
                pages_total=pages_total,
            ),
        )

    @staticmethod
    def _forms(data: dict[str, object]) -> list[FormDetail]:
        forms: list[FormDetail] = []

        for raw in cast(list[object], data.get("forms") or []):
            if not isinstance(raw, dict):
                continue
            inputs = [
                FormInput(name=str(item.get("name") or ""), type=str(item.get("type") or ""))
                for item in cast(list[object], raw.get("inputs") or [])
                if isinstance(item, dict)
            ]
            forms.append(
                FormDetail(
                    action=str(raw.get("action") or ""),
                    method=str(raw.get("method") or "GET"),
                    inputs=inputs,
                )
            )

        return forms

    @staticmethod
    async def _fetch_js(urls: list[str], user_agent: str) -> list[tuple[str, str]]:
        documents: list[tuple[str, str]] = []

        async with httpx.AsyncClient(
            timeout=8.0,
            follow_redirects=True,
            verify=False,
            headers={"User-Agent": user_agent},
        ) as client:
            for url in urls[:25]:
                try:
                    response = await client.get(url)
                except httpx.HTTPError:
                    continue
                if response.status_code == 200:
                    documents.append((url, response.text[:200000]))

        return documents

    async def _run(self, job: ScanJob, payload: ScanRequest) -> None:
        policy = self.policy_for(payload)
        started = datetime.now(UTC)
        job.result.status = ScanStatus.RUNNING
        target = payload.url

        html_documents: list[tuple[str, str]] = []
        js_urls: list[str] = []
        endpoints: set[str] = {target}
        parameters: set[str] = set()
        cookies: list[dict[str, object]] = []
        headers: dict[str, str] = {}

        await self._status(job, ScanPhase.QUEUED, 0, policy.max_pages)

        try:
            target = await resolve_target_url(
                target, self.settings.navigation_timeout_ms, policy.user_agent
            )
            job.result.target = target
            job.result.subdomains = await discover_subdomains(target, policy.user_agent)

            async with BrowserSession() as session:
                if session.browser is None:
                    raise RuntimeError("Navegador no disponible")

                context = await session.browser.new_context(
                    user_agent=policy.user_agent,
                    ignore_https_errors=True,
                )
                page = await context.new_page()
                spider = Spider(policy, page)

                await self._status(job, ScanPhase.DISCOVERING, 0, policy.max_pages)

                async for update in spider.crawl(target):
                    if isinstance(update, PageError):
                        await self._emit(
                            job,
                            ErrorEvent(
                                **self._base(job.scan_id),
                                code=update.code,
                                message=update.message,
                            ),
                        )
                        continue

                    page_url = str(update.page.url)
                    job.result.pages.append(update.page)
                    if not headers:
                        headers = dict(update.headers)
                    cookies = update.cookies

                    html = str(update.data.get("html") or "")[:200000]
                    html_documents.append((page_url, html))
                    forms = self._forms(update.data)
                    job.result.forms.extend(forms)

                    links = [
                        str(link)
                        for link in cast(list[object], update.data.get("links") or [])
                    ]
                    scripts = [
                        str(script)
                        for script in cast(list[object], update.data.get("scripts") or [])
                    ]
                    params = [
                        str(param)
                        for param in cast(list[object], update.data.get("params") or [])
                    ]

                    endpoints.update(links)
                    endpoints.update(form.action for form in forms if form.action)
                    parameters.update(params)
                    js_urls.extend(scripts)

                    await self._emit(
                        job,
                        NodeEvent(
                            **self._base(job.scan_id),
                            id=update.page.id,
                            url=page_url,
                            title=update.page.title,
                            depth=update.page.depth,
                            links=update.page.links,
                            forms=update.page.forms,
                            scripts=update.page.scripts,
                            word_count=update.page.word_count,
                        ),
                    )
                    await self._status(
                        job,
                        ScanPhase.ANALYZING,
                        len(job.result.pages),
                        policy.max_pages,
                    )

            robots_paths: list[str] = []
            sitemap_paths: list[str] = []
            if payload.audit_mode:
                robots_paths, sitemap_paths = await discover_recon_paths(
                    target, policy.user_agent
                )
                job.result.robots_paths = robots_paths
                job.result.sitemap_paths = sitemap_paths
                origin = origin_of(target)
                endpoints.update(
                    path if path.startswith("http") else f"{origin}{path}"
                    for path in robots_paths
                )
                endpoints.update(sitemap_paths)

            js_urls = list(dict.fromkeys(url for url in js_urls if url.startswith(("http://", "https://"))))
            job.result.js_files = js_urls
            js_documents = await self._fetch_js(js_urls, policy.user_agent)

            extra_findings = []
            tls_finding = await inspect_target_tls(
                target, self.settings.navigation_timeout_ms, policy.user_agent
            )
            if tls_finding is not None:
                extra_findings.append(tls_finding)

            analysis = await SecurityAnalyzer(self.settings).analyze(
                AnalysisInput(
                    target=target,
                    audit_mode=payload.audit_mode,
                    headers=headers,
                    cookies=cookies,
                    pages=job.result.pages,
                    html=html_documents,
                    js=js_documents,
                    js_files=js_urls,
                    forms=job.result.forms,
                    endpoints=sorted(endpoints),
                    params=sorted(parameters),
                    robots_paths=robots_paths,
                    sitemap_paths=sitemap_paths,
                    subdomains=job.result.subdomains,
                    extra_findings=extra_findings,
                )
            )

            job.result.headers = analysis.headers
            job.result.technologies = analysis.technologies
            job.result.findings = analysis.findings
            job.result.summary = analysis.summary
            job.result.waf_detections = analysis.waf_detections

            await self._status(
                job,
                ScanPhase.REPORTING,
                len(job.result.pages),
                policy.max_pages,
            )
            for finding in analysis.findings:
                await self._emit(
                    job,
                    FindingEvent(**self._base(job.scan_id), finding=finding),
                )
            await self._emit(
                job,
                SummaryEvent(
                    **self._base(job.scan_id),
                    executive_diagnosis=analysis.summary.executive_diagnosis,
                    severity_counts=analysis.summary.severity_counts,
                    remediation_priorities=analysis.summary.remediation_priorities,
                    scope=analysis.summary.scope,
                    engine=analysis.summary.engine,
                    technologies=analysis.technologies,
                    headers=analysis.headers,
                    subdomains=job.result.subdomains,
                    waf_detections=analysis.waf_detections,
                ),
            )
        except Exception as exc:
            job.result.status = ScanStatus.FAILED
            await self._emit(
                job,
                ErrorEvent(
                    **self._base(job.scan_id),
                    code="SCAN_FAILED",
                    message=str(exc)[:300],
                ),
            )
        else:
            job.result.status = ScanStatus.COMPLETED
        finally:
            job.result.finished_at = datetime.now(UTC)
            duration_ms = int((job.result.finished_at - started).total_seconds() * 1000)
            await self._emit(
                job,
                DoneEvent(
                    **self._base(job.scan_id),
                    pages_scanned=len(job.result.pages),
                    findings_total=len(job.result.findings),
                    duration_ms=duration_ms,
                    export_ready=job.result.status == ScanStatus.COMPLETED,
                ),
            )
            try:
                with SessionLocal() as session:
                    save_scan(session, job.result)
            except Exception as exc:
                logger.warning("No se pudo persistir el escaneo %s: %s", job.scan_id, exc)
            await job.queue.put(None)


CrawlerService = ScanService
