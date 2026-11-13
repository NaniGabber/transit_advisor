from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from transit_advisor.api.auth import Role, require_role
from transit_advisor.api.dependencies import (
    get_subscription_repository,
    get_subscription_service,
)
from transit_advisor.api.schemas import (
    CreateSubscriptionRequest,
    SubscriptionResponse,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from transit_advisor.services.subscription_service import (
    SubscriptionService,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.USER, Role.ADMIN))],
    responses={
        403: {"description": "Only user or admin can subscribe."},
        409: {"description": "Subscription already exists."},
    },
)
def create_subscription(
    request: CreateSubscriptionRequest,
    service: Annotated[
        SubscriptionService,
        Depends(get_subscription_service),
    ],
) -> SubscriptionResponse:
    subscription = service.subscribe(
        user_id=request.user_id,
        route_id=request.route_id,
    )

    if subscription is None or subscription.id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists.",
        )

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        route_id=subscription.route_id,
        is_active=subscription.is_active,
    )


@router.get(
    "/users/{user_id}",
    response_model=list[SubscriptionResponse],
)
def get_subscriptions(
    user_id: int,
    repository: Annotated[
        SqlAlchemySubscriptionRepository,
        Depends(get_subscription_repository),
    ],
) -> list[SubscriptionResponse]:
    subscriptions = repository.find_by_user_id(
        user_id,
    )

    return [
        SubscriptionResponse(
            id=subscription.id or 0,
            user_id=subscription.user_id,
            route_id=subscription.route_id,
            is_active=subscription.is_active,
        )
        for subscription in subscriptions
    ]
