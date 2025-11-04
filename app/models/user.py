from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class UserRole(str):
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum(UserRole.ADMIN, UserRole.STUDENT, name="user_role"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    internships: Mapped[list["Internship"]] = relationship(back_populates="creator")
    applications: Mapped[list["Application"]] = relationship(back_populates="user")


