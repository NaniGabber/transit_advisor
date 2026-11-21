from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from transit_advisor.infrastructure.database.base import Base


class StopTimeModel(Base):
    __tablename__ = "stop_times"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "stop_sequence",
            name="uq_stop_times_trip_sequence",
        ),
        Index("ix_stop_times_stop_departure", "stop_id", "departure_time"),
        Index("ix_stop_times_stop_arrival", "stop_id", "arrival_time"),
        Index("ix_stop_times_stop_trip", "stop_id", "trip_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
    )

    stop_id: Mapped[int] = mapped_column(
        ForeignKey("stops.id", ondelete="CASCADE"),
        nullable=False,
    )

    arrival_time: Mapped[str] = mapped_column(String(20), nullable=False)

    departure_time: Mapped[str] = mapped_column(String(20), nullable=False)

    stop_sequence: Mapped[int] = mapped_column(nullable=False)

    trip = relationship("TripModel", back_populates="stop_times")
    stop = relationship("StopModel", back_populates="stop_times")
