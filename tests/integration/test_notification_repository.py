from datetime import datetime

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.notification import (
    Notification,
)
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
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


def _make_subscription(user_id: int, route_id: str) -> Subscription:
    return Subscription(
        id=None,
        user_id=user_id,
        route_id=route_id,
    )


def _make_schedule_version() -> ScheduleVersion:
    return ScheduleVersion(
        id=None,
        checksum="a" * 64,
        imported_at=datetime.now(),
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


def _seed_parents(
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    route_gtfs_id: str = "11",
    user_id: int = 1,
) -> tuple[int, int]:
    if agency.id is None:
        raise RuntimeError("agency fixture must save the agency")

    route = route_repository.save(_make_route(agency.id, route_gtfs_id))
    if route.id is None:
        raise RuntimeError("route repository did not assign an id")

    subscription = subscription_repository.save(
        _make_subscription(user_id, route.route_id)
    )
    if subscription.id is None:
        raise RuntimeError("subscription repository did not assign an id")

    version = schedule_version_repository.save(_make_schedule_version())
    if version.id is None:
        raise RuntimeError("schedule version repository did not assign an id")

    return subscription.id, version.id


def test_save_notification(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
) -> None:
    subscription_id, version_id = _seed_parents(
        agency,
        route_repository,
        subscription_repository,
        schedule_version_repository,
    )

    notification = _make_notification(
        user_id=1,
        subscription_id=subscription_id,
        schedule_version_id=version_id,
        message="Route 15 was added",
    )

    saved = notification_repository.save(
        notification,
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.message == "Route 15 was added"


def test_find_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
) -> None:
    subscription_id, version_id = _seed_parents(
        agency,
        route_repository,
        subscription_repository,
        schedule_version_repository,
    )

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


def test_find_unread_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
) -> None:
    subscription_id, version_id = _seed_parents(
        agency,
        route_repository,
        subscription_repository,
        schedule_version_repository,
    )

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


def test_find_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notifications = notification_repository.find_by_user_id(
        999,
    )

    assert notifications == []


def test_find_unread_by_user_id_returns_only_unread_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
) -> None:
    subscription_id_1, version_id = _seed_parents(
        agency,
        route_repository,
        subscription_repository,
        schedule_version_repository,
        route_gtfs_id="11",
    )

    if agency.id is None:
        raise RuntimeError("agency fixture must save the agency")

    route_2 = route_repository.save(_make_route(agency.id, "12"))
    if route_2.id is None:
        raise RuntimeError("route repository did not assign an id")

    subscription_2 = subscription_repository.save(
        _make_subscription(1, route_2.route_id)
    )
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
