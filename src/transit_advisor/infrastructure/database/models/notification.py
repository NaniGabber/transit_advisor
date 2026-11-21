from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from transit_advisor.infrastructure.database.base import (
    Base,
)


class NotificationModel(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "schedule_version_id",
            name="uq_notification",
        ),
        Index(
            "ix_notifications_user_read_created",
            "user_id",
            "is_read",
            "created_at",
        ),
        Index("ix_notifications_subscription_id", "subscription_id"),
        Index("ix_notifications_schedule_version_id", "schedule_version_id"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    # TODO
    # user_id: Mapped[int] = mapped_column(
    #    ForeignKey("users.id"),
    # )

    user_id: Mapped[int] = mapped_column()

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id"),
    )

    schedule_version_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_versions.id"),
    )

    message: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
