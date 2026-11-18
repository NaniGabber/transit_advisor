import logging

from transit_advisor.infrastructure.repositories.analytics import (
    SqlAlchemyAnalyticsRepository,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(
        self,
        analytics_repository: SqlAlchemyAnalyticsRepository,
    ) -> None:
        self._analytics_repository = analytics_repository

    def trips_by_day(self, route_id: int) -> dict[str, int]:
        result = self._analytics_repository.count_trips_by_day(route_id)
        logger.debug(
            "trips_by_day_calculated route_id=%s services=%s",
            route_id,
            len(result),
        )
        return result

    def average_headway(self, route_id: int) -> float | None:
        result = self._analytics_repository.average_headway_minutes(route_id)
        logger.debug(
            "headway_calculated route_id=%s has_result=%s",
            route_id,
            result is not None,
        )
        return result

    def top_stops(self, limit: int = 10) -> list[tuple[int, int]]:
        result = self._analytics_repository.top_stops(limit)
        logger.debug("top_stops_calculated limit=%s count=%s", limit, len(result))
        return result
