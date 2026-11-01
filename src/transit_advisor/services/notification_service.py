from datetime import datetime

from transit_advisor.domain.notification import (
    Notification,
)
from transit_advisor.domain.repositories.notification import (
    NotificationRepository,
)
from transit_advisor.domain.schedulediff import (
    ScheduleDiff,
)
from transit_advisor.domain.subscription import (
    Subscription,
)


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
    ) -> None:
        self._notification_repository = notification_repository

    def create_notification(
        self,
        user_id: int,
        subscription_id: int,
        schedule_version_id: int,
        message: str,
    ) -> Notification:
        notification = Notification(
            id=None,
            user_id=user_id,
            subscription_id=subscription_id,
            schedule_version_id=schedule_version_id,
            message=message,
            created_at=datetime.now(),
        )

        return self._notification_repository.save(
            notification,
        )

    def notify_about_added_routes(
        self,
        diff: ScheduleDiff,
        subscriptions: list[Subscription],
        schedule_version_id: int,
    ) -> int:
        created = 0

        for route_id in diff.added_routes:
            for subscription in subscriptions:
                if subscription.id is None:
                    continue

                if subscription.route_id != int(route_id):
                    continue

                self.create_notification(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id,
                    schedule_version_id=schedule_version_id,
                    message=f"Route {route_id} was added",
                )

                created += 1

        return created
