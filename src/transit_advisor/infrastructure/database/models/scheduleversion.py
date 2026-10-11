from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class ScheduleVersionModel(Base):
    __tablename__ = "schedule_versions"

    id: Mapped[int] = mapped_column(primary_key=True)

    checksum: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )

    imported_at: Mapped[datetime] = mapped_column(DateTime)
