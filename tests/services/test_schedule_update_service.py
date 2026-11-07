from tests.services.fake_repos import (
    FakeNotificationRepository,
    FakeRouteRepository,
    FakeSubscriptionRepository,
)
from transit_advisor.domain.route import Route
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.subscription import Subscription
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


def make_route(
    route_repository: FakeRouteRepository,
    route_id: str = "15",
) -> Route:
    return route_repository.save(
        Route(
            id=None,
            agency_id=1,
            route_id=route_id,
            short_name=route_id,
            long_name=f"Route {route_id}",
            route_type=3,
        )
    )


def make_stop_time(
    trip_id: int,
    arrival_time: str,
    departure_time: str,
    stop_id: int = 1,
    stop_sequence: int = 1,
) -> StopTime:
    return StopTime(
        id=None,
        trip_id=trip_id,
        stop_id=stop_id,
        arrival_time=arrival_time,
        departure_time=departure_time,
        stop_sequence=stop_sequence,
    )


def test_create_notification_for_added_route() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    ) = get_schedule_update_service()

    route = make_route(route_repository)
    assert route.id is not None

    subscription = subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )
    assert subscription.id is not None

    created = service.process_update(
        old_routes=[],
        new_routes=[route],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
        ],
        trip_to_route={1: route.route_id},
    )

    assert created == 1

    saved = notification_repository.saved
    assert len(saved) == 1
    assert saved[0].user_id == 1
    assert saved[0].subscription_id == subscription.id
    assert saved[0].schedule_version_id == 1
    assert "15" in saved[0].message


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
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        trip_to_route={1: route.route_id},
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

    route = make_route(route_repository)
    assert route.id is not None

    created = service.process_update(
        old_routes=[],
        new_routes=[route],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
        ],
        trip_to_route={1: route.route_id},
    )

    assert created == 0
    assert notification_repository.saved == []


def test_no_notifications_for_unrelated_subscription() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    ) = get_schedule_update_service()

    changed_route = make_route(route_repository, route_id="15")
    other_route = make_route(route_repository, route_id="16")
    assert changed_route.id is not None
    assert other_route.id is not None

    subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=other_route.id)
    )

    created = service.process_update(
        old_routes=[],
        new_routes=[changed_route],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
        ],
        trip_to_route={1: changed_route.route_id},
    )

    assert created == 0
    assert notification_repository.saved == []


def test_no_notifications_when_route_not_found() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        _,
    ) = get_schedule_update_service()

    subscription_repository.save(Subscription(id=None, user_id=1, route_id=1))

    created = service.process_update(
        old_routes=[],
        new_routes=[
            Route(
                id=None,
                agency_id=1,
                route_id="15",
                short_name="15",
                long_name="Center",
                route_type=3,
            )
        ],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
        ],
        trip_to_route={1: "15"},
    )

    assert created == 0
    assert notification_repository.saved == []


def test_notifications_for_all_subscribers_of_changed_route() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    ) = get_schedule_update_service()

    route = make_route(route_repository)
    assert route.id is not None

    subscription_repository.save(Subscription(id=None, user_id=1, route_id=route.id))
    subscription_repository.save(Subscription(id=None, user_id=2, route_id=route.id))

    created = service.process_update(
        old_routes=[],
        new_routes=[route],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
        ],
        trip_to_route={1: route.route_id},
    )

    assert created == 2
    assert len(notification_repository.saved) == 2
    assert {n.user_id for n in notification_repository.saved} == {1, 2}


def test_notifications_for_multiple_changed_routes() -> None:
    (
        service,
        notification_repository,
        subscription_repository,
        route_repository,
    ) = get_schedule_update_service()

    route_15 = make_route(route_repository, route_id="15")
    route_16 = make_route(route_repository, route_id="16")
    assert route_15.id is not None
    assert route_16.id is not None

    subscription_repository.save(Subscription(id=None, user_id=1, route_id=route_15.id))
    subscription_repository.save(Subscription(id=None, user_id=2, route_id=route_16.id))

    created = service.process_update(
        old_routes=[],
        new_routes=[route_15, route_16],
        schedule_version_id=1,
        old_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:00:00", departure_time="08:01:00"
            ),
            make_stop_time(
                trip_id=2, arrival_time="09:00:00", departure_time="09:01:00"
            ),
        ],
        new_stop_times=[
            make_stop_time(
                trip_id=1, arrival_time="08:05:00", departure_time="08:06:00"
            ),
            make_stop_time(
                trip_id=2, arrival_time="09:05:00", departure_time="09:06:00"
            ),
        ],
        trip_to_route={1: route_15.route_id, 2: route_16.route_id},
    )

    assert created == 2
    assert len(notification_repository.saved) == 2
    assert {n.user_id for n in notification_repository.saved} == {1, 2}
    assert all(n.schedule_version_id == 1 for n in notification_repository.saved)
