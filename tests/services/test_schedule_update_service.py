from tests.services.fake_repos import (
    FakeNotificationRepository,
    FakeRouteRepository,
    FakeSubscriptionRepository,
)
from transit_advisor.domain.route import Route
from transit_advisor.domain.subscription import (
    Subscription,
)
from transit_advisor.services.notification_service import (
    NotificationService,
)
from transit_advisor.services.schedule_diff_service import (
    ScheduleDiffService,
)
from transit_advisor.services.schedule_update_service import (
    ScheduleUpdateService,
)


def get_schedule_update_service() -> tuple[
    ScheduleUpdateService,
    FakeNotificationRepository,
    FakeSubscriptionRepository,
    FakeRouteRepository,
]:
    notification_repository = FakeNotificationRepository()

    subscription_repository = FakeSubscriptionRepository()

    route_repository = FakeRouteRepository()

    service = ScheduleUpdateService(
        diff_service=ScheduleDiffService(),
        notification_service=NotificationService(
            notification_repository,
        ),
        subscription_repository=subscription_repository,
        route_repository=route_repository,
    )

    return (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    )


def test_create_notification_for_added_route() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    ) = get_schedule_update_service()

    route = route_repository.save(
        Route(
            id=None,
            agency_id=1,
            route_id="15",
            short_name="15",
            long_name="Center",
            route_type=3,
        )
    )

    assert route.id is not None

    subscription_repository.save(
        Subscription(
            id=1,
            user_id=1,
            route_id=route.id,
        )
    )

    created = service.process_update(
        old_routes=[],
        new_routes=[route],
        schedule_version_id=1,
    )

    assert created == 1
    assert (
        len(
            notification_repository.saved,
        )
        == 1
    )


def test_no_notifications_when_no_changes() -> None:
    (
        service,
        notification_repository,
        _,
        _,
    ) = get_schedule_update_service()

    route = Route(
        id=1,
        agency_id=1,
        route_id="15",
        short_name="15",
        long_name="Center",
        route_type=3,
    )

    created = service.process_update(
        old_routes=[route],
        new_routes=[route],
        schedule_version_id=1,
    )

    assert created == 0
    assert notification_repository.saved == []


def test_no_notifications_without_subscribers() -> None:
    (
        service,
        notification_repository,
        _,
        route_repository,
    ) = get_schedule_update_service()

    route = route_repository.save(
        Route(
            id=None,
            agency_id=1,
            route_id="15",
            short_name="15",
            long_name="Center",
            route_type=3,
        )
    )

    created = service.process_update(
        old_routes=[],
        new_routes=[route],
        schedule_version_id=1,
    )

    assert created == 0
    assert notification_repository.saved == []
