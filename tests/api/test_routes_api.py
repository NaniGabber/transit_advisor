from collections.abc import Callable
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.trip import SqlAlchemyTripRepository


def test_search_routes_returns_all(
    client: TestClient,
    route_factory: Callable[[str], Route],
) -> None:
    route_factory("11")
    route_factory("15")

    response = client.get("/api/v1/routes")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_search_routes_by_query(
    client: TestClient,
    route_factory: Callable[[str], Route],
) -> None:
    route_factory("11")
    route_factory("15")

    response = client.get("/api/v1/routes?q=15")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["route_id"] == "15"


def test_search_routes_returns_empty_for_unknown_query(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/routes?q=nonexistent")

    assert response.status_code == 200
    assert response.json() == []


def test_search_routes_applies_pagination(
    client: TestClient,
    route_factory: Callable[[str], Route],
) -> None:
    for i in range(5):
        route_factory(f"route_{i}")

    response = client.get("/api/v1/routes?page=2&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_route_diff_compares_non_consecutive_versions(
    client: TestClient,
    route_factory: Callable[[str], Route],
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_factory: Callable[[int, str], Trip],
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    stop_factory: Callable[[str, str], Stop],
    stop: Stop,
) -> None:
    route = route_factory("1001")
    assert route.id is not None
    assert stop.id is not None
    intermediate_stop = stop_factory("2", "Intermediate stop")
    assert intermediate_stop.id is not None

    intermediate_version = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="b" * 64,
            imported_at=datetime(2026, 2, 1, tzinfo=UTC),
        )
    )
    version_3 = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="c" * 64,
            imported_at=datetime(2026, 3, 1, tzinfo=UTC),
        )
    )
    assert intermediate_version.id is not None
    assert version_3.id is not None

    trip_1 = trip_factory(route.id, "trip_1")
    assert trip_1.id is not None
    assert trip_1.schedule_version_id is not None
    assert trip_1.schedule_version_id < intermediate_version.id < version_3.id

    intermediate_trip = trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="trip_1",
            service_id="WEEKDAY",
            schedule_version_id=intermediate_version.id,
        )
    )
    assert intermediate_trip.id is not None
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=intermediate_trip.id,
            stop_id=intermediate_stop.id,
            arrival_time="10:00:00",
            departure_time="10:00:00",
            stop_sequence=1,
        )
    )
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_1.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:00:00",
            stop_sequence=1,
        )
    )

    trip_2 = trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="trip_1",
            service_id="WEEKDAY",
            schedule_version_id=version_3.id,
        )
    )
    assert trip_2.id is not None
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_2.id,
            stop_id=stop.id,
            arrival_time="09:00:00",
            departure_time="09:00:00",
            stop_sequence=1,
        )
    )

    response = client.get(
        f"/api/v1/routes/{route.id}/diff?from_version={trip_1.schedule_version_id}"
        f"&to_version={version_3.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["from_version"] == trip_1.schedule_version_id
    assert data["to_version"] == version_3.id
    assert data["changed_stop_times"] == {"1001": [stop.id]}


def test_route_diff_returns_404_for_unknown_route(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/routes/999/diff?from_version=1&to_version=2")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_route_diff_returns_404_when_route_has_no_trips_in_either_version(
    client: TestClient,
    route_factory: Callable[[str], Route],
    schedule_version: ScheduleVersion,
) -> None:
    route = route_factory("1001")
    assert route.id is not None
    assert schedule_version.id is not None

    response = client.get(
        f"/api/v1/routes/{route.id}/diff"
        f"?from_version={schedule_version.id}&to_version={schedule_version.id}"
    )

    assert response.status_code == 404
    assert "no trips" in response.json()["detail"].lower()
