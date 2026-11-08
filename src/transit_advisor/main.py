from fastapi import FastAPI

from transit_advisor.api.feeds import (
    router as feeds_router,
)
from transit_advisor.api.notification import (
    router as notifications_router,
)
from transit_advisor.api.subscription import (
    router as subscriptions_router,
)

from transit_advisor.api.routes import (
    router as routes_router,
)

app = FastAPI()

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
