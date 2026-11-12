from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class TripModel(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("schedule_version_id", "trip_id", name="uq_trip_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))

    trip_id: Mapped[str] = mapped_column(
        String(100),
    )
    schedule_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schedule_versions.id"),
        nullable=True,
    )
    headsign: Mapped[str | None]

    service_id: Mapped[str] = mapped_column(String(100))
