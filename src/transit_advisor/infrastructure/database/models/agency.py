from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class AgencyModel(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(primary_key=True)

    agency_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    name: Mapped[str] = mapped_column(String(255))
    timezone: Mapped[str] = mapped_column(String(100))

    language: Mapped[str | None]
    phone: Mapped[str | None]
    fare_url: Mapped[str | None]
    email: Mapped[str | None]
