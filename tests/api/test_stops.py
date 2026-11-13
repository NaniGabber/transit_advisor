from collections.abc import Callable

from fastapi.testclient import TestClient

from transit_advisor.domain.route import Route
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)


def _save_stop_time(
    repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
    arrival_time: str,
    departure_time: str,
    stop_sequence: int,
) -> StopTime:
    assert trip.id is not None
    assert stop.id is not None
    return repository.save(
        StopTime(
            id=None,
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_sequence=stop_sequence,
        )
    )


def test_get_departures_returns_departures(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    _save_stop_time(stoptime_repository, trip, stop, "08:00:00", "08:00:00", 1)
    _save_stop_time(stoptime_repository, trip, stop, "09:00:00", "09:00:00", 2)

    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "00:00"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_departures_filters_by_from_time(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    _save_stop_time(stoptime_repository, trip, stop, "07:00:00", "07:00:00", 1)
    _save_stop_time(stoptime_repository, trip, stop, "08:00:00", "08:00:00", 2)
    _save_stop_time(stoptime_repository, trip, stop, "09:00:00", "09:00:00", 3)

    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "08:00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(dep["departure_time"] >= "08:00:00" for dep in data)


def test_get_departures_returns_empty_when_no_match(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    _save_stop_time(stoptime_repository, trip, stop, "07:00:00", "07:00:00", 1)

    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "23:00"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_departures_invalid_time_format_returns_422(
    client: TestClient,
    stop: Stop,
) -> None:
    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "not-a-time"},
    )

    assert response.status_code == 422
    assert "Invalid time format" in response.json()["detail"]


def test_get_departures_applies_pagination(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip_factory: Callable[[int, str], Trip],
    route: Route,
    stop: Stop,
) -> None:
    assert route.id is not None

    for i in range(1, 6):
        trip = trip_factory(route.id, f"trip_{i}")
        _save_stop_time(
            stoptime_repository,
            trip,
            stop,
            f"{8 + i:02d}:00:00",
            f"{8 + i:02d}:00:00",
            i,
        )

    assert stop.id is not None

    page1 = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "00:00", "page": 1, "page_size": 2},
    )
    page2 = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "00:00", "page": 2, "page_size": 2},
    )
    page3 = client.get(
        f"/stops/{stop.id}/departures",
        params={"from": "00:00", "page": 3, "page_size": 2},
    )

    assert page1.status_code == 200
    assert page2.status_code == 200
    assert page3.status_code == 200
    assert len(page1.json()) == 2
    assert len(page2.json()) == 2
    assert len(page3.json()) == 1
    assert page1.json()[0]["departure_time"] < page2.json()[0]["departure_time"]


def test_get_departures_page_size_exceeds_max_returns_422(
    client: TestClient,
    stop: Stop,
) -> None:
    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"page_size": 101},
    )
    assert response.status_code == 422


def test_get_departures_page_less_than_one_returns_422(
    client: TestClient,
    stop: Stop,
) -> None:
    assert stop.id is not None
    response = client.get(
        f"/stops/{stop.id}/departures",
        params={"page": 0},
    )
    assert response.status_code == 422


def test_get_departures_filters_by_stop(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop_factory: Callable[[str, str], Stop],
) -> None:
    stop1 = stop_factory("1", "Stop 1")
    stop2 = stop_factory("2", "Stop 2")

    _save_stop_time(stoptime_repository, trip, stop1, "08:00:00", "08:00:00", 1)
    _save_stop_time(stoptime_repository, trip, stop2, "09:00:00", "09:00:00", 2)

    assert stop1.id is not None
    response = client.get(
        f"/stops/{stop1.id}/departures",
        params={"from": "00:00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stop_id"] == stop1.id


def test_get_departures_nonexistent_stop_returns_empty(
    client: TestClient,
) -> None:
    response = client.get(
        "/stops/999999/departures",
        params={"from": "00:00"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_departures_defaults_to_now(
    client: TestClient,
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    """Без `from` — фільтр `from_time = now`. Перевіряємо, що запит
    не падає і повертає список (кількість залежить від поточного часу)."""
    _save_stop_time(stoptime_repository, trip, stop, "00:00:00", "00:00:00", 1)
    _save_stop_time(stoptime_repository, trip, stop, "23:59:00", "23:59:00", 2)

    assert stop.id is not None
    response = client.get(f"/stops/{stop.id}/departures")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
