from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from transit_advisor.infrastructure.database.base import Base


class RouteModel(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)

    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.id"))

    route_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    short_name: Mapped[str] = mapped_column(String(50))

    long_name: Mapped[str] = mapped_column(String(255))

    route_type: Mapped[int]

    description: Mapped[str | None]
    color: Mapped[str | None]
    text_color: Mapped[str | None]

    agency = relationship("AgencyModel")
