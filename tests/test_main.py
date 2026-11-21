import asyncio
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient as StarletteTestClient

from transit_advisor.main import app as production_app
from transit_advisor.main import log_http_requests
from transit_advisor.rate_limit import SourceRateLimitMiddleware


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


def test_http_middleware_logs_request_statuses(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="transit_advisor.main"):
        with TestClient(production_app) as production_client:
            ok_response = production_client.get("/")
            missing_response = production_client.get("/not-found")

    assert ok_response.status_code == 200
    assert missing_response.status_code == 404
    assert "http_request method=GET path=/ status=200" in caplog.text
    assert "http_request method=GET path=/not-found status=404" in caplog.text


def test_http_middleware_logs_server_errors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/forced-error",
            "raw_path": b"/forced-error",
            "query_string": b"",
            "headers": [],
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "root_path": "",
        }
    )

    async def return_server_error(_: Request) -> Response:
        return Response(status_code=500)

    with caplog.at_level(logging.ERROR, logger="transit_advisor.main"):
        response = asyncio.run(log_http_requests(request, return_server_error))

    assert response.status_code == 500
    assert "http_request method=GET path=/forced-error status=500" in caplog.text


def test_http_middleware_logs_unhandled_exceptions(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/crash",
            "raw_path": b"/crash",
            "query_string": b"",
            "headers": [],
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "root_path": "",
        }
    )

    async def raise_exception(_: Request) -> Response:
        raise RuntimeError("test exception")

    with caplog.at_level(logging.ERROR, logger="transit_advisor.main"):
        with pytest.raises(RuntimeError, match="test exception"):
            asyncio.run(log_http_requests(request, raise_exception))

    assert "http_request_failed method=GET path=/crash" in caplog.text
    assert any(record.exc_info for record in caplog.records)


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


def test_source_rate_limit_returns_429() -> None:
    limited_app = FastAPI()
    limited_app.add_middleware(
        SourceRateLimitMiddleware,
        requests=2,
        window_seconds=60,
    )

    @limited_app.get("/")
    def root() -> dict[str, str]:
        return {"status": "ok"}

    with StarletteTestClient(limited_app) as limited_client:
        first = limited_client.get("/")
        second = limited_client.get("/")
        limited = limited_client.get("/")

    assert first.status_code == 200
    assert second.status_code == 200
    assert limited.status_code == 429
    assert limited.json() == {"detail": "Too many requests"}
    assert limited.headers["Retry-After"] == "60"
    assert limited.headers["X-RateLimit-Limit"] == "2"
    assert limited.headers["X-RateLimit-Remaining"] == "0"
