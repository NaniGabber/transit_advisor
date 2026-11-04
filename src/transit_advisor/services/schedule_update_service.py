from transit_advisor.domain.repositories.route import (
    RouteRepository,
)
from transit_advisor.domain.repositories.subscription import (
    SubscriptionRepository,
)
from transit_advisor.domain.route import Route
from transit_advisor.services.notification_service import (
    NotificationService,
)
from transit_advisor.services.schedule_diff_service import (
    ScheduleDiffService,
)


class ScheduleUpdateService:
    def __init__(
        self,
        diff_service: ScheduleDiffService,
        notification_service: NotificationService,
        subscription_repository: SubscriptionRepository,
        route_repository: RouteRepository,
    ) -> None:
        self._diff_service = diff_service
        self._notification_service = notification_service
        self._subscription_repository = subscription_repository
        self._route_repository = route_repository

    def process_update(
        self,
        old_routes: list[Route],
        new_routes: list[Route],
        schedule_version_id: int,
    ) -> int:
        diff = self._diff_service.compare_routes(
            old_routes,
            new_routes,
        )

        created_notifications = 0

        for gtfs_route_id in diff.added_routes:
            route = self._route_repository.find_by_route_id(
                gtfs_route_id,
            )

            if route is None:
                continue

            if route.id is None:
                continue

            subscriptions = self._subscription_repository.find_by_route_id(
                route.id,
            )

            for subscription in subscriptions:
                self._notification_service.create_notification(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id or 0,
                    schedule_version_id=schedule_version_id,
                    message=f"Route {gtfs_route_id} was added",
                )
                created_notifications += 1

        return created_notifications
