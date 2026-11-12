from fastapi import FastAPI

from transit_advisor.api.analytics import router as analytics_router
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

app = FastAPI()


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
