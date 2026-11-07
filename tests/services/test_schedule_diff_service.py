from transit_advisor.domain.route import Route
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.services.schedule_diff_service import (
    ScheduleDiffService,
)


def test_detect_added_route() -> None:
    service = ScheduleDiffService()

    old_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
    ]

    new_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
        Route(
            id=2,
            agency_id=1,
            route_id="12",
            short_name="12",
            long_name="Center",
            route_type=3,
        ),
    ]

    diff = service.compare_routes(
        old_routes,
        new_routes,
    )

    assert diff.added_routes == ["12"]
    assert diff.removed_routes == []


def test_detect_removed_route() -> None:
    service = ScheduleDiffService()

    old_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
        Route(
            id=2,
            agency_id=1,
            route_id="12",
            short_name="12",
            long_name="Center",
            route_type=3,
        ),
    ]

    new_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
    ]

    diff = service.compare_routes(
        old_routes,
        new_routes,
    )

    assert diff.added_routes == []
    assert diff.removed_routes == ["12"]


def test_detect_no_changes() -> None:
    service = ScheduleDiffService()

    old_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
    ]

    new_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
    ]

    diff = service.compare_routes(
        old_routes,
        new_routes,
    )

    assert diff.added_routes == []
    assert diff.removed_routes == []


def test_detect_added_and_removed_routes() -> None:
    service = ScheduleDiffService()

    old_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
        Route(
            id=2,
            agency_id=1,
            route_id="12",
            short_name="12",
            long_name="Center",
            route_type=3,
        ),
    ]

    new_routes = [
        Route(
            id=1,
            agency_id=1,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        ),
        Route(
            id=3,
            agency_id=1,
            route_id="15",
            short_name="15",
            long_name="Airport",
            route_type=3,
        ),
    ]

    diff = service.compare_routes(
        old_routes,
        new_routes,
    )

    assert diff.added_routes == ["15"]
    assert diff.removed_routes == ["12"]


def _make_stop_time(
    trip_id: int,
    stop_id: int,
    arrival_hour: int,
    departure_hour: int,
) -> StopTime:
    return StopTime(
        id=None,
        trip_id=trip_id,
        stop_id=stop_id,
        arrival_time=f"{arrival_hour:02d}:00:00",
        departure_time=f"{departure_hour:02d}:00:00",
        stop_sequence=1,
    )


def test_detect_changed_stop_time() -> None:
    service = ScheduleDiffService()

    old_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=8, departure_hour=8),
    ]
    new_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=9, departure_hour=9),
    ]

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
        old_stop_times=old_stop_times,
        new_stop_times=new_stop_times,
        trip_to_route={1: "15"},
    )

    assert diff.changed_stop_times == {"15": [1]}


def test_no_changes_in_stop_times() -> None:
    service = ScheduleDiffService()

    old_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=8, departure_hour=8),
    ]
    new_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=8, departure_hour=8),
    ]

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
        old_stop_times=old_stop_times,
        new_stop_times=new_stop_times,
        trip_to_route={1: "15"},
    )

    assert diff.changed_stop_times == {}


def test_added_stop_time_is_detected() -> None:
    service = ScheduleDiffService()

    old_stop_times: list[StopTime] = []
    new_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=8, departure_hour=8),
    ]

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
        old_stop_times=old_stop_times,
        new_stop_times=new_stop_times,
        trip_to_route={1: "15"},
    )

    assert diff.changed_stop_times == {"15": [1]}


def test_multiple_changed_stops_for_same_route() -> None:
    service = ScheduleDiffService()

    old_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=8, departure_hour=8),
        _make_stop_time(trip_id=1, stop_id=2, arrival_hour=8, departure_hour=8),
    ]
    new_stop_times = [
        _make_stop_time(trip_id=1, stop_id=1, arrival_hour=9, departure_hour=9),
        _make_stop_time(trip_id=1, stop_id=2, arrival_hour=9, departure_hour=9),
    ]

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
        old_stop_times=old_stop_times,
        new_stop_times=new_stop_times,
        trip_to_route={1: "15"},
    )

    assert diff.changed_stop_times == {"15": [1, 2]}


def test_stop_time_without_route_mapping_is_ignored() -> None:
    service = ScheduleDiffService()

    old_stop_times = [
        _make_stop_time(trip_id=99, stop_id=1, arrival_hour=8, departure_hour=8),
    ]
    new_stop_times = [
        _make_stop_time(trip_id=99, stop_id=1, arrival_hour=9, departure_hour=9),
    ]

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
        old_stop_times=old_stop_times,
        new_stop_times=new_stop_times,
        trip_to_route={},
    )

    assert diff.changed_stop_times == {}


def test_existing_behavior_without_stop_times() -> None:
    service = ScheduleDiffService()

    diff = service.compare_routes(
        old_routes=[],
        new_routes=[],
    )

    assert diff.changed_stop_times == {}
