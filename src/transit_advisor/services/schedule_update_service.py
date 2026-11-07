from transit_advisor.domain.repositories.route import (
    RouteRepository,
)
from transit_advisor.domain.repositories.stoptime import (
    StopTimeRepository,
)
from transit_advisor.domain.repositories.subscription import (
    SubscriptionRepository,
)
from transit_advisor.domain.repositories.trip import TripRepository
from transit_advisor.domain.route import Route
from transit_advisor.domain.stoptime import StopTime
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
        trip_repository: TripRepository,
        stoptime_repository: StopTimeRepository,
    ) -> None:
        self._diff_service = diff_service
        self._notification_service = notification_service
        self._subscription_repository = subscription_repository
        self._route_repository = route_repository
        self._trip_repository = trip_repository
        self._stoptime_repository = stoptime_repository

    def process_update(
        self,
        old_routes: list[Route],
        new_routes: list[Route],
        schedule_version_id: int,
        old_stop_times: list[StopTime] | None = None,
        new_stop_times: list[StopTime] | None = None,
        trip_to_route: dict[int, str] | None = None,
    ) -> int:
        diff = self._diff_service.compare_routes(
            old_routes,
            new_routes,
            old_stop_times=old_stop_times,
            new_stop_times=new_stop_times,
            trip_to_route=trip_to_route,
        )

        created_notifications = 0

        for gtfs_route_id in diff.changed_stop_times:
            route = self._route_repository.find_by_route_id(gtfs_route_id)
            if route is None or route.id is None:
                continue

            subscriptions = self._subscription_repository.find_by_route_id(route.id)
            for subscription in subscriptions:
                self._notification_service.create_notification(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id or 0,
                    schedule_version_id=schedule_version_id,
                    message=f"Schedule for route {gtfs_route_id} has changed",
                )
                created_notifications += 1

        return created_notifications

    def process_version_update(
        self,
        old_version_id: int,
        new_version_id: int,
        schedule_version_id: int,
    ) -> int:
        old_trips = self._trip_repository.find_by_schedule_version_id(old_version_id)
        new_trips = self._trip_repository.find_by_schedule_version_id(new_version_id)

        old_stop_times = self._stoptime_repository.find_by_trip_ids(
            [t.id for t in old_trips if t.id is not None]
        )
        new_stop_times = self._stoptime_repository.find_by_trip_ids(
            [t.id for t in new_trips if t.id is not None]
        )

        trip_to_route: dict[str, str] = {}
        for trip in [*old_trips, *new_trips]:
            route = self._route_repository.find_by_id(trip.route_id)
            if route is not None:
                trip_to_route[trip.trip_id] = route.route_id

        diff = self._diff_service.compare_versions(
            old_trips=old_trips,
            new_trips=new_trips,
            old_stop_times=old_stop_times,
            new_stop_times=new_stop_times,
            trip_to_route=trip_to_route,
        )

        created_notifications = 0
        for gtfs_route_id, changed_stop_ids in diff.changed_stop_times.items():
            route = self._route_repository.find_by_route_id(gtfs_route_id)
            if route is None or route.id is None:
                continue

            subscriptions = self._subscription_repository.find_by_route_id(route.id)
            for subscription in subscriptions:
                self._notification_service.create_notification(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id or 0,
                    schedule_version_id=schedule_version_id,
                    message=(
                        f"Schedule for route {gtfs_route_id} has changed "
                        f"at stops {sorted(changed_stop_ids)}"
                    ),
                )
                created_notifications += 1

        return created_notifications
