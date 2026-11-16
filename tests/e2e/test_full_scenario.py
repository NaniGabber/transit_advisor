from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import make_zip
from transit_advisor.infrastructure.database.models.notification import (
    NotificationModel,
)
from transit_advisor.infrastructure.database.models.route import RouteModel
from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)
from transit_advisor.infrastructure.database.models.stoptime import (
    StopTimeModel,
)
from transit_advisor.infrastructure.database.models.trip import TripModel


def test_full_e2e_flow(
    client: TestClient,
    session: Session,
) -> None:
    # ---------- GTFS v1 ----------

    feed_v1 = make_zip(
        {
            "agency.txt": (
                b"agency_id,agency_name,agency_timezone\nagency_1,Metro,Europe/Kyiv\n"
            ),
            "routes.txt": (
                b"route_id,agency_id,route_short_name,route_type\n"
                b"route_1,agency_1,11,3\n"
            ),
            "stops.txt": (
                b"stop_id,stop_name,stop_lat,stop_lon\nstop_1,Central,50.0,36.0\n"
            ),
            "trips.txt": (b"route_id,trip_id,service_id\nroute_1,trip_1,WEEKDAY\n"),
            "stop_times.txt": (
                b"trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                b"trip_1,08:00:00,08:00:00,stop_1,1\n"
            ),
        }
    )

    response = client.post(
        "/api/v1/imports/gtfs",
        headers={"X-Role": "admin"},
        files={
            "file": (
                "feed_v1.zip",
                feed_v1,
                "application/zip",
            )
        },
    )

    assert response.status_code == 201

    checksum_v1 = response.json()["checksum"]

    # ---------- Повторний імпорт ----------

    duplicate = client.post(
        "/api/v1/imports/gtfs",
        headers={"X-Role": "admin"},
        files={
            "file": (
                "feed_v1.zip",
                feed_v1,
                "application/zip",
            )
        },
    )

    assert duplicate.status_code == 409

    # ---------- Пошук маршруту ----------

    routes = client.get("/api/v1/routes?q=11")

    assert routes.status_code == 200
    assert len(routes.json()) == 1

    route_id = routes.json()[0]["id"]

    # ---------- Створення підписки ----------

    subscription = client.post(
        "/api/v1/subscriptions",
        headers={"X-Role": "user"},
        json={
            "user_id": 1,
            "route_id": route_id,
        },
    )

    assert subscription.status_code == 201

    # ---------- GTFS v2 ----------

    feed_v2 = make_zip(
        {
            "agency.txt": (
                b"agency_id,agency_name,agency_timezone\nagency_1,Metro,Europe/Kyiv\n"
            ),
            "routes.txt": (
                b"route_id,agency_id,route_short_name,route_type\n"
                b"route_1,agency_1,11,3\n"
            ),
            "stops.txt": (
                b"stop_id,stop_name,stop_lat,stop_lon\nstop_1,Central,50.0,36.0\n"
            ),
            "trips.txt": (b"route_id,trip_id,service_id\nroute_1,trip_1,WEEKDAY\n"),
            "stop_times.txt": (
                b"trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                b"trip_1,08:30:00,08:30:00,stop_1,1\n"
            ),
        }
    )

    response = client.post(
        "/api/v1/imports/gtfs",
        headers={"X-Role": "admin"},
        files={
            "file": (
                "feed_v2.zip",
                feed_v2,
                "application/zip",
            )
        },
    )

    assert response.status_code == 201

    checksum_v2 = response.json()["checksum"]

    assert checksum_v1 != checksum_v2

    # ---------- Перевірка повідомлень ----------

    notifications = client.get("/api/v1/notifications/users/1")

    assert notifications.status_code == 200

    payload = notifications.json()

    assert len(payload) == 1
    assert "changed" in payload[0]["message"].lower()

    # ---------- Перевірка БД ----------

    assert session.query(ScheduleVersionModel).count() == 2
    assert session.query(RouteModel).count() == 1
    assert session.query(TripModel).count() >= 1
    assert session.query(StopTimeModel).count() >= 1
    assert session.query(NotificationModel).count() == 1
