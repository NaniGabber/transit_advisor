from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import make_zip


def _gtfs_zip() -> bytes:
    return make_zip(
        {
            "agency.txt": b"agency_id,agency_name\nmetro,Kharkiv Metro\n",
            "routes.txt": b"",
            "stops.txt": b"",
            "trips.txt": b"",
            "stop_times.txt": b"",
        }
    )


def test_upload_imports_new_feed(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post(
        "/feeds",
        files={
            "file": (
                "feed.zip",
                _gtfs_zip(),
                "application/zip",
            ),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["imported"] is True
    assert body["duplicate"] is False
    assert body["checksum"]


def test_upload_duplicate_returns_409(
    client: TestClient,
    session: Session,
) -> None:
    client.post(
        "/feeds",
        files={
            "file": (
                "feed.zip",
                _gtfs_zip(),
                "application/zip",
            ),
        },
    )

    response = client.post(
        "/feeds",
        files={
            "file": (
                "feed.zip",
                _gtfs_zip(),
                "application/zip",
            ),
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_upload_invalid_feed_returns_422(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post(
        "/feeds",
        files={
            "file": (
                "feed.zip",
                make_zip(
                    {
                        "not_a_gtfs_file.txt": b"",
                    }
                ),
                "application/zip",
            ),
        },
    )

    assert response.status_code == 422
    assert "validation" in response.json()["detail"].lower()


def test_upload_non_zip_file_returns_422(
    client: TestClient,
    session: Session,
) -> None:
    response = client.post(
        "/feeds",
        files={
            "file": (
                "feed.zip",
                b"this is not a zip archive",
                "application/zip",
            ),
        },
    )

    assert response.status_code == 422
    assert "zip" in response.json()["detail"].lower()
