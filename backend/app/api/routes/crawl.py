from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response, StreamingResponse

from app.api.deps import AuthenticatedUser, get_current_user, get_scan_service
from app.models.security import ScanAccepted, ScanRequest, ScanResult
from app.services.crawler_service import ScanService
from app.services.export_service import to_markdown
from app.services.pdf_service import to_pdf

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", status_code=202)
async def start_scan(
    payload: ScanRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    service: ScanService = Depends(get_scan_service),
) -> ScanAccepted:
    scan_id, result = await service.start(payload, user.id)
    return ScanAccepted(scan_id=scan_id, status=result.status)


@router.get("/{scan_id}/report.md", response_class=PlainTextResponse)
async def get_report(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    service: ScanService = Depends(get_scan_service),
) -> PlainTextResponse:
    result = await service.get(scan_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")

    return PlainTextResponse(
        to_markdown(result),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="neurospider-{scan_id}.md"'
        },
    )


@router.get("/{scan_id}/report.pdf", response_class=Response)
async def get_pdf_report(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    service: ScanService = Depends(get_scan_service),
) -> Response:
    result = await service.get(scan_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")

    return Response(
        content=to_pdf(result),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="neurospider-audit-{scan_id}.pdf"'
        },
    )


@router.get("/{scan_id}")
async def get_scan(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    service: ScanService = Depends(get_scan_service),
) -> ScanResult:
    result = await service.get(scan_id, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")
    return result


@router.get("/{scan_id}/stream")
async def stream_scan(
    scan_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    service: ScanService = Depends(get_scan_service),
) -> StreamingResponse:
    async def generate() -> AsyncIterator[str]:
        async for event in service.stream(scan_id, user.id):
            yield f"event: {event.type.value}\ndata: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
