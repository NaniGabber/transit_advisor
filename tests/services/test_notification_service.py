from transit_advisor.domain.schedulediff import (
    ScheduleDiff,
)
from transit_advisor.domain.subscription import (
    Subscription,
)

from .fake_repos import (
    get_notification_service,
)


def test_create_notification() -> None:
    container = get_notification_service()

    notification = container.service.create_notification(
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route 11 was added",
    )

    assert notification.id == 1
    assert notification.user_id == 1
    assert notification.subscription_id == 1
    assert notification.schedule_version_id == 1


def test_notification_saved() -> None:
    container = get_notification_service()

    container.service.create_notification(
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route 11 was added",
    )

    assert (
        len(
            container.notification_repository.saved,
        )
        == 1
    )


def test_notify_about_added_route() -> None:
    container = get_notification_service()

    diff = ScheduleDiff(
        added_routes=["11"],
        removed_routes=[],
    )

    subscriptions = [
        Subscription(
            id=1,
            user_id=1,
            route_id=11,
        ),
    ]

    created = container.service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 1

    assert (
        len(
            container.notification_repository.saved,
        )
        == 1
    )


def test_no_notifications_when_no_matching_subscriptions() -> None:
    container = get_notification_service()

    diff = ScheduleDiff(
        added_routes=["11"],
        removed_routes=[],
    )

    subscriptions = [
        Subscription(
            id=1,
            user_id=1,
            route_id=99,
        ),
    ]

    created = container.service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 0

    assert container.notification_repository.saved == []


def test_no_notifications_when_no_changes() -> None:
    container = get_notification_service()

    diff = ScheduleDiff(
        added_routes=[],
        removed_routes=[],
    )

    subscriptions = [
        Subscription(
            id=1,
            user_id=1,
            route_id=11,
        ),
    ]

    created = container.service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 0

    assert container.notification_repository.saved == []


def test_multiple_subscribers_receive_notifications() -> None:
    container = get_notification_service()

    diff = ScheduleDiff(
        added_routes=["11"],
        removed_routes=[],
    )

    subscriptions = [
        Subscription(
            id=1,
            user_id=1,
            route_id=11,
        ),
        Subscription(
            id=2,
            user_id=2,
            route_id=11,
        ),
    ]

    created = container.service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 2

    assert (
        len(
            container.notification_repository.saved,
        )
        == 2
    )
