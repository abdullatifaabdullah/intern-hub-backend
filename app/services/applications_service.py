from __future__ import annotations

from typing import Iterable
from fastapi import HTTPException, status
from sqlalchemy import select, asc, desc, and_
from sqlalchemy.orm import selectinload, joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.application import Application
from app.models.internship import Internship
from app.models.user import User
from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationUpdateStatus,
    ApplicationOut,
    ApplicationOutWithUser,
)


def _apply_sort(query, sort: str | None, model):
    if not sort:
        return query.order_by(desc(model.created_at))
    direction = desc if sort.startswith("-") else asc
    field = sort.lstrip("-")
    column = getattr(model, field, None)
    if column is None:
        return query
    return query.order_by(direction(column))


async def apply_to_internship(db: AsyncSession, internship_id: int, student_id: int, payload: ApplicationCreate):
    # Ensure internship exists
    res = await db.execute(select(Internship.id).where(Internship.id == internship_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Internship not found")

    # Prevent duplicate applications
    dup_q = await db.execute(
        select(Application.id).where(and_(Application.user_id == student_id, Application.internship_id == internship_id))
    )
    if dup_q.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Already applied")

    obj = Application(user_id=student_id, internship_id=internship_id, cover_letter=payload.cover_letter)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    
    # Convert SQLAlchemy object to Pydantic model while session is still open
    # This prevents MissingGreenlet errors during FastAPI's response serialization
    app_data = {
        "id": obj.id,
        "user_id": obj.user_id,
        "internship_id": obj.internship_id,
        "status": obj.status,
        "cover_letter": obj.cover_letter,
        "created_at": obj.created_at,
        "internship": None,  # Explicitly set to None - not loaded for this endpoint
    }
    
    return ApplicationOut.model_validate(app_data)


async def list_my_applications(
    db: AsyncSession,
    student_id: int,
    include: Iterable[str] | None,
    page: int,
    limit: int,
    sort: str | None,
):
    query = select(Application).where(Application.user_id == student_id)
    
    # Normalize include parameter - handle both list and single values
    include_set = set()
    if include:
        if isinstance(include, str):
            include_set.add(include)
        else:
            include_set = set(include)
    
    if "internship" in include_set:
        # Use selectinload for async SQLAlchemy - this properly eager loads relationships
        # selectinload is the recommended approach for async operations
        query = query.options(
            selectinload(Application.internship)
        )
    elif settings.LAZY_LOADING:
        # Only use load_only when not loading relationships
        # Include cover_letter to avoid MissingGreenlet error when serializing
        query = query.options(load_only(Application.id, Application.user_id, Application.internship_id, Application.status, Application.cover_letter, Application.created_at))

    query = _apply_sort(query, sort, Application)
    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    applications = list(res.scalars().all())
    
    # Convert SQLAlchemy objects to Pydantic models while session is still open
    # This ensures all relationship data is fully loaded and accessible before session closes
    # This prevents MissingGreenlet errors during FastAPI's response serialization
    result = []
    for app in applications:
        # Access all relationship data while session is open
        app_data = {
            "id": app.id,
            "user_id": app.user_id,
            "internship_id": app.internship_id,
            "status": app.status,
            "cover_letter": app.cover_letter,
            "created_at": app.created_at,
        }
        
        # If internship is requested, load it while session is open
        if "internship" in include_set:
            try:
                internship = app.internship
                if internship is not None:
                    # Convert internship to dict while session is open
                    app_data["internship"] = {
                        "id": internship.id,
                        "title": internship.title,
                        "description": internship.description,
                        "company": internship.company,
                        "location": internship.location,
                        "application_deadline": internship.application_deadline,
                        "created_at": internship.created_at,
                        "created_by": internship.created_by,
                    }
                else:
                    app_data["internship"] = None
            except Exception as e:
                print(f"Warning: Could not access internship for application {app.id}: {e}")
                app_data["internship"] = None
        
        # Convert to Pydantic model while session is still open
        result.append(ApplicationOut.model_validate(app_data))
    
    return result


async def list_internship_applications(
    db: AsyncSession,
    internship_id: int,
    include: Iterable[str] | None,
    page: int,
    limit: int,
    sort: str | None,
):
    query = select(Application).where(Application.internship_id == internship_id)
    
    include = set(include or [])
    if "user" in include:
        # Use selectinload for async SQLAlchemy - this properly eager loads relationships
        # selectinload is the recommended approach for async operations
        query = query.options(selectinload(Application.user))
    elif settings.LAZY_LOADING:
        # Only use load_only when not loading relationships
        # Include cover_letter to avoid MissingGreenlet error when serializing
        query = query.options(load_only(Application.id, Application.user_id, Application.internship_id, Application.status, Application.cover_letter, Application.created_at))

    query = _apply_sort(query, sort, Application)
    query = query.offset((page - 1) * limit).limit(limit)
    res = await db.execute(query)
    applications = list(res.scalars().all())
    
    # Convert SQLAlchemy objects to Pydantic models while session is still open
    # This ensures all relationship data is fully loaded and accessible before session closes
    result = []
    for app in applications:
        # Access all relationship data while session is open
        app_data = {
            "id": app.id,
            "user_id": app.user_id,
            "internship_id": app.internship_id,
            "status": app.status,
            "cover_letter": app.cover_letter,
            "created_at": app.created_at,
            "internship": None,  # Explicitly set to None - not loaded for this endpoint
        }
        
        # If user is requested, load it while session is open
        if "user" in include:
            try:
                user = app.user
                if user is not None:
                    # Convert user to dict while session is open
                    app_data["user"] = {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role,
                    }
                else:
                    app_data["user"] = None
            except Exception as e:
                print(f"Warning: Could not access user for application {app.id}: {e}")
                app_data["user"] = None
        
        # Convert to Pydantic model while session is still open
        result.append(ApplicationOutWithUser.model_validate(app_data))
    
    return result


async def update_application_status(db: AsyncSession, application_id: int, payload: ApplicationUpdateStatus):
    res = await db.execute(select(Application).where(Application.id == application_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Application not found")
    obj.status = payload.status
    await db.commit()
    await db.refresh(obj)
    
    # Convert SQLAlchemy object to Pydantic model while session is still open
    # This prevents MissingGreenlet errors during FastAPI's response serialization
    app_data = {
        "id": obj.id,
        "user_id": obj.user_id,
        "internship_id": obj.internship_id,
        "status": obj.status,
        "cover_letter": obj.cover_letter,
        "created_at": obj.created_at,
        "internship": None,  # Explicitly set to None - not loaded for this endpoint
    }
    
    return ApplicationOut.model_validate(app_data)


