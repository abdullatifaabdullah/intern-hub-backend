from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdateStatus,
    ApplicationOutWithUser,
    ApplicationOutWithInternship,
)
from app.services.applications_service import (
    apply_to_internship,
    list_my_applications,
    list_internship_applications,
    update_application_status,
)
from app.core.security import require_student, require_admin

router = APIRouter(tags=["applications"])  # explicit paths per spec


@router.post("/internships/{internship_id}/applications", response_model=ApplicationOut)
async def route_apply(
    internship_id: int,
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current=Depends(require_student),
):
    return await apply_to_internship(db=db, internship_id=internship_id, student_id=current.id, payload=payload)


@router.get("/applications/me", response_model=list[ApplicationOut])
async def route_list_my_applications(
    db: AsyncSession = Depends(get_db),
    current=Depends(require_student),
    include: list[str] | None = Query(None, description="include relations: internship"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None),
):
    return await list_my_applications(db=db, student_id=current.id, include=include, page=page, limit=limit, sort=sort)


@router.get("/internships/{internship_id}/applications", response_model=list[ApplicationOutWithUser])
async def route_list_internship_applications(
    internship_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
    include: list[str] | None = Query(None, description="include relations: user"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None),
):
    return await list_internship_applications(db=db, internship_id=internship_id, include=include, page=page, limit=limit, sort=sort)


@router.patch("/applications/{application_id}", response_model=ApplicationOut)
async def route_update_application_status(
    application_id: int,
    payload: ApplicationUpdateStatus,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    return await update_application_status(db=db, application_id=application_id, payload=payload)

 