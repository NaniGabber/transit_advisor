from tests.services.fake_repos import (
    FakeNotificationRepository,
    FakeRouteRepository,
    FakeStopTimeRepository,
    FakeSubscriptionRepository,
    FakeTripRepository,
)
from transit_advisor.domain.route import Route
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.subscription import Subscription
from transit_advisor.domain.trip import Trip
from transit_advisor.services.schedule_update_service import (
    ScheduleUpdateService,
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


def make_trip(
    trip_repository: FakeTripRepository,
    route: Route,
    schedule_version_id: int,
    trip_id: str = "trip_1",
) -> Trip:
    assert route.id is not None
    return trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id=trip_id,
            headsign=None,
            schedule_version_id=schedule_version_id,
        )
    )


def test_create_notification_for_added_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    subscription = fake_subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )
    assert subscription.id is not None

    created = schedule_update_service.process_update(
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

    saved = fake_notification_repository.saved
    assert len(saved) == 1
    assert saved[0].user_id == 1
    assert saved[0].subscription_id == subscription.id
    assert saved[0].schedule_version_id == 1
    assert "15" in saved[0].message


def test_no_notifications_when_no_changes(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
) -> None:
    route = Route(
        id=1,
        agency_id=1,
        route_id="15",
        short_name="15",
        long_name="Center",
        route_type=3,
    )

    created = schedule_update_service.process_update(
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
    assert fake_notification_repository.saved == []


def test_no_notifications_without_subscribers(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    created = schedule_update_service.process_update(
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
    assert fake_notification_repository.saved == []


def test_no_notifications_for_unrelated_subscription(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    changed_route = make_route(fake_route_repository, route_id="15")
    other_route = make_route(fake_route_repository, route_id="16")
    assert changed_route.id is not None
    assert other_route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=other_route.id)
    )

    created = schedule_update_service.process_update(
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
    assert fake_notification_repository.saved == []


def test_no_notifications_when_route_not_found(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
) -> None:
    fake_subscription_repository.save(Subscription(id=None, user_id=1, route_id=1))

    created = schedule_update_service.process_update(
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
    assert fake_notification_repository.saved == []


def test_notifications_for_all_subscribers_of_changed_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )
    fake_subscription_repository.save(
        Subscription(id=None, user_id=2, route_id=route.id)
    )

    created = schedule_update_service.process_update(
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
    assert len(fake_notification_repository.saved) == 2
    assert {n.user_id for n in fake_notification_repository.saved} == {1, 2}


def test_notifications_for_multiple_changed_routes(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    route_15 = make_route(fake_route_repository, route_id="15")
    route_16 = make_route(fake_route_repository, route_id="16")
    assert route_15.id is not None
    assert route_16.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route_15.id)
    )
    fake_subscription_repository.save(
        Subscription(id=None, user_id=2, route_id=route_16.id)
    )

    created = schedule_update_service.process_update(
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
    assert len(fake_notification_repository.saved) == 2
    assert {n.user_id for n in fake_notification_repository.saved} == {1, 2}
    assert all(n.schedule_version_id == 1 for n in fake_notification_repository.saved)


def test_process_update_ignores_removed_routes(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    removed_route = make_route(fake_route_repository, route_id="15")
    assert removed_route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=removed_route.id)
    )

    created = schedule_update_service.process_update(
        old_routes=[removed_route],
        new_routes=[],
        schedule_version_id=1,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_creates_notification_for_changed_stop_time(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    subscription = fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )
    assert subscription.id is not None

    old_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=1,
    )
    new_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=2,
    )
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            arrival_time="08:05:00",
            departure_time="08:06:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 1
    assert len(fake_notification_repository.saved) == 1
    assert fake_notification_repository.saved[0].schedule_version_id == 2
    assert fake_notification_repository.saved[0].user_id == 1
    assert fake_notification_repository.saved[0].subscription_id == subscription.id


def test_process_version_update_no_notifications_when_no_changes(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    old_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=1,
    )
    new_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=2,
    )
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_no_notifications_without_subscribers(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    old_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=1,
    )
    new_trip = make_trip(
        fake_trip_repository,
        route=route,
        schedule_version_id=2,
    )
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            arrival_time="08:05:00",
            departure_time="08:06:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_detects_added_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
) -> None:
    route_15 = make_route(fake_route_repository, route_id="15")
    route_16 = make_route(fake_route_repository, route_id="16")
    assert route_15.id is not None
    assert route_16.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route_16.id)
    )

    make_trip(fake_trip_repository, route=route_15, schedule_version_id=1)
    make_trip(fake_trip_repository, route=route_15, schedule_version_id=2)
    make_trip(fake_trip_repository, route=route_16, schedule_version_id=2)

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_creates_notification_for_removed_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
) -> None:
    route = make_route(fake_route_repository, route_id="15")
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    make_trip(fake_trip_repository, route=route, schedule_version_id=1)
    make_trip(fake_trip_repository, route=route, schedule_version_id=2)

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_notifies_all_subscribers_of_changed_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )
    fake_subscription_repository.save(
        Subscription(id=None, user_id=2, route_id=route.id)
    )

    old_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=1)
    new_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=2)
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            arrival_time="08:05:00",
            departure_time="08:06:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 2
    assert len(fake_notification_repository.saved) == 2
    assert {n.user_id for n in fake_notification_repository.saved} == {1, 2}


def test_process_version_update_does_not_notify_unrelated_route(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    changed_route = make_route(fake_route_repository, route_id="15")
    other_route = make_route(fake_route_repository, route_id="16")
    assert changed_route.id is not None
    assert other_route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=other_route.id)
    )

    old_trip = make_trip(
        fake_trip_repository, route=changed_route, schedule_version_id=1
    )
    new_trip = make_trip(
        fake_trip_repository, route=changed_route, schedule_version_id=2
    )
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            arrival_time="08:05:00",
            departure_time="08:06:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_detects_added_stop(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    old_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=1)
    new_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=2)
    assert old_trip.id is not None
    assert new_trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            stop_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            stop_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            stop_id=2,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 1
    assert len(fake_notification_repository.saved) == 1


def test_process_version_update_detects_multiple_changed_stops(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    old_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=1)
    new_trip = make_trip(fake_trip_repository, route=route, schedule_version_id=2)
    assert old_trip.id is not None
    assert new_trip.id is not None

    for trip_id in (old_trip.id, new_trip.id):
        fake_stoptime_repository.save(
            make_stop_time(
                trip_id=trip_id,
                stop_id=1,
                arrival_time="08:00:00",
                departure_time="08:01:00",
            )
        )
        fake_stoptime_repository.save(
            make_stop_time(
                trip_id=trip_id,
                stop_id=2,
                arrival_time="08:10:00",
                departure_time="08:11:00",
                stop_sequence=2,
            )
        )

    fake_stoptime_repository.saved.clear()
    fake_stoptime_repository._next_id = 1

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            stop_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=old_trip.id,
            stop_id=2,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            stop_id=1,
            arrival_time="08:05:00",
            departure_time="08:06:00",
        )
    )
    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=new_trip.id,
            stop_id=2,
            arrival_time="08:15:00",
            departure_time="08:16:00",
            stop_sequence=2,
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 1
    assert len(fake_notification_repository.saved) == 1
    message = fake_notification_repository.saved[0].message
    assert "1" in message
    assert "2" in message


def test_process_version_update_same_version_produces_no_notifications(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
    fake_trip_repository: FakeTripRepository,
    fake_stoptime_repository: FakeStopTimeRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    trip = make_trip(fake_trip_repository, route=route, schedule_version_id=1)
    assert trip.id is not None

    fake_stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=1,
        schedule_version_id=1,
    )

    assert created == 0
    assert fake_notification_repository.saved == []


def test_process_version_update_with_empty_versions(
    schedule_update_service: ScheduleUpdateService,
    fake_notification_repository: FakeNotificationRepository,
    fake_subscription_repository: FakeSubscriptionRepository,
    fake_route_repository: FakeRouteRepository,
) -> None:
    route = make_route(fake_route_repository)
    assert route.id is not None

    fake_subscription_repository.save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )

    created = schedule_update_service.process_version_update(
        old_version_id=1,
        new_version_id=2,
        schedule_version_id=2,
    )

    assert created == 0
    assert fake_notification_repository.saved == []
