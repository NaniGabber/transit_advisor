from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class ScheduleVersionModel(Base):
    __tablename__ = "schedule_versions"
    __table_args__ = (Index("ix_schedule_versions_imported_at", "imported_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    checksum: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )

    imported_at: Mapped[datetime] = mapped_column(DateTime)
