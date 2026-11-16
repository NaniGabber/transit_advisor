from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_app_is_created(
    app: FastAPI,
) -> None:
    assert app is not None
    assert app.title == "FastAPI"


def test_root_endpoint(
    client: TestClient,
) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_is_available(
    client: TestClient,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "paths" in schema

    assert "/api/v1/imports/gtfs" in schema["paths"]
    assert "/api/v1/subscriptions" in schema["paths"]
    assert "/api/v1/notifications/users/{user_id}" in schema["paths"]
    assert "/api/v1/routes" in schema["paths"]
    assert "/api/v1/stops/{stop_id}/departures" in schema["paths"]


def test_docs_endpoint_is_available(
    client: TestClient,
) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint_is_available(
    client: TestClient,
) -> None:
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
