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

    response = client.get("/routes")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_search_routes_by_query(
    client: TestClient,
    route_factory: Callable[[str], Route],
) -> None:
    route_factory("11")
    route_factory("15")

    response = client.get("/routes?q=15")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["route_id"] == "15"


def test_search_routes_returns_empty_for_unknown_query(
    client: TestClient,
) -> None:
    response = client.get("/routes?q=nonexistent")

    assert response.status_code == 200
    assert response.json() == []


def test_search_routes_applies_pagination(
    client: TestClient,
    route_factory: Callable[[str], Route],
) -> None:
    for i in range(5):
        route_factory(f"route_{i}")

    response = client.get("/routes?page=2&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_route_diff_returns_changes(
    client: TestClient,
    route_factory: Callable[[str], Route],
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_factory: Callable[[int, str], Trip],
    trip_repository: SqlAlchemyTripRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    stop: Stop,
) -> None:
    route = route_factory("1001")
    assert route.id is not None
    assert stop.id is not None

    version_2 = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="b" * 64,
            imported_at=datetime(2026, 2, 1, tzinfo=UTC),
        )
    )
    assert version_2.id is not None

    trip_1 = trip_factory(route.id, "trip_1")
    assert trip_1.id is not None
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
            schedule_version_id=version_2.id,
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
        f"/routes/{route.id}/diff?from_version={trip_1.schedule_version_id}&to_version={version_2.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["from_version"] == trip_1.schedule_version_id
    assert data["to_version"] == version_2.id
    assert data["changed_stop_times"] == {"1001": [stop.id]}


def test_route_diff_returns_404_for_unknown_route(
    client: TestClient,
) -> None:
    response = client.get("/routes/999/diff?from_version=1&to_version=2")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
