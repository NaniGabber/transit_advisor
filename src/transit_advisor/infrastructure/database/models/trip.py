from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from transit_advisor.infrastructure.database.base import Base


class TripModel(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("schedule_version_id", "trip_id", name="uq_trip_version"),
        Index(
            "ix_trips_route_schedule_service",
            "route_id",
            "schedule_version_id",
            "service_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"),
        index=True,
    )

    trip_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )
    schedule_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schedule_versions.id"),
        nullable=True,
        index=True,
    )
    headsign: Mapped[str | None]

    service_id: Mapped[str] = mapped_column(String(100))

    route = relationship("RouteModel", back_populates="trips")
    stop_times = relationship("StopTimeModel", back_populates="trip")
