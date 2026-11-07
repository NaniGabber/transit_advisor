from datetime import datetime

from tests.services.fake_repos import (
    FakeNotificationRepository,
)
from transit_advisor.domain.schedulediff import (
    ScheduleDiff,
)
from transit_advisor.domain.subscription import (
    Subscription,
)
from transit_advisor.services.notification_service import (
    NotificationService,
)


def test_create_notification(
    notification_service: NotificationService,
) -> None:
    notification = notification_service.create_notification(
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route 11 was added",
    )

    assert notification.id == 1
    assert notification.user_id == 1
    assert notification.subscription_id == 1
    assert notification.schedule_version_id == 1
    assert notification.message == "Route 11 was added"
    assert isinstance(notification.created_at, datetime)


def test_notification_saved(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
    notification_service.create_notification(
        user_id=1,
        subscription_id=1,
        schedule_version_id=1,
        message="Route 11 was added",
    )

    assert len(fake_notification_repository.saved) == 1


def test_notification_persists_schedule_version_id(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
    notification_service.create_notification(
        user_id=1,
        subscription_id=1,
        schedule_version_id=42,
        message="Route 11 was added",
    )

    saved = fake_notification_repository.saved
    assert len(saved) == 1
    assert saved[0].schedule_version_id == 42


def test_notify_about_added_route(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
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

    created = notification_service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 1
    assert len(fake_notification_repository.saved) == 1


def test_no_notifications_when_no_matching_subscriptions(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
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

    created = notification_service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_no_notifications_when_no_changes(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
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

    created = notification_service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_multiple_subscribers_receive_notifications(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
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

    created = notification_service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=1,
    )

    assert created == 2
    assert len(fake_notification_repository.saved) == 2
    assert {n.user_id for n in fake_notification_repository.saved} == {1, 2}


def test_notifications_use_given_schedule_version_id(
    notification_service: NotificationService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
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

    created = notification_service.notify_about_added_routes(
        diff=diff,
        subscriptions=subscriptions,
        schedule_version_id=42,
    )

    assert created == 2
    saved = fake_notification_repository.saved
    assert len(saved) == 2
    assert all(n.schedule_version_id == 42 for n in saved)
