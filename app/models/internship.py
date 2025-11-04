from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    application_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    creator: Mapped["User"] = relationship(back_populates="internships")

    applications: Mapped[list["Application"]] = relationship(back_populates="internship", cascade="all,delete-orphan")


