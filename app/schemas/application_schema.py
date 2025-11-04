from datetime import datetime
from pydantic import BaseModel
from app.schemas.user_schema import UserOut
from app.schemas.internship_schema import InternshipOut


class ApplicationBase(BaseModel):
    cover_letter: str | None = None
    status: str | None = None

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    cover_letter: str | None = None


class ApplicationUpdateStatus(BaseModel):
    status: str


class ApplicationOut(ApplicationBase):
    id: int
    user_id: int
    internship_id: int
    created_at: datetime
    internship: InternshipOut | None = None  # Optional - included when requested via include parameter


class ApplicationOutWithUser(ApplicationOut):
    user: UserOut | None = None


class ApplicationOutWithInternship(ApplicationOut):
    internship: InternshipOut | None = None


