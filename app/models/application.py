from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class ApplicationStatus(str):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Enum(
        ApplicationStatus.PENDING,
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
        name="application_status",
    ), default=ApplicationStatus.PENDING, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id", ondelete="CASCADE"), index=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="applications")
    internship: Mapped["Internship"] = relationship(back_populates="applications")


