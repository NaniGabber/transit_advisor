from typing import Protocol

from transit_advisor.domain.notification import (
    Notification,
)


class NotificationRepository(Protocol):
    def save(
        self,
        notification: Notification,
    ) -> Notification: ...

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]: ...

    def find_unread_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]: ...
