from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from transit_advisor.infrastructure.database.base import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "route_id",
            name="uq_user_route",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int]

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
