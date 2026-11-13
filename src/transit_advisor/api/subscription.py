from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from transit_advisor.api.auth import Role, require_role
from transit_advisor.api.dependencies import get_subscription_service
from transit_advisor.api.schemas import (
    CreateSubscriptionRequest,
    SubscriptionResponse,
)
from transit_advisor.domain.exceptions import (
    AlreadySubscribedError,
    RouteNotFoundError,
)
from transit_advisor.services.subscription_service import SubscriptionService

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
        404: {"description": "Route not found."},
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
    try:
        subscription = service.subscribe(
            user_id=request.user_id,
            route_id=request.route_id,
        )
    except RouteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route {request.route_id} not found",
        ) from exc
    except AlreadySubscribedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists.",
        ) from exc

    if subscription.id is None:
        raise RuntimeError("Subscription was saved without an id")

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
    service: Annotated[
        SubscriptionService,
        Depends(get_subscription_service),
    ],
) -> list[SubscriptionResponse]:
    subscriptions = service.list_for_user(user_id)

    return [
        SubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            route_id=sub.route_id,
            is_active=sub.is_active,
        )
        for sub in subscriptions
        if sub.id is not None
    ]
