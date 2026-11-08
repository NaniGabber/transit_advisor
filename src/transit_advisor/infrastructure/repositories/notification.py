from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.notification import (
    Notification,
)
from transit_advisor.infrastructure.database.models.notification import (
    NotificationModel,
)


class SqlAlchemyNotificationRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def _to_domain(self, model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            user_id=model.user_id,
            subscription_id=model.subscription_id,
            schedule_version_id=model.schedule_version_id,
            message=model.message,
            created_at=model.created_at,
            is_read=model.is_read,
        )

    def save(
        self,
        notification: Notification,
    ) -> Notification:
        model = NotificationModel(
            user_id=notification.user_id,
            subscription_id=notification.subscription_id,
            schedule_version_id=notification.schedule_version_id,
            message=notification.message,
            created_at=notification.created_at,
            is_read=notification.is_read,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_domain(model)

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]:
        statement = select(
            NotificationModel,
        ).where(
            NotificationModel.user_id == user_id,
        )

        models = self._session.scalars(
            statement,
        ).all()

        return [self._to_domain(model) for model in models]

    def find_unread_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]:
        statement = select(
            NotificationModel,
        ).where(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read.is_(False),
        )

        models = self._session.scalars(
            statement,
        ).all()

        return [self._to_domain(model) for model in models]
