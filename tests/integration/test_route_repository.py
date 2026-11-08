from collections.abc import Callable

import pytest

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.trip import SqlAlchemyTripRepository


@pytest.fixture
def make_route(
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> Callable[..., Route]:
    def create(
        route_id: str = "11",
        short_name: str = "11",
        long_name: str = "Railway Station",
        route_type: int = 3,
    ) -> Route:
        assert agency.id is not None
        return route_repository.save(
            Route(
                id=None,
                agency_id=agency.id,
                route_id=route_id,
                short_name=short_name,
                long_name=long_name,
                route_type=route_type,
            )
        )

    return create


def test_save_route(
    make_route: Callable[..., Route],
) -> None:
    saved = make_route()

    assert saved.id is not None


def test_save_persists_all_fields(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    saved = make_route(
        route_id="15",
        short_name="15A",
        long_name="Center",
        route_type=3,
    )
    assert saved.id is not None
    found = route_repository.find_by_id(saved.id)

    assert found is not None
    assert found.route_id == "15"
    assert found.short_name == "15A"
    assert found.long_name == "Center"
    assert found.route_type == 3


def test_find_by_route_id(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11")

    found = route_repository.find_by_route_id("11")

    assert found is not None
    assert found.route_id == "11"
    assert found.short_name == "11"


def test_find_by_route_id_returns_none_for_missing_route(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    found = route_repository.find_by_route_id("missing")

    assert found is None


def test_saved_route_can_be_loaded(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    saved = make_route(route_id="11")

    loaded = route_repository.find_by_route_id(saved.route_id)

    assert loaded is not None
    assert loaded.route_id == saved.route_id
    assert loaded.agency_id == saved.agency_id


def test_find_by_id_returns_route(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    saved = make_route(route_id="11")
    assert saved.id is not None

    found = route_repository.find_by_id(saved.id)

    assert found is not None
    assert found.id == saved.id
    assert found.route_id == "11"


def test_find_by_id_returns_none_for_missing_route(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    assert route_repository.find_by_id(999) is None


def test_search_returns_all_when_no_filters(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11")
    make_route(route_id="12")

    found = route_repository.search()

    assert len(found) == 2


def test_search_by_query_matches_route_id(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11", short_name="11", long_name="Station")
    make_route(route_id="15", short_name="15", long_name="Center")

    found = route_repository.search(query="15")

    assert len(found) == 1
    assert found[0].route_id == "15"


def test_search_by_query_matches_short_name(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11", short_name="A11", long_name="Station")
    make_route(route_id="15", short_name="A15", long_name="Center")

    found = route_repository.search(query="a11")

    assert len(found) == 1
    assert found[0].short_name == "A11"


def test_search_by_query_matches_long_name(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11", short_name="11", long_name="Railway Station")
    make_route(route_id="15", short_name="15", long_name="Center")

    found = route_repository.search(query="railway")

    assert len(found) == 1
    assert found[0].long_name == "Railway Station"


def test_search_returns_empty_when_no_match(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11")

    found = route_repository.search(query="nonexistent")

    assert found == []


def test_search_by_stop_id(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
    stop: Stop,
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    schedule_version: ScheduleVersion,
) -> None:
    route_1 = make_route(route_id="1001", short_name="1001", long_name="Station")

    assert route_1.id is not None
    assert stop.id is not None
    assert schedule_version.id is not None

    trip_1 = trip_repository.save(
        Trip(
            id=None,
            route_id=route_1.id,
            trip_id="trip_1001",
            schedule_version_id=schedule_version.id,
        )
    )
    assert trip_1.id is not None

    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_1.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=1,
        )
    )

    found = route_repository.search(stop_id=stop.id)

    assert len(found) == 1
    assert found[0].id == route_1.id


def test_search_applies_pagination(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11")
    make_route(route_id="12")
    make_route(route_id="13")

    found = route_repository.search(offset=1, limit=1)

    assert len(found) == 1
