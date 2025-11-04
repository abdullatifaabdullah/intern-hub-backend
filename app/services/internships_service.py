from __future__ import annotations

from typing import Iterable
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.internship import Internship
from app.models.user import User
from app.schemas.internship_schema import InternshipCreate, InternshipUpdate


def _apply_sort(query, sort: str | None):
    if not sort:
        return query.order_by(desc(Internship.created_at))
    direction = desc if sort.startswith("-") else asc
    field = sort.lstrip("-")
    column = getattr(Internship, field, None)
    if column is None:
        return query
    return query.order_by(direction(column))


async def list_internships(
    db: AsyncSession,
    include: Iterable[str] | None,
    page: int,
    limit: int,
    sort: str | None,
):
    query = select(Internship)

    if settings.LAZY_LOADING:
        query = query.options(load_only(Internship.id, Internship.title, Internship.description, Internship.company, Internship.location, Internship.application_deadline, Internship.created_at, Internship.created_by))

    include = set(include or [])
    if "creator" in include:
        query = query.options(selectinload(Internship.creator).load_only(User.id, User.email, User.role))

    query = _apply_sort(query, sort)
    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())


async def list_my_internships(
    db: AsyncSession,
    creator_id: int,
    include: Iterable[str] | None,
    page: int,
    limit: int,
    sort: str | None,
):
    query = select(Internship).where(Internship.created_by == creator_id)

    if settings.LAZY_LOADING:
        query = query.options(load_only(Internship.id, Internship.title, Internship.description, Internship.company, Internship.location, Internship.application_deadline, Internship.created_at, Internship.created_by))

    include = set(include or [])
    if "creator" in include:
        query = query.options(selectinload(Internship.creator).load_only(User.id, User.email, User.role))

    query = _apply_sort(query, sort)
    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())


async def get_internship_by_id(db: AsyncSession, internship_id: int, include: Iterable[str] | None):
    query = select(Internship).where(Internship.id == internship_id)
    if settings.LAZY_LOADING:
        query = query.options(load_only(Internship.id, Internship.title, Internship.description, Internship.company, Internship.location, Internship.application_deadline, Internship.created_at, Internship.created_by))
    include = set(include or [])
    if "creator" in include:
        query = query.options(selectinload(Internship.creator).load_only(User.id, User.email, User.role))
    res = await db.execute(query)
    obj = res.scalar_one_or_none()
    if not obj:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internship not found")
    return obj


async def create_internship(db: AsyncSession, payload: InternshipCreate, creator_id: int):
    obj = Internship(
        title=payload.title,
        description=payload.description,
        company=payload.company,
        location=payload.location,
        application_deadline=payload.application_deadline,
        created_by=creator_id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_internship(db: AsyncSession, internship_id: int, payload: InternshipUpdate, creator_id: int | None = None):
    obj = await get_internship_by_id(db, internship_id, include=None)
    
    # Verify ownership if creator_id is provided
    if creator_id is not None and obj.created_by != creator_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own internships")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_internship(db: AsyncSession, internship_id: int, creator_id: int | None = None) -> None:
    obj = await get_internship_by_id(db, internship_id, include=None)
    
    # Verify ownership if creator_id is provided
    if creator_id is not None and obj.created_by != creator_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own internships")
    
    await db.delete(obj)
    await db.commit()


