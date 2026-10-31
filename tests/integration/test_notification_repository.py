from datetime import datetime

from transit_advisor.domain.notification import (
    Notification,
)
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)


def test_save_notification(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notification = Notification(
        id=None,
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route 15 was added",
        created_at=datetime.now(),
    )

    saved = notification_repository.save(
        notification,
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.message == "Route 15 was added"


def test_find_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notification_repository.save(
        Notification(
            id=None,
            user_id=1,
            subscription_id=1,
            schedule_version_id=1,
            message="Route 15 was added",
            created_at=datetime.now(),
        )
    )

    notifications = notification_repository.find_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].user_id == 1


def test_find_unread_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notification_repository.save(
        Notification(
            id=None,
            user_id=1,
            subscription_id=1,
            schedule_version_id=1,
            message="Route 15 was added",
            created_at=datetime.now(),
            is_read=False,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].user_id == 1
    assert notifications[0].is_unread


def test_find_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notifications = notification_repository.find_by_user_id(
        999,
    )

    assert notifications == []


def test_find_unread_by_user_id_returns_only_unread_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notification_repository.save(
        Notification(
            id=None,
            user_id=1,
            subscription_id=1,
            schedule_version_id=1,
            message="Unread notification",
            created_at=datetime.now(),
            is_read=False,
        )
    )

    notification_repository.save(
        Notification(
            id=None,
            user_id=1,
            subscription_id=2,
            schedule_version_id=1,
            message="Read notification",
            created_at=datetime.now(),
            is_read=True,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].is_unread
