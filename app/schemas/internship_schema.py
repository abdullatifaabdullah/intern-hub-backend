from datetime import datetime
from pydantic import BaseModel
from app.schemas.user_schema import UserOut


class InternshipBase(BaseModel):
    title: str
    description: str
    company: str
    location: str | None = None
    application_deadline: datetime

    class Config:
        from_attributes = True


class InternshipCreate(InternshipBase):
    pass


class InternshipUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    company: str | None = None
    location: str | None = None
    application_deadline: datetime | None = None


class InternshipOut(InternshipBase):
    id: int
    created_at: datetime
    created_by: int


class InternshipOutWithCreator(InternshipOut):
    creator: UserOut | None = None


