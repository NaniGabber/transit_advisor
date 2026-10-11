from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))

    trip_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    headsign: Mapped[str | None]
