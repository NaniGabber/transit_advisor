from typing import Annotated

from fastapi import APIRouter, Depends

from transit_advisor.api.dependencies import get_notification_repository
from transit_advisor.api.schemas import NotificationResponse
from transit_advisor.domain.notification import Notification
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get(
    "/users/{user_id}",
    response_model=list[NotificationResponse],
)
def get_notifications(
    user_id: int,
    repository: Annotated[
        SqlAlchemyNotificationRepository,
        Depends(get_notification_repository),
    ],
) -> list[Notification]:
    return repository.find_by_user_id(user_id)


@router.get(
    "/users/{user_id}/unread",
    response_model=list[NotificationResponse],
)
def get_unread_notifications(
    user_id: int,
    repository: Annotated[
        SqlAlchemyNotificationRepository,
        Depends(get_notification_repository),
    ],
) -> list[Notification]:
    return repository.find_unread_by_user_id(user_id)
