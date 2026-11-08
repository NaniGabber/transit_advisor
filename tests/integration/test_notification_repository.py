from datetime import datetime

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.notification import Notification
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


def _make_route(agency_id: int, route_id: str) -> Route:
    return Route(
        id=None,
        agency_id=agency_id,
        route_id=route_id,
        short_name=route_id,
        long_name=f"Route {route_id}",
        route_type=3,
    )


def _make_subscription(user_id: int, route_id: int) -> Subscription:
    return Subscription(
        id=None,
        user_id=user_id,
        route_id=route_id,
    )


def _make_notification(
    user_id: int,
    subscription_id: int,
    schedule_version_id: int,
    message: str,
    is_read: bool = False,
) -> Notification:
    return Notification(
        id=None,
        user_id=user_id,
        subscription_id=subscription_id,
        schedule_version_id=schedule_version_id,
        message=message,
        created_at=datetime.now(),
        is_read=is_read,
    )


def test_save_notification(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
        )
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.subscription_id == subscription_id
    assert saved.schedule_version_id == version_id
    assert saved.message == "Route 15 was added"
    assert saved.is_read is False
    assert isinstance(saved.created_at, datetime)


def test_save_assigns_distinct_ids(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    first = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="First",
        )
    )
    second = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Second",
        )
    )

    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id


def test_find_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
        )
    )

    notifications = notification_repository.find_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].user_id == 1
    assert notifications[0].message == "Route 15 was added"


def test_find_by_user_id_returns_all_for_user(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="First",
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Second",
        )
    )

    notifications = notification_repository.find_by_user_id(1)

    assert len(notifications) == 2
    assert {n.message for n in notifications} == {"First", "Second"}


def test_find_by_user_id_does_not_leak_other_users(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="For user 1",
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="For user 2",
        )
    )

    notifications = notification_repository.find_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "For user 1"


def test_find_unread_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
            is_read=False,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].user_id == 1
    assert notifications[0].is_unread


def test_find_unread_by_user_id_excludes_read(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Unread",
            is_read=False,
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Read",
            is_read=True,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "Unread"
    assert notifications[0].is_unread


def test_find_unread_by_user_id_returns_empty_when_all_read(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Read",
            is_read=True,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert notifications == []


def test_find_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notifications = notification_repository.find_by_user_id(
        999,
    )

    assert notifications == []


def test_find_unread_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notifications = notification_repository.find_unread_by_user_id(
        999,
    )

    assert notifications == []


def test_find_unread_by_user_id_returns_only_unread_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id_1, version_id = notification_parents

    if agency.id is None:
        raise RuntimeError("agency fixture must save the agency")

    route_2 = route_repository.save(_make_route(agency.id, "12"))
    if route_2.id is None:
        raise RuntimeError("route repository did not assign an id")

    subscription_2 = subscription_repository.save(_make_subscription(1, route_2.id))
    if subscription_2.id is None:
        raise RuntimeError("subscription repository did not assign an id")

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id_1,
            schedule_version_id=version_id,
            message="Unread notification",
            is_read=False,
        )
    )

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_2.id,
            schedule_version_id=version_id,
            message="Read notification",
            is_read=True,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(
        1,
    )

    assert len(notifications) == 1
    assert notifications[0].is_unread
    assert notifications[0].message == "Unread notification"


def test_save_persists_is_read_true(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Read notification",
            is_read=True,
        )
    )

    assert saved.is_read is True


def test_find_unread_by_user_id_does_not_leak_other_users(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Unread for user 1",
            is_read=False,
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Unread for user 2",
            is_read=False,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "Unread for user 1"
