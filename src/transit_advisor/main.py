import logging
from time import perf_counter

from fastapi import FastAPI
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from transit_advisor.api.analytics import router as analytics_router
from transit_advisor.api.database_transfer import router as database_transfer_router
from transit_advisor.api.feeds import (
    router as feeds_router,
)
from transit_advisor.api.journeys import router as journeys_router
from transit_advisor.api.notification import (
    router as notifications_router,
)
from transit_advisor.api.routes import (
    router as routes_router,
)
from transit_advisor.api.stops import router as stops_router
from transit_advisor.api.subscription import (
    router as subscriptions_router,
)
from transit_advisor.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI()


@app.middleware("http")
async def log_http_requests(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "http_request_failed method=%s path=%s",
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    log_message = (
        "http_request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    if response.status_code >= 500:
        logger.error(*log_message)
    elif response.status_code >= 400:
        logger.warning(*log_message)
    else:
        logger.info(*log_message)
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    feeds_router,
)

app.include_router(
    subscriptions_router,
)

app.include_router(
    notifications_router,
)

app.include_router(
    routes_router,
)

app.include_router(
    stops_router,
)

app.include_router(
    journeys_router,
)

app.include_router(
    analytics_router,
)

app.include_router(
    database_transfer_router,
)
