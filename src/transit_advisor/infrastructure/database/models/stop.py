from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class StopModel(Base):
    __tablename__ = "stops"

    id: Mapped[int] = mapped_column(primary_key=True)

    stop_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    name: Mapped[str] = mapped_column(String(255))

    latitude: Mapped[float] = mapped_column(Float)

    longitude: Mapped[float] = mapped_column(Float)

    code: Mapped[str | None]
    description: Mapped[str | None]
