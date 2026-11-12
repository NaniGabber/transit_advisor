from fastapi.testclient import TestClient

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.stop import (
    SqlAlchemyStopRepository,
)
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.trip import (
    SqlAlchemyTripRepository,
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


def _make_trip(route_id: int, trip_id: str, version_id: int) -> Trip:
    return Trip(
        id=None,
        route_id=route_id,
        trip_id=trip_id,
        service_id="WEEKDAY",
        schedule_version_id=version_id,
    )


def _make_stop(stop_id: str, name: str) -> Stop:
    return Stop(
        id=None,
        stop_id=stop_id,
        name=name,
        latitude=50.0,
        longitude=36.0,
    )


def _make_stop_time(
    trip_id: int,
    stop_id: int,
    arrival: str,
    departure: str,
    sequence: int,
) -> StopTime:
    return StopTime(
        id=None,
        trip_id=trip_id,
        stop_id=stop_id,
        arrival_time=arrival,
        departure_time=departure,
        stop_sequence=sequence,
    )


def test_find_direct_journey(
    client: TestClient,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    stop_repository: SqlAlchemyStopRepository,
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    schedule_version: ScheduleVersion,
) -> None:
    assert agency.id is not None
    assert schedule_version.id is not None

    route = route_repository.save(_make_route(agency.id, "1001"))
    assert route.id is not None

    stop_1 = stop_repository.save(_make_stop("s1", "Station"))
    stop_2 = stop_repository.save(_make_stop("s2", "Center"))
    assert stop_1.id is not None
    assert stop_2.id is not None

    trip = trip_repository.save(_make_trip(route.id, "trip_1", schedule_version.id))
    assert trip.id is not None

    stoptime_repository.save(
        _make_stop_time(trip.id, stop_1.id, "08:00:00", "08:00:00", 1)
    )
    stoptime_repository.save(
        _make_stop_time(trip.id, stop_2.id, "08:10:00", "08:10:00", 2)
    )

    response = client.get(f"/journeys?from_stop={stop_1.id}&to_stop={stop_2.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["trip_id"] == trip.id
    assert data[0]["from_stop_id"] == stop_1.id
    assert data[0]["to_stop_id"] == stop_2.id
    assert data[0]["departure_time"] == "08:00:00"
    assert data[0]["arrival_time"] == "08:10:00"


def test_no_journeys_when_stops_not_connected(
    client: TestClient,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    stop_repository: SqlAlchemyStopRepository,
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    schedule_version: ScheduleVersion,
) -> None:
    assert agency.id is not None
    assert schedule_version.id is not None

    route = route_repository.save(_make_route(agency.id, "1002"))
    assert route.id is not None

    stop_1 = stop_repository.save(_make_stop("s3", "Station"))
    stop_2 = stop_repository.save(_make_stop("s4", "Center"))
    stop_3 = stop_repository.save(_make_stop("s5", "Airport"))
    assert stop_1.id is not None
    assert stop_2.id is not None
    assert stop_3.id is not None

    trip = trip_repository.save(_make_trip(route.id, "trip_2", schedule_version.id))
    assert trip.id is not None

    # trip проходить лише через stop_1 і stop_2
    stoptime_repository.save(
        _make_stop_time(trip.id, stop_1.id, "08:00:00", "08:00:00", 1)
    )
    stoptime_repository.save(
        _make_stop_time(trip.id, stop_2.id, "08:10:00", "08:10:00", 2)
    )

    # Запитуємо stop_1 -> stop_3, але stop_3 не в trip
    response = client.get(f"/journeys?from_stop={stop_1.id}&to_stop={stop_3.id}")

    assert response.status_code == 200
    assert response.json() == []


def test_no_journey_when_stops_in_reverse_order(
    client: TestClient,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    stop_repository: SqlAlchemyStopRepository,
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    schedule_version: ScheduleVersion,
) -> None:
    assert agency.id is not None
    assert schedule_version.id is not None

    route = route_repository.save(_make_route(agency.id, "1003"))
    assert route.id is not None

    stop_1 = stop_repository.save(_make_stop("s6", "Station"))
    stop_2 = stop_repository.save(_make_stop("s7", "Center"))
    assert stop_1.id is not None
    assert stop_2.id is not None

    trip = trip_repository.save(_make_trip(route.id, "trip_3", schedule_version.id))
    assert trip.id is not None

    stoptime_repository.save(
        _make_stop_time(trip.id, stop_1.id, "08:00:00", "08:00:00", 1)
    )
    stoptime_repository.save(
        _make_stop_time(trip.id, stop_2.id, "08:10:00", "08:10:00", 2)
    )

    # Запитуємо stop_2 -> stop_1 (у зворотному напрямку)
    response = client.get(f"/journeys?from_stop={stop_2.id}&to_stop={stop_1.id}")

    assert response.status_code == 200
    assert response.json() == []


def test_journeys_pagination(
    client: TestClient,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    stop_repository: SqlAlchemyStopRepository,
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    schedule_version: ScheduleVersion,
) -> None:
    assert agency.id is not None
    assert schedule_version.id is not None

    route = route_repository.save(_make_route(agency.id, "1004"))
    assert route.id is not None

    stop_1 = stop_repository.save(_make_stop("s8", "Station"))
    stop_2 = stop_repository.save(_make_stop("s9", "Center"))
    assert stop_1.id is not None
    assert stop_2.id is not None

    # Створюємо 5 рейсів, що проходять через stop_1 -> stop_2
    for i in range(5):
        trip = trip_repository.save(
            _make_trip(route.id, f"trip_{i}", schedule_version.id)
        )
        assert trip.id is not None
        stoptime_repository.save(
            _make_stop_time(trip.id, stop_1.id, f"08:0{i}:00", f"08:0{i}:00", 1)
        )
        stoptime_repository.save(
            _make_stop_time(trip.id, stop_2.id, f"08:1{i}:00", f"08:1{i}:00", 2)
        )

    response = client.get(
        f"/journeys?from_stop={stop_1.id}&to_stop={stop_2.id}&page=2&page_size=2"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
