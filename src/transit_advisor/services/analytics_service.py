from transit_advisor.infrastructure.repositories.analytics import (
    SqlAlchemyAnalyticsRepository,
)


class AnalyticsService:
    def __init__(
        self,
        analytics_repository: SqlAlchemyAnalyticsRepository,
    ) -> None:
        self._analytics_repository = analytics_repository

    def trips_by_day(self, route_id: int) -> dict[str, int]:
        return self._analytics_repository.count_trips_by_day(route_id)

    def average_headway(self, route_id: int) -> float | None:
        return self._analytics_repository.average_headway_minutes(route_id)

    def top_stops(self, limit: int = 10) -> list[tuple[int, int]]:
        return self._analytics_repository.top_stops(limit)
