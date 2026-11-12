from fastapi.testclient import TestClient


def test_trips_by_day_returns_dict(client: TestClient) -> None:
    response = client.get("/analytics/routes/1/trips-by-day")

    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == 1
    assert isinstance(data["trips_by_day"], dict)


def test_headway_returns_float_or_none(client: TestClient) -> None:
    response = client.get("/analytics/routes/1/headway")

    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == 1
    assert "average_headway_minutes" in data
    assert data["average_headway_minutes"] is None or isinstance(
        data["average_headway_minutes"], float
    )


def test_top_stops_returns_list(client: TestClient) -> None:
    response = client.get("/analytics/stops/top?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert "stops" in data
    assert isinstance(data["stops"], list)
    assert len(data["stops"]) <= 3


def test_trips_by_day_for_unknown_route_returns_empty(client: TestClient) -> None:
    response = client.get("/analytics/routes/999/trips-by-day")

    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == 999
    assert data["trips_by_day"] == {}


def test_headway_for_unknown_route_returns_none(client: TestClient) -> None:
    response = client.get("/analytics/routes/999/headway")

    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == 999
    assert data["average_headway_minutes"] is None
