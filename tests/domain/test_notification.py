from datetime import datetime

import pytest

from transit_advisor.domain.notification import (
    Notification,
)


@pytest.mark.parametrize(
    "user_id, subscription_id, schedule_version_id, message",
    [
        (0, 1, 1, "changed"),
        (-1, 1, 1, "changed"),
        (1, 0, 1, "changed"),
        (1, -1, 1, "changed"),
        (1, 1, 0, "changed"),
        (1, 1, -1, "changed"),
        (1, 1, 1, ""),
    ],
)
def test_invalid_notification_rejected(
    user_id: int,
    subscription_id: int,
    schedule_version_id: int,
    message: str,
) -> None:
    with pytest.raises(ValueError):
        Notification(
            id=None,
            user_id=user_id,
            subscription_id=subscription_id,
            schedule_version_id=schedule_version_id,
            message=message,
            created_at=datetime.now(),
        )


def test_create_valid_notification() -> None:
    notification = Notification(
        id=None,
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route changed",
        created_at=datetime.now(),
    )

    assert notification.user_id == 1


def test_notification_is_unread_by_default() -> None:
    notification = Notification(
        id=None,
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route changed",
        created_at=datetime.now(),
    )

    assert notification.is_unread


def test_read_notification_is_not_unread() -> None:
    notification = Notification(
        id=None,
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route changed",
        created_at=datetime.now(),
        is_read=True,
    )

    assert not notification.is_unread
