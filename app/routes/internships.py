from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.internship_schema import (
    InternshipCreate,
    InternshipOut,
    InternshipUpdate,
    InternshipOutWithCreator,
)
from app.services.internships_service import (
    list_internships,
    get_internship_by_id,
    create_internship,
    update_internship,
    delete_internship,
    list_my_internships,
)
from app.core.security import require_admin, get_current_user

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("/", response_model=list[InternshipOut])
async def route_list_internships(
    db: AsyncSession = Depends(get_db),
    include: list[str] | None = Query(None, description="include relations: creator"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, description="e.g., -created_at or title"),
):
    return await list_internships(db=db, include=include, page=page, limit=limit, sort=sort)


@router.get("/me", response_model=list[InternshipOut | InternshipOutWithCreator])
async def route_list_my_internships(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
    include: list[str] | None = Query(None, description="include relations: creator"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, description="e.g., -created_at or title"),
):
    return await list_my_internships(db=db, creator_id=admin.id, include=include, page=page, limit=limit, sort=sort)


@router.get("/{internship_id}", response_model=InternshipOut | InternshipOutWithCreator)
async def route_get_internship(
    internship_id: int,
    db: AsyncSession = Depends(get_db),
    include: list[str] | None = Query(None, description="include relations: creator"),
):
    return await get_internship_by_id(db=db, internship_id=internship_id, include=include)


@router.post("/", response_model=InternshipOut)
async def route_create_internship(
    payload: InternshipCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    return await create_internship(db=db, payload=payload, creator_id=admin.id)


@router.patch("/{internship_id}", response_model=InternshipOut)
async def route_update_internship(
    internship_id: int,
    payload: InternshipUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    return await update_internship(db=db, internship_id=internship_id, payload=payload, creator_id=admin.id)


@router.delete("/{internship_id}")
async def route_delete_internship(
    internship_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    await delete_internship(db=db, internship_id=internship_id, creator_id=admin.id)
    return {"ok": True}

 