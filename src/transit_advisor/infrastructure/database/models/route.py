from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from transit_advisor.infrastructure.database.base import Base


class RouteModel(Base):
    __tablename__ = "routes"
    __table_args__ = (
        Index("ix_routes_agency_id", "agency_id"),
        Index(
            "ix_routes_route_id_trgm",
            "route_id",
            postgresql_using="gin",
            postgresql_ops={"route_id": "gin_trgm_ops"},
        ),
        Index(
            "ix_routes_short_name_trgm",
            "short_name",
            postgresql_using="gin",
            postgresql_ops={"short_name": "gin_trgm_ops"},
        ),
        Index(
            "ix_routes_long_name_trgm",
            "long_name",
            postgresql_using="gin",
            postgresql_ops={"long_name": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.id"))

    route_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    short_name: Mapped[str] = mapped_column(String(50))

    long_name: Mapped[str] = mapped_column(String(255))

    route_type: Mapped[int]

    agency = relationship("AgencyModel")

    description: Mapped[str | None]
    color: Mapped[str | None]
    text_color: Mapped[str | None]
    trips = relationship("TripModel", back_populates="route")
