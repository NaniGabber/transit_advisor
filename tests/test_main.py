from fastapi.testclient import TestClient

from transit_advisor.main import app

client = TestClient(app)


def test_app_is_created() -> None:
    assert app is not None
    assert app.title == "FastAPI"


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_is_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/feeds" in schema["paths"]
    assert "/subscriptions" in schema["paths"]
    assert "/notifications/users/{user_id}" in schema["paths"]
    assert "/routes" in schema["paths"]
    assert "/stops/{stop_id}/departures" in schema["paths"]


def test_docs_endpoint_is_available() -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint_is_available() -> None:
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
