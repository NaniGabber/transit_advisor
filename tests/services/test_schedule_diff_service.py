from transit_advisor.domain.route import Route
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
