from sqlalchemy import select, update
from sqlalchemy.orm import Session

from transit_advisor.domain.notification import Notification
from transit_advisor.infrastructure.database.models.notification import (
    NotificationModel,
)


class SqlAlchemyNotificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, notification: Notification) -> Notification:
        model = self._to_model(notification)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def save_all(self, notifications: list[Notification]) -> list[Notification]:
        """Bulk insert — для масових розсилок (наприклад, нова версія розкладу)."""
        if not notifications:
            return []
        models = [self._to_model(n) for n in notifications]
        self._session.add_all(models)
        self._session.flush()
        return [self._to_domain(m) for m in models]

    def find_by_user_id(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Notification]:
        statement = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_unread_by_user_id(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Notification]:
        statement = (
            select(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read.is_(False),
            )
            .order_by(NotificationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def mark_as_read(self, notification_id: int) -> bool:
        """Позначити одне сповіщення прочитаним. False — якщо не знайдено."""
        model = self._session.get(NotificationModel, notification_id)
        if model is None:
            return False
        model.is_read = True
        self._session.flush()
        return True

    def mark_all_as_read(self, user_id: int) -> None:
        """Позначити всі непрочитані сповіщення користувача прочитаними."""
        self._session.execute(
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read.is_(False),
            )
            .values(is_read=True)
        )
        self._session.flush()

    def _to_model(self, notification: Notification) -> NotificationModel:
        return NotificationModel(
            user_id=notification.user_id,
            subscription_id=notification.subscription_id,
            schedule_version_id=notification.schedule_version_id,
            message=notification.message,
            created_at=notification.created_at,
            is_read=notification.is_read,
        )

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
