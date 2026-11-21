from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, get_current_user
from app.db.database import get_session
from app.db.repository import (
    delete_monitored_target,
    get_monitored_target,
    list_monitored_targets,
    set_monitored_active,
    upsert_monitored_target,
)
from app.models.history import (
    MonitoredTargetCreate,
    MonitoredTargetRead,
    MonitoredTargetUpdate,
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/targets", response_model=MonitoredTargetRead, status_code=201)
async def create_target(
    payload: MonitoredTargetCreate,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MonitoredTargetRead:
    target = upsert_monitored_target(
        session,
        user.id,
        payload.domain,
        payload.frequency,
        payload.webhook_url,
    )
    return MonitoredTargetRead.model_validate(target)


@router.get("/targets", response_model=list[MonitoredTargetRead])
async def list_targets(
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[MonitoredTargetRead]:
    return [
        MonitoredTargetRead.model_validate(item)
        for item in list_monitored_targets(session, user.id)
    ]


@router.patch("/targets/{target_id}", response_model=MonitoredTargetRead)
async def update_target(
    target_id: int,
    payload: MonitoredTargetUpdate,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MonitoredTargetRead:
    target = get_monitored_target(session, target_id, user.id)
    if target is None:
        raise HTTPException(status_code=404, detail="Dominio vigilado no encontrado")
    return MonitoredTargetRead.model_validate(
        set_monitored_active(session, target, payload.active)
    )


@router.delete("/targets/{target_id}")
async def remove_target(
    target_id: int,
    user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    target = get_monitored_target(session, target_id, user.id)
    if target is None:
        raise HTTPException(status_code=404, detail="Dominio vigilado no encontrado")
    delete_monitored_target(session, target)
    return {"deleted": True}
