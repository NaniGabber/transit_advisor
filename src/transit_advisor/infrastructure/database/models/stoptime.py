from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class StopTimeModel(Base):
    __tablename__ = "stop_times"

    __table_args__ = (
        UniqueConstraint(
            "trip_id",
            "stop_sequence",
            name="uq_stop_times_trip_sequence",
        ),
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
