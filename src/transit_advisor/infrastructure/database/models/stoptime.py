from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class StopTimeModel(Base):
    __tablename__ = "stop_times"

    id: Mapped[int] = mapped_column(primary_key=True)

    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))

    stop_id: Mapped[int] = mapped_column(ForeignKey("stops.id"))

    arrival_time: Mapped[str] = mapped_column(String(20))

    departure_time: Mapped[str] = mapped_column(String(20))

    stop_sequence: Mapped[int]
