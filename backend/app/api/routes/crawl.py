from uuid import UUID

from fastapi import APIRouter

from app.models.crawl import CrawlAccepted, CrawlRequest, CrawlResult

router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post("", status_code=202)
async def start_crawl(payload: CrawlRequest) -> CrawlAccepted:
    raise NotImplementedError


@router.get("/{crawl_id}")
async def get_crawl(crawl_id: UUID) -> CrawlResult:
    raise NotImplementedError


@router.get("/{crawl_id}/stream")
async def stream_crawl(crawl_id: UUID) -> None:
    raise NotImplementedError
